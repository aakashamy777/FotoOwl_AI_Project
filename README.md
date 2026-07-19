# FotoOwl AI Engineer Task — Image-to-Video Multiagent Pipeline

## Overview
A 5-agent LangGraph pipeline that converts a folder of event photos + a free-text 
prompt into a Remotion video reel: Image Analyser → Storyboard Writer → 
Script Generator → Compiler & Fixer → Renderer.

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GOOGLE_API_KEY
npx create-video@latest remotion-app   # if remotion-app/ not present
python src/rag_store.py   # ingest RAG corpus into local Chroma
PYTHONPATH=. python src/graph.py   # run the full pipeline
```

## Architecture
5-node LangGraph StateGraph with a conditional retry loop between 
Compiler & Fixer and Script Generator (max 3 retries, hard cap → structured 
failure state). See `outputs/graph_diagram.mmd` for the Mermaid diagram.

## Model Routing
| Node | Model | Reason |
|---|---|---|
| Intent Parser | gemini-2.5-flash | cheap structured classification |
| Image Analyser | gemini-2.5-flash | 12x calls per run, vision tagging, cost-sensitive |
| Storyboard Writer | gemini-2.5-flash | structured sequencing, moderate reasoning |
| Script Generator | gemini-2.5-pro | highest reasoning needed for correct, compilable TSX |
| Compiler & Fixer | gemini-2.5-flash | error classification, targeted retrieval |

All LLM calls use `.with_structured_output()` with Pydantic models — no 
free-text parsing anywhere in the pipeline.

## RAG Design
Two local Chroma collections (`chroma_db/`), embedded with Gemini 
`gemini-embedding-001`:
- **style_guides**: chunked by markdown header (`##` sections) so each chunk 
  is one concept (pacing, visual treatment, caption tone, transitions) per style.
- **remotion_snippets**: one chunk per file — each file is a self-contained 
  code concept (Sequence, transitions, captions, composition root), so 
  splitting further would break code coherence.

Storyboard Writer retrieves style_guides by `visual_style`. Script Generator 
retrieves remotion_snippets by transition type; on retry, it additionally 
retrieves the snippet most relevant to the last compile error, so fixes are 
targeted rather than blind regenerations.

## Known Limitations
- Free-tier Gemini rate limits (429s) required retry/backoff logic; under 
  heavy load some nodes fall back to deterministic defaults (documented in 
  code) rather than crash the pipeline.
- Remotion render step (bonus, +5) may not complete end-to-end within the 
  submission window — pipeline exits gracefully with a structured failure 
  state and the storyboard/script artifacts are saved regardless, per the 
  task's partial-credit guidance.
- With more time: swap local sleep-based rate limiting for a proper token-
  bucket limiter, add image selection diversity scoring beyond quality_score, 
  expand RAG corpus with more style/snippet variety.

## Sample Output
See `outputs/sample_storyboard.json` and `outputs/sample_remotion_script.tsx` 
for a pipeline trace without needing to run the code.
