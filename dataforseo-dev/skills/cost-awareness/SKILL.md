---
name: cost-awareness
description: This skill should be used before any paid DataForSEO call, and when the user asks about "DataForSEO cost", "DataForSEO pricing", "how much will this cost", "DataForSEO budget", "credits", "billing", or wants to keep DataForSEO spending under control.
---

# Cost awareness

Every `api_request` is billed to the user's DataForSEO account. The documentation tools are free. This skill is the gate between the two.

## The rule

**Do not call `api_request` until the user has agreed a budget for the task.** A budget is a ceiling in USD or a number of calls, stated or confirmed by the user in this conversation. A command or an agent that lists `api_request` in its allowed tools is not an agreement: the permission only removes the prompt, so the plan below is where the user says yes.

In a non-interactive run with no stated budget, do the free steps (docs, planning, the balance check) and stop before the first paid call.

## What is free

- `docs_list_sections`, `docs_index`, `docs_search`.
- The GET lookups: locations, languages, model lists, filters.
- `GET /v3/appendix/user_data`: the account balance, rates and spending. DataForSEO states that calling it is not charged.
- DataForSEO's sandbox (`docs_search({url: "appendix/sandbox"})`): free, returns dummy data in the real response shape. Useful for checking a body. Whether `api_request` accepts the sandbox host through its `url` field has not been verified.

## Before the first paid call

1. **Read the endpoint pages** with `docs_search` for every path in the plan. Each lists a Pricing link; prices differ by endpoint and some are billed per result row or per 10 SERP results, so do not guess from another endpoint.
2. **Write the plan** as a short table: path, what it answers, `limit` or `depth`, number of calls.
3. **Show the plan and a cost estimate** built from the Pricing pages, with the unknowns named. Ask the user for the ceiling.
4. **Check the balance** with `api_request({method: "GET", path: "/v3/appendix/user_data", noAiMode: true})` and read `money.balance`. The cropped `.ai` form is documented for Live and Task GET endpoints only, so this Appendix call goes out unchanged. If the balance cannot cover the plan, say so before spending anything.
5. **Run the plan** in the order that lets an early answer cancel later calls.
6. **Report the spend.** Read the balance again, or send the one call that matters with `noAiMode: true` to see `cost`. The cropped `.ai` envelope has no `cost` field.

## Keeping the bill small

| Lever | Why |
|---|---|
| Bulk endpoints (`keyword_overview` up to 700 keywords, `bulk_keyword_difficulty` and the Backlinks `bulk_*` endpoints up to 1000 targets, `ai_keyword_data/keywords_search_volume` up to 1000) | One call instead of a loop |
| An explicit `limit` or `depth` | In `.ai` mode the default is 10; 1000 rows when 50 will do costs more |
| `filters` and `order_by` in the request | Pay for the rows you need, not the rows you discard |
| `_lite` variants of the LLM Mentions endpoints | Cheaper answers when the full breakdown is not needed |
| SERP `depth` in steps of 10 | The SERP is billed per 10 results |
| `max_crawl_pages` kept small on OnPage crawls | It multiplies the cost of a crawl |
| Keep every answer in the conversation | Never fetch the same data twice |
| Test a body in the sandbox or with `docs_search` first | A failed paid request is a wasted request |

## When a call fails

Stop and read `status_code` and `status_message` against `docs_search({url: "appendix/errors"})`. Fix the body, then retry once. Do not loop on a failing call.
