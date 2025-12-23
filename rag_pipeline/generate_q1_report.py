"""
Q1: Revenue Growth Guidance - Simplified Fast Report
"""
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent / "core"))

from vector_store.tfidf_store import TFIDFVectorStore

def main():
    print("="*100)
    print("Q1: REVENUE GROWTH GUIDANCE & MANAGEMENT HINTS")
    print("="*100)
    print()
    
    # Load vector store
    vector_db_path = Path(__file__).parent / "data" / "vector_db_all"
    print(f"Loading vector database from: {vector_db_path}")
    store = TFIDFVectorStore(persist_dir=str(vector_db_path))
    store.load()
    print(f"✓ Loaded {len(store.texts)} chunks\n")
    
    companies = [
        "ACC Limited", "Ambuja Cements", "Birla Corporation", 
        "Dalmia Bharat Ltd", "Grasim Industries", "India Cements",
        "J K Cement", "JK Lakshmi Cement", "Nuvoco Vistas",
        "Shree Cement", "Star Cement", "The Ramco Cements",
        "UltraTech Cement"
    ]
    
    # Search queries - focused on revenue/growth guidance
    queries = [
        "revenue growth guidance FY26 FY27 target",
        "topline growth outlook projection",
        "management guidance revenue target expectations",
        "capacity expansion volumes future growth"
    ]
    
    print("REVENUE GROWTH GUIDANCE BY COMPANY")
    print("="*100)
    print()
    
    for company in companies:
        print(f"\n{company.upper()}")
        print("-" * 100)
        
        # Search for this company with more comprehensive results
        all_results = []
        for query in queries:
            results = store.search(query, top_k=20)
            # Filter by company
            company_filtered = [r for r in results if r.get('metadata', {}).get('company_name') == company]
            all_results.extend(company_filtered)
        
        # Remove duplicates
        seen_texts = set()
        unique_results = []
        for result in all_results:
            text_hash = hash(result['text'][:100])
            if text_hash not in seen_texts:
                seen_texts.add(text_hash)
                unique_results.append(result)
        
        # Sort by score and keep top 5 for comprehensive coverage
        unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        top_results = unique_results[:5]
        
        if not top_results:
            print("   No specific revenue guidance found.\n")
            continue
        
        for i, result in enumerate(top_results, 1):
            metadata = result.get('metadata', {})
            source_file = metadata.get('source_file', 'Unknown')
            score = result.get('score', 0.0)
            
            print(f"\n{i}. Source: {source_file} | Score: {score:.3f}")
            
            # Print relevant excerpt
            text = result['text'][:700]
            if len(result['text']) > 700:
                text += "..."
            
            # Highlight guidance-related keywords
            keywords = ['guidance', 'growth', 'revenue', 'target', 'expect', 'forecast', 
                       'outlook', 'FY', 'capacity', 'expansion', 'projection']
            
            lines = text.split('\n')
            for line in lines:
                if any(kw.lower() in line.lower() for kw in keywords):
                    print(f"   ► {line.strip()}")
                elif line.strip():
                    print(f"     {line.strip()}")
            print()
    
    print("\n" + "="*100)
    print("KEY INSIGHTS TO LOOK FOR:")
    print("="*100)
    print("""
1. FORMAL GUIDANCE:
   - Explicit revenue/EBITDA % growth targets
   - Volume growth projections (MT)
   - Specific fiscal year targets (FY26, FY27, etc.)

2. INDIRECT HINTS:
   - Capacity expansion announcements (MT additions)
   - Capex plans indicating growth investments  
   - Market share aspirations
   - New plant commissioning timelines
   - Utilization rate improvement expectations

3. MANAGEMENT TONE:
   - Confidence in demand trajectory
   - Commentary on infrastructure/housing growth
   - Pricing power outlook
   - Competitive positioning statements
    """)
    
    print("✅ Report complete!")
    print("="*100)

if __name__ == "__main__":
    main()
