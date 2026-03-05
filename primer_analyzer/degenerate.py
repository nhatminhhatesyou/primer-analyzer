import itertools

# Mapping IUPAC degenerate bases -> possible nucleotides
IUPAC = {
    "A": "A", "C": "C", "G": "G", "T": "T",
    "R": "AG", "Y": "CT", "W": "AT", "S": "GC",
    "K": "GT", "M": "AC",
    "B": "CGT", "D": "AGT", "H": "ACT", "V": "ACG",
    "N": "ACGT",
}

# Standard DNA bases
STANDARD = set("ACGT")


def has_degenerate(seq: str) -> bool:
    """Check if a sequence contains degenerate bases."""
    seq = seq.strip().upper()
    return any(ch not in STANDARD for ch in seq)


def expand_degenerate(seq, max_variants=128):
    """
    Expand a degenerate DNA sequence into all possible concrete sequences.

    Example:
        ATN -> ATA, ATC, ATG, ATT

    max_variants limits expansion to avoid combinatorial explosion.
    """
    seq = seq.upper()

    # Create a list of possible bases for each position
    pools = [IUPAC[b] for b in seq]

    variants = []

    # Cartesian product of all base options
    for combo in itertools.product(*pools):
        variants.append("".join(combo))

        # Stop early if limit reached
        if len(variants) >= max_variants:
            break

    return variants