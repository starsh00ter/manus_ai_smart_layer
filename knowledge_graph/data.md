content = 


[
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/system_brief.md", "title": "System Brief", "file_type": "system_brief"},
    "relationship": "HAS_TAG",
    "entity2": {"type": "TAG", "name": "SystemArchitecture"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/user_profile.md", "title": "User Profile", "file_type": "user_profile"},
    "relationship": "HAS_TAG",
    "entity2": {"type": "TAG", "name": "UserPreferences"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/master_plan.md", "title": "Master Plan", "file_type": "master_plan"},
    "relationship": "HAS_TAG",
    "entity2": {"type": "TAG", "name": "TaskPlanning"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/library/monitored_keywords.md", "title": "Monitored Keywords", "file_type": "keyword_list"},
    "relationship": "DISCUSSES",
    "entity2": {"type": "CONCEPT", "name": "KeywordMonitoring"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/library/roles/master_prompt_engineer.md", "title": "Master Prompt Engineer Role", "file_type": "role_definition"},
    "relationship": "DEFINES",
    "entity2": {"type": "ROLE", "name": "Master Prompt Engineer"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/library/prompts/memory_system_optimization_prompt.md", "title": "Memory System Optimization Prompt", "file_type": "prompt_definition"},
    "relationship": "TARGETS",
    "entity2": {"type": "BOTTLENECK", "description": "Lack of a Meta-Index"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/library/prompts/memory_system_optimization_prompt.md", "title": "Memory System Optimization Prompt", "file_type": "prompt_definition"},
    "relationship": "TARGETS",
    "entity2": {"type": "BOTTLENECK", "description": "Static RAG Protocol"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/archive/2025-09-10_Lakera_Prompt_Engineering_Summary.md", "title": "Lakera Prompt Engineering Summary", "file_type": "archive_document"},
    "relationship": "DISCUSSES",
    "entity2": {"type": "CONCEPT", "name": "PromptEngineering"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/archive/2025-09-10_Advanced_RAG_Architectures_Synthesis.md", "title": "Advanced RAG Architectures Synthesis", "file_type": "archive_document"},
    "relationship": "DISCUSSES",
    "entity2": {"type": "CONCEPT", "name": "RAG"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/archive/2025-09-10_Knowledge_Graph_LLM_Integration_Synthesis.md", "title": "Knowledge Graph LLM Integration Synthesis", "file_type": "archive_document"},
    "relationship": "DISCUSSES",
    "entity2": {"type": "CONCEPT", "name": "KnowledgeGraph"}
  },
  {
    "entity1": {"type": "FILE", "path": "/home/ubuntu/my_manus_knowledge/archive/2025-09-10_Self_Improving_Retrieval_Protocols_Synthesis.md", "title": "Self Improving Retrieval Protocols Synthesis", "file_type": "archive_document"},
    "relationship": "DISCUSSES",
    "entity2": {"type": "CONCEPT", "name": "AdaptiveRAG"}
  },
  {
    "entity1": {"type": "USER", "name": "user"},
    "relationship": "IDENTIFIES",
    "entity2": {"type": "BOTTLENECK", "description": "Lack of a Meta-Index"}
  },
  {
    "entity1": {"type": "USER", "name": "user"},
    "relationship": "IDENTIFIES",
    "entity2": {"type": "BOTTLENECK", "description": "Static RAG Protocol"}
  },
  {
    "entity1": {"type": "BOTTLENECK", "description": "Lack of a Meta-Index"},
    "relationship": "ADDRESSED_BY",
    "entity2": {"type": "SOLUTION", "description": "Meta-Index via Simplified Knowledge Graph"}
  },
  {
    "entity1": {"type": "BOTTLENECK", "description": "Static RAG Protocol"},
    "relationship": "ADDRESSED_BY",
    "entity2": {"type": "SOLUTION", "description": "Dynamic and Adaptive RAG Protocol"}
  }
]

