import argparse
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

from .config import DEFAULT_PARAMS
from .metrics import gc_content, calc_tm, calc_self_dimer
from .idt_api import analyze_hairpin_batch

load_dotenv()


def run_parallel(func, items, workers=8, desc="Processing"):
    """Run a function on a list of items using multiple threads."""
    results = [None] * len(items)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # map future -> original index to keep output order
        futures = {executor.submit(func, item): i for i, item in enumerate(items)}

        for f in tqdm(as_completed(futures), total=len(items), desc=desc):
            idx = futures[f]
            results[idx] = f.result()

    return results


def chunked(xs, size):
    """Split a list into smaller batches."""
    for i in range(0, len(xs), size):
        yield xs[i:i+size]


def main():
    # parse CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_csv", required=True)
    parser.add_argument("--out", dest="output_csv", required=True)
    parser.add_argument("--col", default="PrimerSeq")   # column containing sequences
    parser.add_argument("--sep", default="\t")          # file separator
    parser.add_argument("--batch", type=int, default=100)  # hairpin API batch size
    args = parser.parse_args()

    # read input file
    df = pd.read_csv(args.input_csv, sep=args.sep)
    if args.col not in df.columns:
        raise ValueError(f"Column {args.col} not found")

    # normalize sequences (strip spaces + uppercase)
    seqs = df[args.col].astype(str).map(lambda s: s.strip().upper()).tolist()

    # 1) compute GC content locally
    gc_rows = [gc_content(s) for s in tqdm(seqs, desc="GC")]

    # 2) compute Tm and SelfDimer in parallel
    tm_rows = run_parallel(
        lambda s: calc_tm(s, DEFAULT_PARAMS),
        seqs,
        workers=8,
        desc="Tm"
    )

    sd_rows = run_parallel(
        calc_self_dimer,
        seqs,
        workers=8,
        desc="SelfDimer"
    )

    # 3) call IDT API to calculate hairpin energy (batched)
    hairpin_dg = [None] * len(seqs)
    idx = 0

    for batch in tqdm(list(chunked(seqs, args.batch)), desc="HairpinBatch"):
        res = analyze_hairpin_batch(batch, DEFAULT_PARAMS)

        batch_dg = []
        for r in res:
            dg = r.get("DeltaG", r.get("deltaG"))
            batch_dg.append(float(dg) if dg is not None else None)

        # store results in correct position
        hairpin_dg[idx: idx + len(batch)] = batch_dg
        idx += len(batch)

    hp_rows = [{"Hairpin_dG_min": dg} for dg in hairpin_dg]

    # merge original data with calculated metrics
    out_df = pd.concat(
        [
            df.reset_index(drop=True),
            pd.DataFrame(gc_rows),
            pd.DataFrame(tm_rows),
            pd.DataFrame(sd_rows),
            pd.DataFrame(hp_rows),
        ],
        axis=1
    )

    # write output file
    out_df.to_csv(args.output_csv, index=False)


if __name__ == "__main__":
    main()