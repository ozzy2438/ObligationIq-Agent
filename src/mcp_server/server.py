"""Local stdio MCP surface over the working evidence pipeline."""

import json

from mcp.server import MCPServer

from src.agents.pipeline import build_evidence_pack as run_pipeline


mcp = MCPServer(
    "ObligationIQ",
    instructions=("Build source-backed evidence packs. Deterministic controls own the supplied "
                  "compliance status; model-generated text cannot override it."),
)


@mcp.tool()
def build_evidence_pack(case_json: str, use_model: bool = False, tier: str = "cheap",
                        escalation_reason: str | None = None) -> dict:
    """Build one cited pack from a JSON case using the local reviewed register and corpus."""
    try:
        case = json.loads(case_json)
    except json.JSONDecodeError:
        raise ValueError("case_json must contain one JSON object") from None
    if not isinstance(case, dict):
        raise ValueError("case_json must contain one JSON object")
    pack, review = run_pipeline(
        case, use_model=use_model, tier=tier, escalation_reason=escalation_reason)
    return {"evidence_pack": pack.to_dict(), "critic": review.to_dict()}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
