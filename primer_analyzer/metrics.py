from .degenerate import expand_degenerate, has_degenerate
from .config import DEFAULT_PARAMS
from .idt_api import analyze_sequence, analyze_hairpin_batch, analyze_self_dimer


def gc_content(seq):
    """Calculate GC% statistics (min, max, mean). Supports degenerate primers."""

    def mean(xs): 
        return sum(xs) / len(xs)

    gc_vals = []

    # Check if sequence contains degenerate bases
    deg = has_degenerate(seq)

    if deg:
        # Expand degenerate sequence into possible variants
        variants = expand_degenerate(seq, max_variants=DEFAULT_PARAMS["max_variants"])
    else:
        variants = [seq]  # normal primer: only one variant

    # Compute GC% for each variant
    for v in variants:
        gc = sum(1 for b in v if b in ["G", "C"])
        gc_vals.append(100 * gc / len(v))

    return {
        "GC_min": min(gc_vals),
        "GC_max": max(gc_vals),
        "GC_mean": mean(gc_vals),
    }


def calc_tm(seq, params):
    """Calculate melting temperature (Tm) using IDT API."""

    res = analyze_sequence(seq, params)

    tm_min = res["MinMeltTemp"]
    tm_max = res["MaxMeltTemp"]

    tm_mean = (tm_min + tm_max) / 2

    return {
        "Tm_min_C": tm_min,
        "Tm_max_C": tm_max,
        "Tm_mean_C": tm_mean,
    }


def _extract_dg(item):
    """Extract ΔG value from API response (handle different key names)."""

    if "DeltaG" in item:
        return item["DeltaG"]
    if "deltaG" in item:
        return item["deltaG"]
    return None


def calc_self_dimer(seq):
    """Calculate minimum self-dimer ΔG for a sequence."""

    res = analyze_self_dimer(seq)  # API usually returns a list

    dgs = [_extract_dg(x) for x in res]
    dgs = [float(d) for d in dgs if d is not None]

    return {
        "SelfDimer_dG_min": min(dgs) if dgs else None
    }


def calc_hairpin_batch(sequences, params):
    """Calculate hairpin ΔG for a batch of sequences."""

    res = analyze_hairpin_batch(sequences, params)  # results follow input order

    dgs = []
    for r in res:
        dg = _extract_dg(r)
        dgs.append(float(dg) if dg is not None else None)

    return dgs