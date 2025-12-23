"""
LLM client for response generation
"""
from openai import OpenAI
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for LLM generation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_response(
        self,
        query: str,
        context_documents: List[Dict],
        system_prompt: str = None
    ) -> str:
        """
        Generate response using LLM
        
        Args:
            query: User query
            context_documents: Retrieved context documents
            system_prompt: System prompt for LLM
            
        Returns:
            Generated response
        """
        # Format context
        context = self._format_context(context_documents)
        
        # Create messages
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        user_message = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
        
        messages.append({"role": "user", "content": user_message})
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Format context documents for prompt"""
        context_parts = []
        for idx, doc in enumerate(documents, 1):
            metadata = doc.get('metadata', {})
            company = metadata.get('company_name', 'Unknown')
            date = metadata.get('date', 'Unknown')
            
            context_parts.append(
                f"[{idx}] Company: {company}, Date: {date}\n{doc['text']}\n"
            )
        
        return "\n".join(context_parts)
