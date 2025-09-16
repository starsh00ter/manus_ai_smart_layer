#!/usr/bin/env python3

import os
import sys

# Set environment variables
os.environ["SUPABASE_URL"] = "https://wxqhercmwmyhihfcuwti.supabase.co"
os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4cWhlcmNtd215aGloZmN1d3RpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1NzAyNzksImV4cCI6MjA3MzE0NjI3OX0.XrExZWhz4sE0E08Z7rXBlJyYb8bKxpyh4i7uk2bnvx8"

from memory.supabase_client import get_client

def setup_database():
    """Set up the database schema for the Manus AI Smart Layer"""
    print("Setting up database schema...")
    
    try:
        supabase = get_client()
        print("✅ Connected to Supabase")
        
        # SQL commands to create tables
        sql_commands = [
            # Enable pgvector extension (this might need to be done manually in Supabase dashboard)
            """
            -- Enable pgvector extension for vector similarity search
            -- Note: This might need to be enabled manually in Supabase dashboard
            -- CREATE EXTENSION IF NOT EXISTS vector;
            """,
            
            # Create thoughts table for storing AI thoughts and embeddings
            """
            CREATE TABLE IF NOT EXISTS thoughts (
                id BIGSERIAL PRIMARY KEY,
                thought_text TEXT NOT NULL,
                embedding VECTOR(1536),  -- OpenAI embedding dimension
                trajectory JSONB,
                timestamp BIGINT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            # Create trajectory table for tracking AI decision-making
            """
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
            """,
            
            # Create credit_log table for tracking token usage
            """
            CREATE TABLE IF NOT EXISTS credit_log (
                id BIGSERIAL PRIMARY KEY,
                operation TEXT NOT NULL,
                tokens_used INTEGER NOT NULL,
                cost_estimate FLOAT,
                timestamp BIGINT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            # Create knowledge_graph table for storing relationships
            """
            CREATE TABLE IF NOT EXISTS knowledge_graph (
                id BIGSERIAL PRIMARY KEY,
                entity_a TEXT NOT NULL,
                relationship TEXT NOT NULL,
                entity_b TEXT NOT NULL,
                confidence FLOAT DEFAULT 1.0,
                metadata JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            # Create indexes for better performance
            """
            CREATE INDEX IF NOT EXISTS idx_thoughts_timestamp ON thoughts(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_trajectory_session ON trajectory(session_id);
            CREATE INDEX IF NOT EXISTS idx_trajectory_timestamp ON trajectory(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_credit_log_timestamp ON credit_log(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_knowledge_graph_entities ON knowledge_graph(entity_a, entity_b);
            """
        ]
        
        # Execute SQL commands
        for i, sql in enumerate(sql_commands):
            if sql.strip():
                try:
                    print(f"Executing SQL command {i+1}...")
                    # Note: Supabase Python client doesn't directly support raw SQL execution
                    # We'll need to create tables through the Supabase dashboard or use the REST API
                    print(f"SQL to execute:\n{sql}")
                except Exception as e:
                    print(f"❌ Error executing SQL command {i+1}: {e}")
        
        print("\n📝 Database setup instructions:")
        print("1. Go to your Supabase dashboard: https://app.supabase.com/project/wxqhercmwmyhihfcuwti")
        print("2. Navigate to the SQL Editor")
        print("3. Execute the SQL commands shown above")
        print("4. Enable the pgvector extension if needed")
        
        # Test table creation by trying to insert a test record
        print("\nTesting table access...")
        try:
            # Try to select from thoughts table to see if it exists
            result = supabase.table('thoughts').select('*').limit(1).execute()
            print("✅ Thoughts table is accessible")
        except Exception as e:
            print(f"❌ Thoughts table not accessible: {e}")
            print("Please create the tables manually using the SQL commands above")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")

if __name__ == "__main__":
    setup_database()

