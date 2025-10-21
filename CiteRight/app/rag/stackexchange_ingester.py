"""
StackExchange data ingestion module for CiteRight-Multiverse
"""
from stackapi import StackAPI
from typing import List, Dict, Any
import time
import logging

logger = logging.getLogger(__name__)

class StackExchangeIngester:
    def __init__(self, site: str = "stackoverflow"):
        """Initialize StackExchange ingester with site setting"""
        self.api = StackAPI(site)
        self.site = site
        
    def search_questions(self, query: str, max_questions: int = 10) -> List[Dict[str, Any]]:
        """Search StackExchange for questions related to query"""
        try:
            # Search for questions
            questions = self.api.fetch(
                'search/advanced',
                q=query,
                sort='relevance',
                order='desc',
                pagesize=max_questions
            )
            
            processed_questions = []
            
            for item in questions.get('items', []):
                try:
                    processed_item = self._process_question(item)
                    if processed_item:
                        processed_questions.append(processed_item)
                except Exception as e:
                    logger.warning(f"Failed to process question {item.get('question_id', 'unknown')}: {e}")
                    continue
                    
            return processed_questions
            
        except Exception as e:
            logger.error(f"StackExchange search failed: {e}")
            return []
    
    def get_question_with_answers(self, question_id: int) -> Dict[str, Any]:
        """Get a specific question with its answers"""
        try:
            # Get question
            question = self.api.fetch('questions/{ids}', ids=[question_id])
            question_item = question['items'][0] if question['items'] else None
            
            if not question_item:
                return None
                
            # Get answers
            answers = self.api.fetch(
                'questions/{ids}/answers',
                ids=[question_id],
                sort='votes',
                order='desc',
                pagesize=5
            )
            
            return self._process_question_with_answers(question_item, answers.get('items', []))
            
        except Exception as e:
            logger.error(f"Failed to get question {question_id}: {e}")
            return None
    
    def _process_question(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single StackExchange question item"""
        try:
            # Clean HTML content
            title = self._clean_html(item.get('title', ''))
            body = self._clean_html(item.get('body', ''))
            
            return {
                "title": title,
                "content": f"Question: {title}\n\nAnswer: {body}",
                "summary": title,
                "url": item.get('link', ''),
                "source": f"Question {item.get('question_id', 'unknown')}",
                "origin": "StackExchange",
                "license": "CC BY-SA 4.0",
                "metadata": {
                    "question_id": item.get('question_id'),
                    "score": item.get('score', 0),
                    "view_count": item.get('view_count', 0),
                    "answer_count": item.get('answer_count', 0),
                    "tags": item.get('tags', []),
                    "creation_date": item.get('creation_date'),
                    "last_activity_date": item.get('last_activity_date'),
                    "owner": item.get('owner', {}).get('display_name', 'Unknown')
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to process question item: {e}")
            return None
    
    def _process_question_with_answers(self, question: Dict[str, Any], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a question with its answers"""
        try:
            title = self._clean_html(question.get('title', ''))
            question_body = self._clean_html(question.get('body', ''))
            
            # Combine question and top answers
            content_parts = [f"Question: {title}\n\n{question_body}"]
            
            for answer in answers[:3]:  # Top 3 answers
                answer_body = self._clean_html(answer.get('body', ''))
                score = answer.get('score', 0)
                content_parts.append(f"Answer (Score: {score}):\n{answer_body}")
            
            content = "\n\n---\n\n".join(content_parts)
            
            return {
                "title": title,
                "content": content,
                "summary": title,
                "url": question.get('link', ''),
                "source": f"Question {question.get('question_id', 'unknown')}",
                "origin": "StackExchange",
                "license": "CC BY-SA 4.0",
                "metadata": {
                    "question_id": question.get('question_id'),
                    "score": question.get('score', 0),
                    "view_count": question.get('view_count', 0),
                    "answer_count": question.get('answer_count', 0),
                    "tags": question.get('tags', []),
                    "top_answer_scores": [ans.get('score', 0) for ans in answers[:3]],
                    "creation_date": question.get('creation_date'),
                    "last_activity_date": question.get('last_activity_date')
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to process question with answers: {e}")
            return None
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content from StackExchange"""
        if not html_content:
            return ""
            
        # Simple HTML cleaning - remove tags but keep content
        import re
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', html_content)
        # Decode HTML entities
        clean = clean.replace('&amp;', '&')
        clean = clean.replace('&lt;', '<')
        clean = clean.replace('&gt;', '>')
        clean = clean.replace('&quot;', '"')
        clean = clean.replace('&#39;', "'")
        # Clean up whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def get_trending_questions(self, max_questions: int = 10) -> List[Dict[str, Any]]:
        """Get trending questions from StackExchange"""
        try:
            questions = self.api.fetch(
                'questions',
                sort='hot',
                order='desc',
                pagesize=max_questions
            )
            
            processed_questions = []
            for item in questions.get('items', []):
                processed_item = self._process_question(item)
                if processed_item:
                    processed_questions.append(processed_item)
                    
            return processed_questions
            
        except Exception as e:
            logger.error(f"Failed to get trending questions: {e}")
            return []


def ingest_stackexchange_content(query: str, max_questions: int = 10) -> List[Dict[str, Any]]:
    """Convenience function to ingest StackExchange content"""
    ingester = StackExchangeIngester()
    return ingester.search_questions(query, max_questions)
