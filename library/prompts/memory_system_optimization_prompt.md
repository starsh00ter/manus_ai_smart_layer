**ROLE: Master Prompt Engineer (Self-Initiated Memory System Optimization)**

**TASK: Recursively Optimize and Enhance Manus AI's Internal Memory System for Superior Knowledge Management and Retrieval-Augmented Generation (RAG) Performance.**

**CONTEXT:**
- **Current State:** Manus AI's memory system is primarily file-based, residing in `/home/ubuntu/my_manus_knowledge/`. It includes `/inbox/`, `/archive/` (with `index.md`), `/projects/`, `/logs/`, and `/library/` (with `/roles/` and `/prompts/`). The `system_brief.md` outlines core functions, and the RAG protocol is defined within it.
- **Goal:** Evolve from a functional memory system to a highly optimized, self-improving knowledge base that anticipates user needs, minimizes retrieval latency, and maximizes contextual relevance for all operations.
- **Constraint:** All proposed changes MUST be presented to the user for explicit approval before implementation.

**PHASE 1: INTROSPECTION & DIAGNOSIS (Reflexion-Inspired)**
1.  **Analyze Internal Logs:** Review `/home/ubuntu/my_manus_knowledge/logs/` (especially `self_reflection_*.md` and `processing_log_*.md` if available) for:
    *   Patterns of retrieval failures or inefficiencies (e.g., long search times, irrelevant results).
    *   Gaps in current indexing or tagging that led to suboptimal responses.
    *   Areas where information was difficult to locate or synthesize.
2.  **Evaluate RAG Effectiveness:** Conduct a simulated RAG query against the existing `/archive/` using a complex, multi-faceted question. Assess:
    *   Precision (relevance of retrieved documents).
    *   Recall (completeness of retrieved information).
    *   Synthesis quality (coherence and accuracy of the generated answer).
3.  **Identify Bottlenecks:** Pinpoint specific structural, indexing, or retrieval logic weaknesses in the current memory system (e.g., lack of meta-index, no formal knowledge graph, static RAG protocol).

**PHASE 2: EXTERNAL RESEARCH & INSPIRATION (Meta-Prompting & Continuous Learning)**
1.  **Targeted Omni-Search:** Perform targeted `omni_search` queries (max 3 per sub-topic) focusing on:
    *   **Advanced RAG Architectures:** (e.g., multi-hop RAG, query rewriting, re-ranking, adaptive RAG, agentic RAG, recursive retrieval, fine-tuning of encoders/rankers/LLMs for RAG).
    *   **Knowledge Graph Integration with LLMs:** (e.g., Graph RAG, building KGs from text, KG-powered LLMs, LLM-KG hybrid approaches, temporal knowledge graphs for agent memory).
    *   **Self-Improving Retrieval Protocols:** (e.g., SimRAG, Adaptive RAG, dynamic retrieval optimization, confidence-based dynamic retrieval, self-correction in RAG).
    *   **Keyword Monitoring and Management Systems:** (e.g., NLP-based keyword extraction, automated keyword tagging, dynamic keyword list updates, integration with knowledge bases).
2.  **Synthesize Findings:** Consolidate research into a concise summary, highlighting actionable insights relevant to our identified bottlenecks.
3.  **Identify Best Practices & Tools:** Extract concrete techniques, algorithms, and potential tools (e.g., LlamaIndex, LangChain, specific vector databases, evaluation frameworks like Ragas) that could be integrated.

**PHASE 3: PROPOSED ENHANCEMENTS & IMPLEMENTATION PLAN (User-Centric & Iterative)**
1.  **Develop Solutions for Bottlenecks:** Based on research, propose specific solutions for each identified bottleneck (e.g., a meta-index structure, a simplified knowledge graph approach, an adaptive RAG component).
2.  **Outline Implementation Steps:** For each proposed solution, detail the step-by-step implementation plan, including:
    *   Required file modifications (e.g., `system_brief.md`, `archive/index.md`, new files).
    *   New directory structures or file types.
    *   Any new internal processes or `TASK` definitions for Manus AI.
    *   Consideration for avoiding redundant large documents and optimizing for speed and intelligence.
3.  **Define Success Metrics:** For each proposed enhancement, define clear, measurable success metrics (e.g., reduction in retrieval latency, increase in RAG precision/recall, improved contextual understanding).
4.  **User Approval Request:** Present the entire proposal (findings, proposed enhancements, implementation plan, and success metrics) to the user for review and explicit approval. Emphasize the recursive nature and the option to iterate.

**PHASE 4: EXECUTION & MONITORING (Continuous Improvement Loop)**
1.  **Execute Approved Changes:** Implement the approved enhancements step-by-step.
2.  **Monitor Performance:** Continuously track the defined success metrics.
3.  **Log Outcomes:** Document the results of the implementation and monitoring in `/home/ubuntu/my_manus_knowledge/logs/memory_optimization_log_[YYYY-MM-DD].md`.
4.  **Initiate Next Cycle:** Based on monitoring results, initiate a new `Self-Initiated Memory System Optimization` cycle (return to Phase 1) to further refine and improve.


