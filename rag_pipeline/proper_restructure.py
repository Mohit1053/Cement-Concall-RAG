"""
Proper restructuring: Group by functionality, not by technical layers
"""
import os
import shutil
from pathlib import Path

def proper_restructure():
    """Restructure by functionality groups."""
    
    base_dir = Path(".")
    
    print("="*80)
    print("PROPER RESTRUCTURING - GROUPING BY FUNCTIONALITY")
    print("="*80)
    
    # Define proper structure
    structure = {
        "rag_pipeline": {
            "description": "All RAG-related files (vector DB, search, analysis)",
            "subdirs": ["core", "tasks", "data", "tests", "configs"],
            "files": []
        },
        "concall_downloader": {
            "description": "All concall downloading and processing scripts",
            "subdirs": [],
            "files": [
                "download_concalls_final.py",
                "download_concalls_v2.py", 
                "download_concalls.py",
                "retry_failed_downloads.py",
                "download_summary.py",
                "download_transcripts.py",
                "download_verdict.py",
                "extract_concall_urls_2years.py",
                "filter_concalls_2years.py",
                "CONCALL_README.md",
                "concall_download_results.json",
                "concall_results.json"
            ]
        },
        "data_scraping": {
            "description": "Company data scraping and extraction",
            "subdirs": [],
            "files": [
                "extract_cement_companies.py",
                "find_cement_companies.py",
                "search_missing_companies.py",
                "check_cement_data.py",
                "clean_cement_data.py",
                "create_final_clean.py",
                "verify_final_data.py",
                "verify_matches.py",
                "test_screener.py",
                "test_companies.json",
                "Cement_Companies_Concalls_2Years_FINAL_20251202_121207.csv"
            ]
        },
        "reports": {
            "description": "Final reports and analysis outputs",
            "subdirs": [],
            "files": [
                "final_check.py",
                "FINAL_COMPLETE_REPORT.py",
                "FINAL_SUMMARY_REPORT.py",
                "manual_instructions.py"
            ]
        }
    }
    
    # Create main directories
    print("\n1. Creating proper directory structure...")
    for folder, details in structure.items():
        folder_path = base_dir / folder
        folder_path.mkdir(exist_ok=True)
        print(f"   ✓ {folder}/ - {details['description']}")
        
        for subdir in details['subdirs']:
            subdir_path = folder_path / subdir
            subdir_path.mkdir(exist_ok=True)
            print(f"     ✓ {folder}/{subdir}/")
    
    # Move RAG files
    print("\n2. Moving RAG pipeline files...")
    rag_dir = base_dir / "rag_pipeline"
    
    # Move core components
    if (base_dir / "core").exists():
        shutil.move(str(base_dir / "core"), str(rag_dir / "core"))
        print("   ✓ core/ → rag_pipeline/core/")
    
    # Move tasks
    if (base_dir / "tasks").exists():
        shutil.move(str(base_dir / "tasks"), str(rag_dir / "tasks"))
        print("   ✓ tasks/ → rag_pipeline/tasks/")
    
    # Move data/vector_db
    if (base_dir / "data" / "vector_db").exists():
        data_dir = rag_dir / "data"
        data_dir.mkdir(exist_ok=True)
        shutil.move(str(base_dir / "data" / "vector_db"), str(data_dir / "vector_db"))
        print("   ✓ data/vector_db/ → rag_pipeline/data/vector_db/")
    
    # Move tests
    if (base_dir / "tests").exists():
        shutil.move(str(base_dir / "tests"), str(rag_dir / "tests"))
        print("   ✓ tests/ → rag_pipeline/tests/")
    
    # Move configs
    if (base_dir / "configs").exists():
        shutil.move(str(base_dir / "configs"), str(rag_dir / "configs"))
        print("   ✓ configs/ → rag_pipeline/configs/")
    
    # Move utils
    if (base_dir / "utils").exists():
        shutil.move(str(base_dir / "utils"), str(rag_dir / "utils"))
        print("   ✓ utils/ → rag_pipeline/utils/")
    
    # Move docs
    if (base_dir / "docs").exists():
        shutil.move(str(base_dir / "docs"), str(rag_dir / "docs"))
        print("   ✓ docs/ → rag_pipeline/docs/")
    
    # Move other RAG files
    rag_files = [
        "cement_rag_config.yaml",
        "test_embeddings.py",
        "test_pdf_extraction.py", 
        "test_preprocessing_pipeline.py",
        "RAG_PIPELINE_DESIGN.md",
        "IMPLEMENTATION_PROGRESS.md",
        "PDF_EXTRACTION_TEST_RESULTS.md",
        "REVENUE_GROWTH_GUIDANCE_ANALYSIS.md",
        "REVENUE_GROWTH_GUIDANCE_ANALYSIS.py",
        "README_TASK_BASED.md",
        "QUICK_START_GUIDE.md"
    ]
    
    for file in rag_files:
        src = base_dir / file
        if src.exists():
            dst = rag_dir / file
            shutil.move(str(src), str(dst))
            print(f"   ✓ {file} → rag_pipeline/")
    
    # Move concall downloader files
    print("\n3. Moving concall downloader files...")
    concall_dir = base_dir / "concall_downloader"
    
    for file in structure["concall_downloader"]["files"]:
        src = base_dir / file
        if src.exists():
            dst = concall_dir / file
            shutil.move(str(src), str(dst))
            print(f"   ✓ {file} → concall_downloader/")
    
    # Move Cement_Concall_Transcripts folder
    transcripts_src = base_dir.parent / "Cement_Concall_Transcripts"
    if transcripts_src.exists():
        transcripts_dst = concall_dir / "Cement_Concall_Transcripts"
        if not transcripts_dst.exists():
            shutil.copytree(str(transcripts_src), str(transcripts_dst))
            print(f"   ✓ Cement_Concall_Transcripts/ → concall_downloader/")
    
    # Move data scraping files
    print("\n4. Moving data scraping files...")
    scraping_dir = base_dir / "data_scraping"
    
    for file in structure["data_scraping"]["files"]:
        src = base_dir / file
        if src.exists():
            dst = scraping_dir / file
            shutil.move(str(src), str(dst))
            print(f"   ✓ {file} → data_scraping/")
    
    # Move nifty50_results and verdict_reports
    if (base_dir / "nifty50_results").exists():
        shutil.move(str(base_dir / "nifty50_results"), str(scraping_dir / "nifty50_results"))
        print(f"   ✓ nifty50_results/ → data_scraping/")
    
    if (base_dir / "verdict_reports").exists():
        shutil.move(str(base_dir / "verdict_reports"), str(scraping_dir / "verdict_reports"))
        print(f"   ✓ verdict_reports/ → data_scraping/")
    
    # Move report files
    print("\n5. Moving report files...")
    reports_dir = base_dir / "reports"
    
    for file in structure["reports"]["files"]:
        src = base_dir / file
        if src.exists():
            dst = reports_dir / file
            shutil.move(str(src), str(dst))
            print(f"   ✓ {file} → reports/")
    
    # Create master README
    print("\n6. Creating master README...")
    create_proper_readme(base_dir)
    
    # Keep common files
    common_files = ["config.py", "requirements.txt", "README.md"]
    print("\n7. Common files kept at root:")
    for file in common_files:
        if (base_dir / file).exists():
            print(f"   ✓ {file}")
    
    print("\n" + "="*80)
    print("✅ PROPER RESTRUCTURING COMPLETE!")
    print("="*80)
    
    print("\nNew structure:")
    print("""
    Data_Scraping/
    ├── rag_pipeline/              # All RAG-related work
    │   ├── core/                  # Vector store, processing
    │   ├── tasks/                 # Business questions
    │   ├── data/vector_db/        # Vector database
    │   ├── tests/                 # RAG tests
    │   ├── utils/                 # Build scripts
    │   └── docs/                  # RAG documentation
    │
    ├── concall_downloader/        # All concall downloading
    │   ├── download_*.py          # Download scripts
    │   ├── extract_*.py           # URL extraction
    │   └── Cement_Concall_Transcripts/  # Downloaded PDFs
    │
    ├── data_scraping/             # Company data scraping
    │   ├── extract_cement_companies.py
    │   ├── find_cement_companies.py
    │   ├── check_cement_data.py
    │   └── nifty50_results/       # Scraping results
    │
    ├── reports/                   # Final reports
    │   ├── FINAL_COMPLETE_REPORT.py
    │   └── FINAL_SUMMARY_REPORT.py
    │
    ├── config.py                  # Common config
    ├── requirements.txt           # Dependencies
    └── README.md                  # Main README
    """)
    
    print("\nClean separation by functionality:")
    print("  • Want to work on RAG? → rag_pipeline/")
    print("  • Need to download concalls? → concall_downloader/")
    print("  • Scraping company data? → data_scraping/")
    print("  • Generate reports? → reports/")

def create_proper_readme(base_dir):
    """Create proper master README."""
    
    readme_content = """# Data Scraping & Analysis Project

## 📁 Project Structure (Organized by Functionality)

### 1. rag_pipeline/
**Purpose:** Complete RAG (Retrieval Augmented Generation) system for analyzing cement concall transcripts

**Contents:**
- `core/` - Vector store, text processing, entity extraction
- `tasks/` - Business analysis tasks (growth, profitability, costs, etc.)
- `data/vector_db/` - 4,185 indexed chunks from 55 concalls
- `tests/` - RAG testing scripts
- `utils/` - Index building utilities
- `docs/` - RAG documentation

**Quick Start:**
```bash
cd rag_pipeline
python tasks/growth_analysis/run_analysis.py
```

**Documentation:** See `rag_pipeline/QUICK_START_GUIDE.md`

---

### 2. concall_downloader/
**Purpose:** Download and manage cement company conference call transcripts

**Contents:**
- `download_concalls_final.py` - Main download script
- `retry_failed_downloads.py` - Retry failed downloads
- `extract_concall_urls_2years.py` - Extract URLs
- `Cement_Concall_Transcripts/` - Downloaded PDFs (55 files)

**Quick Start:**
```bash
cd concall_downloader
python download_concalls_final.py
```

**Output:** PDFs in `Cement_Concall_Transcripts/` organized by company

---

### 3. data_scraping/
**Purpose:** Scrape and clean cement company data from various sources

**Contents:**
- `extract_cement_companies.py` - Extract company lists
- `find_cement_companies.py` - Find cement companies
- `check_cement_data.py` - Validate data
- `clean_cement_data.py` - Clean datasets
- `nifty50_results/` - Scraping results
- `Cement_Companies_Concalls_2Years_FINAL_*.csv` - Final dataset

**Quick Start:**
```bash
cd data_scraping
python extract_cement_companies.py
```

---

### 4. reports/
**Purpose:** Generate final analysis reports

**Contents:**
- `FINAL_COMPLETE_REPORT.py` - Complete analysis report
- `FINAL_SUMMARY_REPORT.py` - Summary report
- `final_check.py` - Data validation

**Quick Start:**
```bash
cd reports
python FINAL_COMPLETE_REPORT.py
```

---

## 🚀 Common Workflows

### Workflow 1: Download New Concalls
```bash
cd concall_downloader
python download_concalls_final.py
```

### Workflow 2: Rebuild RAG Index
```bash
cd rag_pipeline
python utils/build_vector_index.py --reset
```

### Workflow 3: Run Analysis
```bash
cd rag_pipeline
python tasks/growth_analysis/run_analysis.py
```

### Workflow 4: Scrape New Data
```bash
cd data_scraping
python extract_cement_companies.py
```

---

## 📊 Project Status

- **Concalls Downloaded:** 55 PDFs (13 companies, 2 years)
- **RAG Index:** 4,185 chunks indexed
- **Companies:** 13 cement companies
- **Analysis Complete:** Growth analysis (Q1)
- **Ready Tasks:** 6 more analysis tasks available

---

## 🛠️ Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configuration
Edit `config.py` for common settings used across all modules.

---

## 📚 Documentation

- **RAG Pipeline:** `rag_pipeline/QUICK_START_GUIDE.md`
- **Concall Downloader:** `concall_downloader/CONCALL_README.md`
- **Main README:** This file

---

## 🗂️ File Organization Philosophy

**Grouped by WHAT you want to do, not HOW it's implemented:**

✅ **Want to analyze concalls?** → `rag_pipeline/`
✅ **Need to download transcripts?** → `concall_downloader/`
✅ **Scraping company data?** → `data_scraping/`
✅ **Generate reports?** → `reports/`

❌ **NOT organized by:** technical layers (src/, scripts/, tests/)

---

**Last Updated:** December 2, 2025
"""
    
    readme_path = base_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✓ Created: README.md")

if __name__ == "__main__":
    proper_restructure()
