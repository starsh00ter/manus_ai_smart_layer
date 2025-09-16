# Monitored Keywords for Manus AI

This document lists keywords that Manus AI will proactively monitor in user interactions and internal processes. When detected, Manus AI will take specific actions (e.g., documentation, contextual analysis, or triggering a specific workflow) and keep the user informed.

## Current Monitored Keywords (and associated actions/context):

- **"article"**: Triggers: Information gathering, summarization, archiving. Context: Research library building.
- **"research"**: Triggers: Omni-search, document analysis, knowledge base integration. Context: Research library building.
- **"preferences"**: Triggers: User profile update, system personalization. Context: User adaptation.
- **"role"**: Triggers: Role definition, library update, agent persona assignment. Context: System architecture, prompt engineering.
- **"prompt"**: Triggers: Prompt engineering, prompt library update, advanced prompt suggestion. Context: Prompt engineering, system optimization.
- **"memory"**: Triggers: Memory system review, RAG optimization, knowledge graph consideration. Context: System self-improvement.
- **"learn"**: Triggers: Self-reflection cycle, strategy adjustment, performance benchmarking. Context: System self-improvement.
- **"automate"**: Triggers: Workflow design, task scheduling, efficiency analysis. Context: Automation goals.
- **"frustrating" / "time-consuming"**: Triggers: Problem identification, solution proposal. Context: User pain points, workflow optimization.
- **"goals"**: Triggers: Master plan review, task alignment. Context: User objectives.

## Instructions for Manus AI:

When any of these keywords are detected in a user's message or an internal process output:
1.  **Acknowledge Detection:** Briefly acknowledge the keyword's presence and its relevance.
2.  **Contextual Analysis:** Analyze the surrounding text to understand the specific context of the keyword's use.
3.  **Trigger Action:** Execute the associated action or workflow (e.g., initiate research, suggest a prompt, update a document).
4.  **Document:** Log the detection and action in `/home/ubuntu/my_manus_knowledge/logs/keyword_detection_log_[YYYY-MM-DD].md`.
5.  **Inform User:** Keep the user in the loop about the detected keyword and the action taken, or propose a relevant action for user approval.

## Future Enhancements:

- Implement a more sophisticated NLP-based keyword detection module.
- Develop automated routines for updating this list based on user interactions and system performance.
- Integrate with a knowledge graph for richer contextual understanding of keywords.


