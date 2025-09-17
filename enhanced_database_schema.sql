-- Enhanced Database Schema with Atomic Credit Ledger
-- Addresses critical gaps identified in system analysis

-- ============================================================================
-- ATOMIC CREDIT LEDGER SYSTEM
-- ============================================================================

-- Atomic credit ledger for transactional credit management
CREATE TABLE IF NOT EXISTS credit_ledger (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT DEFAULT 'system',
    session_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    operation_type TEXT NOT NULL, -- 'ESTIMATE', 'ACTUAL', 'REFUND'
    tokens_estimated INTEGER NOT NULL,
    tokens_actual INTEGER DEFAULT 0,
    cost_estimate FLOAT NOT NULL,
    cost_actual FLOAT DEFAULT 0.0,
    remaining_balance FLOAT NOT NULL,
    transaction_type TEXT NOT NULL, -- 'DEBIT', 'CREDIT'
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for credit ledger performance
CREATE INDEX IF NOT EXISTS idx_credit_ledger_user_session ON credit_ledger(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_credit_ledger_task ON credit_ledger(task_id);
CREATE INDEX IF NOT EXISTS idx_credit_ledger_timestamp ON credit_ledger(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_credit_ledger_operation_type ON credit_ledger(operation_type);
CREATE INDEX IF NOT EXISTS idx_credit_ledger_user_date ON credit_ledger(user_id, DATE(created_at));

-- Function to update remaining balance atomically
CREATE OR REPLACE FUNCTION update_credit_balance()
RETURNS TRIGGER AS $$
DECLARE
    current_balance FLOAT;
    daily_limit FLOAT := 300000.0;
BEGIN
    -- Get the most recent balance for this user
    SELECT COALESCE(remaining_balance, daily_limit) 
    INTO current_balance
    FROM credit_ledger 
    WHERE user_id = NEW.user_id 
    ORDER BY created_at DESC 
    LIMIT 1;
    
    -- If no previous balance found, use daily limit
    IF current_balance IS NULL THEN
        current_balance := daily_limit;
    END IF;
    
    -- Calculate new balance based on transaction type
    IF NEW.transaction_type = 'DEBIT' THEN
        NEW.remaining_balance := current_balance - NEW.tokens_estimated;
    ELSE -- CREDIT (refund)
        NEW.remaining_balance := current_balance + NEW.tokens_estimated;
    END IF;
    
    -- Ensure balance doesn't go negative or exceed daily limit
    NEW.remaining_balance := GREATEST(0, LEAST(NEW.remaining_balance, daily_limit));
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update credit balance
DROP TRIGGER IF EXISTS trigger_update_credit_balance ON credit_ledger;
CREATE TRIGGER trigger_update_credit_balance
    BEFORE INSERT ON credit_ledger
    FOR EACH ROW
    EXECUTE FUNCTION update_credit_balance();

-- Function to reset daily credits
CREATE OR REPLACE FUNCTION reset_daily_credits()
RETURNS VOID AS $$
DECLARE
    daily_limit FLOAT := 300000.0;
BEGIN
    -- Insert reset entries for all active users
    INSERT INTO credit_ledger (user_id, session_id, task_id, operation_type, 
                              tokens_estimated, tokens_actual, cost_estimate, 
                              cost_actual, remaining_balance, transaction_type, metadata)
    SELECT DISTINCT user_id, 
           'daily_reset_' || EXTRACT(EPOCH FROM NOW())::TEXT,
           'daily_reset',
           'RESET',
           0, 0, 0.0, 0.0,
           daily_limit,
           'CREDIT',
           jsonb_build_object('reset_date', CURRENT_DATE, 'reset_type', 'daily')
    FROM credit_ledger 
    WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
    AND NOT EXISTS (
        SELECT 1 FROM credit_ledger cl2 
        WHERE cl2.user_id = credit_ledger.user_id 
        AND cl2.operation_type = 'RESET' 
        AND DATE(cl2.created_at) = CURRENT_DATE
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SYSTEM CONFIGURATION TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key TEXT UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    config_type TEXT NOT NULL, -- 'credit', 'system', 'feature'
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default configuration
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('daily_credit_limit', '300000', 'credit', 'Daily credit limit in tokens'),
('credit_warning_threshold', '0.8', 'credit', 'Warning threshold as percentage'),
('credit_emergency_threshold', '0.95', 'credit', 'Emergency threshold as percentage'),
('max_single_operation', '50000', 'credit', 'Maximum tokens for single operation'),
('session_timeout', '3600', 'system', 'Session timeout in seconds'),
('reflection_interval', '14400', 'system', 'Reflection interval in seconds (4 hours)'),
('max_trajectory_length', '1000', 'system', 'Maximum trajectory entries to keep'),
('cache_ttl', '86400', 'system', 'Cache TTL in seconds (24 hours)'),
('credit_budget_required', 'true', 'feature', 'Require credit budget for operations'),
('auto_reflection', 'true', 'feature', 'Enable automatic reflection'),
('schema_validation', 'true', 'feature', 'Enable schema validation'),
('self_optimization', 'true', 'feature', 'Enable self-optimization')
ON CONFLICT (config_key) DO NOTHING;

-- ============================================================================
-- AUDIT LOG TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    operation_type TEXT NOT NULL, -- 'CREATE', 'READ', 'UPDATE', 'DELETE'
    table_name TEXT NOT NULL,
    record_id TEXT,
    operation_id TEXT NOT NULL,
    estimated_cost FLOAT,
    actual_cost FLOAT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for audit log
CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_operation ON audit_log(operation_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_operation_id ON audit_log(operation_id);

-- ============================================================================
-- COMPONENT RATINGS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS component_ratings (
    id BIGSERIAL PRIMARY KEY,
    component_id TEXT NOT NULL,
    component_type TEXT NOT NULL,
    rating_type TEXT NOT NULL, -- 'confidence', 'alignment', 'functionality', etc.
    score FLOAT NOT NULL CHECK (score >= 0.0 AND score <= 1.0),
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    reasoning TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for component ratings
CREATE INDEX IF NOT EXISTS idx_component_ratings_component ON component_ratings(component_id);
CREATE INDEX IF NOT EXISTS idx_component_ratings_type ON component_ratings(rating_type);
CREATE INDEX IF NOT EXISTS idx_component_ratings_timestamp ON component_ratings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_component_ratings_score ON component_ratings(score DESC);

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    version_number TEXT NOT NULL,
    description TEXT,
    migration_script TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by TEXT DEFAULT 'system'
);

-- Insert current schema version
INSERT INTO schema_versions (version_number, description, migration_script) VALUES
('2.0.0', 'Enhanced schema with atomic credit ledger and unified CRUD support', 'enhanced_database_schema.sql')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PERFORMANCE METRICS TABLE (Enhanced)
-- ============================================================================

-- Drop existing table if it exists and recreate with enhanced structure
DROP TABLE IF EXISTS performance_metrics CASCADE;

CREATE TABLE performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    metric_type TEXT NOT NULL, -- 'credit_efficiency', 'response_time', 'error_rate', etc.
    metric_value FLOAT NOT NULL,
    metric_unit TEXT, -- 'tokens', 'seconds', 'percentage', etc.
    component_id TEXT,
    operation_id TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance metrics
CREATE INDEX IF NOT EXISTS idx_performance_metrics_session ON performance_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON performance_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_component ON performance_metrics(component_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(created_at DESC);

-- ============================================================================
-- VIEWS FOR EASY ACCESS
-- ============================================================================

-- View for current credit status
CREATE OR REPLACE VIEW current_credit_status AS
SELECT 
    user_id,
    remaining_balance,
    (300000 - remaining_balance) AS used_today,
    ((300000 - remaining_balance) / 300000.0) * 100 AS usage_percentage,
    created_at AS last_update
FROM credit_ledger cl1
WHERE cl1.created_at = (
    SELECT MAX(cl2.created_at) 
    FROM credit_ledger cl2 
    WHERE cl2.user_id = cl1.user_id
)
ORDER BY last_update DESC;

-- View for daily credit usage
CREATE OR REPLACE VIEW daily_credit_usage AS
SELECT 
    user_id,
    DATE(created_at) AS usage_date,
    SUM(CASE WHEN transaction_type = 'DEBIT' THEN tokens_actual ELSE 0 END) AS total_used,
    COUNT(CASE WHEN transaction_type = 'DEBIT' THEN 1 END) AS operation_count,
    AVG(CASE WHEN transaction_type = 'DEBIT' THEN tokens_actual ELSE NULL END) AS avg_per_operation
FROM credit_ledger
WHERE operation_type IN ('ACTUAL', 'ESTIMATE')
GROUP BY user_id, DATE(created_at)
ORDER BY usage_date DESC;

-- View for component health
CREATE OR REPLACE VIEW component_health AS
SELECT 
    component_id,
    component_type,
    AVG(score) AS avg_score,
    AVG(confidence) AS avg_confidence,
    COUNT(*) AS rating_count,
    MAX(created_at) AS last_rated
FROM component_ratings
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY component_id, component_type
ORDER BY avg_score DESC;

-- View for system performance
CREATE OR REPLACE VIEW system_performance AS
SELECT 
    metric_type,
    AVG(metric_value) AS avg_value,
    MIN(metric_value) AS min_value,
    MAX(metric_value) AS max_value,
    COUNT(*) AS measurement_count,
    MAX(created_at) AS last_measured
FROM performance_metrics
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY metric_type
ORDER BY metric_type;

-- ============================================================================
-- FUNCTIONS FOR CREDIT MANAGEMENT
-- ============================================================================

-- Function to check credit availability
CREATE OR REPLACE FUNCTION check_credit_availability(
    p_user_id TEXT,
    p_estimated_tokens INTEGER
) RETURNS JSONB AS $$
DECLARE
    current_balance FLOAT;
    result JSONB;
BEGIN
    -- Get current balance
    SELECT remaining_balance INTO current_balance
    FROM credit_ledger
    WHERE user_id = p_user_id
    ORDER BY created_at DESC
    LIMIT 1;
    
    -- If no balance found, use daily limit
    IF current_balance IS NULL THEN
        current_balance := 300000.0;
    END IF;
    
    -- Check availability
    IF current_balance >= p_estimated_tokens THEN
        result := jsonb_build_object(
            'allowed', true,
            'remaining_balance', current_balance,
            'estimated_tokens', p_estimated_tokens,
            'usage_percentage', ((300000 - current_balance) / 300000.0) * 100
        );
    ELSE
        result := jsonb_build_object(
            'allowed', false,
            'remaining_balance', current_balance,
            'estimated_tokens', p_estimated_tokens,
            'shortage', p_estimated_tokens - current_balance,
            'usage_percentage', ((300000 - current_balance) / 300000.0) * 100
        );
    END IF;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to reserve credits
CREATE OR REPLACE FUNCTION reserve_credits(
    p_user_id TEXT,
    p_session_id TEXT,
    p_operation_id TEXT,
    p_operation_type TEXT,
    p_estimated_tokens INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    availability JSONB;
BEGIN
    -- Check availability first
    availability := check_credit_availability(p_user_id, p_estimated_tokens);
    
    IF (availability->>'allowed')::BOOLEAN THEN
        -- Insert reservation entry
        INSERT INTO credit_ledger (
            user_id, session_id, task_id, operation_type,
            tokens_estimated, cost_estimate, transaction_type,
            metadata
        ) VALUES (
            p_user_id, p_session_id, p_operation_id, p_operation_type,
            p_estimated_tokens, p_estimated_tokens / 1000.0, 'DEBIT',
            jsonb_build_object('reservation', true, 'timestamp', NOW())
        );
        
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CLEANUP AND MAINTENANCE FUNCTIONS
-- ============================================================================

-- Function to cleanup old audit logs
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM audit_log 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to cleanup old performance metrics
CREATE OR REPLACE FUNCTION cleanup_old_performance_metrics(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM performance_metrics 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to cleanup old component ratings
CREATE OR REPLACE FUNCTION cleanup_old_component_ratings(days_to_keep INTEGER DEFAULT 60)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Keep only the latest rating for each component/type combination
    DELETE FROM component_ratings cr1
    WHERE cr1.created_at < NOW() - INTERVAL '1 day' * days_to_keep
    AND EXISTS (
        SELECT 1 FROM component_ratings cr2
        WHERE cr2.component_id = cr1.component_id
        AND cr2.rating_type = cr1.rating_type
        AND cr2.created_at > cr1.created_at
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

