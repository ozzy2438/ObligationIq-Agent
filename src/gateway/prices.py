"""Pinned AUD retail rates, not invoice totals. No runtime price/network lookup."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING

SOURCE = "https://prices.azure.com/api/retail/prices"
RETRIEVED_ON = "2026-09-13"


class UnknownPrice(ValueError):
    pass


@dataclass(frozen=True)
class Price:
    model: str
    version: str
    input_per_million: Decimal
    output_per_million: Decimal
    cached_input_per_million: Decimal
    currency: str = "AUD"
    region: str = "australiaeast"
    sku: str = "GlobalStandard"
    source_url: str = SOURCE
    retrieved_on: str = RETRIEVED_ON

    @property
    def identity(self):
        return f"{self.model}:{self.version}:{self.region}:{self.sku}"

    def cost_microaud(self, input_tokens, output_tokens, cached_tokens=0):
        counts = (input_tokens, output_tokens, cached_tokens)
        if any(type(n) is not int or n < 0 for n in counts) or cached_tokens > input_tokens:
            raise ValueError("Invalid token usage")
        # AUD/1M tokens equals micro-AUD/token. Always round upward, never float.
        amount = ((input_tokens - cached_tokens) * self.input_per_million +
                  cached_tokens * self.cached_input_per_million +
                  output_tokens * self.output_per_million)
        return int(amount.to_integral_value(rounding=ROUND_CEILING))


PRICES = {
    "gpt-5-nano": Price("gpt-5-nano", "2025-08-07", Decimal("0.069500"),
                        Decimal("0.556200"), Decimal("0.007000")),
    "gpt-5-mini": Price("gpt-5-mini", "2025-08-07", Decimal("0.347600"),
                        Decimal("2.781100"), Decimal("0.034800")),
}
ROUTES = {"cheap": "gpt-5-nano", "strong": "gpt-5-mini", "embed": "text-embedding-3-small"}


def get_price(model):
    try:
        return PRICES[model]
    except KeyError:
        raise UnknownPrice("Requested model has no pinned price; call refused") from None
