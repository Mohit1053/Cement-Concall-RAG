"""
Query template for Profitability Analysis
"""
import sys
from pathlib import Path

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from vector_store.tfidf_store import TFIDFVectorStore

def query_profitability_analysis():
    """Query for profitability analysis."""
    
    print("="*80)
    print("PROFITABILITY ANALYSIS")
    print("="*80)
    
    # Load vector store
    store = TFIDFVectorStore(persist_dir="../../data/vector_db")
    
    if not store.load():
        print("❌ Failed to load vector store")
        return
    
    stats = store.get_stats()
    print(f"\n✓ Loaded: {stats['total_vectors']} chunks\n")
    
    # Define queries
    queries = ['EBITDA margins guidance and trends', 'Cost reduction initiatives and savings', 'Operational efficiency improvements', 'Profitability per ton expectations']
    
    # Search for each query
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. {query}")
        print("-" * 80)
        
        results = store.search(query, top_k=5)
        
        for j, result in enumerate(results, 1):
            company = result.get('company_name', 'N/A')
            quarter = result.get('quarter', 'N/A')
            fy = result.get('fiscal_year', 'N/A')
            score = result['score']
            text = result['text'][:200].replace('\n', ' ')
            
            print(f"\n   Result {j} (Score: {score:.3f})")
            print(f"   Company: {company} | {quarter} {fy}")
            print(f"   Text: {text}...")
    
    print("\n" + "="*80)
    print("✅ Analysis complete!")

if __name__ == "__main__":
    query_profitability_analysis()
