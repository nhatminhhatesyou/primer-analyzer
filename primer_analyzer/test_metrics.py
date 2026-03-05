from __future__ import annotations

import argparse
from pprint import pprint

from .config import DEFAULT_PARAMS
from .degenerate import has_degenerate, expand_degenerate
from .aggregate import aggregate_metrics


def main():
    parser = argparse.ArgumentParser(
        description="Test metrics for a single primer sequence (manual input)."
    )
    parser.add_argument(
        "--seq",
        required=True,
        help="Primer sequence (can include IUPAC degenerate bases, e.g. R,Y,W,S,N).",
    )
    parser.add_argument(
        "--max-variants",
        type=int,
        default=DEFAULT_PARAMS.get("max_variants", 128),
        help="Max number of variants to expand for degenerate primers.",
    )
    args = parser.parse_args()

    seq = args.seq.strip().upper()
    deg = has_degenerate(seq)

    if deg:
        variants = expand_degenerate(seq, max_variants=args.max_variants)
    else:
        variants = [seq]

    # IMPORTANT: ensure your aggregate_metrics signature matches:
    # aggregate_metrics(variants, params, has_deg=deg)
    metrics = aggregate_metrics(variants, DEFAULT_PARAMS, has_deg=deg)

    print("\n=== INPUT ===")
    print("PrimerSeq:", seq)
    print("HasDegenerate:", deg)
    print("VariantsEvaluated:", len(variants))

    print("\n=== METRICS (new columns) ===")
    pprint(metrics, sort_dicts=False)


if __name__ == "__main__":
    main()