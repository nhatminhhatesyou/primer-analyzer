# Primer Analyzer

Primer Analyzer is a lightweight Python CLI tool for analyzing DNA primer sequences using both **local calculations** and the **IDT OligoAnalyzer API**.

The tool reads a CSV/TSV file containing primer sequences and outputs additional metrics such as **GC content**, **melting temperature (Tm)**, **self‑dimer ΔG**, and **hairpin ΔG**.

---

## Features

- GC content calculation (supports **degenerate IUPAC bases**)
- Melting temperature (Tm) analysis via the **IDT OligoAnalyzer API**
- Self‑dimer stability analysis
- Hairpin structure analysis with **batch API calls**
- Parallel processing for faster computation
- Degenerate primer expansion with a configurable limit

---

## Installation

Clone the repository:

```
git clone https://github.com/nhatminhhatesyou/primer-analyzer.git

```

Create a virtual environment (recommended):

```
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file containing your **IDT API credentials**:

```
IDT_TOKEN_URL=your_token_url
IDT_API_BASE=your_api_base

IDT_CLIENT_ID=your_client_id
IDT_CLIENT_SECRET=your_client_secret

IDT_USERNAME=your_username
IDT_PASSWORD=your_password
```

---

## Input Format

The tool expects a CSV/TSV file with a column containing primer sequences.

Example:

| PrimerSeq |
|-----------|
| ATGCGTAC |
| ATGNNNTA |
| CGTAGCTA |

Default column name:

```
PrimerSeq
```

---

## Usage

Run the CLI tool:

```
python -m primer_analyzer.cli --in input.csv --out output.csv --col PrimerSeq
```

Optional arguments:

| Argument | Description | Default |
|---------|-------------|--------|
| `--sep` | Input file separator | `\t` |
| `--batch` | Batch size for hairpin API calls | `100` |

Example:

```
python -m primer_analyzer.cli \
    --in primers.tsv \
    --out analyzed_primers.csv \
    --col PrimerSeq \
    --batch 100
```

---

## Output

The output file will contain the original input columns plus additional calculated metrics:

| Column | Description |
|------|-------------|
| GC_min | Minimum GC percentage |
| GC_max | Maximum GC percentage |
| GC_mean | Mean GC percentage |
| Tm_min_C | Minimum melting temperature |
| Tm_max_C | Maximum melting temperature |
| Tm_mean_C | Mean melting temperature |
| SelfDimer_dG_min | Minimum self‑dimer free energy |
| Hairpin_dG_min | Minimum hairpin free energy |

---

## Project Structure

```
primer-analyzer-idt/
│
├── primer_analyzer/          # Main Python package
│   ├── cli.py                # Command line interface
│   ├── metrics.py            # GC, Tm, dimer, hairpin calculations
│   ├── degenerate.py         # Degenerate base expansion utilities
│   ├── idt_api.py            # IDT API client
│   └── config.py             # Default analysis parameters
│
├── primers.csv               # Example input file
├── scored.csv                # Example output file
│
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

---

## Notes

- Hairpin analysis uses **batch API calls** to reduce request overhead.
- Self‑dimer and Tm calculations are executed in **parallel** for performance.
- Degenerate sequences are expanded only up to a configurable limit to avoid combinatorial explosion.

---