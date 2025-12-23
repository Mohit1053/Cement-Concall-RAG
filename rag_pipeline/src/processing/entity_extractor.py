"""
Entity extraction for financial and business entities
"""
import re
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

class EntityExtractor:
    """Extract named entities and financial metrics"""
    
    def __init__(self):
        # Company names in cement industry
        self.cement_companies = {
            'acc', 'ambuja', 'ultratech', 'shree cement', 'dalmia',
            'birla corporation', 'grasim', 'india cements', 'jk cement',
            'jk lakshmi', 'nuvoco', 'star cement', 'ramco', 'orient cement'
        }
        
        # Competitor companies (non-cement)
        self.competitors = {
            'tata steel', 'jsw', 'hindalco', 'vedanta', 'coal india'
        }
        
        # Financial metric patterns
        self.metric_patterns = {
            'revenue': r'revenue\s+(?:of\s+)?(?:Rs\.?\s*)?(\d+[,\d]*\.?\d*)\s*(crore|cr|million|billion|bn)',
            'ebitda': r'ebitda\s+(?:of\s+)?(?:Rs\.?\s*)?(\d+[,\d]*\.?\d*)\s*(crore|cr|million)',
            'ebitda_margin': r'ebitda\s+margin\s+(?:of\s+)?(\d+\.?\d*)\s*(%|percent|per\s*cent)',
            'profit': r'(?:net\s+)?profit\s+(?:of\s+)?(?:Rs\.?\s*)?(\d+[,\d]*\.?\d*)\s*(crore|cr|million)',
            'volume': r'volume\s+(?:of\s+)?(\d+[,\d]*\.?\d*)\s*(million\s*tonnes?|mt|tonnes?)',
            'capacity': r'capacity\s+(?:of\s+)?(\d+[,\d]*\.?\d*)\s*(million\s*tonnes?|mtpa|mt)',
            'utilization': r'(?:capacity\s+)?utilization\s+(?:of\s+)?(\d+\.?\d*)\s*(%|percent)',
            'realization': r'realization\s+(?:of\s+)?(?:Rs\.?\s*)?(\d+[,\d]*)\s*(?:per\s+)?(?:tonne|ton|bag)',
            'coal_cost': r'coal\s+cost\s+(?:of\s+)?(?:Rs\.?\s*)?(\d+[,\d]*)\s*(?:per\s+)?(?:tonne|ton)',
        }
        
        # Location patterns (Indian states/regions)
        self.regions = {
            'north', 'south', 'east', 'west', 'central',
            'gujarat', 'rajasthan', 'maharashtra', 'karnataka', 'tamil nadu',
            'andhra pradesh', 'telangana', 'madhya pradesh', 'chhattisgarh',
            'uttar pradesh', 'bihar', 'jharkhand', 'odisha', 'bengal'
        }
    
    def extract_all_entities(self, text: str) -> Dict:
        """
        Extract all entity types from text
        
        Returns:
            Dictionary with entity types and their values
        """
        entities = {
            'companies': self.extract_companies(text),
            'financial_metrics': self.extract_financial_metrics(text),
            'locations': self.extract_locations(text),
            'time_periods': self.extract_time_periods(text),
            'key_terms': self.extract_key_terms(text),
        }
        
        return entities
    
    def extract_companies(self, text: str) -> List[str]:
        """Extract mentioned company names"""
        found_companies = set()
        text_lower = text.lower()
        
        # Check cement companies
        for company in self.cement_companies:
            if company in text_lower:
                found_companies.add(company.title())
        
        # Check competitors
        for company in self.competitors:
            if company in text_lower:
                found_companies.add(company.title())
        
        return sorted(list(found_companies))
    
    def extract_financial_metrics(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract financial metrics with values
        
        Returns:
            Dict with metric names and list of {value, unit} dicts
        """
        metrics = {}
        
        for metric_name, pattern in self.metric_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if matches:
                metric_values = []
                for match in matches:
                    if isinstance(match, tuple):
                        value = match[0].replace(',', '')
                        unit = match[1] if len(match) > 1 else ''
                        metric_values.append({
                            'value': value,
                            'unit': unit
                        })
                
                metrics[metric_name] = metric_values
        
        return metrics
    
    def extract_locations(self, text: str) -> List[str]:
        """Extract geographical locations mentioned"""
        found_locations = set()
        text_lower = text.lower()
        
        for region in self.regions:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(region) + r'\b'
            if re.search(pattern, text_lower):
                found_locations.add(region.title())
        
        return sorted(list(found_locations))
    
    def extract_time_periods(self, text: str) -> List[str]:
        """Extract time periods (quarters, years, months)"""
        periods = set()
        
        # Quarter patterns
        quarter_patterns = [
            r'Q[1-4]\s*(?:FY)?(\d{2,4})',
            r'(?:first|second|third|fourth)\s+quarter',
            r'(?:Q1|Q2|Q3|Q4)',
        ]
        
        for pattern in quarter_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match:
                    periods.add(match)
        
        # Year patterns
        year_matches = re.findall(r'\b(20\d{2})\b', text)
        periods.update(year_matches)
        
        # Fiscal year patterns
        fy_matches = re.findall(r'FY\s*(\d{2,4}(?:-\d{2})?)', text, re.IGNORECASE)
        periods.update(fy_matches)
        
        return sorted(list(periods))
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract important business/industry terms"""
        key_terms = {
            'demand', 'supply', 'pricing', 'competition', 'expansion',
            'capacity', 'utilization', 'margin', 'cost', 'realization',
            'sustainability', 'green', 'acquisition', 'merger', 'capex',
            'debottlenecking', 'clinker', 'cement', 'ready mix', 'blended cement',
            'infrastructure', 'housing', 'monsoon', 'logistics'
        }
        
        found_terms = set()
        text_lower = text.lower()
        
        for term in key_terms:
            if term in text_lower:
                found_terms.add(term)
        
        return sorted(list(found_terms))
    
    def extract_qa_entities(self, text: str) -> Dict:
        """
        Extract entities specifically from Q&A sections
        
        Returns:
            Dictionary with analysts, questions count, topics
        """
        qa_entities = {
            'analysts': [],
            'questions_asked': 0,
            'topics_discussed': [],
        }
        
        # Extract analyst names
        analyst_pattern = r'(?:Analyst|Mr\.|Ms\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        analysts = re.findall(analyst_pattern, text)
        qa_entities['analysts'] = list(set(analysts))[:10]  # Limit to 10
        
        # Count questions
        qa_entities['questions_asked'] = text.count('?')
        
        # Extract topics from questions
        topics = self.extract_key_terms(text)
        qa_entities['topics_discussed'] = topics
        
        return qa_entities
    
    def create_entity_summary(self, text: str) -> str:
        """
        Create a human-readable summary of entities
        """
        entities = self.extract_all_entities(text)
        
        summary_parts = []
        
        if entities['companies']:
            summary_parts.append(f"Companies mentioned: {', '.join(entities['companies'])}")
        
        if entities['financial_metrics']:
            metrics_list = [f"{k}({len(v)})" for k, v in entities['financial_metrics'].items()]
            summary_parts.append(f"Financial metrics: {', '.join(metrics_list)}")
        
        if entities['locations']:
            summary_parts.append(f"Locations: {', '.join(entities['locations'][:5])}")
        
        if entities['key_terms']:
            summary_parts.append(f"Key topics: {', '.join(entities['key_terms'][:8])}")
        
        return ' | '.join(summary_parts)
