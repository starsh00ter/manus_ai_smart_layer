#!/usr/bin/env python3

"""
Shared Database Client for Manus AI Projects

Provides unified database access for both projects with proper schema isolation
and shared resource management.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️ Supabase client not available. Install with: pip install supabase")
    Client = None

class SharedDBClient:
    """Shared database client for both Manus AI projects"""
    
    def __init__(self, project_name: str = "smart_layer"):
        self.project_name = project_name
        self.client = self._init_client()
        self.schema_map = {
            "smart_layer": "smart_layer",
            "manus_origin": "manus_origin",
            "shared": "shared"
        }
        
    def _init_client(self) -> Optional[Client]:
        """Initialize Supabase client"""
        if not Client:
            return None
            
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            logging.warning("Supabase credentials not found. Using local fallback.")
            return None
            
        return create_client(url, key)
    
    def _get_table_name(self, table: str, schema: str = None) -> str:
        """Get fully qualified table name with schema"""
        if not schema:
            schema = self.schema_map.get(self.project_name, "smart_layer")
        
        return f"{schema}.{table}"
    
    def insert(self, table: str, data: Dict[str, Any], schema: str = None) -> Optional[Dict[str, Any]]:
        """Insert data into a table"""
        if not self.client:
            return self._local_fallback("insert", table, data, schema)
        
        try:
            table_name = self._get_table_name(table, schema)
            response = self.client.table(table_name).insert(data).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            logging.error(f"Database insert error: {e}")
            return self._local_fallback("insert", table, data, schema)
    
    def select(self, table: str, columns: str = "*", filters: Dict[str, Any] = None, 
               schema: str = None, limit: int = None, order_by: str = None) -> List[Dict[str, Any]]:
        """Select data from a table"""
        if not self.client:
            return self._local_fallback("select", table, columns, schema, filters, limit, order_by)
        
        try:
            table_name = self._get_table_name(table, schema)
            query = self.client.table(table_name).select(columns)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            # Apply ordering
            if order_by:
                desc = order_by.startswith("-")
                column = order_by.lstrip("-")
                query = query.order(column, desc=desc)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            return response.data or []
            
        except Exception as e:
            logging.error(f"Database select error: {e}")
            return self._local_fallback("select", table, columns, schema, filters, limit, order_by)
    
    def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any], 
               schema: str = None) -> bool:
        """Update data in a table"""
        if not self.client:
            return self._local_fallback("update", table, data, filters, schema)
        
        try:
            table_name = self._get_table_name(table, schema)
            query = self.client.table(table_name).update(data)
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            return len(response.data) > 0
            
        except Exception as e:
            logging.error(f"Database update error: {e}")
            return self._local_fallback("update", table, data, filters, schema)
    
    def delete(self, table: str, filters: Dict[str, Any], schema: str = None) -> bool:
        """Delete data from a table"""
        if not self.client:
            return self._local_fallback("delete", table, filters, schema)
        
        try:
            table_name = self._get_table_name(table, schema)
            query = self.client.table(table_name).delete()
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            return len(response.data) > 0
            
        except Exception as e:
            logging.error(f"Database delete error: {e}")
            return self._local_fallback("delete", table, filters, schema)
    
    def rpc(self, function_name: str, params: Dict[str, Any] = None) -> Any:
        """Call a database function"""
        if not self.client:
            logging.warning(f"Cannot call RPC function {function_name} without database connection")
            return None
        
        try:
            response = self.client.rpc(function_name, params or {}).execute()
            return response.data
            
        except Exception as e:
            logging.error(f"RPC call error: {e}")
            return None
    
    def vector_search(self, table: str, embedding: List[float], column: str = "embedding", 
                     limit: int = 10, schema: str = None) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        if not self.client:
            return []
        
        try:
            table_name = self._get_table_name(table, schema)
            
            # Use RPC for vector search (requires custom function in database)
            response = self.client.rpc('vector_search', {
                'table_name': table_name,
                'query_embedding': embedding,
                'match_count': limit,
                'embedding_column': column
            }).execute()
            
            return response.data or []
            
        except Exception as e:
            logging.error(f"Vector search error: {e}")
            return []
    
    def _local_fallback(self, operation: str, *args, **kwargs) -> Any:
        """Local file-based fallback for database operations"""
        fallback_dir = "local_db_fallback"
        os.makedirs(fallback_dir, exist_ok=True)
        
        if operation == "insert":
            table, data, schema = args[0], args[1], kwargs.get('schema')
            file_path = os.path.join(fallback_dir, f"{schema or self.project_name}_{table}.jsonl")
            
            # Add timestamp and ID
            data['_timestamp'] = datetime.now().isoformat()
            data['_id'] = hash(json.dumps(data, sort_keys=True))
            
            with open(file_path, 'a') as f:
                f.write(json.dumps(data) + '\n')
            
            return data
        
        elif operation == "select":
            table, columns, schema = args[0], args[1], kwargs.get('schema')
            filters = kwargs.get('filters', {})
            limit = kwargs.get('limit')
            
            file_path = os.path.join(fallback_dir, f"{schema or self.project_name}_{table}.jsonl")
            
            if not os.path.exists(file_path):
                return []
            
            results = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        
                        # Apply filters
                        if filters:
                            match = all(record.get(k) == v for k, v in filters.items())
                            if not match:
                                continue
                        
                        results.append(record)
                        
                        if limit and len(results) >= limit:
                            break
                            
                    except json.JSONDecodeError:
                        continue
            
            return results
        
        # For other operations, just log and return appropriate default
        logging.warning(f"Local fallback for {operation} not fully implemented")
        return False if operation in ["update", "delete"] else None
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about available schemas and tables"""
        if not self.client:
            return {"error": "No database connection"}
        
        try:
            # Get table information from information_schema
            response = self.client.table('information_schema.tables').select(
                'table_schema, table_name, table_type'
            ).in_('table_schema', ['shared', 'smart_layer', 'manus_origin']).execute()
            
            schema_info = {}
            for table in response.data or []:
                schema = table['table_schema']
                if schema not in schema_info:
                    schema_info[schema] = []
                schema_info[schema].append({
                    'name': table['table_name'],
                    'type': table['table_type']
                })
            
            return schema_info
            
        except Exception as e:
            logging.error(f"Error getting schema info: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check database connection health"""
        if not self.client:
            return {
                "status": "disconnected",
                "message": "No Supabase connection",
                "fallback": "local files"
            }
        
        try:
            # Simple query to test connection
            response = self.client.table('shared.system_manifest').select('id').limit(1).execute()
            
            return {
                "status": "connected",
                "message": "Database connection healthy",
                "tables_accessible": len(response.data) >= 0
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Database connection error: {e}",
                "fallback": "local files"
            }

# Singleton instance management
_shared_clients = {}

def get_shared_client(project_name: str = "smart_layer") -> SharedDBClient:
    """Get a shared database client instance"""
    if project_name not in _shared_clients:
        _shared_clients[project_name] = SharedDBClient(project_name)
    
    return _shared_clients[project_name]

def reset_client_cache():
    """Reset the client cache (useful for testing)"""
    global _shared_clients
    _shared_clients = {}

if __name__ == "__main__":
    # Test the shared client
    client = get_shared_client("smart_layer")
    
    print("🔍 Testing Shared Database Client...")
    
    # Health check
    health = client.health_check()
    print(f"Health: {health['status']} - {health['message']}")
    
    # Schema info
    schema_info = client.get_schema_info()
    if "error" not in schema_info:
        for schema, tables in schema_info.items():
            print(f"Schema {schema}: {len(tables)} tables")
    
    # Test insert (will use fallback if no connection)
    test_data = {
        "test_field": "test_value",
        "timestamp": datetime.now().isoformat()
    }
    
    result = client.insert("test_table", test_data, "shared")
    print(f"Insert test: {'✅' if result else '❌'}")
    
    print("✅ Shared client test complete")

