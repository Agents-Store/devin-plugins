# Embedding providers: credentials and how each one fails

The families the runtime can embed with, what credential each one actually expects, and the signature
that tells you which failure you are looking at. Provider identifiers and model names in a real config
are **echoed from this instance** (`memory status --json`, the runtime's own docs, the model
catalogue) — the families below are for recognition, not for pasting.

## Reading the real identifiers off the instance

The provider **id** that goes into a config is an enum value of the installed runtime, so it is
fetched, never recalled: list what this build actually supports (`memory status --json` for what is
configured now, the runtime's own provider documentation for the full set, the model catalogue for
model names) and match it against the family rows below. A family name here is a recognition handle;
the id you write into a config, and every model name beside it, is copied from that read. An id
that no longer exists in the installed build is a finding, not a typo to guess around.

## The table

| Provider family | Credential it expects | Runs locally | How its failure reads |
|---|---|---|---|
| Hosted default (the general-purpose API vendor, also the shape every "compatible" endpoint imitates) | API key, delivered by name from the secret store | no | authorization error on the embedding route while chat still works → almost always the key/session confusion below |
| Second large-vendor API | API key from that vendor's console | no | authorization error naming the vendor's own auth scheme; a chat-only credential does not carry over |
| Dedicated embedding vendors (retrieval specialists) | API key | no | plan/quota errors are common and read as authorization failures; check quota before rotating anything |
| Aggregators and inference marketplaces | API key issued by the aggregator | no | the aggregator's error text names the *upstream* model, which misleads you into blaming the model vendor |
| Cloud-platform embeddings | cloud credentials plus a region, not a bare key | no | fails at signing or region resolution, not at "invalid key"; a key-shaped fix will not apply |
| Subscription coding-assistant backends | an OAuth **session**, not a key | no | **covers chat completions only and does not satisfy embedding requests** — see below. This is the single most common cause of a fleet-wide dead index |
| Local runtimes (a local model server, a desktop model host, an in-process engine) | none | **yes** | connection refused, model not present, or a dimension mismatch — never an authorization error |
| Generic compatible endpoint | whatever that endpoint requires, usually an API key | depends | inherits the failure vocabulary of whatever is behind it; identify the real backend before diagnosing |

## Credential classes, and why the class is the whole diagnosis

Four classes, and they are not interchangeable:

1. **API key** — a long-lived string, scoped to an account, valid on every route that account can use.
2. **OAuth session** — issued for an interactive product, scoped to that product's routes, refreshed
   on a **single-use** rotating token.
3. **Cloud signature** — derived from platform credentials and a region.
4. **None** — local providers.

An embedding call that fails authorization while chat succeeds on the same account is class 2
presented where class 1 was required. The account is fine, the session is fine, the route is not
covered. No amount of re-authenticating changes that, and each attempt spends a single-use refresh
token that another consumer of the same account may be relying on. Fix the class, not the token.

## Diagnostic ladder

Run in this order; stop at the first answer. Every step is a read.

1. **What does the config actually name** as the embedding provider and model — as opposed to what
   the chat chain names? They are separate settings and drift apart silently.
2. **Which credential does that provider expect** (the table above)? If it expects a key and the
   configuration points at a session profile, you are done.
3. **Is the key delivered?** By **name and length only** — the environment name is populated inside
   the container, or it is not. `fleet.secrets.delivery-short` when a referenced name is missing.
4. **Does the fingerprint match** the one in the secret store? `redact.fp` gives the comparison; the
   values never appear on either side of it.
5. **Is the index paused** on an identity mismatch rather than failing? Then nothing is broken —
   something changed and the reindex has not been run.
6. **Is the last index timestamp** far behind current activity? Indexing stopped when the provider
   broke; fix the provider before reindexing, or the reindex just fails more slowly.
7. **Was the provider recently fixed but search is still poor?** Full restart, not reload.

## Choosing or changing a provider

- **Any** change of provider, model or chunking invalidates the index identity and requires an
  explicit reindex. There is no in-place migration and no partial reuse: different models produce
  vectors that are not comparable, and a dimension change is not even representable in the old index.
- Local providers remove the credential problem entirely and replace it with a capacity problem: the
  model must be present, resident, and fast enough that reindexing a corpus finishes.
- Per-instance keys over one shared key: a shared key makes a single revocation a fleet-wide outage,
  makes spend unattributable, and makes rotation a fleet-wide reindex instead of a local one.
- Cost lands in two places — the one-off reindex of the whole corpus, and the per-write embedding
  after that. Only the first is visible as a spike, and it is the one that lands mid-workday if
  nobody schedules it.

## Standing rules

- **Never read or print a key value**, in any step, for any reason. Presence, fingerprint, size
  bucket and expiry answer every diagnostic question a value could answer.
- **Never copy an OAuth profile between instances.** Key- and static-token entries are portable;
  OAuth entries are not, and a copy authenticates for a while before failing in a way that looks
  like something else.
- **Never disable an explicitly configured provider to make an error go away.** Fail-closed is what
  makes this subsystem observable; removing it buys silence, not health.
