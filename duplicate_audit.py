"""Audit duplicate document hashes in a blockchain ledger JSON file.

Usage:
  python duplicate_audit.py
  python duplicate_audit.py --chain chain.json
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from main import load_chain, validate_chain


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report duplicate document file hashes in the chain."
    )
    parser.add_argument(
        "--chain",
        default="chain.json",
        help="Path to blockchain JSON file (default: chain.json)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    chain_path = Path(args.chain)

    if not chain_path.exists():
        print(f"Chain file not found: {chain_path}")
        return 1

    chain = load_chain(chain_path)
    is_valid, message = validate_chain(chain)
    if not is_valid:
        print(f"Cannot audit duplicates: {message}")
        return 1

    by_hash: dict[str, list] = defaultdict(list)
    for block in chain:
        payload = block.payload
        if payload.get("type") != "document":
            continue
        file_hash = payload.get("file_hash")
        if isinstance(file_hash, str) and file_hash:
            by_hash[file_hash].append(block)

    duplicates = {key: value for key, value in by_hash.items() if len(value) > 1}

    if not duplicates:
        print("No duplicate document hashes found.")
        return 0

    print(f"Duplicate hash groups found: {len(duplicates)}")
    for file_hash, blocks in duplicates.items():
        print("-" * 72)
        print(f"File SHA256: {file_hash}")
        print(f"Occurrences: {len(blocks)}")
        for block in blocks:
            payload = block.payload
            print(
                "  "
                f"Block={block.index}, "
                f"Document ID={payload.get('document_id')}, "
                f"Owner={payload.get('owner')}, "
                f"File={payload.get('file_name')}"
            )

    print("-" * 72)
    print("Recommendation: keep one canonical issuance per file hash.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
