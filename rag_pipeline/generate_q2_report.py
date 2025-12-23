"""
Q2: Capex Guidance - Simplified Fast Report
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
    print("Q2: CAPITAL EXPENDITURE GUIDANCE ANALYSIS")
    print("="*100)
    print()
    
    # Load vector store
    # Correctly resolve the path to the data directory
    base_dir = Path(__file__).resolve().parent
    vector_db_path = base_dir / "data" / "vector_db_all"
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
    
    # Search queries - focused on capex guidance with multiple angles
    queries = [
        "capex capital expenditure budget FY26 FY27 FY28 guidance",
        "capex crores investment spending plan allocation",
        "growth capex maintenance capex expansion modernization",
        "capex percentage revenue ratio outlook",
        "capex spending guidance next year projects",
        "capacity expansion investment capex commitment"
    ]
    
    print("CAPITAL EXPENDITURE GUIDANCE BY COMPANY")
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
            print("   No specific capex guidance found.\n")
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
            
            # Highlight capex-related keywords
            keywords = ['capex', 'capital expenditure', 'investment', 'spending', 
                       'crore', 'expansion', 'maintenance', 'growth', 'budget']
            
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
1. CONCRETE FIGURES:
   - Absolute capex amounts (INR crores)
   - FY-specific capex budgets
   - Multi-year capex commitments

2. CAPEX COMPOSITION:
   - Growth vs Maintenance capex split
   - % allocated to expansion vs modernization
   - Capex as % of revenue guidance

3. INVESTMENT PRIORITIES:
   - Capacity expansion (grinding/clinker)
   - Waste heat recovery systems
   - Green energy investments (solar/wind)
   - Logistics & distribution infrastructure
   - Digital transformation

4. DIRECTIONAL COMMENTARY:
   - Increasing vs decreasing capex trend
   - Completion timelines for major projects
   - ROI expectations from capex
    """)
    
    print("✅ Report complete!")
    print("="*100)

if __name__ == "__main__":
    main()
