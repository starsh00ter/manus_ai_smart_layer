import os
from supabase import create_client, Client
import json
import time

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Supabase credentials not found in environment variables.")
    # Fallback or raise error if Supabase is critical

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_thought(thought_text: str, embedding: list, trajectory_data: dict):
    try:
        data, count = supabase.table("thoughts").insert({
            "thought_text": thought_text,
            "embedding": embedding,
            "trajectory": trajectory_data,
            "timestamp": int(time.time())
        }).execute()
        print(f"✅ Thought inserted into Supabase: {data}")
        return data
    except Exception as e:
        print(f"❌ Error inserting thought into Supabase: {e}")
        return None

def get_thoughts(limit: int = 10):
    try:
        response = supabase.table("thoughts").select("*").order("timestamp", desc=True).limit(limit).execute()
        print(f"✅ Retrieved {len(response.data)} thoughts from Supabase.")
        return response.data
    except Exception as e:
        print(f"❌ Error retrieving thoughts from Supabase: {e}")
        return None

# Placeholder for embedding generation (will be integrated later)
def generate_embedding(text: str) -> list:
    # This would typically involve an LLM call or a dedicated embedding model
    # For now, return a dummy embedding
    return [0.0] * 1536 # Example for OpenAI embeddings dimension

# Example usage (for testing purposes, not part of regular operation)
if __name__ == "__main__":
    # Set environment variables for testing
    os.environ["SUPABASE_URL"] = "https://wxqhercmwmyhihfcuwti.supabase.co"
    os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4cWhlcmNtd215aGloZmN1d3RpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1NzAyNzksImV4cCI6MjA3MzE0NjI3OX0.XrExZWhz4sE0E08Z7rXBlJyYb8bKxpyh4i7uk2bnvx8"

    test_thought = "This is a test thought to be stored in Supabase."
    test_embedding = generate_embedding(test_thought)
    test_trajectory = {"action": "test_insert", "cost": 0, "timestamp": time.time()}

    inserted_data = insert_thought(test_thought, test_embedding, test_trajectory)
    if inserted_data:
        print("Successfully inserted test thought.")
        retrieved_data = get_thoughts(1)
        print("Retrieved thought:", retrieved_data)

    # Clean up environment variables after test
    del os.environ["SUPABASE_URL"]
    del os.environ["SUPABASE_KEY"]


