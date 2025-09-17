-- Shared Database Schema for Both Manus AI Projects
-- This schema enables coordination between sister projects

-- Create shared schema for cross-project coordination
CREATE SCHEMA IF NOT EXISTS shared;

-- Create project-specific schemas
CREATE SCHEMA IF NOT EXISTS smart_layer;
CREATE SCHEMA IF NOT EXISTS manus_origin;

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- SHARED SCHEMA TABLES
-- ============================================================================

-- System Manifest for project coordination
CREATE TABLE IF NOT EXISTS shared.system_manifest (
    id SERIAL PRIMARY KEY,
    latest_commit_hash_project1 TEXT, -- smart_layer project
    latest_commit_hash_project2 TEXT, -- manus_origin project
    core_library_version TEXT,
    schema_version TEXT,
    daily_credits_project1 INTEGER DEFAULT 0,
    daily_credits_project2 INTEGER DEFAULT 0,
    daily_limit_project1 INTEGER DEFAULT 300000,
    daily_limit_project2 INTEGER DEFAULT 300000,
    last_reset_date DATE DEFAULT CURRENT_DATE,
    project1_last_update TIMESTAMP DEFAULT NOW(),
    project2_last_update TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Shared embeddings cache for both projects
CREATE TABLE IF NOT EXISTS shared.embeddings_cache (
    id SERIAL PRIMARY KEY,
    content_hash TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384), -- Using 384-dim for efficiency
    model_name TEXT DEFAULT 'text-embedding-3-small',
    created_by TEXT, -- 'smart_layer' or 'manus_origin'
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW(),
    access_count INTEGER DEFAULT 1
);

-- Shared knowledge concepts for cross-project learning
CREATE TABLE IF NOT EXISTS shared.knowledge_concepts (
    id SERIAL PRIMARY KEY,
    concept_name TEXT NOT NULL,
    concept_type TEXT, -- 'technical', 'process', 'optimization', etc.
    description TEXT,
    embedding vector(384),
    source_project TEXT, -- 'smart_layer' or 'manus_origin'
    confidence_score FLOAT DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Shared optimization insights
CREATE TABLE IF NOT EXISTS shared.optimization_insights (
    id SERIAL PRIMARY KEY,
    insight_type TEXT, -- 'credit_optimization', 'performance', 'architecture'
    title TEXT NOT NULL,
    description TEXT,
    implementation_code TEXT,
    estimated_savings INTEGER, -- in tokens or percentage
    source_project TEXT,
    applied_by_project1 BOOLEAN DEFAULT FALSE,
    applied_by_project2 BOOLEAN DEFAULT FALSE,
    effectiveness_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Shared communication log
CREATE TABLE IF NOT EXISTS shared.communication_log (
    id SERIAL PRIMARY KEY,
    from_project TEXT,
    to_project TEXT,
    message_type TEXT, -- 'insight', 'warning', 'coordination', 'update'
    title TEXT,
    content TEXT,
    metadata JSONB,
    read_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- SMART LAYER PROJECT SCHEMA
-- ============================================================================

-- Trajectory tracking for smart layer
CREATE TABLE IF NOT EXISTS smart_layer.trajectory (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    action TEXT NOT NULL,
    input_data JSONB,
    output_data JSONB,
    cost_tokens INTEGER DEFAULT 0,
    score FLOAT DEFAULT 0.0,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Self-reflection data
CREATE TABLE IF NOT EXISTS smart_layer.reflections (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    reflection_type TEXT, -- 'scheduled', 'triggered', 'manual'
    performance_score FLOAT,
    insights JSONB,
    optimizations JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Learning integration data
CREATE TABLE IF NOT EXISTS smart_layer.learning_sessions (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    learning_data JSONB,
    performance_metrics JSONB,
    improvements JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- MANUS ORIGIN PROJECT SCHEMA (for coordination)
-- ============================================================================

-- Conversation turns (from brother project)
CREATE TABLE IF NOT EXISTS manus_origin.conv_turn (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP DEFAULT NOW(),
    role TEXT, -- 'user', 'assistant', 'system', 'self'
    text TEXT,
    meta JSONB,
    embedding vector(192)
);

-- Concepts (from brother project)
CREATE TABLE IF NOT EXISTS manus_origin.concept (
    id SERIAL PRIMARY KEY,
    name TEXT,
    aliases TEXT[],
    summary TEXT,
    meta JSONB,
    embedding vector(192)
);

-- Debug log (from brother project)
CREATE TABLE IF NOT EXISTS manus_origin.debug_log (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP DEFAULT NOW(),
    source TEXT,
    level TEXT, -- 'info', 'warn', 'error', 'fix'
    msg TEXT,
    patch TEXT
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Shared schema indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_cache_hash ON shared.embeddings_cache(content_hash);
CREATE INDEX IF NOT EXISTS idx_embeddings_cache_created_by ON shared.embeddings_cache(created_by);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_type ON shared.knowledge_concepts(concept_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_source ON shared.knowledge_concepts(source_project);
CREATE INDEX IF NOT EXISTS idx_optimization_insights_type ON shared.optimization_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_communication_log_projects ON shared.communication_log(from_project, to_project);

-- Smart layer indexes
CREATE INDEX IF NOT EXISTS idx_trajectory_session ON smart_layer.trajectory(session_id);
CREATE INDEX IF NOT EXISTS idx_trajectory_timestamp ON smart_layer.trajectory(timestamp);
CREATE INDEX IF NOT EXISTS idx_reflections_session ON smart_layer.reflections(session_id);

-- Vector similarity search indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_cache_vector ON shared.embeddings_cache USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_vector ON shared.knowledge_concepts USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update manifest timestamp
CREATE OR REPLACE FUNCTION shared.update_manifest_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for manifest updates
DROP TRIGGER IF EXISTS trigger_update_manifest_timestamp ON shared.system_manifest;
CREATE TRIGGER trigger_update_manifest_timestamp
    BEFORE UPDATE ON shared.system_manifest
    FOR EACH ROW
    EXECUTE FUNCTION shared.update_manifest_timestamp();

-- Function to reset daily credits
CREATE OR REPLACE FUNCTION shared.reset_daily_credits()
RETURNS VOID AS $$
BEGIN
    UPDATE shared.system_manifest 
    SET daily_credits_project1 = 0,
        daily_credits_project2 = 0,
        last_reset_date = CURRENT_DATE
    WHERE last_reset_date < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Function to update embedding access
CREATE OR REPLACE FUNCTION shared.update_embedding_access(content_hash_param TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE shared.embeddings_cache 
    SET last_accessed = NOW(),
        access_count = access_count + 1
    WHERE content_hash = content_hash_param;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Initialize system manifest
INSERT INTO shared.system_manifest (
    core_library_version,
    schema_version,
    latest_commit_hash_project1,
    latest_commit_hash_project2
) VALUES (
    '1.0.0',
    '1.0.0',
    'initial',
    'initial'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- PERMISSIONS (if using RLS)
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE shared.system_manifest ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared.communication_log ENABLE ROW LEVEL SECURITY;

-- Create policies for project access
-- (These would be customized based on your authentication setup)

-- ============================================================================
-- VIEWS FOR EASY ACCESS
-- ============================================================================

-- View for current system status
CREATE OR REPLACE VIEW shared.system_status AS
SELECT 
    core_library_version,
    schema_version,
    daily_credits_project1,
    daily_credits_project2,
    daily_limit_project1,
    daily_limit_project2,
    (daily_credits_project1::FLOAT / daily_limit_project1) * 100 AS usage_percent_project1,
    (daily_credits_project2::FLOAT / daily_limit_project2) * 100 AS usage_percent_project2,
    last_reset_date,
    project1_last_update,
    project2_last_update,
    updated_at
FROM shared.system_manifest
ORDER BY updated_at DESC
LIMIT 1;

-- View for recent communications
CREATE OR REPLACE VIEW shared.recent_communications AS
SELECT 
    from_project,
    to_project,
    message_type,
    title,
    content,
    read_status,
    created_at
FROM shared.communication_log
ORDER BY created_at DESC
LIMIT 50;

-- View for optimization opportunities
CREATE OR REPLACE VIEW shared.optimization_opportunities AS
SELECT 
    insight_type,
    title,
    description,
    estimated_savings,
    source_project,
    CASE 
        WHEN applied_by_project1 AND applied_by_project2 THEN 'Both Applied'
        WHEN applied_by_project1 THEN 'Project 1 Applied'
        WHEN applied_by_project2 THEN 'Project 2 Applied'
        ELSE 'Not Applied'
    END AS application_status,
    effectiveness_score,
    created_at
FROM shared.optimization_insights
ORDER BY estimated_savings DESC, created_at DESC;

