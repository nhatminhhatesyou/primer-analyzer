# 🧬 Primer Analyzer

**Primer Analyzer** is a lightweight Python CLI tool for analyzing DNA primer sequences.  
It combines **local thermodynamic calculations** with the **IDT OligoAnalyzer API** to compute common primer quality metrics.

The tool reads a CSV/TSV file containing primer sequences and outputs additional metrics such as:

- 🧪 **GC content**
- 🌡️ **Melting temperature (Tm)**
- 🔗 **Self‑dimer ΔG**
- 🪢 **Hairpin ΔG**

The tool is designed to run inside **Docker** so the environment is reproducible and does not depend on the host operating system.

---

# ✨ Features

- 🧬 GC content calculation (supports **degenerate IUPAC bases**)
- 🌡️ Melting temperature (Tm) calculation using the **IDT OligoAnalyzer API**
- 🔗 Self‑dimer stability analysis via **IDT API**
- 🪢 Hairpin analysis using **UNAFold / OligoArrayAux (local)**
- ⚡ Parallel processing for faster analysis
- 🧩 Degenerate primer expansion with configurable limits
- 🐳 Fully containerized with **Docker**

---

# 🐳 Installation (Docker)

The recommended way to run Primer Analyzer is using Docker.

## 1️⃣ Clone the repository

```
git clone https://github.com/nhatminhhatesyou/primer-analyzer.git
```

## 2️⃣ Build the Docker image

```
docker build -t primer-analyzer .
```

This will:

- install Python dependencies
- build **mFold / UNAFold tools**
- prepare the CLI environment

---

# 🔑 Environment Variables

Create a `.env` file containing your **IDT API credentials**.

Example:

```
IDT_TOKEN_URL=your_token_url
IDT_API_BASE=your_api_base

IDT_CLIENT_ID=your_client_id
IDT_CLIENT_SECRET=your_client_secret

IDT_USERNAME=your_username
IDT_PASSWORD=your_password
```

These credentials are required for:

- **Tm calculation**
- **Self‑dimer analysis**

Hairpin analysis runs **locally** and does not require the API.

---

# 📄 Input Format

The tool expects a CSV or TSV file containing primer sequences.

Example input:

| PrimerSeq |
|-----------|
| ATGCGTAC |
| ATGNNNTA |
| CGTAGCTA |

Default column name:

```
PrimerSeq
```

You can change the column name using the `--col` argument.

---

# ▶️ Usage

Run the tool using Docker:

macOS / Linux (bash, zsh):

```
docker run --rm \
-v $(pwd):/app \
primer-analyzer \
--in input.csv \
--out output.csv \
--col PrimerSeq
```

Windows (PowerShell):

```
docker run --rm `
-v ${PWD}:/app `
primer-analyzer `
--in input.csv `
--out output.csv `
--col PrimerSeq
```

### Explanation

| Argument | Description |
|--------|-------------|
| `--in` | Input CSV/TSV file |
| `--out` | Output file with calculated metrics |
| `--col` | Column containing primer sequences |
| `--sep` | Input file separator (`\t` default) |
| `--workers` | Number of parallel threads |

Example:

```
docker run --rm \
-v $(pwd):/app \
primer-analyzer \
--in primers.tsv \
--out analyzed_primers.csv \
--col PrimerSeq
```

---

# 📊 Output

The output file contains the original input columns plus additional calculated metrics.

| Column | Description |
|------|-------------|
| GC_min | Minimum GC percentage |
| GC_max | Maximum GC percentage |
| GC_mean | Mean GC percentage |
| Tm_min_C | Minimum melting temperature |
| Tm_max_C | Maximum melting temperature |
| Tm_mean_C | Mean melting temperature |
| SelfDimer_dG_min | Minimum self‑dimer free energy |
| Hairpin_BasePairs | Number of base pairs in the predicted hairpin structure |
| Hairpin_dG_min | Hairpin free energy (local UNAFold calculation) |

---

# 🧠 How Calculations Work

Primer Analyzer uses a hybrid approach:

| Metric | Method |
|------|------|
| GC content | Local calculation |
| Hairpin | **UNAFold / OligoArrayAux (local)** |
| Tm | **IDT OligoAnalyzer API** |
| Self‑dimer | **IDT OligoAnalyzer API** |

Hairpin was moved to a local calculation because the legacy IDT API sometimes produced results that differed from the official OligoAnalyzer tool.

---

# 📂 Project Structure

```
primer-analyzer/
│
├── primer_analyzer/
│   ├── cli.py
│   ├── metrics.py
│   ├── hairpin_unafold.py
│   ├── degenerate.py
│   ├── idt_api.py
│   └── config.py
│
├── vendor/
│   ├── mfold-3.6.tar
│   └── oligoarrayaux-3.8.1.tar
│
├── Dockerfile
├── requirements.txt
├── README.md
├── .env
├── .dockerignore
├── .gitignore
│
│
├──input.csv
└──output.csv
```

---

# ⚠️ Notes

- Hairpin analysis runs **locally** using UNAFold.
- Tm and Self‑dimer calculations still require the **IDT API**.
- Degenerate sequences are expanded only up to a configurable limit to avoid combinatorial explosion.

---

# 🧬 Example Workflow

```
Primer CSV
     │
     ▼
Primer Analyzer CLI
     │
     ├── GC content (local)
     ├── Hairpin (UNAFold)
     ├── Tm (IDT API)
     └── Self‑dimer (IDT API)
     │
     ▼
Analyzed CSV output
```

---

# 💡 Future Improvements

Possible future improvements:

- 🔬 Local Tm calculation (remove API dependency)
- 🔗 Local self‑dimer calculation
- 🚀 GPU / batch optimization for large primer sets

---

# 🧑‍💻 Author

Built for fast primer screening and reproducible primer analysis pipelines.

Happy PCR designing! 🧬✨