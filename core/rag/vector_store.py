import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Union
import json
import logging

from app.config import settings
from core.rag.embeddings import get_embeddings, get_single_embedding

logger = logging.getLogger("vector_store")

class VectorStore:
    def __init__(self, collection_name: str):
        """
        Initialize vector store with specified collection name.
        
        Args:
            collection_name: Name of collection to use
        """
        # Create client
        self.client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"Using existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {collection_name}")
            
        self.collection_name = collection_name
    
    def add_texts(
        self, 
        texts: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of texts to add
            metadatas: Optional list of metadata for each text
            ids: Optional list of IDs for each text, will be auto-generated if not provided
            
        Returns:
            List of IDs for the added texts
        """
        if not texts:
            return []
            
        # Generate embeddings using OpenAI
        embeddings = get_embeddings(texts)
        
        # Generate IDs if not provided
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]
            
        # Add documents to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
        
    def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search with the given query.
        
        Args:
            query: Query text
            k: Number of results to return
            filter: Optional filter for the search
            
        Returns:
            List of documents with metadata and similarity scores
        """
        # Generate query embedding
        query_embedding = get_single_embedding(query)
        
        # Search the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        documents = []
        
        if not results["documents"]:
            return documents
            
        for i in range(len(results["documents"][0])):
            documents.append({
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None
            })
            
        return documents