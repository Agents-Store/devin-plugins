---
name: sdk-patterns
description: This skill should be used when the user asks for a "Vaultwarden SDK" or "Bitwarden SDK for Vaultwarden", to "automate Vaultwarden from Python", "use python-vaultwarden", "manage Vaultwarden with Terraform", or wants a library rather than curl/bw for a self-hosted Vaultwarden.
---

# Vaultwarden SDK Patterns — Python and Terraform

There is no official Vaultwarden SDK, and Bitwarden's SDKs (`bitwarden-sdk`, `sdk-sm`) target Secrets Manager, which Vaultwarden does not implement. Two community libraries cover most automation:

| Need | Library | Status (2026-10) |
|---|---|---|
| Server admin (users, 2FA, invites) and org members/collections from Python | `python-vaultwarden` (Numberly, Apache-2.0) | 1.1.2, 2026-05-27; tested upstream up to Vaultwarden 1.34.3 |
| Vault items, folders, collections as infrastructure-as-code | Terraform provider `maxlaverse/bitwarden` (MPL-2.0) | v0.21.0, 2026-09-30; tested against Vaultwarden 1.33.2 |

Neither is tested against 1.37.x by its maintainers — run a read-only call against the target server before relying on writes, and report breakage to the library's issue tracker (and to this plugin via `/plugin-creator:feedback` where available).

## python-vaultwarden

```bash
python3 -m pip install python-vaultwarden        # Python >= 3.10
```

### Admin client (wraps `/admin`)

```python
import os
from vaultwarden.clients.vaultwarden import VaultwardenAdminClient

admin = VaultwardenAdminClient(
    url=os.environ["VW_URL"],                     # https://vault.example.com
    admin_secret_token=os.environ["VW_ADMIN_TOKEN"],
    preload_users=True,                           # required argument, no default
)

for user in admin.users(enabled=True):
    print(user.Email, user.Id)

user = admin.get_user(email="someone@example.com")   # None if absent; admin.user(...) raises instead
if user:
    admin.remove_2fa(uuid=str(user.Id))              # pass uuid=; email= alone posts to users/None/...
    admin.disable(user.Id)                           # also ends all sessions
    admin.enable(user.Id)

admin.invite("new.person@example.com")               # a 409 "already exists" counts as success
```

Methods: `users(as_email_dict=False, as_uuid_dict=False, force_refresh=False, mfa=None, enabled=None, exclude_invited=False)`, `user(email=, uuid=)`, `get_user(email=, uuid=)`, `invite(email)`, `delete(identifier)`, `disable(identifier)`, `enable(identifier)`, `set_user_enabled(identifier, enabled)`, `remove_2fa(uuid=)`, `reset_account(email, admin_bitwarden_client)`, `transfer_account_rights(previous_email, new_email, admin_bitwarden_client)`. There is no `deauth` method — call `POST /admin/users/<id>/deauth` directly (`vaultwarden-dev:admin-panel`).

### Bitwarden API client (org members and collections)

Logs in with a personal API key and decrypts org keys and collection names with the master password.

```python
import os
from vaultwarden.clients.bitwarden import BitwardenAPIClient
from vaultwarden.models.bitwarden import get_organization

bw = BitwardenAPIClient(
    url=os.environ["VW_URL"],
    email=os.environ.get("VW_EMAIL"),               # fetched from the profile when None
    password=os.environ["BW_PASSWORD"],             # master password: decrypts org key + collection names
    client_id=os.environ["BW_CLIENTID"],            # user.<uuid>
    client_secret=os.environ["BW_CLIENTSECRET"],
    device_id=os.environ["VW_DEVICE_ID"],           # required (README omits it); keep it stable
)

org = get_organization(bw, os.environ["VW_ORG_ID"])
infra = org.collection("Infra") or org.create_collection("Infra")
org.invite("new.person@example.com", collections=[infra.Id], default_readonly=True)

for member in org.users():
    print(member.Email, member.Status, member.Type)

member = org.user_search("new.person@example.com")
member.add_collections([infra.Id])
```

`Organization` also offers `users(search=, mfa=)`, `user(id)`, `collections(as_dict=)`, `delete_collection(id)`, `rename(name)`, `ciphers(collection=)`; a collection offers `users()` and `set_users([...], default_readonly=, default_hide_passwords=, default_manage=)`; a member offers `add_collections`, `remove_collections`, `update_collection`, `delete()`. For anything missing, `bw.api_request("GET", "api/organizations/<org-uuid>/policies")` sends an authenticated raw call.

Notes:
- Keep `device_id` constant (store it with the script's config) so each run is not a new device with a new-device email.
- It cannot confirm members — use `bw confirm org-member`.
- Read all credentials from the environment or a secret store; never hardcode them in the script.

## Terraform: `maxlaverse/bitwarden`

```hcl
terraform {
  required_providers {
    bitwarden = { source = "maxlaverse/bitwarden", version = ">= 0.21.0" }
  }
}

provider "bitwarden" {
  server                = "https://vault.example.com"
  email                 = "terraform@example.com"
  client_implementation = "embedded"   # built-in crypto, no bw binary; "cli" is the default
  # master_password, client_id, client_secret come from BW_PASSWORD, BW_CLIENTID, BW_CLIENTSECRET
}

data "bitwarden_item_login" "db" {
  search = "prod-postgres"             # or: id = "<item-id>"
}

resource "bitwarden_folder" "infra" {
  name = "Infra"
}

resource "bitwarden_item_login" "grafana" {
  name      = "Grafana admin"
  folder_id = bitwarden_folder.infra.id
  username  = "admin"
  password  = var.grafana_admin_password
}

variable "grafana_admin_password" {
  type      = string
  sensitive = true
}

output "db_password" {
  value     = data.bitwarden_item_login.db.password
  sensitive = true
}
```

Provider arguments (all optional, env fallback in brackets): `server` (`BW_URL`), `email` (`BW_EMAIL`), `master_password` (`BW_PASSWORD`), `client_id` (`BW_CLIENTID`), `client_secret` (`BW_CLIENTSECRET`), `session_key` (`BW_SESSION`), `client_implementation` (`embedded` | `cli`), `vault_path` (`BITWARDENCLI_APPDATA_DIR`, default `.bitwarden/`), `extra_ca_certs` (`NODE_EXTRA_CA_CERTS`, CLI mode only). `experimental { embedded_client = true }` is deprecated in favour of `client_implementation`.

Resources: `bitwarden_item_login`, `bitwarden_item_secure_note`, `bitwarden_item_ssh_key`, `bitwarden_folder`, `bitwarden_org_collection`, `bitwarden_attachment` (`bitwarden_project` / `bitwarden_secret` are Secrets Manager — not on Vaultwarden). Data sources add `bitwarden_organization`, `bitwarden_org_member` (`organization_id`, `email`) and `bitwarden_org_group`.

Rules for Terraform with a vault:
- Mark every secret variable and output `sensitive = true`; the values still land in **state** in clear text, so the state backend must be encrypted and access-controlled.
- Persist `.bitwarden/` (it holds `device_identifier`) between CI runs, or every run registers a new device and mails the account owner.
- Use a dedicated Vaultwarden account for Terraform with access only to the collections it manages.
