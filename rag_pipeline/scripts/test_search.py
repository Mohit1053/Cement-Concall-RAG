"""
Test vector store search functionality
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vectorstore.tfidf_store import TFIDFVectorStore

def test_search():
    """Test searching the vector database."""
    print("="*80)
    print("VECTOR STORE SEARCH TEST")
    print("="*80)
    
    # Load vector store
    print("\n1. Loading vector store...")
    store = TFIDFVectorStore(persist_dir="data/vector_db")
    
    if not store.load():
        print("❌ Failed to load vector store. Run build_vector_index.py first.")
        return
    
    stats = store.get_stats()
    print(f"✓ Loaded: {stats['total_vectors']} vectors, {stats['vocabulary_size']} vocabulary")
    
    # Test queries
    queries = [
        "What was ACC Limited's revenue in Q2?",
        "Tell me about cement capacity expansion",
        "EBITDA margins and profitability",
        "Cost of production and fuel expenses",
        "What are the future growth plans?"
    ]
    
    print("\n" + "="*80)
    print("RUNNING TEST QUERIES")
    print("="*80)
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 80)
        
        results = store.search(query, top_k=3)
        
        if not results:
            print("   No results found.")
            continue
        
        for j, result in enumerate(results, 1):
            print(f"\n   Result {j} (Score: {result['score']:.3f})")
            print(f"   Company: {result.get('company_name', 'N/A')}")
            print(f"   Quarter: {result.get('quarter', 'N/A')} {result.get('fiscal_year', 'N/A')}")
            print(f"   Type: {result.get('chunk_type', 'N/A')}")
            text = result['text'][:200].replace('\n', ' ')
            print(f"   Text: {text}...")
    
    # Test filtered search
    print("\n" + "="*80)
    print("FILTERED SEARCH TEST")
    print("="*80)
    
    print("\nQuery: 'revenue and margins'")
    print("Filter: company_name = 'ACC Limited'")
    print("-" * 80)
    
    results = store.search(
        "revenue and margins", 
        top_k=3,
        filters={'company_name': 'ACC Limited'}
    )
    
    for j, result in enumerate(results, 1):
        print(f"\n   Result {j} (Score: {result['score']:.3f})")
        print(f"   Quarter: {result.get('quarter', 'N/A')} {result.get('fiscal_year', 'N/A')}")
        text = result['text'][:150].replace('\n', ' ')
        print(f"   Text: {text}...")
    
    print("\n" + "="*80)
    print("✅ Search test complete!")
    print("="*80)


if __name__ == "__main__":
    test_search()
