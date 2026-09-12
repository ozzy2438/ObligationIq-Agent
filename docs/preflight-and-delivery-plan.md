# ObligationIQ — preflight and delivery decisions

Date: 12 September 2026, Australia/Melbourne.

## Instruction precedence

The user's current request takes precedence over the attached `OBLIGATIONIQ_AGENT_BRIEF.md`: use senior engineering judgement, minimise cost and unnecessary code, and do not repeatedly generate test populations. The brief remains the source of the intended functional scope and evidence standards. Its request for a large cloud configuration block does not require the user to provision every listed service before a local implementation can be designed.

This preflight is not completion of Phase 0. The gateway and application still need implementation. No legal source, obligation record or synthetic population has been verified in this step.

## Verified authentication

Azure CLI is installed. Live Azure Resource Manager requests succeeded against the single enabled default subscription, displayed as `Osman Orka`. Azure subscription policies report pay-as-you-go and `spendingLimit: Off`.

The user does not need to log in again for the current management operations. Budget creation succeeded with the existing identity. Tokens and keys were neither requested from the user nor written to project files.

| Capability | Status and next requirement |
|---|---|
| Azure subscription and budget management | Live access verified; budget created. |
| Local implementation, public-source research and deterministic controls | No additional service login needed. |
| Azure OpenAI inference | Not verified. Later select an eligible low-cost deployment, confirm regional availability and prices, and verify Entra data-plane permissions before a paid call. Management-plane access alone does not establish inference access. |
| Databricks / Unity Catalog | No workspace found in the subscription resource inventory. Use a documented local alternative for the pilot; do not represent it as deployed Unity Catalog. |
| GitHub publishing | Not part of this preflight. Authentication and repository destination can be checked when publication is requested. |

## Azure budget

| Field | Value |
|---|---|
| New project resource group | `rg-obligationiq-pilot` |
| Resource group location | `australiaeast` |
| Budget name | `obligationiq-pilot-aud-3` |
| Budget scope | Only this project resource group |
| Amount | 3 AUD; currency follows the verified subscription currency |
| Time grain | Annually |
| Start | 1 September 2026, 00:00 UTC |
| Expiration | 31 August 2027, 23:59:59 UTC |
| Actual-cost email thresholds | 50%, 75%, 90%, 100%: 1.50, 2.25, 2.70, 3.00 AUD |
| Recipient | Existing account budget notification address; kept in private local configuration |

The annual setting avoids a new monthly allowance during this build. The Azure budget expires at the stated date; it is not a perpetual lifetime cap. A future application ledger must enforce the project-total limit independently of calendar resets.

The existing subscription-wide budget `procurelens-demo-usd-2` was left unchanged. Despite its name, its API-reported currency is AUD. The new budget covers neither unrelated resource groups nor charges that Azure cannot attribute to this project group. Reusing another project's model endpoint would therefore require an explicit attribution decision first.

The budget request and server readback are stored under the gitignored `.local/` directory. They contain account metadata and are not intended for publication.

**A budget is an alert, not a hard stop.** Microsoft states that budgets do not stop consumption; cost data can take 8–24 hours to arrive and budgets are evaluated every 24 hours. Pay-as-you-go subscriptions do not support a user-defined 3-dollar platform spending limit. Budget emails cannot guarantee a 3 AUD final invoice.

Sources, checked 12 September 2026:

- [Microsoft: Create and manage budgets](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets)
- [Microsoft: Azure spending limit](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/spending-limit)
- [Microsoft: Budgets create/update API](https://learn.microsoft.com/en-us/rest/api/consumption/budgets/create-or-update?view=rest-consumption-2024-08-01)

## Proposed cost policy — not yet implemented

Target application spend: at most **2 AUD for the entire build**, leaving 1 AUD of headroom below the requested 3 AUD ceiling. This is a design target, not measured spend or a guarantee about provider billing adjustments and taxes.

1. Keep development entirely local and network model calls disabled by default.
2. Route every future paid model request through one gateway; enforce daily and lifetime limits in one durable, atomic ledger.
3. Before sending a request, reserve its conservative maximum cost from bounded input and maximum output tokens. Reserve retries separately; stop on an unknown price, ambiguous previous request, or insufficient balance.
4. Pin the exact model/deployment rate, currency conversion assumption and pricing retrieval date before live usage. Account for relevant billed token classes, including reasoning tokens. Provider invoice cost remains distinct from the application's estimate.
5. Persist responses and embeddings. A repeat evaluation should use cached results, not buy the same work again.
6. Use serial, small final evaluations. No always-on compute, scheduled pipelines, managed search, paid Databricks warehouse or API Management deployment is required for local development.
7. Do not enable live mode until the gateway protections are implemented and meaningfully checked. If a service cannot be bounded inside the allowance, retain its local implementation and disclose the missing cloud validation.

No paid inference, model deployment, storage account or compute resource was created during this preflight. The subscription cost query returned HTTP 429; the existing budget reported zero spend, but that lagged value is not a fresh invoice reconciliation. No claim of zero historical subscription cost is made.

## Delivery approach

The business question is whether a control can establish an obligation's status at a specified date and supply traceable evidence. The smallest useful output is a reproducible evidence pack, not a chat interface.

Follow the brief's phases while keeping the first complete path compact:

1. **Phase 0:** implement configuration and the dry-run/cached gateway, durable budget control and minimal audit logging. Record local-versus-cloud decisions explicitly.
2. **Phase 1:** retrieve official regulatory material; capture version, effective dates, jurisdiction, clause reference and reuse terms before extraction. Start with the documents needed by the two obligation families; record unavailable items rather than filling gaps.
3. **Phase 2:** prepare the 25–40 obligation records required by the brief for human review. An agent must never set `verified_by_human=true` on its own. No unverified obligation can produce a compliance determination. This is a real downstream human-review gate.
4. **Phase 3:** inspect real calibration data first. Generate one reproducible population only if needed for the agreed evaluation, preserving the seed and provenance. Do not repeatedly generate datasets or claim calibration before measuring it. Published aggregate data alone cannot establish a particular customer's compliance.
5. **Phase 4:** build pure deterministic controls and a small set of meaningful deadline, jurisdiction, missing-evidence and version-boundary checks. Missing evidence must not silently become `compliant`.
6. **Phase 5:** establish the rule-based risk baseline first. Implement or retain ML only when a defensible evaluation demonstrates an improvement; a synthetic benchmark is not production validation.
7. **Phase 6:** assemble retrieval, timeline, drafting and completeness checks as simple components. Add the MCP surface around the working core. The model never decides the compliance status.
8. **Phases 7–8:** evaluate on the bounded held-out cases, publish measured results and limitations, and package reproduction instructions. Azure inference is a final, bounded option after access and cost checks.

The cloud target architecture can remain in the architecture document. A local pilot must not be described as an implemented Databricks, Unity Catalog or Azure production platform. Any deferred deliverable remains explicitly pending.

## Current limitations

- Only authentication, resource inventory and the budget setup have been performed.
- The application spending guard has not been implemented; paid execution remains disabled by absence of any model integration.
- No regulatory interpretation, compliance result, human review, evaluation metric or business benefit has been established.
- No synthetic population or test dataset has been generated.
- The user's currency preference remains provisional; AUD was selected conservatively from live subscription evidence.
