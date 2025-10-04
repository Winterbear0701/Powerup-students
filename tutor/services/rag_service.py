"""
RAG Service - Retrieval Augmented Generation
Handles ChromaDB queries for NCERT content retrieval
"""
import chromadb
from django.conf import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Service for retrieving context from NCERT textbooks using ChromaDB"""
    
    def __init__(self):
        self.db_path = settings.CHROMA_DB_PATH
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collection"""
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"✅ Connected to ChromaDB. Collection has {self.collection.count()} chunks.")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    def retrieve_context(
        self,
        query: str,
        grade: int,
        n_results: int = 3,
        subject: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Retrieve relevant context from ChromaDB
        
        Args:
            query: User's question
            grade: Student's grade level (5-10)
            n_results: Number of chunks to retrieve
            subject: Optional subject filter (math, science, etc.)
        
        Returns:
            Dict with documents, metadatas, and relevance scores
        """
        try:
            # Build filter for grade level if metadata supports it
            where_filter = None
            if hasattr(self.collection, 'metadata') and subject:
                where_filter = {"subject": subject}
            
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # Extract and format results
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            # Calculate relevance scores (lower distance = higher relevance)
            relevance_scores = [1 / (1 + dist) for dist in distances] if distances else []
            
            context_data = {
                'documents': documents,
                'metadatas': metadatas,
                'relevance_scores': relevance_scores,
                'found': len(documents) > 0,
                'count': len(documents)
            }
            
            logger.info(f"Retrieved {len(documents)} chunks for query: {query[:50]}...")
            return context_data
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {
                'documents': [],
                'metadatas': [],
                'relevance_scores': [],
                'found': False,
                'count': 0,
                'error': str(e)
            }
    
    def format_context_for_prompt(self, context_data: Dict) -> str:
        """
        Format retrieved documents into a context string for LLM
        
        Args:
            context_data: Output from retrieve_context()
        
        Returns:
            Formatted context string
        """
        if not context_data['found']:
            return ""
        
        documents = context_data['documents']
        metadatas = context_data['metadatas']
        
        formatted_chunks = []
        for i, doc in enumerate(documents):
            metadata_info = ""
            if metadatas and i < len(metadatas):
                meta = metadatas[i]
                if meta:
                    metadata_info = f"[Source: {meta.get('source', 'NCERT')}]"
            
            formatted_chunks.append(f"{metadata_info}\n{doc}")
        
        return "\n\n---\n\n".join(formatted_chunks)
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the ChromaDB collection"""
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection_name,
                'db_path': self.db_path
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'error': str(e)}


# Singleton instance
_rag_service_instance = None


def get_rag_service() -> RAGService:
    """Get or create RAG service singleton"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
