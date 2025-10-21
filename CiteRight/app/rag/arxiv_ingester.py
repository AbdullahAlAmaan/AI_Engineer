"""
arXiv data ingestion module for CiteRight-Multiverse
"""
import arxiv
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ArxivIngester:
    def __init__(self):
        """Initialize arXiv ingester"""
        pass
        
    def search_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search arXiv for papers related to query"""
        try:
            # Create search query
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending
            )
            
            papers = []
            for result in search.results():
                try:
                    paper = self._process_paper(result)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Failed to process paper {result.entry_id}: {e}")
                    continue
                    
            return papers
            
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
            return []
    
    def get_paper_by_id(self, paper_id: str) -> Dict[str, Any]:
        """Get a specific arXiv paper by ID"""
        try:
            # Remove version suffix if present
            clean_id = paper_id.split('v')[0]
            
            search = arxiv.Search(
                id_list=[clean_id],
                max_results=1
            )
            
            for result in search.results():
                return self._process_paper(result)
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to get paper {paper_id}: {e}")
            return None
    
    def get_recent_papers(self, category: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent papers from arXiv"""
        try:
            query = f"cat:{category}" if category else ""
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            papers = []
            for result in search.results():
                try:
                    paper = self._process_paper(result)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Failed to process paper {result.entry_id}: {e}")
                    continue
                    
            return papers
            
        except Exception as e:
            logger.error(f"Failed to get recent papers: {e}")
            return []
    
    def _process_paper(self, result: arxiv.Result) -> Dict[str, Any]:
        """Process a single arXiv paper result"""
        try:
            # Clean abstract
            abstract = result.summary.replace('\n', ' ').strip()
            
            # Format authors
            authors = [str(author) for author in result.authors]
            author_list = ", ".join(authors[:5])  # Limit to first 5 authors
            if len(authors) > 5:
                author_list += f" et al. ({len(authors)} total)"
            
            # Format categories
            categories = [cat for cat in result.categories]
            
            # Create content combining title, abstract, and key info
            content_parts = [
                f"Title: {result.title}",
                f"Authors: {author_list}",
                f"Abstract: {abstract}"
            ]
            
            if result.comment:
                content_parts.append(f"Comments: {result.comment}")
                
            content = "\n\n".join(content_parts)
            
            return {
                "title": result.title,
                "content": content,
                "summary": f"{result.title} - {abstract[:200]}...",
                "url": result.entry_id,
                "source": f"arXiv:{result.entry_id.split('/')[-1]}",
                "origin": "arXiv",
                "license": "CC BY 4.0",
                "metadata": {
                    "arxiv_id": result.entry_id.split('/')[-1],
                    "authors": authors,
                    "categories": categories,
                    "published": result.published.isoformat() if result.published else None,
                    "updated": result.updated.isoformat() if result.updated else None,
                    "pdf_url": result.pdf_url,
                    "comment": result.comment,
                    "journal_ref": result.journal_ref,
                    "doi": result.doi
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to process paper result: {e}")
            return None
    
    def search_by_category(self, category: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search papers by arXiv category"""
        try:
            search = arxiv.Search(
                query=f"cat:{category}",
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending
            )
            
            papers = []
            for result in search.results():
                try:
                    paper = self._process_paper(result)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Failed to process paper {result.entry_id}: {e}")
                    continue
                    
            return papers
            
        except Exception as e:
            logger.error(f"Failed to search by category {category}: {e}")
            return []


def ingest_arxiv_content(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Convenience function to ingest arXiv content"""
    ingester = ArxivIngester()
    return ingester.search_papers(query, max_results)
