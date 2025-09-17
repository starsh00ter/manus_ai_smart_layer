#!/usr/bin/env python3

"""
Shared Manifest Client for Manus AI Project Coordination

This module handles coordination between the two Manus AI projects through
a shared system manifest stored in Supabase.
"""

import os
import json
import hashlib
import subprocess
from datetime import datetime, date
from typing import Dict, Optional, List, Any
from dataclasses import dataclass

try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️ Supabase client not available. Install with: pip install supabase")
    Client = None

@dataclass
class ProjectStatus:
    """Status information for a project"""
    project_name: str
    commit_hash: str
    daily_credits: int
    daily_limit: int
    last_update: datetime
    
    @property
    def usage_percentage(self) -> float:
        """Calculate credit usage percentage"""
        return (self.daily_credits / self.daily_limit) * 100 if self.daily_limit > 0 else 0
    
    @property
    def remaining_credits(self) -> int:
        """Calculate remaining credits"""
        return max(0, self.daily_limit - self.daily_credits)

class ManifestClient:
    """Client for managing the shared system manifest"""
    
    def __init__(self, project_name: str = "smart_layer"):
        self.project_name = project_name
        self.supabase_client = self._init_supabase()
        self.current_commit = self._get_current_commit()
        
    def _init_supabase(self) -> Optional[Client]:
        """Initialize Supabase client"""
        if not Client:
            return None
            
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print("⚠️ Supabase credentials not found. Set SUPABASE_URL and SUPABASE_KEY.")
            return None
            
        return create_client(url, key)
    
    def _get_current_commit(self) -> str:
        """Get current Git commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            return result.stdout.strip()[:8] if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"
    
    def get_manifest(self) -> Optional[Dict[str, Any]]:
        """Get current system manifest"""
        if not self.supabase_client:
            return self._get_local_manifest()
        
        try:
            response = self.supabase_client.table('system_manifest').select('*').order('updated_at', desc=True).limit(1).execute()
            
            if response.data:
                return response.data[0]
            else:
                # Create initial manifest
                return self._create_initial_manifest()
                
        except Exception as e:
            print(f"❌ Error getting manifest: {e}")
            return self._get_local_manifest()
    
    def _get_local_manifest(self) -> Dict[str, Any]:
        """Get local fallback manifest"""
        local_file = "shared_manifest.json"
        
        if os.path.exists(local_file):
            with open(local_file, 'r') as f:
                return json.load(f)
        
        # Create default manifest
        default_manifest = {
            "latest_commit_hash_project1": "unknown",
            "latest_commit_hash_project2": "unknown", 
            "core_library_version": "1.0.0",
            "schema_version": "1.0.0",
            "daily_credits_project1": 0,
            "daily_credits_project2": 0,
            "daily_limit_project1": 300000,
            "daily_limit_project2": 300000,
            "last_reset_date": str(date.today()),
            "project1_last_update": datetime.now().isoformat(),
            "project2_last_update": datetime.now().isoformat()
        }
        
        with open(local_file, 'w') as f:
            json.dump(default_manifest, f, indent=2)
        
        return default_manifest
    
    def _create_initial_manifest(self) -> Dict[str, Any]:
        """Create initial manifest in database"""
        initial_data = {
            "latest_commit_hash_project1": "initial",
            "latest_commit_hash_project2": "initial",
            "core_library_version": "1.0.0", 
            "schema_version": "1.0.0",
            "daily_credits_project1": 0,
            "daily_credits_project2": 0,
            "daily_limit_project1": 300000,
            "daily_limit_project2": 300000
        }
        
        try:
            response = self.supabase_client.table('system_manifest').insert(initial_data).execute()
            return response.data[0] if response.data else initial_data
        except Exception as e:
            print(f"❌ Error creating initial manifest: {e}")
            return initial_data
    
    def update_project_status(self, credits_used: int = 0) -> bool:
        """Update this project's status in the manifest"""
        manifest = self.get_manifest()
        if not manifest:
            return False
        
        # Determine which project fields to update
        if self.project_name == "smart_layer":
            update_data = {
                "latest_commit_hash_project1": self.current_commit,
                "daily_credits_project1": manifest.get("daily_credits_project1", 0) + credits_used,
                "project1_last_update": datetime.now().isoformat()
            }
        else:  # manus_origin
            update_data = {
                "latest_commit_hash_project2": self.current_commit,
                "daily_credits_project2": manifest.get("daily_credits_project2", 0) + credits_used,
                "project2_last_update": datetime.now().isoformat()
            }
        
        return self._update_manifest(update_data)
    
    def _update_manifest(self, update_data: Dict[str, Any]) -> bool:
        """Update manifest with new data"""
        if not self.supabase_client:
            return self._update_local_manifest(update_data)
        
        try:
            # Reset daily credits if it's a new day
            self._reset_daily_credits_if_needed()
            
            response = self.supabase_client.table('system_manifest').update(update_data).eq('id', 1).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"❌ Error updating manifest: {e}")
            return self._update_local_manifest(update_data)
    
    def _update_local_manifest(self, update_data: Dict[str, Any]) -> bool:
        """Update local manifest file"""
        try:
            manifest = self._get_local_manifest()
            manifest.update(update_data)
            
            with open("shared_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Error updating local manifest: {e}")
            return False
    
    def _reset_daily_credits_if_needed(self):
        """Reset daily credits if it's a new day"""
        if not self.supabase_client:
            return
        
        try:
            # Call the database function to reset credits
            self.supabase_client.rpc('reset_daily_credits').execute()
        except Exception as e:
            print(f"⚠️ Could not reset daily credits: {e}")
    
    def get_project_status(self, project_name: str = None) -> Optional[ProjectStatus]:
        """Get status for a specific project"""
        if not project_name:
            project_name = self.project_name
        
        manifest = self.get_manifest()
        if not manifest:
            return None
        
        if project_name == "smart_layer":
            return ProjectStatus(
                project_name="smart_layer",
                commit_hash=manifest.get("latest_commit_hash_project1", "unknown"),
                daily_credits=manifest.get("daily_credits_project1", 0),
                daily_limit=manifest.get("daily_limit_project1", 300000),
                last_update=datetime.fromisoformat(manifest.get("project1_last_update", datetime.now().isoformat()))
            )
        else:  # manus_origin
            return ProjectStatus(
                project_name="manus_origin",
                commit_hash=manifest.get("latest_commit_hash_project2", "unknown"),
                daily_credits=manifest.get("daily_credits_project2", 0),
                daily_limit=manifest.get("daily_limit_project2", 300000),
                last_update=datetime.fromisoformat(manifest.get("project2_last_update", datetime.now().isoformat()))
            )
    
    def get_both_projects_status(self) -> Dict[str, ProjectStatus]:
        """Get status for both projects"""
        return {
            "smart_layer": self.get_project_status("smart_layer"),
            "manus_origin": self.get_project_status("manus_origin")
        }
    
    def check_credit_availability(self, estimated_cost: int) -> Dict[str, Any]:
        """Check if credits are available for an operation"""
        status = self.get_project_status()
        if not status:
            return {"allowed": False, "reason": "Cannot get project status"}
        
        if status.remaining_credits < estimated_cost:
            return {
                "allowed": False,
                "reason": f"Insufficient credits. Need {estimated_cost}, have {status.remaining_credits}",
                "remaining": status.remaining_credits,
                "usage_percent": status.usage_percentage
            }
        
        # Warn if usage is high
        if status.usage_percentage > 80:
            return {
                "allowed": True,
                "warning": f"High credit usage: {status.usage_percentage:.1f}%",
                "remaining": status.remaining_credits,
                "usage_percent": status.usage_percentage
            }
        
        return {
            "allowed": True,
            "remaining": status.remaining_credits,
            "usage_percent": status.usage_percentage
        }
    
    def log_communication(self, to_project: str, message_type: str, title: str, content: str, metadata: Dict = None):
        """Log communication to the other project"""
        if not self.supabase_client:
            return False
        
        try:
            comm_data = {
                "from_project": self.project_name,
                "to_project": to_project,
                "message_type": message_type,
                "title": title,
                "content": content,
                "metadata": metadata or {}
            }
            
            response = self.supabase_client.table('communication_log').insert(comm_data).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"❌ Error logging communication: {e}")
            return False
    
    def get_unread_communications(self) -> List[Dict[str, Any]]:
        """Get unread communications for this project"""
        if not self.supabase_client:
            return []
        
        try:
            response = self.supabase_client.table('communication_log').select('*').eq('to_project', self.project_name).eq('read_status', False).order('created_at', desc=True).execute()
            
            return response.data or []
            
        except Exception as e:
            print(f"❌ Error getting communications: {e}")
            return []
    
    def mark_communication_read(self, comm_id: int) -> bool:
        """Mark a communication as read"""
        if not self.supabase_client:
            return False
        
        try:
            response = self.supabase_client.table('communication_log').update({"read_status": True}).eq('id', comm_id).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"❌ Error marking communication read: {e}")
            return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        both_status = self.get_both_projects_status()
        manifest = self.get_manifest()
        
        if not both_status["smart_layer"] or not both_status["manus_origin"]:
            return {"status": "error", "message": "Cannot get project status"}
        
        total_credits = both_status["smart_layer"].daily_credits + both_status["manus_origin"].daily_credits
        total_limit = both_status["smart_layer"].daily_limit + both_status["manus_origin"].daily_limit
        combined_usage = (total_credits / total_limit) * 100 if total_limit > 0 else 0
        
        # Determine health status
        if combined_usage > 90:
            status = "critical"
        elif combined_usage > 75:
            status = "warning"
        elif combined_usage > 50:
            status = "caution"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "combined_usage_percent": combined_usage,
            "total_credits_used": total_credits,
            "total_limit": total_limit,
            "projects": {
                "smart_layer": {
                    "usage_percent": both_status["smart_layer"].usage_percentage,
                    "remaining": both_status["smart_layer"].remaining_credits,
                    "last_update": both_status["smart_layer"].last_update.isoformat()
                },
                "manus_origin": {
                    "usage_percent": both_status["manus_origin"].usage_percentage,
                    "remaining": both_status["manus_origin"].remaining_credits,
                    "last_update": both_status["manus_origin"].last_update.isoformat()
                }
            },
            "core_library_version": manifest.get("core_library_version", "unknown"),
            "schema_version": manifest.get("schema_version", "unknown")
        }

# Convenience functions for easy import
def get_manifest_client(project_name: str = "smart_layer") -> ManifestClient:
    """Get a manifest client instance"""
    return ManifestClient(project_name)

def check_credits_before_operation(estimated_cost: int, project_name: str = "smart_layer") -> bool:
    """Quick check if credits are available for an operation"""
    client = get_manifest_client(project_name)
    result = client.check_credit_availability(estimated_cost)
    
    if not result["allowed"]:
        print(f"❌ {result['reason']}")
        return False
    
    if "warning" in result:
        print(f"⚠️ {result['warning']}")
    
    return True

def update_credits_after_operation(credits_used: int, project_name: str = "smart_layer") -> bool:
    """Update credits after an operation"""
    client = get_manifest_client(project_name)
    return client.update_project_status(credits_used)

def get_system_status() -> Dict[str, Any]:
    """Get overall system status"""
    client = get_manifest_client()
    return client.get_system_health()

if __name__ == "__main__":
    # Test the manifest client
    client = get_manifest_client()
    
    print("🔍 Testing Manifest Client...")
    
    # Get current status
    status = client.get_system_health()
    print(f"System Status: {status['status']}")
    print(f"Combined Usage: {status['combined_usage_percent']:.1f}%")
    
    # Test credit check
    credit_check = client.check_credit_availability(1000)
    print(f"Credit Check (1000T): {'✅' if credit_check['allowed'] else '❌'}")
    
    # Get both projects status
    both_status = client.get_both_projects_status()
    for project, proj_status in both_status.items():
        if proj_status:
            print(f"{project}: {proj_status.usage_percentage:.1f}% used, {proj_status.remaining_credits} remaining")
    
    print("✅ Manifest client test complete")

