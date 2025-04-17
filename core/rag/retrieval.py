from typing import List, Dict, Any
import logging

from core.rag.vector_store import VectorStore

logger = logging.getLogger("retrieval")

class DocumentRetriever:
    """
    Class for retrieving relevant documents for RAG.
    """
    def __init__(self, collection_name: str):
        """
        Initialize the document retriever.
        
        Args:
            collection_name: Name of the vector store collection to use
        """
        self.vector_store = VectorStore(collection_name)
        
    def add_document(
        self, 
        text: str, 
        metadata: Dict[str, Any],
        doc_id: str = None
    ) -> str:
        """
        Add a document to the retriever.
        
        Args:
            text: Document text
            metadata: Document metadata
            doc_id: Optional document ID
            
        Returns:
            Document ID
        """
        ids = self.vector_store.add_texts(
            texts=[text],
            metadatas=[metadata],
            ids=[doc_id] if doc_id else None
        )
        return ids[0]
        
    def retrieve(
        self, 
        query: str, 
        k: int = 3, 
        filter: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            k: Number of documents to retrieve
            filter: Optional filter for the search
            
        Returns:
            List of relevant documents
        """
        return self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter
        )