"""The Phase 0 end-to-end smoke path is explicitly offline."""

import json
from src.config import settings
from src.gateway.llm_client import LLMClient


def main(config=settings):
    if config.mode != "dry_run":
        raise RuntimeError("The Phase 0 demo requires LLM_MODE=dry_run")
    client = LLMClient(config)
    response = client.complete("Check the Phase 0 gateway wiring.")
    print(json.dumps({"mode": config.mode, "result": response.text,
                      "ledger": client.ledger.summary()}, indent=2))


if __name__ == "__main__":
    main()
