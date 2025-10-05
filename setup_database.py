#!/usr/bin/env python3

import os
import sys
import time
import json

# Add manus_core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'manus_core'))

from manus_core.db.client import get_shared_client

def setup_database():
    """Set up the database schema for the Manus AI Smart Layer, aligning with shared schemas."""
    print("Setting up database schema...")
    
    try:
        # Ensure Supabase credentials are set as environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials (SUPABASE_URL, SUPABASE_KEY) not found in environment variables.")
            print("Please set them before running this script. Example:")
            print("  export SUPABASE_URL=\"https://your-project-id.supabase.co\"")
            print("  export SUPABASE_KEY=\"your-anon-public-key\"")
            print("  (If using a DATABASE_URL connection string, extract the URL and key from it.)")
            sys.exit(1)

        # Use the shared client from manus_core
        supabase_client = get_shared_client("smart_layer")
        print("✅ Initialized Shared Supabase Client")
        
        # Read the shared schema SQL
        with open("/home/ubuntu/my_manus_knowledge/shared_database_schema.sql", "r") as f:
            shared_sql = f.read()
            
        # Read the enhanced schema SQL (for credit ledger, config, etc.)
        with open("/home/ubuntu/my_manus_knowledge/enhanced_database_schema.sql", "r") as f:
            enhanced_sql = f.read()

        # Combine SQL commands
        combined_sql = shared_sql + "\n" + enhanced_sql

        print("\n📝 Database setup instructions for Account A and B:")
        print("1. Ensure your environment variables are set:")
        print("   export SUPABASE_URL=\"https://wxqhercmwmyhihfcuwti.supabase.co\"")
        print("   export SUPABASE_KEY=\"I<3women\" (or your actual anon public key)")
        print("2. Go to your Supabase dashboard: https://app.supabase.com/project/wxqhercmwmyhihfcuwti")
        print("3. Navigate to the SQL Editor")
        print("4. Execute the following combined SQL commands to create all shared and project-specific tables:")
        print("""\n""" + combined_sql + """\n""")
        print("5. Ensure the pgvector extension is enabled in your Supabase dashboard (Database -> Extensions).")
        
        # Check health and schema info
        health = supabase_client.health_check()
        print(f"\nDatabase Health Check: {health['status']} - {health['message']}")

        if health['status'] == 'connected':
            schema_info = supabase_client.get_schema_info()
            print("\nAvailable Schemas and Tables:")
            if "error" not in schema_info:
                for schema, tables in schema_info.items():
                    print(f"  Schema '{schema}':")
                    for table in tables:
                        print(f"    - {table['name']} ({table['type']})")
            else:
                print(f"  Error retrieving schema info: {schema_info['error']}")

            # Attempt to insert into shared.system_manifest to ensure it exists and is writable
            print("\nAttempting to update shared.system_manifest...")
            try:
                test_manifest_data = {
                    "latest_commit_hash_project1": "setup_test",
                    "schema_version": "1.0.0",
                    "core_library_version": "1.0.0",
                    "project1_last_update": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                }
                response = supabase_client.update(
                    "system_manifest", 
                    test_manifest_data,
                    {"latest_commit_hash_project1": "non_existent_hash"}, 
                    schema="shared"
                )
                if response:
                    print("✅ shared.system_manifest table accessible and writable (update test)")
                else:
                    existing_manifest = supabase_client.select("system_manifest", schema="shared")
                    if not existing_manifest:
                        supabase_client.insert("system_manifest", test_manifest_data, schema="shared")
                        print("✅ shared.system_manifest table accessible and writable (insert test)")
                    else:
                        print("✅ shared.system_manifest table accessible (already contains data)")

            except Exception as e:
                print(f"❌ shared.system_manifest table not accessible or writable: {e}")
                print("Please ensure the shared.system_manifest table is created and accessible.")
        else:
            print("Database not connected, skipping table access tests.")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")

if __name__ == "__main__":
    setup_database()


