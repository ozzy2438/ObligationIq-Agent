"""Download pinned public PDFs and local weights; verified cache hits use no network."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import urllib.request
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT, settings
from src.dataplane.corpus import load_manifest


def acquire(url, destination, expected, *, max_bytes=110_000_000):
    if urlsplit(url).scheme != "https":
        raise ValueError("Only HTTPS source downloads are supported")
    if destination.exists():
        if hashlib.sha256(destination.read_bytes()).hexdigest() != expected:
            raise ValueError("Local asset changed; inspect it before replacing it")
        return "verified_cache"
    request = urllib.request.Request(url, headers={"User-Agent": "ObligationIQ-Research/0.1"})
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = None
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 200 or urlsplit(response.url).scheme != "https":
                raise ValueError("Unexpected download response")
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as file:
                staging = Path(file.name)
                size = 0
                checksum = hashlib.sha256()
                while chunk := response.read(1_048_576):
                    size += len(chunk)
                    if size > max_bytes:
                        raise ValueError("Asset exceeds download bound")
                    checksum.update(chunk)
                    file.write(chunk)
        if checksum.hexdigest() != expected:
            raise ValueError("Remote content differs from pin; review source version, do not auto-update")
        os.replace(staging, destination)
    finally:
        if staging and staging.exists():
            staging.unlink()
    return "downloaded"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="store_true", help="Also download pinned CPU embedding weights")
    parser.add_argument("--review-sources", action="store_true", help="Also acquire supplemental review sources")
    args = parser.parse_args()
    for source in load_manifest()["sources"]:
        status = acquire(source["url"], ROOT / "data/raw" / (source["id"] + ".pdf"), source["sha256"])
        print(source["id"], status)
    if args.review_sources:
        for source in json.loads((ROOT / "data/review-sources.json").read_text())["sources"]:
            print(source["id"], acquire(source["url"], ROOT / "data/raw" / (source["id"] + ".pdf"), source["sha256"]))
    if args.model:
        pin = json.loads((ROOT / "src/gateway/local-model.json").read_text())
        for asset in pin["files"]:
            print(asset["name"], acquire(asset["url"], settings.local_model_dir / asset["name"], asset["sha256"]))


if __name__ == "__main__":
    main()
