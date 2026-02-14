"""
📥 Document Ingestion CLI for RAG System
========================================
Command-line utility to ingest bank documents into the vector store.

Usage:
    python ingest_documents.py --dir ./bank_docs
    python ingest_documents.py --file ./bank_docs/manual/sbi_loans.pdf
    python ingest_documents.py --url "https://www.sbi.co.in/web/personal-banking/loans/education-loans"
    python ingest_documents.py --text "Custom text content" --source "manual_entry"
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from rag_engine import (
    RAGRetriever, 
    RAGConfig, 
    DocumentLoader,
    SENTENCE_TRANSFORMERS_AVAILABLE,
    CHROMADB_AVAILABLE
)


def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        missing.append("sentence-transformers")
    if not CHROMADB_AVAILABLE:
        missing.append("chromadb")
    
    if missing:
        print("❌ Missing required dependencies:")
        print(f"   pip install {' '.join(missing)}")
        return False
    return True


def ingest_directory(rag: RAGRetriever, dir_path: str, recursive: bool = True):
    """Ingest all documents from a directory."""
    print(f"\n📂 Ingesting directory: {dir_path}")
    print(f"   Recursive: {recursive}")
    
    count = rag.ingest_directory(dir_path, recursive)
    print(f"\n✅ Ingested {count} chunks from directory")
    return count


def ingest_file(rag: RAGRetriever, file_path: str):
    """Ingest a single file."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return 0
    
    print(f"\n📄 Ingesting file: {file_path}")
    
    suffix = path.suffix.lower()
    
    if suffix == ".pdf":
        count = rag.ingest_pdf(file_path)
    elif suffix in [".txt", ".md", ".markdown"]:
        doc = DocumentLoader.load_text(file_path)
        count = rag.ingest_document(doc)
    else:
        print(f"❌ Unsupported file type: {suffix}")
        return 0
    
    print(f"✅ Ingested {count} chunks from file")
    return count


def ingest_url(rag: RAGRetriever, url: str, selector: Optional[str] = None):
    """Ingest content from a URL."""
    print(f"\n🌐 Ingesting URL: {url}")
    
    try:
        count = rag.ingest_web(url, selector)
        print(f"✅ Ingested {count} chunks from URL")
        return count
    except Exception as e:
        print(f"❌ Error ingesting URL: {e}")
        return 0


def ingest_text(rag: RAGRetriever, text: str, source: str = "manual_entry"):
    """Ingest text content directly."""
    print(f"\n✏️ Ingesting text (source: {source})")
    
    count = rag.ingest_text(text, source)
    print(f"✅ Ingested {count} chunks")
    return count


def show_stats(rag: RAGRetriever):
    """Show current RAG system statistics."""
    print("\n📊 RAG System Statistics:")
    print("-" * 40)
    
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def test_query(rag: RAGRetriever, query: str):
    """Test retrieval with a query."""
    print(f"\n🔍 Testing query: {query}")
    print("-" * 40)
    
    context, citations = rag.retrieve_with_context(query, top_k=3)
    
    if context:
        print("\n📄 Retrieved Context (first 500 chars):")
        print(context[:500] + "..." if len(context) > 500 else context)
        
        print("\n📌 Citations:")
        for cite in citations:
            print(f"  {cite}")
    else:
        print("❌ No relevant results found")


def clear_index(rag: RAGRetriever):
    """Clear all indexed documents."""
    confirm = input("\n⚠️ This will delete all indexed documents. Continue? (y/N): ")
    if confirm.lower() == 'y':
        rag.clear_index()
        print("✅ Index cleared")
    else:
        print("❌ Cancelled")


def main():
    parser = argparse.ArgumentParser(
        description="Document Ingestion CLI for Loan Agent RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest_documents.py --dir ./bank_docs
  python ingest_documents.py --file ./bank_docs/sbi_education.pdf
  python ingest_documents.py --url "https://bank-website.com/loans"
  python ingest_documents.py --text "Custom content" --source "manual"
  python ingest_documents.py --query "SBI education loan interest rate"
  python ingest_documents.py --stats
  python ingest_documents.py --clear
        """
    )
    
    # Ingestion options
    parser.add_argument("--dir", "-d", help="Directory to ingest documents from")
    parser.add_argument("--file", "-f", help="Single file to ingest")
    parser.add_argument("--url", "-u", help="URL to scrape and ingest")
    parser.add_argument("--text", "-t", help="Text content to ingest")
    parser.add_argument("--source", "-s", default="manual_entry", help="Source name for text input")
    parser.add_argument("--selector", help="CSS selector for URL scraping")
    parser.add_argument("--no-recursive", action="store_true", help="Don't recursively scan directories")
    
    # Utility options
    parser.add_argument("--stats", action="store_true", help="Show RAG system statistics")
    parser.add_argument("--query", "-q", help="Test query against the index")
    parser.add_argument("--clear", action="store_true", help="Clear all indexed documents")
    
    # Config options
    parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size for splitting")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to retrieve")
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create config
    config = RAGConfig(
        chunk_size=args.chunk_size,
        top_k=args.top_k
    )
    
    # Initialize RAG system
    print("\n🔧 Initializing RAG system...")
    rag = RAGRetriever(config)
    
    # Execute commands
    if args.clear:
        clear_index(rag)
    
    if args.dir:
        ingest_directory(rag, args.dir, not args.no_recursive)
    
    if args.file:
        ingest_file(rag, args.file)
    
    if args.url:
        ingest_url(rag, args.url, args.selector)
    
    if args.text:
        ingest_text(rag, args.text, args.source)
    
    if args.query:
        test_query(rag, args.query)
    
    if args.stats:
        show_stats(rag)
    
    # If no action specified, show help
    if not any([args.dir, args.file, args.url, args.text, args.query, args.stats, args.clear]):
        parser.print_help()
        print("\n💡 Quick start:")
        print("   python ingest_documents.py --dir ./bank_docs --stats")


if __name__ == "__main__":
    main()
