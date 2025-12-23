"""
Query the RAG system for revenue growth guidance across cement companies
"""
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
    vector_db_path = Path(__file__).parent.parent.parent / "data" / "vector_db_all"
    store = TFIDFVectorStore(persist_dir=str(vector_db_path))
    
    if not store.load():
        print("❌ Failed to load vector store. Run build_vector_index.py first.")
        return
    
    stats = store.get_stats()
    print(f"✓ Loaded: {stats['total_vectors']} chunks from {stats['vocabulary_size']} vocabulary terms\n")
    
    # Define search queries for revenue guidance
    queries = [
        "revenue growth guidance forecast next year future",
        "management guidance revenue targets projections",
        "expected revenue growth trajectory outlook",
        "top line growth expectations future years",
        "revenue guidance FY26 FY27 FY28 projections",
        "growth plans capacity expansion revenue impact",
        "management commentary future revenue outlook",
        "guidance topline growth targets"
    ]
    
    print("Searching for revenue growth guidance across all companies...\n")
    print("="*80)
    
    # Collect results by company
    company_results = defaultdict(list)
    
    for query in queries:
        results = store.search(query, top_k=10)
        
        for result in results:
            # Extract metadata - company_name is nested in metadata field
            metadata = result.get('metadata', {})
            company = metadata.get('company_name', 'Unknown')
            quarter = result.get('quarter', metadata.get('quarter', 'N/A'))
            fy = result.get('fiscal_year', metadata.get('fiscal_year', 'N/A'))
            score = result['score']
            text = result['text']
            chunk_type = result.get('chunk_type', 'general')
            
            # Store unique results per company
            key = f"{company}_{quarter}_{fy}"
            if key not in [r['key'] for r in company_results[company]]:
                company_results[company].append({
                    'key': key,
                    'quarter': quarter,
                    'fy': fy,
                    'score': score,
                    'text': text,
                    'chunk_type': chunk_type
                })
    
    # Sort companies by relevance (number of relevant chunks)
    sorted_companies = sorted(company_results.items(), 
                            key=lambda x: len(x[1]), 
                            reverse=True)
    
    # Display results by company
    for company, results in sorted_companies:
        print(f"\n{'='*80}")
        print(f"COMPANY: {company}")
        print(f"{'='*80}")
        
        # Sort results by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Show top 5 most relevant chunks per company
        for i, result in enumerate(results[:5], 1):
            print(f"\n{i}. {result['quarter']} {result['fy']} (Score: {result['score']:.3f}, Type: {result['chunk_type']})")
            print("-" * 80)
            
            # Extract and display relevant sentences about guidance
            text = result['text']
            sentences = text.split('. ')
            
            # Find sentences mentioning growth, guidance, revenue, targets, etc.
            relevant_keywords = [
                'guidance', 'growth', 'revenue', 'target', 'expect', 'forecast',
                'outlook', 'trajectory', 'projection', 'plan', 'capex', 'capacity',
                'expansion', 'FY', 'next year', 'going forward', 'future'
            ]
            
            relevant_sentences = []
            for sentence in sentences:
                if any(keyword.lower() in sentence.lower() for keyword in relevant_keywords):
                    relevant_sentences.append(sentence.strip())
            
            # Display relevant sentences (max 5)
            if relevant_sentences:
                for sent in relevant_sentences[:5]:
                    print(f"   • {sent}")
            else:
                # If no keyword match, show first 300 chars
                print(f"   {text[:300]}...")
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal companies analyzed: {len(company_results)}")
    print(f"Companies with guidance mentions: {len(sorted_companies)}")
    print("\nCompanies by relevance:")
    for company, results in sorted_companies[:10]:
        print(f"  • {company}: {len(results)} relevant mentions")
    
    print("\n" + "="*80)
    print("\n💡 KEY INSIGHTS:")
    print("-" * 80)
    print("""
Based on the search results above, look for:

1. FORMAL GUIDANCE:
   - Explicit revenue/EBITDA targets for upcoming years
   - Percentage growth projections
   - Specific FY targets (FY26, FY27, etc.)

2. INDIRECT HINTS:
   - Capacity expansion plans (MT additions)
   - Capex commitments indicating growth investments
   - Market share gain aspirations
   - Utilization rate improvements expected
   - Pricing power commentary
   - Volume growth expectations
   - New plant commissioning timelines
   - Integration synergies from acquisitions

3. MANAGEMENT TONE:
   - Conservative vs optimistic outlook
   - Confidence in demand trajectory
   - Macro commentary (infrastructure, housing, etc.)
   - Competitive positioning statements
    """)
    
    print("\n✅ Analysis complete!")
    print("="*80)


if __name__ == "__main__":
    query_revenue_guidance()
