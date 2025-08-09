import os
import glob
from typing import List, Dict, Tuple
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class DocumentLoader:
    def __init__(self, documents_dir: str = "documents/"):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.documents_dir = documents_dir
        
        # Document categorisation mapping
        self.document_categories = {
            "contact_info.md": "general",
            "faq.md": "general", 
            "faq.pdf": "general",
            "privacy_policy.md": "general",
            "return_policy.md": "general",
            "shipping_policy.md": "general", 
            "terms_of_service.md": "general",
            "warranty_terms.md": "general",
            "product_catalog.md": "product",
            "membership_benefits.md": "product",
            "troubleshooting.md": "technical"
        }
        
        # Table mapping
        self.table_mapping = {
            "general": "general_support_docs",
            "product": "product_docs", 
            "technical": "technical_docs"
        }
    
    def determine_doc_type(self, filename: str) -> str:
        """Determine which agent should handle this document"""
        return self.document_categories.get(filename, "general")
    
    def read_document(self, filepath: str) -> str:
        """Read document content from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"❌ Error reading {filepath}: {str(e)}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary if possible
            if end < len(text):
                # Look for sentence ending in the last 100 characters
                last_period = text.rfind('.', start + chunk_size - 100, end)
                last_newline = text.rfind('\n', start + chunk_size - 100, end)
                break_point = max(last_period, last_newline)
                
                if break_point > start:
                    end = break_point + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
        return chunks
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error generating embedding: {str(e)}")
            return []
    
    def process_document(self, filepath: str) -> List[Dict]:
        """Process a single document into chunks with embeddings"""
        filename = os.path.basename(filepath)
        print(f"📄 Processing {filename}...")
        
        # Read document
        content = self.read_document(filepath)
        if not content:
            return []
        
        # Determine document type
        doc_type = self.determine_doc_type(filename)
        
        # Chunk the document
        chunks = self.chunk_text(content)
        print(f"   Split into {len(chunks)} chunks")
        
        # Process each chunk
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = self.get_embedding(chunk)
            if not embedding:
                continue
            
            # Prepare chunk data
            chunk_data = {
                "content": chunk,
                "metadata": {
                    "source": filename,
                    "doc_type": doc_type,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_path": filepath
                },
                "embedding": embedding
            }
            
            processed_chunks.append((doc_type, chunk_data))
        
        print(f"   Generated {len(processed_chunks)} embedded chunks")
        return processed_chunks
    
    def load_documents(self):
        """Load all documents from the documents directory"""
        print("🚀 Starting document loading...")
        
        # Find all markdown and text files
        file_patterns = [
            os.path.join(self.documents_dir, "*.md"),
            os.path.join(self.documents_dir, "*.txt"),
            os.path.join(self.documents_dir, "*.pdf")  # You'll need a PDF reader for this
        ]
        
        all_files = []
        for pattern in file_patterns:
            all_files.extend(glob.glob(pattern))
        
        if not all_files:
            print(f"❌ No documents found in {self.documents_dir}")
            return
        
        print(f"📚 Found {len(all_files)} documents to process")
        
        # Statistics
        load_stats = {"general": 0, "product": 0, "technical": 0}
        total_chunks = 0
        
        # Process each document
        for filepath in all_files:
            processed_chunks = self.process_document(filepath)
            
            # Group chunks by document type
            chunks_by_type = {"general": [], "product": [], "technical": []}
            
            for doc_type, chunk_data in processed_chunks:
                chunks_by_type[doc_type].append(chunk_data)
            
            # Insert chunks into appropriate tables
            for doc_type, chunks in chunks_by_type.items():
                if not chunks:
                    continue
                
                table_name = self.table_mapping[doc_type]
                try:
                    result = self.supabase.table(table_name).insert(chunks).execute()
                    
                    if result.data:
                        load_stats[doc_type] += len(chunks)
                        total_chunks += len(chunks)
                        print(f"✅ Loaded {len(chunks)} chunks into {table_name}")
                    else:
                        print(f"❌ Failed to load chunks into {table_name}")
                        
                except Exception as e:
                    print(f"❌ Error inserting into {table_name}: {str(e)}")
        
        print("\n📊 Loading Summary:")
        print(f"   General Support: {load_stats['general']} chunks")
        print(f"   Product Docs: {load_stats['product']} chunks")
        print(f"   Technical Docs: {load_stats['technical']} chunks")
        print(f"   Total: {total_chunks} chunks loaded")
    
    def verify_loading(self):
        """Verify the loading worked correctly"""
        print("\n🔍 Verifying document loading...")
        
        for doc_type, table_name in self.table_mapping.items():
            try:
                result = self.supabase.table(table_name).select('*').execute()
                docs = result.data
                
                sources = set(doc['metadata'].get('source', 'unknown') for doc in docs)
                
                print(f"\n📚 {table_name}:")
                print(f"   Total chunks: {len(docs)}")
                print(f"   Source files: {len(sources)}")
                print(f"   Files: {', '.join(sorted(sources))}")
                
            except Exception as e:
                print(f"❌ Error checking {table_name}: {str(e)}")
    
    def test_search_functions(self):
        """Test that the search functions work with loaded data"""
        print("\n🧪 Testing search functions...")
        
        test_queries = {
            "general": "return policy",
            "product": "membership benefits", 
            "technical": "troubleshooting"
        }
        
        search_functions = {
            "general": "match_general_support_docs",
            "product": "match_product_docs",
            "technical": "match_technical_docs"
        }
        
        for doc_type, query in test_queries.items():
            try:
                # Get query embedding
                query_embedding = self.get_embedding(query)
                if not query_embedding:
                    continue
                
                # Test search function
                function_name = search_functions[doc_type]
                result = self.supabase.rpc(function_name, {
                    'query_embedding': query_embedding,
                    'match_count': 3
                }).execute()
                
                docs = result.data
                print(f"✅ {doc_type} search '{query}': {len(docs)} results")
                
                if docs:
                    top_result = docs[0]
                    source = top_result['metadata'].get('source', 'unknown')
                    similarity = top_result['similarity']
                    print(f"   Top result: {source} (similarity: {similarity:.3f})")
                
            except Exception as e:
                print(f"❌ Error testing {doc_type} search: {str(e)}")

if __name__ == "__main__":
    # Adjust the documents directory path as needed
    loader = DocumentLoader(documents_dir="data/")
    
    print("🚀 Starting document loading process...")
    print("This will read documents from files and load them into agent-specific tables\n")
    
    # Load documents
    loader.load_documents()
    
    # Verify results
    loader.verify_loading()
    
    # Test search functions
    loader.test_search_functions()
    
    print("\n✅ Loading complete! Your vector stores are ready for use.")