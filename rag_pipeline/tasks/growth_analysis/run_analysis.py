"""
Launcher for growth analysis - handles console encoding
"""
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from vector_store.tfidf_store import TFIDFVectorStore
from collections import defaultdict

def query_revenue_guidance():
    """Query for revenue growth guidance and management hints."""
    
    print("="*80)
    print("Q1: REVENUE GROWTH GUIDANCE & MANAGEMENT HINTS")
    print("="*80)
    
    # Load vector store
    print("\nLoading vector database...")
    vector_db_path = Path(__file__).parent.parent.parent / "data" / "vector_db"
    store = TFIDFVectorStore(persist_dir=str(vector_db_path))
    
    if not store.load():
        print("Failed to load vector store. Run build_vector_index.py first.")
        return
    
    stats = store.get_stats()
    print(f"Loaded: {stats['total_vectors']} chunks from {stats['vocabulary_size']} vocabulary terms\n")
    
    # Define search queries for revenue guidance
    queries = [
        "revenue growth guidance forecast next year future",
        "management guidance revenue targets projections",
        "capacity expansion FY26 FY27 FY28",
        "growth plans topline outlook"
    ]
    
    print("Searching for revenue growth guidance...\n")
    print("="*80)
    
    # Collect results by company
    company_results = defaultdict(list)
    
    for query in queries:
        results = store.search(query, top_k=8)
        
        for result in results:
            company = result.get('company_name', 'Unknown')
            quarter = result.get('quarter', 'N/A')
            fy = result.get('fiscal_year', 'N/A')
            score = result['score']
            text = result['text']
            
            key = f"{company}_{quarter}_{fy}"
            if key not in [r['key'] for r in company_results[company]]:
                company_results[company].append({
                    'key': key,
                    'quarter': quarter,
                    'fy': fy,
                    'score': score,
                    'text': text
                })
    
    # Sort and display
    sorted_companies = sorted(company_results.items(), 
                            key=lambda x: len(x[1]), 
                            reverse=True)
    
    for company, results in sorted_companies[:5]:  # Top 5 companies
        print(f"\n{'='*80}")
        print(f"COMPANY: {company}")
        print(f"{'='*80}")
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        for i, result in enumerate(results[:3], 1):  # Top 3 results per company
            print(f"\n{i}. {result['quarter']} {result['fy']} (Score: {result['score']:.3f})")
            print("-" * 80)
            
            # Extract relevant sentences
            text = result['text']
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            relevant = [s for s in sentences if any(kw in s.lower() 
                       for kw in ['guidance', 'growth', 'revenue', 'capacity', 
                                  'expansion', 'fy26', 'fy27', 'fy28', 'million tons'])]
            
            if relevant:
                for sent in relevant[:3]:
                    print(f"   - {sent}")
            else:
                print(f"   {text[:250]}...")
    
    print("\n" + "="*80)
    print("Analysis complete! See full report: REVENUE_GROWTH_GUIDANCE_ANALYSIS.md")
    print("="*80)

if __name__ == "__main__":
    query_revenue_guidance()
