"""Exact retrieval for one reviewed obligation; retrieved text is never logged."""

from dataclasses import dataclass
import hashlib
import re

from src.dataplane.corpus import exact_clause


@dataclass(frozen=True, repr=False)
class ClauseEvidence:
    source_id: str
    title: str
    issuer: str
    version: str
    url: str
    regime: str
    cited_reference: str
    parent_reference: str
    page_start: int
    page_end: int
    source_sha256: str
    clause_sha256: str
    text: str
    cited_excerpt: str

    def public_citation(self):
        return {
            "source_id": self.source_id,
            "title": self.title,
            "issuer": self.issuer,
            "version": self.version,
            "url": self.url,
            "regime": self.regime,
            "clause_reference": self.cited_reference,
            "parent_clause": self.parent_reference,
            "pdf_pages": [self.page_start, self.page_end],
            "source_sha256": self.source_sha256,
            "source_clause_sha256": self.clause_sha256,
            "source_text_retained_locally": True,
        }


def referenced_excerpt(text, parent_reference, cited_reference):
    suffix = cited_reference.removeprefix(parent_reference)
    markers = re.findall(r"\([^)]+\)", suffix)
    if not markers:
        return text.strip()
    cursor = 0
    last = None
    for marker in markers:
        match = re.compile(r"(?m)^[ \t]*" + re.escape(marker) + r"(?=\s|[A-Z]|$)").search(text, cursor)
        if match is None:
            raise ValueError("Cited subclause cannot be resolved in the pinned parent clause")
        last = match
        cursor = match.end()
    token = markers[-1][1:-1]
    sibling = r"\d+" if token.isdigit() else r"(?:[a-z]+|\d+)" if token.isalpha() else r"[^)]+"
    following = re.compile(r"(?m)^[ \t]*\(" + sibling + r"\)(?=\s|[A-Z]|$)").search(text, last.end())
    return text[last.start():following.start() if following else len(text)].strip()


class Retriever:
    def __init__(self, loader=exact_clause):
        self.loader = loader

    def retrieve(self, obligation):
        if (obligation.get("review_status") != "APPROVED" or
                obligation.get("operational_review_status") != "ELIGIBLE_FOR_EVALUATION"):
            raise ValueError("Obligation has not passed both review gates")
        block = self.loader(obligation["source_id"], obligation["parent_clause"],
                            as_of=obligation["coverage_as_of"])
        clause_digest = hashlib.sha256(block["text"].encode()).hexdigest()
        checks = {
            "source_id": block["source_id"] == obligation["source_id"],
            "source_sha256": block["source_sha256"] == obligation["source_sha256"],
            "source_version": block["version"] == obligation["source_version"],
            "regime": block["regime"] == obligation["regime"],
            "parent_clause": block["reference"] == obligation["parent_clause"],
            "clause_sha256": clause_digest == obligation["source_clause_sha256"],
            "page_range": (block["page_start"] == obligation["source_page_start"] and
                           block["page_end"] == obligation["source_page_end"]),
        }
        if not all(checks.values()):
            raise ValueError("Retrieved clause does not match the reviewed obligation binding")
        return ClauseEvidence(
            source_id=block["source_id"], title=block["title"], issuer=block["issuer"],
            version=block["version"], url=block["url"], regime=block["regime"],
            cited_reference=obligation["clause_reference"],
            parent_reference=block["reference"], page_start=block["page_start"],
            page_end=block["page_end"], source_sha256=block["source_sha256"],
            clause_sha256=clause_digest, text=block["text"],
            cited_excerpt=referenced_excerpt(
                block["text"], block["reference"], obligation["clause_reference"]),
        )
