# ObligationIQ

Independent reference build for electricity compliance evidence in Australia.

**Status: authentication and Azure budget preflight only. The application has not been implemented or evaluated.**

The intended output is a source-backed evidence pack. Compliance decisions belong to deterministic controls using versioned, human-verified obligations; language models may retrieve, draft and explain evidence.

The current user direction prioritises a compact implementation, a total project ceiling of 2–3 dollars, and avoiding repeated synthetic-data generation. The attached build brief is the architectural specification, subject to that direction. Currency is provisionally AUD, matching the verified Azure subscription currency, pending any user correction.

See [the preflight and delivery decisions](docs/preflight-and-delivery-plan.md) for verified setup, authentication requirements, cost controls and the proposed build sequence.

No customer population, compliance outcome, benchmark or business-impact metric exists yet. Azure Databricks, Unity Catalog, Azure OpenAI inference and cloud deployment have not been verified for this project.

Pilot boundaries: electricity only; Victoria and NERL/NERR regimes remain separate; no billing recalculation, automated customer communication, disconnection decisions or recommendations, or CRM writes. A future CRM interface will be read-only with a mock adapter. This is independent portfolio work, not a client implementation.
