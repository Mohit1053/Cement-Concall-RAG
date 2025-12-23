"""
Enhanced RAG Query System with Improved Accuracy
- Better query preprocessing
- Context-aware retrieval
- Relevance scoring with company/topic matching
- Result deduplication and ranking
"""
import sys
import io
from pathlib import Path
import re
from collections import defaultdict

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent / "core"))

from vector_store.tfidf_store import TFIDFVectorStore

class EnhancedRAG:
    def __init__(self, vector_db_path):
        self.vector_db_path = Path(vector_db_path)
        self.store = None
        self.load_database()
        
        # Financial keywords for relevance boosting
        self.financial_keywords = {
            'revenue': 2.0,
            'growth': 1.8,
            'guidance': 2.5,
            'target': 2.0,
            'expectation': 1.8,
            'outlook': 2.0,
            'capex': 2.5,
            'capital expenditure': 2.5,
            'investment': 1.8,
            'expansion': 1.8,
            'ebitda': 2.0,
            'margin': 2.0,
            'crore': 1.5,
            'fy': 2.0,
            'projection': 2.0,
            'forecast': 2.0
        }
        
        # Company name variations
        self.company_aliases = {
            'dalmia': ['Dalmia Bharat', 'Dalmia Bharat Ltd'],
            'ultratech': ['UltraTech Cement', 'UltraTech'],
            'acc': ['ACC Limited', 'ACC'],
            'ambuja': ['Ambuja Cements'],
            'shree': ['Shree Cement'],
            'birla': ['Birla Corporation'],
            'jk cement': ['J K Cement'],
            'lakshmi': ['JK Lakshmi Cement'],
            'ramco': ['The Ramco Cements'],
            'india cement': ['India Cements'],
            'star': ['Star Cement'],
            'nuvoco': ['Nuvoco Vistas'],
            'grasim': ['Grasim Industries']
        }
    
    def load_database(self):
        """Load the vector database"""
        print("="*80)
        print("ENHANCED RAG SYSTEM - High-Accuracy Financial Analysis")
        print("="*80)
        print(f"\nLoading vector database from: {self.vector_db_path}")
        
        self.store = TFIDFVectorStore(persist_dir=str(self.vector_db_path))
        self.store.load()
        
        print(f"✓ Successfully loaded {len(self.store.texts)} text chunks")
        print(f"✓ Enhanced query system ready\n")
    
    def preprocess_query(self, query):
        """Extract key entities and create enhanced query"""
        # Extract company names
        companies = self._extract_companies(query)
        
        # Extract keywords
        keywords = self._extract_keywords(query)
        
        # Create expanded query with synonyms
        expanded_query = self._expand_query(query, keywords)
        
        return {
            'original': query,
            'expanded': expanded_query,
            'companies': companies,
            'keywords': keywords
        }
    
    def _extract_companies(self, query):
        """Extract company names from query"""
        query_lower = query.lower()
        companies = []
        
        for alias, full_names in self.company_aliases.items():
            if alias in query_lower:
                companies.extend(full_names)
        
        return list(set(companies))
    
    def _extract_keywords(self, query):
        """Extract important keywords"""
        query_lower = query.lower()
        found_keywords = []
        
        for keyword in self.financial_keywords.keys():
            if keyword in query_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _expand_query(self, query, keywords):
        """Expand query with synonyms and related terms"""
        expansions = {
            'revenue growth': ['topline growth', 'sales growth', 'turnover growth'],
            'guidance': ['target', 'projection', 'outlook', 'expectation'],
            'capex': ['capital expenditure', 'investment', 'spending'],
            'expansion': ['capacity addition', 'brownfield', 'greenfield'],
            'indirect hints': ['management commentary', 'outlook', 'strategic plans']
        }
        
        expanded = query
        for term, synonyms in expansions.items():
            if term in query.lower():
                expanded += " " + " ".join(synonyms)
        
        return expanded
    
    def query(self, question, top_k=None):
        """
        Enhanced query with better relevance scoring
        """
        print(f"\n{'='*80}")
        print(f"QUERY: {question}")
        print(f"{'='*80}\n")
        
        # Preprocess query
        processed_query = self.preprocess_query(question)
        
        if processed_query['companies']:
            print(f"📌 Detected Companies: {', '.join(processed_query['companies'])}")
        if processed_query['keywords']:
            print(f"🔑 Key Topics: {', '.join(processed_query['keywords'])}")
        print()
        
        # Auto-detect result count
        if top_k is None:
            top_k = self._detect_result_count(question)
        
        # Get more results for reranking
        search_limit = min(top_k * 5, 100)
        
        # Search with expanded query
        results = self.store.search(processed_query['expanded'], top_k=search_limit)
        
        if not results:
            print("❌ No results found. Try rephrasing your question.\n")
            return []
        
        # Re-rank results based on company match and keyword relevance
        scored_results = self._rerank_results(
            results, 
            processed_query['companies'],
            processed_query['keywords'],
            question
        )
        
        # Deduplicate similar results
        unique_results = self._deduplicate_results(scored_results)
        
        # Take top results
        final_results = unique_results[:top_k]
        
        # Generate concise summary answer
        summary = self._generate_summary_answer(final_results, question, processed_query)
        
        print(f"\n{'='*80}")
        print("📝 CONCISE ANSWER")
        print(f"{'='*80}")
        print(summary)
        print(f"{'='*80}\n")
        
        print(f"📚 Detailed Evidence ({len(final_results)} sources):\n")
        
        # Display results
        for i, result in enumerate(final_results, 1):
            metadata = result.get('metadata', {})
            company = metadata.get('company_name', 'Unknown')
            source = metadata.get('source_file', 'Unknown')
            score = result.get('final_score', 0.0)
            relevance = result.get('relevance_reason', '')
            
            print(f"\n{'─'*80}")
            print(f"Result #{i} | Company: {company} | Relevance Score: {score:.3f}")
            print(f"Source: {source}")
            print(f"Report Date: {result.get('report_date', 'Unknown')}")
            if relevance:
                print(f"Why Relevant: {relevance}")
            print(f"{'─'*80}")
            
            # Show text with highlighting
            text = result.get('text', '')
            self._print_highlighted_text(text, processed_query['keywords'])
            print()
        
        return final_results
    
    def _generate_summary_answer(self, results, question, processed_query):
        """
        Generate a concise 2-3 line answer with source references
        """
        if not results:
            return "No relevant information found."
        
        # Extract key numbers and guidance statements
        key_findings = []
        sources = []
        
        for result in results[:5]:  # Top 5 results
            text = result.get('text', '')
            metadata = result.get('metadata', {})
            company = metadata.get('company_name', 'Unknown')
            source_file = metadata.get('source_file', 'Unknown')
            report_date = result.get('report_date', 'Unknown')
            
            # Extract specific numbers and guidance
            guidance_matches = []
            
            # Extract FY years with numbers
            fy_patterns = [
                r'(fy\s*[\'"]?\d{2}[^.]{0,100}?(?:\d+\s*(?:crore|%|million|ton|billion)[s]?))',
                r'(\d+\s*(?:crore|%)[s]?[^.]{0,80}?(?:growth|target|guidance|capex|revenue))',
                r'((?:growth|capex|revenue|target)[^.]{0,80}?(?:\d+\s*(?:crore|%|million|ton)[s]?))',
            ]
            
            for pattern in fy_patterns:
                matches = re.findall(pattern, text.lower())
                guidance_matches.extend(matches[:2])  # Take top 2 matches
            
            if guidance_matches:
                # Clean and format
                finding = ' | '.join(set(guidance_matches[:2]))
                finding = re.sub(r'\s+', ' ', finding).strip()[:150]
                key_findings.append(f"{company}: {finding}")
                sources.append(f"{source_file} ({report_date})")
        
        # Build concise summary
        if key_findings:
            summary_lines = []
            
            # Add key findings (2-3 lines max)
            for i, finding in enumerate(key_findings[:3], 1):
                summary_lines.append(f"{i}. {finding}")
            
            summary = "\n".join(summary_lines)
            
            # Add source references
            unique_sources = list(dict.fromkeys(sources[:3]))  # Remove duplicates, keep order
            summary += "\n\n📎 Sources:\n"
            for i, src in enumerate(unique_sources, 1):
                summary += f"   [{i}] {src}\n"
        else:
            # Fallback: mention company and general topic
            companies = processed_query.get('companies', [])
            keywords = processed_query.get('keywords', [])
            
            if companies:
                summary = f"Information found for {', '.join(companies[:2])}.\n"
            else:
                summary = "Information found from multiple cement companies.\n"
            
            summary += f"Key topics: {', '.join(keywords[:3]) if keywords else 'financial guidance'}.\n"
            summary += f"See detailed evidence below from {len(results)} sources."
        
        return summary
    
    def _rerank_results(self, results, companies, keywords, original_query):
        """
        Re-rank results based on:
        1. Company name match
        2. Keyword presence
        3. Specific number/guidance mentions
        4. Recency and FY year match (ENHANCED)
        """
        # Extract target FY years from query (e.g., FY26, FY27)
        target_years = re.findall(r'fy\s*[\'"]?(\d{2})', original_query.lower())
        target_years.extend(re.findall(r'20(\d{2})', original_query.lower()))
        target_years = list(set(target_years))
        
        for result in results:
            base_score = result.get('score', 0.0)
            bonus_score = 0.0
            relevance_reasons = []
            
            text_lower = result.get('text', '').lower()
            metadata = result.get('metadata', {})
            company_name = metadata.get('company_name', '')
            source_file = metadata.get('source_file', '')
            
            # Company match bonus
            if companies:
                if any(comp.lower() in company_name.lower() for comp in companies):
                    bonus_score += 0.3
                    relevance_reasons.append(f"Exact company match: {company_name}")
            
            # Keyword presence bonus
            for keyword in keywords:
                if keyword in text_lower:
                    weight = self.financial_keywords.get(keyword, 1.0)
                    bonus_score += 0.05 * weight
                    relevance_reasons.append(f"Contains '{keyword}'")
            
            # Extract report date from filename (e.g., "March_2025", "November_2024")
            date_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)[_\s]+(20\d{2})', source_file.lower())
            report_year = None
            report_month = None
            if date_match:
                report_month = date_match.group(1)
                report_year = date_match.group(2)[-2:]  # Last 2 digits
            
            # HIGH PRIORITY: Match target FY years in both query and text content
            if target_years:
                content_years = re.findall(r'fy\s*[\'"]?(\d{2})', text_lower)
                content_years.extend(re.findall(r'20(\d{2})', text_lower))
                
                # Check if text mentions the target FY years
                matching_years = set(target_years) & set(content_years)
                if matching_years:
                    bonus_score += 0.4  # STRONG boost for FY year match
                    relevance_reasons.append(f"Mentions target FY: {', '.join(['FY' + y for y in matching_years])}")
            
            # Recency bonus based on report date (prioritize latest reports)
            if report_year:
                if report_year in ['25']:  # 2025
                    bonus_score += 0.15
                    relevance_reasons.append("Latest 2025 report")
                elif report_year in ['24']:  # 2024
                    bonus_score += 0.10
                    relevance_reasons.append("Recent 2024 report")
                elif report_year in ['23']:  # 2023
                    bonus_score += 0.05
            
            # Specific guidance indicators
            guidance_patterns = [
                r'fy\s*[\'"]?\d{2}',  # FY26, FY'26
                r'\d+\s*%',  # 15%
                r'\d+\s*crores?',  # 5000 crores
                r'target|guidance|expect|projec',
                r'double.digit|single.digit',
                r'growth\s+of\s+\d+',
            ]
            
            for pattern in guidance_patterns:
                if re.search(pattern, text_lower):
                    bonus_score += 0.1
                    relevance_reasons.append("Contains specific guidance/numbers")
                    break
            
            # Calculate final score
            result['final_score'] = base_score + bonus_score
            result['relevance_reason'] = '; '.join(relevance_reasons[:4])  # Top 4 reasons
            result['report_date'] = f"{report_month.title()} {report_year}" if report_month and report_year else "Unknown"
        
        # Sort by final score
        results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        return results
    
    def _deduplicate_results(self, results):
        """Remove duplicate or very similar results"""
        unique_results = []
        seen_texts = set()
        
        for result in results:
            text = result.get('text', '')
            # Create fingerprint (first 100 chars)
            fingerprint = text[:100].strip()
            
            if fingerprint not in seen_texts:
                seen_texts.add(fingerprint)
                unique_results.append(result)
        
        return unique_results
    
    def _print_highlighted_text(self, text, keywords):
        """Print text with keywords highlighted"""
        # Show first 800 chars
        excerpt = text[:800]
        if len(text) > 800:
            excerpt += "..."
        
        lines = excerpt.split('\n')
        for line in lines:
            line_lower = line.lower()
            # Check if line contains important keywords
            has_keyword = any(kw in line_lower for kw in keywords)
            has_number = bool(re.search(r'\d+\s*(crore|%|million|ton)', line_lower))
            
            if has_keyword or has_number:
                print(f"   ► {line.strip()}")
            elif line.strip():
                print(f"     {line.strip()}")
    
    def _detect_result_count(self, question):
        """Intelligently detect result count"""
        question_lower = question.lower()
        
        comprehensive_keywords = [
            'all companies', 'all cement', 'every company', 'each company',
            'industry', 'sector', 'overall', 'companies are', 'which companies',
            'list of', 'summary of', 'overview', 'comparison', 'compare'
        ]
        
        if any(kw in question_lower for kw in comprehensive_keywords):
            return 20
        
        # For specific company queries, return fewer but higher quality results
        companies = self._extract_companies(question)
        if companies:
            return 8  # More focused results for specific companies
        
        return 5
    
    def interactive_mode(self):
        """Interactive query mode"""
        print("\n" + "="*80)
        print("INTERACTIVE MODE - Enhanced Financial RAG")
        print("="*80)
        print("\nCommands:")
        print("  - Type your question and press Enter")
        print("  - Type 'help' for examples")
        print("  - Type 'exit' to quit")
        print("\nNote: System automatically detects companies and key topics")
        print("="*80 + "\n")
        
        while True:
            try:
                user_input = input("\n💬 Your question: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Goodbye!\n")
                    break
                
                if user_input.lower() == 'help':
                    self.show_examples()
                    continue
                
                self.query(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    def show_examples(self):
        """Show example queries"""
        print("\n" + "="*80)
        print("EXAMPLE QUERIES")
        print("="*80)
        examples = [
            "What guidance has Dalmia Bharat shared on revenue growth?",
            "What is UltraTech's capex guidance for FY26 and FY27?",
            "Which cement companies provided specific growth targets?",
            "What is the capex guidance for all major cement companies?",
            "Tell me about Shree Cement's expansion plans",
            "What EBITDA margin guidance did companies provide?",
            "Which companies are investing in renewable energy?",
            "What is the industry outlook for cement demand?",
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"\n{i}. {example}")
        
        print("\n" + "="*80)


def main():
    script_dir = Path(__file__).resolve().parent
    vector_db_path = script_dir / "data" / "vector_db_all"
    
    if not vector_db_path.exists():
        print(f"❌ Error: Vector database not found at {vector_db_path}")
        return
    
    rag = EnhancedRAG(vector_db_path)
    
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:])
        rag.query(question)
    else:
        rag.interactive_mode()


if __name__ == "__main__":
    main()
