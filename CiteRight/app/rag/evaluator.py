"""
Post-generation evaluation and auditing layer for CiteRight-Multiverse
"""
import requests
import json
import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)

EVALUATOR_PROMPT = """You are CiteRight-Evaluator, a post-generation reasoning and auditing layer for CiteRight-Multiverse. You receive the model's raw answer, the retrieved chunks (with metadata), and must verify, fuse, and label each statement.

### Your Objectives
1. **Evaluate grounding:** For each factual claim, confirm whether it is explicitly supported by at least one retrieved chunk.
2. **Compute metrics:**
   - Precision@k: proportion of top-k retrieved chunks relevant to the query.
   - Citation accuracy: fraction of statements correctly attributed.
   - Faithfulness score: 0–1 scale showing how closely the output matches retrieved content (use entailment reasoning, not paraphrase similarity).
3. **Context fusion:** Merge complementary facts across sources.
   - Align identical entities (e.g., same Wikidata ID) across Wikipedia / arXiv / StackExchange.
   - Synthesize a unified explanation, marking cross-source links explicitly.
4. **Metadata-aware summarization:** Adjust tone automatically.
   - If most retrieved chunks come from arXiv → scholarly tone.
   - If mostly StackExchange → practical explanatory tone.
   - If mixed → balanced neutral style.
5. **Transparency trace:**
   - For each sentence, output the IDs or short hashes of the supporting chunks.
   - Example: "Quantum tunnelling occurs in semiconductors. [#WIKI23, #ARX5]"
6. **Output format:**

Return a structured JSON with fields:
{{
  "final_answer": "...synthesized, cited text...",
  "precision_at_k": float,
  "citation_accuracy": float,
  "faithfulness_score": float,
  "trace": [{{"sentence": "...", "supported_by": ["chunk_id1", "chunk_id2"]}}]
}}

### Context for Evaluation
Retrieved Chunks (with metadata):
{context}

Original Query:
{query}

Model's Raw Answer:
{previous_response}

Follow all citation and license rules from CiteRight-Multiverse.

IMPORTANT: Return ONLY valid JSON. Do not include any text before or after the JSON object."""


def evaluate_answer(query: str, context: str, previous_response: str) -> Dict[str, Any]:
    """
    Evaluate and enhance the generated answer using the evaluator prompt
    
    Args:
        query: The user's original question
        context: The retrieved context chunks
        previous_response: The model's initial response
        
    Returns:
        Dictionary containing evaluation metrics and enhanced answer
    """
    try:
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": EVALUATOR_PROMPT.format(
                context=context,
                query=query,
                previous_response=previous_response
            ),
            "stream": False,
            "options": {
                "temperature": 0.1,  # Lower temperature for more consistent JSON
                "num_predict": 2048
            }
        }
        
        response = requests.post(
            f"{settings.OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=180
        )
        response.raise_for_status()
        
        result = response.json().get("response", "")
        
        # Try to parse JSON from the response
        try:
            # Find JSON content between curly braces
            start = result.find('{')
            end = result.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = result[start:end]
                evaluation = json.loads(json_str)
                
                # Validate structure
                if all(key in evaluation for key in ["final_answer", "precision_at_k", "citation_accuracy", "faithfulness_score"]):
                    return evaluation
                else:
                    logger.warning("Evaluation response missing required fields")
                    return _fallback_evaluation(previous_response)
            else:
                logger.warning("No JSON found in evaluation response")
                return _fallback_evaluation(previous_response)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evaluation JSON: {e}")
            return _fallback_evaluation(previous_response)
            
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return _fallback_evaluation(previous_response)


def _fallback_evaluation(answer: str) -> Dict[str, Any]:
    """
    Return a fallback evaluation when the evaluator fails
    """
    return {
        "final_answer": answer,
        "precision_at_k": 0.0,
        "citation_accuracy": 0.0,
        "faithfulness_score": 0.0,
        "trace": [],
        "evaluation_failed": True
    }


def compute_source_distribution(docs: List) -> Dict[str, int]:
    """
    Compute the distribution of sources in retrieved documents
    
    Args:
        docs: List of retrieved documents with metadata
        
    Returns:
        Dictionary mapping source origins to counts
    """
    distribution = {}
    
    for doc in docs:
        meta = getattr(doc, 'metadata', {}) or {}
        origin = meta.get('origin', 'Unknown')
        distribution[origin] = distribution.get(origin, 0) + 1
        
    return distribution


def determine_dominant_tone(docs: List) -> str:
    """
    Determine the dominant tone based on source distribution
    
    Args:
        docs: List of retrieved documents
        
    Returns:
        Suggested tone (scholarly, practical, or balanced)
    """
    distribution = compute_source_distribution(docs)
    total = sum(distribution.values())
    
    if total == 0:
        return "balanced"
    
    # Calculate percentages
    arxiv_pct = distribution.get('arXiv', 0) / total
    stack_pct = distribution.get('StackExchange', 0) / total
    
    if arxiv_pct >= 0.6:
        return "scholarly"
    elif stack_pct >= 0.6:
        return "practical"
    else:
        return "balanced"

