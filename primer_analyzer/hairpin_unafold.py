from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def parse_dg_file(path: Path) -> float | None:
    """
    Parse a UNAFold/OligoArrayAux .dG file.

    Expected format:
        #T      -RT ln Z        Z
        25      -1.042          5.80488

    Returns:
        The free energy value in kcal/mol, or None if parsing fails.
    """
    if not path.exists():
        return None

    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return None

    lines = text.splitlines()
    if len(lines) < 2:
        return None

    parts = lines[1].split()
    if len(parts) < 2:
        return None

    try:
        return float(parts[1])
    except ValueError:
        return None


def run_hybrid_ss_min(
    seq: str,
    temp_c: float = 25.0,
    sodium_m: float = 0.05,
    magnesium_m: float = 0.003,
) -> float | None:
    """
    Run hybrid-ss-min for a single sequence and return ΔG.
    """
    seq = seq.strip().upper()
    if not seq:
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir)
        seq_file = workdir / "seq.txt"
        prefix = "result"

        seq_file.write_text(seq + "\n", encoding="utf-8")

        cmd = [
            "hybrid-ss-min",
            "-n", "DNA",
            "-t", str(temp_c),
            "-T", str(temp_c),
            "-N", str(sodium_m),
            "-M", str(magnesium_m),
            "--energyOnly",
            "-o", prefix,
            seq_file.name,
        ]

        result = subprocess.run(
            cmd,
            cwd=workdir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return None

        dg_path = workdir / f"{prefix}.dG"
        return parse_dg_file(dg_path)


def calc_hairpin_unafold(
    seq: str,
    temp_c: float = 25.0,
    sodium_m: float = 0.05,
    magnesium_m: float = 0.003,
) -> dict[str, float | None]:
    """
    Calculate hairpin ΔG using UNAFold/OligoArrayAux hybrid-ss-min.

    No degenerate expansion is performed.
    The input sequence is passed directly to UNAFold.
    """
    dg = run_hybrid_ss_min(
        seq=seq,
        temp_c=temp_c,
        sodium_m=sodium_m,
        magnesium_m=magnesium_m,
    )

    return {
        "hairpin_dg": dg,
    }