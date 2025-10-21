"""
Multi-source ingestion system for CiteRight-Multiverse
"""
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from app.rag.wikipedia_ingester import WikipediaIngester
from app.rag.stackexchange_ingester import StackExchangeIngester
from app.rag.arxiv_ingester import ArxivIngester
from app.rag.wikidata_ingester import WikidataIngester
from app.rag.utils import chunk_text
from app.deps import vectorstore
from app.config import settings

logger = logging.getLogger(__name__)

class MultiSourceIngester:
    def __init__(self):
        """Initialize multi-source ingester"""
        self.wikipedia = WikipediaIngester()
        self.stackexchange = StackExchangeIngester()
        self.arxiv = ArxivIngester()
        self.wikidata = WikidataIngester()
        
    def ingest_from_sources(self, 
                          query: str,
                          sources: List[str] = None,
                          max_per_source: int = 5) -> Dict[str, Any]:
        """Ingest content from multiple sources based on query"""
        
        if sources is None:
            sources = ['wikipedia', 'stackexchange', 'arxiv', 'wikidata']
            
        all_content = []
        source_stats = {}
        
        for source in sources:
            try:
                if source == 'wikipedia':
                    content = self.wikipedia.search_and_ingest(query, max_per_source)
                elif source == 'stackexchange':
                    content = self.stackexchange.search_questions(query, max_per_source)
                elif source == 'arxiv':
                    content = self.arxiv.search_papers(query, max_per_source)
                elif source == 'wikidata':
                    content = self.wikidata.search_entities(query, max_per_source)
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue
                    
                source_stats[source] = len(content)
                all_content.extend(content)
                
            except Exception as e:
                logger.error(f"Failed to ingest from {source}: {e}")
                source_stats[source] = 0
                
        # Process and chunk all content
        processed_chunks = self._process_content_chunks(all_content)
        
        # Add to vectorstore
        if processed_chunks:
            vs = vectorstore()
            texts = [chunk['content'] for chunk in processed_chunks]
            metas = [chunk['metadata'] for chunk in processed_chunks]
            
            vs.add_texts(texts=texts, metadatas=metas)
            vs.save_local(settings.VECTOR_INDEX_PATH)
            
        return {
            "total_chunks": len(processed_chunks),
            "source_stats": source_stats,
            "sources_used": sources
        }
    
    def ingest_specific_content(self, 
                              wikipedia_titles: List[str] = None,
                              stackexchange_questions: List[int] = None,
                              arxiv_ids: List[str] = None,
                              wikidata_ids: List[str] = None) -> Dict[str, Any]:
        """Ingest specific content by IDs/titles"""
        
        all_content = []
        source_stats = {}
        
        # Wikipedia specific articles
        if wikipedia_titles:
            try:
                for title in wikipedia_titles:
                    article = self.wikipedia.get_article_by_title(title)
                    if article:
                        all_content.append(article)
                source_stats['wikipedia'] = len([a for a in all_content if a.get('origin') == 'Wikipedia'])
            except Exception as e:
                logger.error(f"Failed to ingest Wikipedia articles: {e}")
                source_stats['wikipedia'] = 0
        
        # StackExchange specific questions
        if stackexchange_questions:
            try:
                for question_id in stackexchange_questions:
                    question = self.stackexchange.get_question_with_answers(question_id)
                    if question:
                        all_content.append(question)
                source_stats['stackexchange'] = len([a for a in all_content if a.get('origin') == 'StackExchange'])
            except Exception as e:
                logger.error(f"Failed to ingest StackExchange questions: {e}")
                source_stats['stackexchange'] = 0
        
        # arXiv specific papers
        if arxiv_ids:
            try:
                for paper_id in arxiv_ids:
                    paper = self.arxiv.get_paper_by_id(paper_id)
                    if paper:
                        all_content.append(paper)
                source_stats['arxiv'] = len([a for a in all_content if a.get('origin') == 'arXiv'])
            except Exception as e:
                logger.error(f"Failed to ingest arXiv papers: {e}")
                source_stats['arxiv'] = 0
        
        # Wikidata specific entities
        if wikidata_ids:
            try:
                for entity_id in wikidata_ids:
                    entity = self.wikidata.get_entity_by_id(entity_id)
                    if entity:
                        all_content.append(entity)
                source_stats['wikidata'] = len([a for a in all_content if a.get('origin') == 'Wikidata'])
            except Exception as e:
                logger.error(f"Failed to ingest Wikidata entities: {e}")
                source_stats['wikidata'] = 0
        
        # Process and chunk all content
        processed_chunks = self._process_content_chunks(all_content)
        
        # Add to vectorstore
        if processed_chunks:
            vs = vectorstore()
            texts = [chunk['content'] for chunk in processed_chunks]
            metas = [chunk['metadata'] for chunk in processed_chunks]
            
            vs.add_texts(texts=texts, metadatas=metas)
            vs.save_local(settings.VECTOR_INDEX_PATH)
            
        return {
            "total_chunks": len(processed_chunks),
            "source_stats": source_stats
        }
    
    def _process_content_chunks(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process content list into chunks with proper metadata"""
        processed_chunks = []
        
        for item in content_list:
            try:
                # Chunk the content
                chunks = chunk_text(item['content'])
                
                for i, chunk in enumerate(chunks):
                    # Create metadata for each chunk
                    metadata = {
                        "source": item.get('source', 'unknown'),
                        "origin": item.get('origin', 'Unknown'),
                        "license": item.get('license', 'Unknown'),
                        "url": item.get('url', ''),
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "title": item.get('title', ''),
                        "summary": item.get('summary', ''),
                        **item.get('metadata', {})
                    }
                    
                    processed_chunks.append({
                        "content": chunk,
                        "metadata": metadata
                    })
                    
            except Exception as e:
                logger.error(f"Failed to process content item: {e}")
                continue
                
        return processed_chunks
    
    def get_source_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available sources"""
        return {
            "wikipedia": {
                "description": "Wikipedia articles",
                "license": "CC BY-SA 3.0",
                "api": "wikipedia library",
                "rate_limit": "Built-in throttling"
            },
            "stackexchange": {
                "description": "StackExchange Q&A content",
                "license": "CC BY-SA 4.0", 
                "api": "StackAPI",
                "rate_limit": "API key recommended"
            },
            "arxiv": {
                "description": "arXiv research papers",
                "license": "CC BY 4.0",
                "api": "arxiv library",
                "rate_limit": "Built-in throttling"
            },
            "wikidata": {
                "description": "Wikidata structured data",
                "license": "CC0 1.0",
                "api": "Wikidata API",
                "rate_limit": "No authentication required"
            }
        }


# Convenience functions
def ingest_multiverse_content(query: str, 
                            sources: List[str] = None,
                            max_per_source: int = 5) -> Dict[str, Any]:
    """Convenience function to ingest from multiple sources"""
    ingester = MultiSourceIngester()
    return ingester.ingest_from_sources(query, sources, max_per_source)

def ingest_specific_multiverse_content(**kwargs) -> Dict[str, Any]:
    """Convenience function to ingest specific content"""
    ingester = MultiSourceIngester()
    return ingester.ingest_specific_content(**kwargs)
