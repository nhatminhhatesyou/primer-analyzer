from .degenerate import expand_degenerate, has_degenerate
from .config import DEFAULT_PARAMS
from .idt_api import analyze_sequence, analyze_hairpin_batch, analyze_self_dimer
from .hairpin_unafold import calc_hairpin_unafold

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
    pairs = []
    for x in res:
        dg = _extract_dg(x)
        if dg is not None:
            pairs.append((float(dg), x["BasePairs"]))
    
    if not pairs:
        return{
            "SelfDimer_dG_min": None,
            "SelfDimer_BasePairs": None,
        }

    dg_min, basepairs = min(pairs, key=lambda x: x[0])

    return {
        "SelfDimer_dG_min": dg_min,
        "SelfDimer_BasePairs": basepairs,
    }


def calc_hairpin_batch(sequences, params):
    """Calculate hairpin ΔG for a batch of sequences."""

    res = analyze_hairpin_batch(sequences, params)  # results follow input order

    dgs = []
    for r in res:
        dg = _extract_dg(r)
        dgs.append(float(dg) if dg is not None else None)

    return dgs

def calc_hairpin(seq, params=None):
    """
    Calculate hairpin ΔG using UNAFold/OligoArrayAux.
    """
    params = params or DEFAULT_PARAMS

    temp_c = params.get("hairpin_temp_c", 25.0)
    sodium_m = params.get("hairpin_sodium_m", 0.05)
    magnesium_m = params.get("hairpin_magnesium_m", 0.003)

    res = calc_hairpin_unafold(
        seq=seq,
        temp_c=temp_c,
        sodium_m=sodium_m,
        magnesium_m=magnesium_m,
    )

    return {
        "Hairpin_dG_min": res["hairpin_dg"],
    }