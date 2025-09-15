# Manus AI Smart Layer

\n


# Manus AI Smart Layer

## Project Overview

This project aims to develop a self-improving, credit-efficient personal management system utilizing Manus AI. The core philosophy revolves around persistence, recursive learning, and phone-first accessibility. The system is designed to operate within strict credit management limits (≤300 kT/day) to ensure cost-effectiveness and sustainability. Integration with GitHub provides robust version control and persistence for code, while Supabase is leveraged for scalable data storage and retrieval.

## Goals

The primary goals of the Manus AI Smart Layer project include:

1.  **Self-Improvement**: The system should continuously learn and adapt based on interactions and feedback, optimizing its performance and utility over time.
2.  **Credit Efficiency**: Operations are meticulously managed to stay within a daily credit budget of 300 kT, ensuring long-term viability without excessive costs.
3.  **Persistence**: All critical data, configurations, and learning trajectories are persistently stored using Git for code and Supabase for dynamic data.
4.  **Recursive Learning**: Implementation of mechanisms that allow the AI to reflect on its own performance, identify areas for improvement, and refine its strategies.
5.  **Phone-First Accessibility**: The system is designed with mobile users in mind, aiming for a seamless and intuitive experience on smartphones, including Progressive Web App (PWA) capabilities.
6.  **Clear Documentation**: Comprehensive and up-to-date documentation to facilitate understanding, collaboration, and onboarding for new contributors.

## Current Progress

As of September 15, 2025, the project has achieved the following milestones:

### 1. Credit Survival Components Implemented

-   **`memory/router.py`**: This module now includes the `call_r1()` function, which acts as the primary interface for LLM calls. It incorporates caching mechanisms to reduce redundant API calls and a `spend()` function for meticulous credit management.
-   **`logs/cost.csv`**: An initialization of this file has been completed, serving as the ledger for tracking token usage and maintaining a detailed credit history. This is crucial for adhering to the daily credit budget.

### 2. Git Repository Setup and Persistence

-   **GitHub Integration**: The project repository is successfully connected to `github.com/starsh00ter/manus_ai_smart_layer`. This ensures all code changes are version-controlled and backed up.
-   **Auto-Push Functionality**: Automated processes are in place to push changes to the GitHub repository, guaranteeing persistence and collaboration readiness.

### 3. Core Documentation Initiated

-   **`README.md`**: The foundational `README.md` file has been initiated. This document serves as the central point for project overview, navigation, and onboarding information for new team members or contributors.

## Technical Context

-   **LLM Provider**: DeepSeek API is utilized for all Large Language Model interactions. The API key `sk-54d1a6b52db44d5dab38fd5725773825` is configured for this purpose.
-   **Version Control**: GitHub is the chosen platform for source code management, with a dedicated token ensuring secure and persistent commits.
-   **Database**: Supabase provides the backend infrastructure for persistent data storage, including a specified URL and key for access. A dedicated bucket is also configured for file storage.
-   **Credit Management**: A strict daily credit limit of ≤300 kT is enforced across all operations.
-   **Accessibility**: Development prioritizes a phone-first approach, with future plans for PWA capabilities to enhance mobile user experience.

## Key Files

-   `/home/ubuntu/my_manus_knowledge/memory/router.py`: Manages API calls, caching, and credit expenditure.
-   `/home/ubuntu/my_manus_knowledge/logs/cost.csv`: Records token usage and credit balance.
-   `/home/ubuntu/my_manus_knowledge/README.md`: Project documentation and navigation guide.
-   `/home/ubuntu/my_manus_knowledge/memory/supabase_client.py`: Handles all interactions with the Supabase database.

## Next Steps

1.  **Complete and Commit `README.md`**: Enhance the existing `README.md` with comprehensive project documentation, including detailed setup instructions, usage guidelines, and contribution policies. Ensure all changes are committed to Git.
2.  **Implement Supabase Integration**: Fully integrate Supabase for persistent data storage. This involves:
    -   Setting up the `pgvector` extension for efficient vector similarity search.
    -   Creating necessary tables to store various types of data.
    -   Implementing embedding storage for AI-related data.
3.  **Develop Recursive Learning Layer**: Build the foundational components for the AI's self-improvement capabilities:
    -   Create `logs/trajectory.csv` to log AI decision-making processes and outcomes.
    -   Implement a task scoring mechanism to evaluate AI performance.
4.  **Add Phone-First UX Features**: Enhance the user experience for mobile devices:
    -   Implement a PWA manifest for installability and offline access.
    -   Integrate Monaco editor for an enhanced coding experience on mobile.
    -   Develop a live dashboard for real-time monitoring of system performance and credit usage.

This `README.md` will be continuously updated as the project evolves.

