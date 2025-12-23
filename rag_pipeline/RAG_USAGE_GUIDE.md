# 🔍 RAG Query System - Quick Start Guide

## ✅ System Status
- **Mode:** 100% Offline
- **Database:** 12,277 text chunks from 171 PDF transcripts
- **Companies:** 13 major cement companies
- **Period:** 2-year concall transcripts
- **New:** Concise answers with source references + date-aware prioritization

---

## 🚀 How to Use

### Method 1: Interactive Mode (Recommended)
```bash
cd C:\Users\mohit1\Desktop\Data_Scraping\rag_pipeline
C:\Python314\python.exe query_rag.py
```

Then type your questions interactively. Commands:
- Type any question and press Enter
- Type `help` to see examples
- Type `exit` or `quit` to exit

### Method 2: Direct Query Mode
```bash
cd C:\Users\mohit1\Desktop\Data_Scraping\rag_pipeline
C:\Python314\python.exe query_rag.py "your question here"
```

---

## 📊 New Output Format

The system now provides **2-section responses**:

### 1. 📝 CONCISE ANSWER (NEW!)
- **2-3 line summary** of key findings
- **Specific numbers** and guidance statements
- **Source references** with report dates
- Example:
  ```
  1. Dalmia Bharat Ltd: revenue growth was 20% | 16% volume
  2. Dalmia Bharat Ltd: 15% CAGR volume target | 110-130 million tons by 2031
  
  📎 Sources:
     [1] Dalmia Bharat Ltd_February_2024_Concall.pdf (February 24)
     [2] Dalmia Bharat Ltd_February_2023_Concall.pdf (February 23)
  ```

### 2. 📚 Detailed Evidence
- Full context from 5-8 source documents
- **Company name**, **relevance score**, **report date**
- Highlighted key statements with ► markers
- Explanation of why each result is relevant

---

## 🎯 Enhanced Features

### Date-Aware Prioritization
- System automatically detects **FY years** in your query (FY26, FY27, 2025, etc.)
- **Prioritizes reports** from the mentioned year or period
- **Latest reports** (2025) get highest priority, followed by 2024, 2023

**Examples:**
```bash
# Automatically prioritizes FY26/FY27 guidance
python query_rag.py "What capex guidance for FY26 and FY27?"

# Prioritizes 2025 reports
python query_rag.py "Latest revenue growth targets 2025"

# Finds historical data from 2023
python query_rag.py "FY23 capex spending actual"
```

### Company Detection
Automatically recognizes company names and aliases:
- "Dalmia" → Dalmia Bharat Ltd
- "UltraTech" → UltraTech Cement
- "Shree" → Shree Cement
- And all 13 cement companies

### Financial Keyword Weighting
Higher priority for:
- **Guidance** (2.5x weight)
- **Capex** (2.5x weight)
- **Revenue** (2.0x weight)
- **Growth** (1.8x weight)
- **FY years** (2.0x weight)

## 📝 Example Queries

### Company-Specific with FY Years (Best Results!)
```bash
# UltraTech
python query_rag.py "What capex guidance did UltraTech provide for FY26 and FY27?"
python query_rag.py "UltraTech revenue growth target FY26"

# Dalmia Bharat
python query_rag.py "What guidance has Dalmia shared on expected revenue growth?"
python query_rag.py "Dalmia capex plan for FY25 and FY26"

# Shree Cement
python query_rag.py "Shree Cement capex guidance FY24 and FY25"
python query_rag.py "What expansion plans does Shree Cement have for FY26?"

# Star Cement
python query_rag.py "Star Cement capex for FY26 FY27"
python query_rag.py "Star Cement volume growth target"
```

### General Industry Questions
```bash
# Revenue Growth
python query_rag.py "What is the revenue growth guidance for FY26?"
python query_rag.py "Which companies are targeting double digit growth?"

# Capex Plans
python query_rag.py "What is the total capex planned for FY26?"
python query_rag.py "Tell me about capacity expansion projects FY26 FY27"

# Market Outlook
python query_rag.py "What is the demand outlook for cement industry?"
python query_rag.py "How are companies viewing pricing trends in 2025?"
```

---

## 💡 Tips for Better Results

1. **Include FY Years:** Mention specific fiscal years for best accuracy
   - ✅ "Dalmia revenue growth guidance for FY26 and FY27"
   - ✅ "What capex planned for FY25?"
   - ❌ "Tell me about capex" (too vague)

2. **Be Specific:** Include company names and numbers
   - ✅ "UltraTech capex 9000 crores FY26"
   - ✅ "Star Cement 823 crores expansion"
   - ❌ "Tell me about cement companies"

3. **Use Financial Keywords:** Include relevant terms
   - capex, revenue, EBITDA, guidance, expansion, capacity, growth, crores, target

4. **Ask Direct Questions:** System optimized for specific queries
   - ✅ "What guidance has Dalmia shared on expected revenue growth?"
   - ✅ "What is UltraTech's capex for FY26?"
   - ❌ "Tell me everything about cement industry"

5. **Latest Data Priority:** For recent guidance, mention 2025 or latest
   - ✅ "Latest capex guidance for 2025"
   - ✅ "Most recent revenue targets"

---

## 📊 Sample Output with New Format

```
================================================================================
QUERY: What capex guidance did UltraTech provide for FY26 and FY27?
================================================================================

📌 Detected Companies: UltraTech, UltraTech Cement
🔑 Key Topics: guidance, capex, fy

================================================================================
📝 CONCISE ANSWER
================================================================================
1. UltraTech Cement: fy27 once we are at 211 million tons
2. JK Lakshmi Cement: fy25 and fy26 - 500 crores, then 700 next year

📎 Sources:
   [1] UltraTech Cement_March_2025_Concall.pdf (March 25)
   [2] JK Lakshmi Cement_November_2024_Concall.pdf (November 24)
================================================================================

📚 Detailed Evidence (8 sources):

────────────────────────────────────────────────────────────────────────────────
Result #1 | Company: UltraTech Cement | Relevance Score: 1.297
Source: UltraTech Cement_March_2025_Concall.pdf
Report Date: March 25
Why Relevant: Exact company match; Contains 'capex'; Mentions target FY: FY27
────────────────────────────────────────────────────────────────────────────────
   ► it will be roughly Rs. 80,000 crores by FY27 once we are at 211 million
     tons, is that the way to look at it, beyond that, we?
...
```

---

## ⚙️ System Requirements

- **Python:** 3.10 or higher
- **Dependencies:** scikit-learn, numpy (already installed)
- **Database:** Must have `data/vector_db_all/` folder with index files
- **Internet:** Not required (100% offline)

---

## 🆘 Troubleshooting

**Problem:** "Vector database not found"
```bash
# Solution: Build the database first
cd C:\Users\mohit1\Desktop\Data_Scraping\rag_pipeline
python build_all_concalls_index.py
```

**Problem:** No relevant results found
- Try rephrasing your question
- Use more specific keywords
- Check spelling of company names

**Problem:** Unicode errors on Windows
- Already handled with UTF-8 encoding wrapper
- If issues persist, check terminal encoding settings

---

## 📁 Related Files

- `query_rag.py` - Main RAG query script (this tool)
- `data/vector_db_all/` - Vector database (12,277 chunks)
- `generate_q1_report.py` - Pre-built Q1 revenue report generator
- `generate_q2_report.py` - Pre-built Q2 capex report generator
- `FINAL_ANALYSIS_SUMMARY.md` - Executive summary of key findings

---

## 🎓 Understanding Results

**Score Interpretation:**
- **0.3 - 1.0:** Highly relevant (exact match on keywords)
- **0.2 - 0.3:** Moderately relevant (partial match)
- **0.1 - 0.2:** Somewhat relevant (tangential)
- **< 0.1:** Low relevance (consider rephrasing)

**Best Practices:**
- Review top 3-5 results carefully
- Cross-reference company names and dates
- Look for specific numbers and guidance statements
- Check source file dates for timeliness

---

**Ready to query? Run:**
```bash
python query_rag.py
```

**Or jump right in with:**
```bash
python query_rag.py "What is the capex guidance for major cement companies?"
```
