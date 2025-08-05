import os
import uuid
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from qdrant_client import QdrantClient
from qdrant_client.http import models
import pdfplumber
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class PDFProcessorSimple:
    def __init__(self, qdrant_url: str = "http://localhost:6333", collection_name: str = "documents"):
        self.qdrant_url = qdrant_url
        self.collection_name = os.getenv("VECTOR_NAME")
        self.model_name = "BAAI/bge-small-en-v1.5"
        
        print(f"Loading model: {self.model_name}")
        self.sentence_transformer = SentenceTransformer(self.model_name)
        print("✅ Model loaded")
        
        print("Connecting to Qdrant...")
        self.qdrant_client = QdrantClient(url=qdrant_url)
        print("✅ Qdrant connected")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self._create_collection_if_not_exists()
    
    def _create_collection_if_not_exists(self):
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                sample_embedding = self.sentence_transformer.encode("test")
                vector_size = len(sample_embedding)
                
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                print(f"✅ Created collection: {self.collection_name} with {vector_size}D vectors")
            else:
                print(f"✅ Collection {self.collection_name} already exists")
        except Exception as e:
            print(f"❌ Error creating collection: {str(e)}")

    def process_pdf_file(self, pdf_path: str, user_id: str, document_category: str, document_id: str) -> List[str]:
        """Process PDF file from path"""
        try:
            print(f"Processing PDF: {pdf_path}")
            
            # Extract content
            chunks, metadata_list = self._extract_pdf_content(
                pdf_path, os.path.basename(pdf_path), document_id, document_category, user_id
            )
            
            if not chunks:
                print("❌ No chunks extracted")
                return []
            
            print(f"✅ Extracted {len(chunks)} chunks")
            
            # Generate embeddings
            print("Generating embeddings...")
            embeddings = self.sentence_transformer.encode(chunks)
            print("✅ Embeddings generated")
            
            # Prepare points for Qdrant
            chunk_ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
            points = []
            
            for i, (chunk, metadata, embedding) in enumerate(zip(chunks, metadata_list, embeddings)):
                metadata["page_content"] = chunk
                points.append(models.PointStruct(
                    id=chunk_ids[i],
                    vector=embedding.tolist(),
                    payload=metadata
                ))
            
            # Upload to Qdrant
            print("Uploading to Qdrant...")
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print("✅ Uploaded to Qdrant")
            
            return chunk_ids
            
        except Exception as e:
            print(f"❌ Error processing PDF: {str(e)}")
            raise
    
    def _extract_pdf_content(self, file_path: str, document_name: str, 
                           document_id: str, document_category: str, user_id: str) -> tuple:
        chunks = []
        metadata_list = []
        
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            print(f"✅ Loaded {len(pages)} pages")
            
            for i, page in enumerate(pages):
                page_chunks = self.text_splitter.split_text(page.page_content)
                chunks.extend(page_chunks)
                
                for j, chunk in enumerate(page_chunks):
                    metadata_list.append({
                        "document_name": document_name,
                        "document_id": document_id,
                        "document_category": document_category,
                        "user_id": user_id,
                        "page_number": i + 1,
                        "chunk_index": j,
                        "total_chunks": len(page_chunks),
                        "embedding_model": self.model_name
                    })
        
        except Exception as e:
            print(f"❌ Error extracting content: {str(e)}")
            raise
        
        return chunks, metadata_list
    
    def search_documents(self, query: str, user_id: str = None, k: int = 5) -> List[dict]:
        try:
            query_embedding = self.sentence_transformer.encode(query).tolist()
            
            search_filter = None
            # if user_id:
            #     search_filter = models.Filter(
            #         must=[
            #             models.FieldCondition(
            #                 key="user_id",
            #                 match=models.MatchValue(value=user_id)
            #             )
            #         ]
            #     )
            print(f"Searching for query: {query} in collection: {self.collection_name}")
            print(f"Query embedding: {query_embedding}")
            print(f"Search filter: {search_filter}")
            k = 10
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=k,
                with_payload=True
            )
            print(f"✅ Found {len(search_results)} results")
            
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "content": result.payload.get("page_content", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "page_content"},
                    "score": result.score,
                    "id": result.id
                })
            print(f"✅ Formatted {len(formatted_results)} results")
        
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching: {str(e)}")
            return []

# Test function
def test_processing():
    processor = PDFProcessorSimple()
    
    # Test with your PDF
    pdf_path = "uploads/2025080.pdf"
    
    if os.path.exists(pdf_path):
        print("🚀 Starting test...")
        chunk_ids = processor.process_pdf_file(pdf_path, "user123", "research", "doc456")
        print(f"✅ Processed {len(chunk_ids)} chunks")
        
        # Test search
        results = processor.search_documents("ball tracking", user_id="user123", k=3)
        print(f"�� Found {len(results)} search results")
        
        for i, result in enumerate(results):
            print(f"Result {i+1}: {result['content'][:100]}...")
    else:
        print(f"❌ File not found: {pdf_path}")

if __name__ == "__main__":
    test_processing() 