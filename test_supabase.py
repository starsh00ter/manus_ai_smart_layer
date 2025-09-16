#!/usr/bin/env python3

import os
import sys

# Set environment variables
os.environ["SUPABASE_URL"] = "https://wxqhercmwmyhihfcuwti.supabase.co"
os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4cWhlcmNtd215aGloZmN1d3RpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1NzAyNzksImV4cCI6MjA3MzE0NjI3OX0.XrExZWhz4sE0E08Z7rXBlJyYb8bKxpyh4i7uk2bnvx8"

print("Testing Supabase connection...")

try:
    from supabase import create_client, Client
    print("✅ Supabase package imported successfully")
    
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    print(f"URL: {SUPABASE_URL[:30]}...")
    print(f"Key: {SUPABASE_KEY[:30]}...")
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created successfully")
    
    # Test connection by trying to access a table
    try:
        result = supabase.table('thoughts').select('*').limit(1).execute()
        print("✅ Connection test successful!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("This might be expected if the 'thoughts' table doesn't exist yet")
        
except ImportError as e:
    print(f"❌ Failed to import supabase: {e}")
    print("Trying to install supabase...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase"])
        print("✅ Supabase installed successfully")
        from supabase import create_client, Client
        print("✅ Supabase imported after installation")
    except Exception as install_error:
        print(f"❌ Failed to install supabase: {install_error}")

except Exception as e:
    print(f"❌ Unexpected error: {e}")

