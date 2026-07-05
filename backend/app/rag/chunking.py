import hashlib
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime

class DocumentChunker:
    def __init__(self, chunk_size: int = 650, chunk_overlap: int = 100):
        # We use RecursiveCharacterTextSplitter as it prefers semantic/paragraph-aware splitting
        # by trying to split on double newline, then newline, then space.
        # Although the prompt asked for "tokens", a recursive character splitter with a good
        # chunk_size acts similarly and is standard in LangChain. 
        # Alternatively, we could use TokenTextSplitter, but it splits mid-word/sentence more often.
        # For ~650 tokens, since 1 token is roughly 4 chars, that's about 2600 chars.
        # Let's adjust chunk_size to character equivalent for standard Recursive splitter, 
        # or just use it assuming chunk_size is in chars, let's make it 2500 chars.
        
        self.char_chunk_size = chunk_size * 4
        self.char_chunk_overlap = chunk_overlap * 4
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.char_chunk_size,
            chunk_overlap=self.char_chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def generate_content_hash(self, content: str, tenant_id: str) -> str:
        """Generates a unique hash for a chunk to prevent duplication."""
        hash_input = f"{tenant_id}:{content}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()

    def process_document(self, content: str, tenant_id: str, source_doc_id: str) -> List[Dict[str, Any]]:
        """
        Splits a document into chunks and attaches the required metadata.
        """
        chunks = self.splitter.split_text(content)
        processed_chunks = []
        last_updated = datetime.utcnow().isoformat()

        for idx, chunk_text in enumerate(chunks):
            content_hash = self.generate_content_hash(chunk_text, tenant_id)
            
            chunk_metadata = {
                "tenant_id": tenant_id,
                "source_doc": source_doc_id,
                "chunk_index": idx,
                "last_updated": last_updated,
                "content_hash": content_hash
            }
            
            processed_chunks.append({
                "page_content": chunk_text,
                "metadata": chunk_metadata
            })
            
        return processed_chunks

# Singleton instance
chunker = DocumentChunker()
