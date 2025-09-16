# Knowledge Graph Schema for Manus AI Memory System

This document defines the entities and relationships within the Manus AI knowledge graph, which serves as a meta-index for the system.

## Entities:

*   **FILE:** Represents any document or file within the `/my_manus_knowledge/` directory.
    *   Properties: `path` (absolute path), `title` (extracted title), `type` (e.g., `system_brief`, `user_profile`, `archive_document`, `log`, `role_definition`, `prompt_definition`, `blueprint`).

*   **CONCEPT:** Represents a key idea, topic, or theme discussed in documents.
    *   Properties: `name`.

*   **TAG:** Represents a keyword or category used for classification.
    *   Properties: `name`.

*   **ROLE:** Represents a defined persona or function within the system.
    *   Properties: `name`.

*   **PROMPT:** Represents a specific instruction or query given to Manus AI.
    *   Properties: `name` (e.g., `memory_system_optimization_prompt`), `type` (e.g., `advanced`, `simple`).

*   **USER:** Represents the human user interacting with Manus AI.
    *   Properties: `name` (e.g., `user`).

*   **BOTTLENECK:** Represents a limitation or inefficiency identified in the system.
    *   Properties: `description`.

*   **SOLUTION:** Represents a proposed method to address a bottleneck.
    *   Properties: `description`.

## Relationships:

*   **FILE --HAS_TAG--> TAG:** A file is associated with a specific tag.
*   **FILE --REFERENCES--> FILE:** One file explicitly references another file.
*   **FILE --DISCUSSES--> CONCEPT:** A file discusses a particular concept.
*   **ROLE --DEFINES--> PROMPT:** A role defines a specific prompt.
*   **PROMPT --TARGETS--> BOTTLENECK:** A prompt is designed to address a specific bottleneck.
*   **BOTTLENECK --ADDRESSED_BY--> SOLUTION:** A bottleneck is addressed by a proposed solution.
*   **SOLUTION --IMPROVES--> CONCEPT:** A solution improves a specific concept (e.g., RAG performance, contextual understanding).
*   **USER --HAS_PREFERENCE--> CONCEPT:** The user has a preference related to a concept.
*   **USER --IDENTIFIES--> BOTTLENECK:** The user identifies a bottleneck.
*   **MANUS_AI --PERFORMS--> TASK:** Manus AI performs a specific task.
*   **TASK --USES--> FILE:** A task uses a specific file.
*   **TASK --GENERATES--> FILE:** A task generates a specific file.

## Example Data Structure (for `data.md`):

```json
[
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/system_brief.md", "title": "System Brief"},
    "relationship": "HAS_TAG",
    "entity2": {"type": "TAG", "name": "SystemArchitecture"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/archive/2025-09-10_Lakera_Prompt_Engineering_Summary.md", "title": "Lakera Prompt Engineering Summary"},
    "relationship": "DISCUSSES",
    "entity2": {"type": "CONCEPT", "name": "PromptEngineering"}
  },
  {
    "entity1": {"type": "ROLE", "name": "Master Prompt Engineer"},
    "relationship": "DEFINES",
    "entity2": {"type": "PROMPT", "name": "memory_system_optimization_prompt"}
  }
]
```


