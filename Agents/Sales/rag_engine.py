"""
🔍 RAG Engine for Loan Sales Agent
===================================
Retrieval-Augmented Generation system for providing accurate,
citation-backed bank policy information.

Components:
- DocumentLoader: Load PDFs, web pages, text files
- TextChunker: Split documents into retrievable chunks
- EmbeddingEngine: Generate embeddings using SentenceTransformers (local)
- VectorStore: ChromaDB wrapper for storage/retrieval
- RAGRetriever: Main class integrating all components
"""

import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

# Third-party imports (will need to be installed)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ sentence-transformers not installed. Run: pip install sentence-transformers")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️ chromadb not installed. Run: pip install chromadb")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️ PyMuPDF not installed. Run: pip install pymupdf")

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    print("⚠️ requests/beautifulsoup4 not installed. Run: pip install requests beautifulsoup4")


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class RAGConfig:
    """Configuration for RAG system."""
    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"  # Good balance of speed/quality
    
    # Chunking settings
    chunk_size: int = 500  # Characters per chunk
    chunk_overlap: int = 50  # Overlap between chunks
    
    # Retrieval settings
    top_k: int = 5  # Number of chunks to retrieve
    similarity_threshold: float = 0.3  # Minimum similarity score
    
    # Storage paths
    chroma_persist_dir: str = "./chroma_db"
    collection_name: str = "bank_policies"
    
    # Document sources directory
    docs_dir: str = "./bank_docs"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Document:
    """Represents a source document."""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    doc_type: str = "text"  # pdf, web, text, markdown
    
    def __post_init__(self):
        if not self.metadata.get("source"):
            self.metadata["source"] = self.source
        if not self.metadata.get("doc_type"):
            self.metadata["doc_type"] = self.doc_type


@dataclass
class Chunk:
    """Represents a chunk of a document."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str = ""
    embedding: Optional[List[float]] = None
    
    def __post_init__(self):
        if not self.chunk_id:
            # Generate unique ID based on content hash
            self.chunk_id = hashlib.md5(self.content.encode()).hexdigest()[:12]


@dataclass
class RetrievalResult:
    """Result from retrieval with citation info."""
    content: str
    source: str
    bank_name: Optional[str]
    loan_type: Optional[str]
    similarity_score: float
    metadata: Dict[str, Any]
    
    def get_citation(self) -> str:
        """Format citation string."""
        parts = []
        if self.bank_name:
            parts.append(self.bank_name)
        if self.loan_type:
            parts.append(f"{self.loan_type} Loan")
        if self.source:
            parts.append(f"Source: {self.source}")
        return " | ".join(parts) if parts else "Unknown Source"


# ============================================================================
# DOCUMENT LOADER
# ============================================================================

class DocumentLoader:
    """Load documents from various sources."""
    
    @staticmethod
    def load_pdf(file_path: str) -> Document:
        """Load text content from PDF file."""
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")
        
        text_content = []
        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                if text.strip():
                    text_content.append(f"[Page {page_num}]\n{text}")
        
        return Document(
            content="\n\n".join(text_content),
            source=path.name,
            doc_type="pdf",
            metadata={
                "file_path": str(path.absolute()),
                "file_name": path.name,
                "page_count": len(text_content),
                "loaded_at": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def load_text(file_path: str) -> Document:
        """Load text/markdown file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        doc_type = "markdown" if path.suffix.lower() in [".md", ".markdown"] else "text"
        
        return Document(
            content=content,
            source=path.name,
            doc_type=doc_type,
            metadata={
                "file_path": str(path.absolute()),
                "file_name": path.name,
                "loaded_at": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def load_web(url: str, selector: Optional[str] = None) -> Document:
        """Scrape content from web page."""
        if not WEB_SCRAPING_AVAILABLE:
            raise ImportError("requests/beautifulsoup4 not installed")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Get text from specific selector or main content
        if selector:
            target = soup.select_one(selector)
            text = target.get_text(separator="\n", strip=True) if target else ""
        else:
            # Try common content selectors
            main_content = (
                soup.select_one("main") or 
                soup.select_one("article") or 
                soup.select_one(".content") or
                soup.select_one("#content") or
                soup.body
            )
            text = main_content.get_text(separator="\n", strip=True) if main_content else ""
        
        # Clean up text
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return Document(
            content=text,
            source=url,
            doc_type="web",
            metadata={
                "url": url,
                "title": soup.title.string if soup.title else "",
                "scraped_at": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def load_from_string(content: str, source: str = "manual_input", 
                         metadata: Dict[str, Any] = None) -> Document:
        """Create document from string content."""
        return Document(
            content=content,
            source=source,
            doc_type="text",
            metadata=metadata or {"created_at": datetime.now().isoformat()}
        )
    
    @classmethod
    def load_directory(cls, dir_path: str, recursive: bool = True) -> List[Document]:
        """Load all supported documents from directory."""
        docs = []
        path = Path(dir_path)
        
        if not path.exists():
            print(f"⚠️ Directory not found: {dir_path}")
            return docs
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in path.glob(pattern):
            if file_path.is_file():
                try:
                    if file_path.suffix.lower() == ".pdf":
                        docs.append(cls.load_pdf(str(file_path)))
                    elif file_path.suffix.lower() in [".txt", ".md", ".markdown"]:
                        docs.append(cls.load_text(str(file_path)))
                except Exception as e:
                    print(f"⚠️ Error loading {file_path}: {e}")
        
        print(f"✅ Loaded {len(docs)} documents from {dir_path}")
        return docs


# ============================================================================
# TEXT CHUNKER
# ============================================================================

class TextChunker:
    """Split documents into retrievable chunks."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(self, doc: Document) -> List[Chunk]:
        """Split document into chunks with metadata."""
        chunks = []
        text = doc.content
        
        # Split by paragraphs first, then by size
        paragraphs = self._split_into_paragraphs(text)
        
        current_chunk = ""
        chunk_idx = 0
        
        for para in paragraphs:
            # If paragraph itself is too long, split it
            if len(para) > self.chunk_size:
                # Save current chunk if exists
                if current_chunk.strip():
                    chunks.append(self._create_chunk(current_chunk, doc, chunk_idx))
                    chunk_idx += 1
                    current_chunk = ""
                
                # Split long paragraph
                para_chunks = self._split_long_text(para)
                for pc in para_chunks:
                    chunks.append(self._create_chunk(pc, doc, chunk_idx))
                    chunk_idx += 1
            
            # If adding paragraph exceeds chunk size
            elif len(current_chunk) + len(para) > self.chunk_size:
                if current_chunk.strip():
                    chunks.append(self._create_chunk(current_chunk, doc, chunk_idx))
                    chunk_idx += 1
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else ""
                current_chunk = overlap_text + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk(current_chunk, doc, chunk_idx))
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        # Split by double newlines or markdown headers
        paragraphs = re.split(r'\n\s*\n|(?=^#{1,6}\s)', text, flags=re.MULTILINE)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_long_text(self, text: str) -> List[str]:
        """Split long text by sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current = ""
        
        for sentence in sentences:
            if len(current) + len(sentence) > self.chunk_size:
                if current:
                    chunks.append(current.strip())
                current = sentence
            else:
                current += " " + sentence if current else sentence
        
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    def _create_chunk(self, content: str, doc: Document, idx: int) -> Chunk:
        """Create a chunk with inherited metadata."""
        metadata = doc.metadata.copy()
        metadata["chunk_index"] = idx
        metadata["source"] = doc.source
        metadata["doc_type"] = doc.doc_type
        
        # Try to extract bank name from content
        bank_name = self._extract_bank_name(content)
        if bank_name:
            metadata["bank_name"] = bank_name
        
        # Try to extract loan type
        loan_type = self._extract_loan_type(content)
        if loan_type:
            metadata["loan_type"] = loan_type
        
        return Chunk(content=content.strip(), metadata=metadata)
    
    def _extract_bank_name(self, text: str) -> Optional[str]:
        """Extract bank name from text."""
        banks = [
            "SBI", "State Bank of India",
            "HDFC", "HDFC Bank",
            "ICICI", "ICICI Bank",
            "Axis", "Axis Bank",
            "PNB", "Punjab National Bank",
            "Bank of Baroda", "BOB",
            "Canara Bank",
            "Union Bank",
            "IDBI",
            "Kotak", "Kotak Mahindra",
            "Yes Bank",
            "IndusInd",
            "Federal Bank",
            "IDFC First",
            "Bajaj Finserv",
            "Tata Capital",
            "Aditya Birla",
            "Credila",
            "Avanse",
            "InCred"
        ]
        
        text_lower = text.lower()
        for bank in banks:
            if bank.lower() in text_lower:
                return bank
        return None
    
    def _extract_loan_type(self, text: str) -> Optional[str]:
        """Extract loan type from text."""
        loan_types = {
            "education": ["education loan", "student loan", "study loan"],
            "home": ["home loan", "housing loan", "mortgage"],
            "personal": ["personal loan"],
            "vehicle": ["car loan", "vehicle loan", "auto loan", "bike loan"],
            "business": ["business loan", "msme loan", "mudra loan"],
            "gold": ["gold loan"]
        }
        
        text_lower = text.lower()
        for loan_type, keywords in loan_types.items():
            if any(kw in text_lower for kw in keywords):
                return loan_type
        return None


# ============================================================================
# EMBEDDING ENGINE
# ============================================================================

class EmbeddingEngine:
    """Generate embeddings using SentenceTransformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not installed")
        
        print(f"🔄 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print(f"✅ Embedding model loaded!")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(
            texts, 
            batch_size=batch_size, 
            show_progress_bar=len(texts) > 10,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    def embed_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Add embeddings to chunks."""
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embed_texts(texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
        
        return chunks


# ============================================================================
# VECTOR STORE (ChromaDB)
# ============================================================================

class VectorStore:
    """ChromaDB wrapper for vector storage and retrieval."""
    
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "bank_policies"):
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb not installed")
        
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        
        # Create persist directory
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Bank loan policies and information"}
        )
        
        print(f"✅ Vector store initialized: {collection_name} ({self.collection.count()} documents)")
    
    def add_chunks(self, chunks: List[Chunk]) -> int:
        """Add chunks to the vector store."""
        if not chunks:
            return 0
        
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            if chunk.embedding is None:
                raise ValueError(f"Chunk {chunk.chunk_id} has no embedding")
            
            ids.append(chunk.chunk_id)
            embeddings.append(chunk.embedding)
            documents.append(chunk.content)
            
            # Clean metadata for ChromaDB (no nested objects)
            clean_metadata = {
                k: str(v) if not isinstance(v, (str, int, float, bool)) else v
                for k, v in chunk.metadata.items()
            }
            metadatas.append(clean_metadata)
        
        # Add to collection (upsert to handle duplicates)
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"✅ Added {len(chunks)} chunks to vector store")
        return len(chunks)
    
    def search(self, query_embedding: List[float], top_k: int = 5, 
               filter_dict: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Search for similar chunks."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # Convert distance to similarity score (ChromaDB uses L2 distance)
                distance = results["distances"][0][i] if results["distances"] else 0
                similarity = 1 / (1 + distance)  # Convert distance to similarity
                
                formatted.append({
                    "id": doc_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "similarity_score": similarity
                })
        
        return formatted
    
    def delete_all(self) -> None:
        """Delete all documents from collection."""
        # Get all IDs and delete
        all_docs = self.collection.get()
        if all_docs["ids"]:
            self.collection.delete(ids=all_docs["ids"])
        print(f"🗑️ Deleted all documents from {self.collection_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            "collection_name": self.collection_name,
            "document_count": self.collection.count(),
            "persist_dir": self.persist_dir
        }


# ============================================================================
# RAG RETRIEVER (Main Class)
# ============================================================================

class RAGRetriever:
    """
    Main RAG system integrating all components.
    
    Usage:
        rag = RAGRetriever()
        rag.ingest_directory("./bank_docs")
        results = rag.retrieve("What is SBI education loan interest rate?")
    """
    
    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()
        
        # Initialize components
        self.embedding_engine = EmbeddingEngine(self.config.embedding_model)
        self.chunker = TextChunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )
        self.vector_store = VectorStore(
            persist_dir=self.config.chroma_persist_dir,
            collection_name=self.config.collection_name
        )
        
        print("✅ RAG Retriever initialized!")
    
    # -------------------------------------------------------------------------
    # Ingestion Methods
    # -------------------------------------------------------------------------
    
    def ingest_document(self, doc: Document) -> int:
        """Ingest a single document."""
        # Chunk the document
        chunks = self.chunker.chunk_document(doc)
        
        # Generate embeddings
        chunks = self.embedding_engine.embed_chunks(chunks)
        
        # Store in vector database
        return self.vector_store.add_chunks(chunks)
    
    def ingest_text(self, content: str, source: str = "manual", 
                    metadata: Dict[str, Any] = None) -> int:
        """Ingest text content directly."""
        doc = DocumentLoader.load_from_string(content, source, metadata)
        return self.ingest_document(doc)
    
    def ingest_pdf(self, file_path: str) -> int:
        """Ingest a PDF file."""
        doc = DocumentLoader.load_pdf(file_path)
        return self.ingest_document(doc)
    
    def ingest_web(self, url: str, selector: Optional[str] = None) -> int:
        """Ingest content from a web page."""
        doc = DocumentLoader.load_web(url, selector)
        return self.ingest_document(doc)
    
    def ingest_directory(self, dir_path: str = None, recursive: bool = True) -> int:
        """Ingest all documents from a directory."""
        dir_path = dir_path or self.config.docs_dir
        docs = DocumentLoader.load_directory(dir_path, recursive)
        
        total_chunks = 0
        for doc in docs:
            total_chunks += self.ingest_document(doc)
        
        print(f"✅ Ingested {len(docs)} documents ({total_chunks} chunks total)")
        return total_chunks
    
    # -------------------------------------------------------------------------
    # Retrieval Methods
    # -------------------------------------------------------------------------
    
    def retrieve(self, query: str, top_k: int = None, 
                 filters: Optional[Dict[str, str]] = None) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Search query
            top_k: Number of results (default from config)
            filters: Optional metadata filters (e.g., {"bank_name": "SBI"})
            
        Returns:
            List of RetrievalResult with content and citations
        """
        top_k = top_k or self.config.top_k
        
        # Generate query embedding
        query_embedding = self.embedding_engine.embed_text(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k, filters)
        
        # Convert to RetrievalResults
        retrieval_results = []
        for result in results:
            if result["similarity_score"] >= self.config.similarity_threshold:
                metadata = result["metadata"]
                retrieval_results.append(RetrievalResult(
                    content=result["content"],
                    source=metadata.get("source", "Unknown"),
                    bank_name=metadata.get("bank_name"),
                    loan_type=metadata.get("loan_type"),
                    similarity_score=result["similarity_score"],
                    metadata=metadata
                ))
        
        return retrieval_results
    
    def retrieve_with_context(self, query: str, top_k: int = None) -> Tuple[str, List[str]]:
        """
        Retrieve and format context with citations.
        
        Returns:
            Tuple of (formatted_context, list_of_citations)
        """
        results = self.retrieve(query, top_k)
        
        if not results:
            return "", []
        
        context_parts = []
        citations = []
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{i}] {result.content}")
            citations.append(f"[{i}] {result.get_citation()}")
        
        context = "\n\n".join(context_parts)
        return context, citations
    
    def get_bank_info(self, bank_name: str, loan_type: Optional[str] = None) -> List[RetrievalResult]:
        """Get information about a specific bank."""
        filters = {"bank_name": bank_name}
        if loan_type:
            filters["loan_type"] = loan_type
        
        query = f"{bank_name} {loan_type or ''} loan details interest rate eligibility"
        return self.retrieve(query, filters=filters)
    
    def compare_banks(self, bank_names: List[str], loan_type: str) -> Dict[str, List[RetrievalResult]]:
        """Compare multiple banks for a loan type."""
        comparison = {}
        for bank in bank_names:
            comparison[bank] = self.get_bank_info(bank, loan_type)
        return comparison
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        return {
            "embedding_model": self.config.embedding_model,
            "chunk_size": self.config.chunk_size,
            "top_k": self.config.top_k,
            **self.vector_store.get_stats()
        }
    
    def clear_index(self) -> None:
        """Clear all indexed documents."""
        self.vector_store.delete_all()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_rag_retriever(config: Optional[RAGConfig] = None) -> RAGRetriever:
    """Factory function to create RAG retriever."""
    return RAGRetriever(config)


def quick_ingest(content: str, source: str = "quick_add") -> RAGRetriever:
    """Quick way to ingest content and return retriever."""
    rag = RAGRetriever()
    rag.ingest_text(content, source)
    return rag


# ============================================================================
# CLI / DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("RAG ENGINE - DEMO")
    print("=" * 60)
    
    # Check dependencies
    deps = {
        "sentence-transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
        "chromadb": CHROMADB_AVAILABLE,
        "PyMuPDF": PYMUPDF_AVAILABLE,
        "requests/bs4": WEB_SCRAPING_AVAILABLE
    }
    
    print("\n📦 Dependencies:")
    for dep, available in deps.items():
        status = "✅" if available else "❌"
        print(f"  {status} {dep}")
    
    if not (SENTENCE_TRANSFORMERS_AVAILABLE and CHROMADB_AVAILABLE):
        print("\n⚠️ Core dependencies missing. Install with:")
        print("  pip install sentence-transformers chromadb")
        exit(1)
    
    # Demo with sample content
    print("\n🔧 Initializing RAG system...")
    rag = RAGRetriever()
    
    # Sample bank data for demo
    sample_data = """
    # SBI Education Loan
    
    State Bank of India offers education loans for studies in India and abroad.
    
    ## Key Features
    - Loan Amount: Up to ₹1.5 crore for abroad, ₹50 lakh for India
    - Interest Rate: Floating rate linked to RLLR (currently around 8.5% - 10.5%)
    - Tenure: Up to 15 years after moratorium
    - Moratorium: Course period + 6-12 months
    - Collateral: Required for loans above ₹7.5 lakh
    
    ## Eligibility
    - Indian citizen
    - Secured admission in recognized institution
    - Co-applicant (parent/guardian) required
    
    ## Processing Fee
    - No processing fee for loans up to ₹7.5 lakh
    - 0.5% for higher amounts
    
    ---
    
    # HDFC Credila Education Loan
    
    HDFC Credila is India's largest education loan NBFC.
    
    ## Key Features
    - Loan Amount: Up to ₹1 crore
    - Interest Rate: 9.5% - 13% (depending on profile)
    - Tenure: Up to 12 years
    - Moratorium: Course period + 6 months
    - Faster processing (7-10 days)
    
    ## Eligibility
    - Admission to recognized course abroad
    - Co-applicant required
    - Good academic record preferred
    """
    
    print("\n📥 Ingesting sample data...")
    rag.ingest_text(sample_data, "sample_bank_data.md", {"type": "demo"})
    
    print("\n🔍 Testing retrieval...")
    
    test_queries = [
        "What is SBI education loan interest rate?",
        "Compare SBI and HDFC education loan",
        "What is the maximum loan amount for abroad studies?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        context, citations = rag.retrieve_with_context(query, top_k=2)
        
        print(f"\n📄 Retrieved Context:\n{context[:500]}...")
        print(f"\n📌 Citations:")
        for cite in citations:
            print(f"  {cite}")
        print("-" * 40)
    
    # Show stats
    print("\n📊 RAG Stats:")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
