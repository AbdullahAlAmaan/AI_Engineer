"""
PDF processing module for CiteRight-Multiverse
"""
import io
from typing import List, Dict, Any
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        """Initialize PDF processor"""
        pass
        
    def process_pdf(self, pdf_content: bytes, filename: str = "uploaded.pdf") -> List[Dict[str, Any]]:
        """Process uploaded PDF content"""
        try:
            # Create PDF reader from bytes
            pdf_stream = io.BytesIO(pdf_content)
            reader = PdfReader(pdf_stream)
            
            # Extract text from all pages
            full_text = ""
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        full_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            if not full_text.strip():
                logger.warning("No text could be extracted from PDF")
                return []
            
            # Get PDF metadata
            metadata = self._extract_metadata(reader, filename)
            
            # Create content structure
            content = {
                "title": metadata.get("title", filename),
                "content": full_text.strip(),
                "summary": f"PDF Document: {filename}",
                "url": "",
                "source": filename,
                "origin": "User Upload",
                "license": "User Provided",
                "metadata": metadata
            }
            
            return [content]
            
        except Exception as e:
            logger.error(f"Failed to process PDF {filename}: {e}")
            return []
    
    def _extract_metadata(self, reader: PdfReader, filename: str) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        metadata = {
            "filename": filename,
            "page_count": len(reader.pages),
            "file_type": "PDF"
        }
        
        try:
            if reader.metadata:
                pdf_metadata = reader.metadata
                metadata.update({
                    "title": pdf_metadata.get("/Title", ""),
                    "author": pdf_metadata.get("/Author", ""),
                    "subject": pdf_metadata.get("/Subject", ""),
                    "creator": pdf_metadata.get("/Creator", ""),
                    "producer": pdf_metadata.get("/Producer", ""),
                    "creation_date": str(pdf_metadata.get("/CreationDate", "")),
                    "modification_date": str(pdf_metadata.get("/ModDate", ""))
                })
        except Exception as e:
            logger.warning(f"Failed to extract PDF metadata: {e}")
        
        return metadata
    
    def validate_pdf(self, pdf_content: bytes) -> bool:
        """Validate if the uploaded file is a valid PDF"""
        try:
            pdf_stream = io.BytesIO(pdf_content)
            reader = PdfReader(pdf_stream)
            # Try to access page count to validate
            _ = len(reader.pages)
            return True
        except Exception:
            return False


def process_uploaded_pdf(pdf_content: bytes, filename: str = "uploaded.pdf") -> List[Dict[str, Any]]:
    """Convenience function to process uploaded PDF"""
    processor = PDFProcessor()
    return processor.process_pdf(pdf_content, filename)
