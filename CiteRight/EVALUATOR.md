# CiteRight-Multiverse Evaluator 🔍

## Overview

The **CiteRight-Evaluator** is a post-generation reasoning and auditing layer that transforms CiteRight-Multiverse into a **self-evaluating knowledge engine**. Every answer is measured, every citation verified, and every sentence traceable.

## Key Features

### 1. **Grounding Evaluation**
- Verifies each factual claim against retrieved chunks
- Prevents hallucination by ensuring all statements are supported
- Provides quantitative **faithfulness score** (0-1 scale)

### 2. **Quality Metrics**

#### **Faithfulness Score**
- Measures how closely the output matches retrieved content
- Uses entailment reasoning (not just paraphrase similarity)
- Scale: 0.0 (completely unsupported) to 1.0 (fully grounded)

#### **Citation Accuracy**
- Fraction of statements correctly attributed to sources
- Ensures proper citation practices
- Identifies missing or incorrect citations

#### **Precision@k**
- Proportion of top-k retrieved chunks relevant to the query
- Helps optimize retrieval and reranking quality
- Indicates retrieval effectiveness

### 3. **Context Fusion**
- Merges complementary facts across sources
- Aligns identical entities (e.g., same Wikidata ID) across Wikipedia/arXiv/StackExchange
- Synthesizes unified explanations with cross-source links

### 4. **Metadata-Aware Summarization**
- **Automatic tone adjustment** based on source distribution:
  - **Scholarly tone**: When most chunks from arXiv (≥60%)
  - **Practical tone**: When mostly StackExchange (≥60%)
  - **Balanced tone**: Mixed sources
- Adapts writing style to content domain

### 5. **Transparency Trace**
- **Sentence-level provenance tracking**
- Each sentence tagged with supporting chunk IDs
- Example: "Quantum tunnelling occurs in semiconductors. [#WIKI23, #ARX5]"
- Enables "expand-to-see-evidence" UI features

## How It Works

### Pipeline Flow

```
1. multi_rag_query → Generate raw answer
2. multiverse_evaluator → Audit & enhance answer
3. Parse JSON → Display metrics + enhanced answer
```

### Code Example

```python
# Generate initial answer
answer = generate_with_ollama(query, context)

# Evaluate and enhance
evaluation = evaluate_answer(
    query=query,
    context=retrieved_context,
    previous_response=answer
)

# Use enhanced answer
final_answer = evaluation["final_answer"]

# Show metrics
print(f"Faithfulness: {evaluation['faithfulness_score']}")
print(f"Citation Accuracy: {evaluation['citation_accuracy']}")
print(f"Precision@k: {evaluation['precision_at_k']}")

# Display transparency trace
for item in evaluation['trace']:
    print(f"{item['sentence']} → {item['supported_by']}")
```

## API Usage

### Enable Evaluation in Query

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is quantum mechanics?",
    "sources": ["wikipedia", "arxiv"],
    "max_per_source": 3,
    "enable_evaluation": true
  }'
```

### Response Structure

```json
{
  "answer": "Enhanced, synthesized answer with improved citations...",
  "citations": [...],
  "used_reask": true,
  "timings_ms": {...},
  "evaluation": {
    "final_answer": "Same as answer field",
    "precision_at_k": 0.85,
    "citation_accuracy": 0.92,
    "faithfulness_score": 0.88,
    "trace": [
      {
        "sentence": "Quantum mechanics is a fundamental theory...",
        "supported_by": ["#WIKI1", "#ARX3"]
      }
    ]
  }
}
```

## UI Features

### In Streamlit

1. **Enable Evaluation Checkbox**
   - Toggle to activate the evaluator layer
   - Note: Increases response time but provides quality insights

2. **Quality Metrics Display**
   - Three-column metric view
   - Real-time scores for faithfulness, citation accuracy, and precision

3. **Transparency Trace Expander**
   - Collapsible section showing sentence-level sources
   - Users can verify each claim's provenance

## Benefits

### For Users
- **Trust**: See exactly which sources support each statement
- **Quality**: Quantified answer reliability
- **Learning**: Understand how conclusions are derived

### For Developers
- **Debugging**: Identify retrieval issues
- **Optimization**: Tune based on metric feedback
- **Monitoring**: Track answer quality over time

### For Research
- **Reproducibility**: Full transparency of reasoning chain
- **Evaluation**: Benchmark against ground truth
- **Analysis**: Study cross-source synthesis patterns

## Performance Considerations

- **Additional Latency**: ~5-10 seconds per query
- **Cost**: Extra LLM call (same as selective re-ask)
- **Benefit**: Measurable quality improvement
- **Recommendation**: Enable for high-stakes queries or quality auditing

## Future Enhancements

1. **Multi-hop Reasoning Chains**
   - Track reasoning steps across multiple inference passes
   
2. **Contradiction Detection**
   - Flag conflicting information across sources
   
3. **Confidence Calibration**
   - Learn to predict accuracy before evaluation
   
4. **Automated Quality Improvement**
   - Iteratively refine based on low metric scores

## Architecture

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Retrieval      │
│  (Hybrid)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Reranking      │
│  (Cross-Enc)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generation     │
│  (Ollama)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  EVALUATOR      │◄── Optional Layer
│  - Verify       │
│  - Fuse         │
│  - Measure      │
│  - Trace        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Enhanced       │
│  Response       │
└─────────────────┘
```

## Summary

The CiteRight-Evaluator transforms your RAG system from a simple Q&A tool into a **self-auditing knowledge engine**:

- ✅ **Every answer measured** (faithfulness, accuracy, precision)
- ✅ **Every citation verified** (proper attribution)
- ✅ **Every sentence traceable** (transparency trace)
- ✅ **Cross-source reasoning** (context fusion)
- ✅ **Adaptive tone** (metadata-aware)

**Result**: Trust + Transparency + Quality = Enterprise-grade RAG

