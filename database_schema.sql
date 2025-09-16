-- Manus AI Smart Layer Database Schema
-- Execute this in your Supabase SQL Editor

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create thoughts table for storing AI thoughts and embeddings
CREATE TABLE IF NOT EXISTS thoughts (
    id BIGSERIAL PRIMARY KEY,
    thought_text TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI embedding dimension
    trajectory JSONB,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create trajectory table for tracking AI decision-making
CREATE TABLE IF NOT EXISTS trajectory (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT,
    action TEXT NOT NULL,
    input_data JSONB,
    output_data JSONB,
    cost_tokens INTEGER DEFAULT 0,
    score FLOAT DEFAULT 0.0,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create credit_log table for tracking token usage
CREATE TABLE IF NOT EXISTS credit_log (
    id BIGSERIAL PRIMARY KEY,
    operation TEXT NOT NULL,
    tokens_used INTEGER NOT NULL,
    cost_estimate FLOAT,
    timestamp BIGINT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create knowledge_graph table for storing relationships
CREATE TABLE IF NOT EXISTS knowledge_graph (
    id BIGSERIAL PRIMARY KEY,
    entity_a TEXT NOT NULL,
    relationship TEXT NOT NULL,
    entity_b TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create self_reflection table for storing AI self-reflection logs
CREATE TABLE IF NOT EXISTS self_reflection (
    id BIGSERIAL PRIMARY KEY,
    reflection_text TEXT NOT NULL,
    insights JSONB,
    action_items JSONB,
    performance_score FLOAT,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create performance_metrics table for tracking system performance
CREATE TABLE IF NOT EXISTS performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_type TEXT, -- 'credit_efficiency', 'task_success_rate', 'response_time', etc.
    timestamp BIGINT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_thoughts_timestamp ON thoughts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_thoughts_embedding ON thoughts USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_trajectory_session ON trajectory(session_id);
CREATE INDEX IF NOT EXISTS idx_trajectory_timestamp ON trajectory(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trajectory_action ON trajectory(action);

CREATE INDEX IF NOT EXISTS idx_credit_log_timestamp ON credit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_credit_log_operation ON credit_log(operation);

CREATE INDEX IF NOT EXISTS idx_knowledge_graph_entities ON knowledge_graph(entity_a, entity_b);
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_relationship ON knowledge_graph(relationship);

CREATE INDEX IF NOT EXISTS idx_self_reflection_timestamp ON self_reflection(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp DESC);

-- Create RLS (Row Level Security) policies if needed
-- ALTER TABLE thoughts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE trajectory ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE credit_log ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE knowledge_graph ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE self_reflection ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;

-- Insert initial test data
INSERT INTO performance_metrics (metric_name, metric_value, metric_type, timestamp, metadata) 
VALUES ('system_initialization', 1.0, 'setup', EXTRACT(EPOCH FROM NOW()), '{"status": "initialized"}');

-- Create a view for recent activity
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    'thought' as activity_type,
    id,
    thought_text as content,
    timestamp,
    created_at
FROM thoughts
UNION ALL
SELECT 
    'trajectory' as activity_type,
    id,
    action as content,
    timestamp,
    created_at
FROM trajectory
UNION ALL
SELECT 
    'reflection' as activity_type,
    id,
    reflection_text as content,
    timestamp,
    created_at
FROM self_reflection
ORDER BY timestamp DESC
LIMIT 100;

