#!/usr/bin/env python3

"""
Project Coordination System

Manages coordination between both Manus AI projects through shared manifest,
communication protocols, and resource management.
"""

import time
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from ..config import get_config
from ..db.client import get_shared_client
from ..utils.credits import get_credit_manager

@dataclass
class CoordinationMessage:
    """Message for inter-project communication"""
    message_id: str
    from_project: str
    to_project: str
    message_type: str  # 'insight', 'warning', 'coordination', 'update', 'optimization'
    title: str
    content: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    metadata: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None

@dataclass
class ProjectStatus:
    """Status information for a project"""
    project_name: str
    commit_hash: str
    core_library_version: str
    daily_credits_used: int
    daily_credits_limit: int
    last_update: datetime
    health_score: float
    active_operations: int
    
    @property
    def credit_usage_percentage(self) -> float:
        """Calculate credit usage percentage"""
        return (self.daily_credits_used / self.daily_credits_limit) * 100 if self.daily_credits_limit > 0 else 0

class ProjectCoordinator:
    """Coordinates activities between both Manus AI projects"""
    
    def __init__(self, project_name: str = "smart_layer"):
        self.project_name = project_name
        self.other_project = "manus_origin" if project_name == "smart_layer" else "smart_layer"
        self.config = get_config()
        self.db_client = get_shared_client(project_name)
        self.credit_manager = get_credit_manager(project_name)
        
        # Coordination settings
        self.sync_interval = 300  # 5 minutes
        self.last_sync = 0
        self.coordination_enabled = True
        
    def update_project_status(self, commit_hash: str = None, health_score: float = None,
                            active_operations: int = None) -> bool:
        """Update this project's status in the shared manifest"""
        try:
            # Get current credit status
            credit_status = self.credit_manager.get_credit_status("system")
            
            # Prepare update data
            update_data = {
                f"latest_commit_hash_{'project1' if self.project_name == 'smart_layer' else 'project2'}": commit_hash or self._get_current_commit(),
                f"daily_credits_{'project1' if self.project_name == 'smart_layer' else 'project2'}": credit_status.get("used_today", 0),
                f"{'project1' if self.project_name == 'smart_layer' else 'project2'}_last_update": datetime.now().isoformat(),
                f"{'project1' if self.project_name == 'smart_layer' else 'project2'}_health_score": health_score or 0.8,
                f"{'project1' if self.project_name == 'smart_layer' else 'project2'}_active_operations": active_operations or 0
            }
            
            # Update manifest
            success = self.db_client.update(
                table="system_manifest",
                data=update_data,
                filters={"id": 1},
                schema="shared"
            )
            
            if success:
                self.last_sync = time.time()
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to update project status: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for both projects"""
        try:
            # Get manifest data
            manifest_data = self.db_client.select(
                table="system_manifest",
                columns="*",
                schema="shared",
                order_by="-updated_at",
                limit=1
            )
            
            if not manifest_data:
                return {"error": "No manifest data found"}
            
            manifest = manifest_data[0]
            
            # Parse project statuses
            smart_layer_status = ProjectStatus(
                project_name="smart_layer",
                commit_hash=manifest.get("latest_commit_hash_project1", "unknown"),
                core_library_version=manifest.get("core_library_version", "1.0.0"),
                daily_credits_used=manifest.get("daily_credits_project1", 0),
                daily_credits_limit=manifest.get("daily_limit_project1", 300000),
                last_update=datetime.fromisoformat(manifest.get("project1_last_update", datetime.now().isoformat())),
                health_score=manifest.get("project1_health_score", 0.0),
                active_operations=manifest.get("project1_active_operations", 0)
            )
            
            manus_origin_status = ProjectStatus(
                project_name="manus_origin",
                commit_hash=manifest.get("latest_commit_hash_project2", "unknown"),
                core_library_version=manifest.get("core_library_version", "1.0.0"),
                daily_credits_used=manifest.get("daily_credits_project2", 0),
                daily_credits_limit=manifest.get("daily_limit_project2", 300000),
                last_update=datetime.fromisoformat(manifest.get("project2_last_update", datetime.now().isoformat())),
                health_score=manifest.get("project2_health_score", 0.0),
                active_operations=manifest.get("project2_active_operations", 0)
            )
            
            # Calculate system-wide metrics
            total_credits_used = smart_layer_status.daily_credits_used + manus_origin_status.daily_credits_used
            total_credits_limit = smart_layer_status.daily_credits_limit + manus_origin_status.daily_credits_limit
            combined_usage = (total_credits_used / total_credits_limit) * 100 if total_credits_limit > 0 else 0
            
            # Determine system health
            avg_health = (smart_layer_status.health_score + manus_origin_status.health_score) / 2
            
            if combined_usage > 90 or avg_health < 0.3:
                system_health = "critical"
            elif combined_usage > 75 or avg_health < 0.5:
                system_health = "warning"
            elif combined_usage > 50 or avg_health < 0.7:
                system_health = "caution"
            else:
                system_health = "healthy"
            
            return {
                "system_health": system_health,
                "combined_credit_usage": combined_usage,
                "total_credits_used": total_credits_used,
                "total_credits_limit": total_credits_limit,
                "average_health_score": avg_health,
                "projects": {
                    "smart_layer": asdict(smart_layer_status),
                    "manus_origin": asdict(manus_origin_status)
                },
                "core_library_version": manifest.get("core_library_version", "1.0.0"),
                "schema_version": manifest.get("schema_version", "1.0.0"),
                "last_reset_date": manifest.get("last_reset_date"),
                "manifest_updated_at": manifest.get("updated_at")
            }
            
        except Exception as e:
            print(f"❌ Failed to get system status: {e}")
            return {"error": str(e)}
    
    def send_message(self, to_project: str, message_type: str, title: str, 
                    content: str, priority: str = "medium", 
                    metadata: Dict[str, Any] = None, expires_hours: int = 24) -> bool:
        """Send a coordination message to the other project"""
        try:
            message_id = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(hours=expires_hours)
            
            message_data = {
                "message_id": message_id,
                "from_project": self.project_name,
                "to_project": to_project,
                "message_type": message_type,
                "title": title,
                "content": content,
                "priority": priority,
                "metadata": metadata or {},
                "expires_at": expires_at.isoformat()
            }
            
            # Insert into communication log
            result = self.db_client.insert("communication_log", message_data, "shared")
            
            if result:
                print(f"📨 Sent {message_type} message to {to_project}: {title}")
                return True
            else:
                print(f"❌ Failed to send message to {to_project}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def get_unread_messages(self, limit: int = 50) -> List[CoordinationMessage]:
        """Get unread messages for this project"""
        try:
            messages_data = self.db_client.select(
                table="communication_log",
                columns="*",
                filters={
                    "to_project": self.project_name,
                    "read_status": False
                },
                schema="shared",
                order_by="-created_at",
                limit=limit
            )
            
            messages = []
            for msg_data in messages_data:
                try:
                    message = CoordinationMessage(
                        message_id=msg_data.get("message_id", ""),
                        from_project=msg_data.get("from_project", ""),
                        to_project=msg_data.get("to_project", ""),
                        message_type=msg_data.get("message_type", ""),
                        title=msg_data.get("title", ""),
                        content=msg_data.get("content", ""),
                        priority=msg_data.get("priority", "medium"),
                        metadata=msg_data.get("metadata", {}),
                        created_at=datetime.fromisoformat(msg_data.get("created_at", datetime.now().isoformat())),
                        expires_at=datetime.fromisoformat(msg_data.get("expires_at")) if msg_data.get("expires_at") else None
                    )
                    messages.append(message)
                except Exception as e:
                    print(f"⚠️ Error parsing message: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            print(f"❌ Error getting unread messages: {e}")
            return []
    
    def mark_message_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        try:
            success = self.db_client.update(
                table="communication_log",
                data={"read_status": True},
                filters={"message_id": message_id},
                schema="shared"
            )
            
            return success
            
        except Exception as e:
            print(f"❌ Error marking message read: {e}")
            return False
    
    def check_coordination_requirements(self) -> Dict[str, Any]:
        """Check if coordination is needed based on system status"""
        try:
            system_status = self.get_system_status()
            
            if "error" in system_status:
                return {"coordination_needed": False, "reason": "Cannot get system status"}
            
            coordination_needed = False
            reasons = []
            actions = []
            
            # Check credit usage
            combined_usage = system_status.get("combined_credit_usage", 0)
            if combined_usage > 80:
                coordination_needed = True
                reasons.append(f"High combined credit usage: {combined_usage:.1f}%")
                actions.append("coordinate_credit_usage")
            
            # Check health scores
            avg_health = system_status.get("average_health_score", 1.0)
            if avg_health < 0.6:
                coordination_needed = True
                reasons.append(f"Low average health score: {avg_health:.2f}")
                actions.append("coordinate_health_improvement")
            
            # Check if projects are out of sync
            projects = system_status.get("projects", {})
            smart_layer_update = projects.get("smart_layer", {}).get("last_update")
            manus_origin_update = projects.get("manus_origin", {}).get("last_update")
            
            if smart_layer_update and manus_origin_update:
                time_diff = abs((smart_layer_update - manus_origin_update).total_seconds())
                if time_diff > 3600:  # 1 hour
                    coordination_needed = True
                    reasons.append(f"Projects out of sync by {time_diff/3600:.1f} hours")
                    actions.append("coordinate_sync")
            
            # Check for unread critical messages
            unread_messages = self.get_unread_messages(10)
            critical_messages = [msg for msg in unread_messages if msg.priority == "critical"]
            if critical_messages:
                coordination_needed = True
                reasons.append(f"{len(critical_messages)} critical unread messages")
                actions.append("process_critical_messages")
            
            return {
                "coordination_needed": coordination_needed,
                "reasons": reasons,
                "suggested_actions": actions,
                "system_status": system_status,
                "unread_messages": len(unread_messages),
                "critical_messages": len(critical_messages)
            }
            
        except Exception as e:
            print(f"❌ Error checking coordination requirements: {e}")
            return {"coordination_needed": False, "error": str(e)}
    
    def coordinate_credit_usage(self) -> bool:
        """Coordinate credit usage between projects"""
        try:
            system_status = self.get_system_status()
            projects = system_status.get("projects", {})
            
            smart_layer_usage = projects.get("smart_layer", {}).get("credit_usage_percentage", 0)
            manus_origin_usage = projects.get("manus_origin", {}).get("credit_usage_percentage", 0)
            
            # Send coordination message if usage is imbalanced
            if abs(smart_layer_usage - manus_origin_usage) > 30:
                high_usage_project = "smart_layer" if smart_layer_usage > manus_origin_usage else "manus_origin"
                low_usage_project = "manus_origin" if high_usage_project == "smart_layer" else "smart_layer"
                
                message = f"Credit usage imbalance detected. {high_usage_project}: {smart_layer_usage if high_usage_project == 'smart_layer' else manus_origin_usage:.1f}%, {low_usage_project}: {manus_origin_usage if low_usage_project == 'manus_origin' else smart_layer_usage:.1f}%. Consider redistributing workload."
                
                return self.send_message(
                    to_project=self.other_project,
                    message_type="coordination",
                    title="Credit Usage Coordination",
                    content=message,
                    priority="high",
                    metadata={
                        "smart_layer_usage": smart_layer_usage,
                        "manus_origin_usage": manus_origin_usage,
                        "action": "redistribute_workload"
                    }
                )
            
            return True
            
        except Exception as e:
            print(f"❌ Error coordinating credit usage: {e}")
            return False
    
    def share_optimization_insight(self, insight_type: str, title: str, 
                                 description: str, implementation_code: str = None,
                                 estimated_savings: int = 0) -> bool:
        """Share an optimization insight with the other project"""
        try:
            insight_data = {
                "insight_type": insight_type,
                "title": title,
                "description": description,
                "implementation_code": implementation_code or "",
                "estimated_savings": estimated_savings,
                "source_project": self.project_name,
                "applied_by_project1": self.project_name == "smart_layer",
                "applied_by_project2": self.project_name == "manus_origin",
                "effectiveness_score": 0.0  # To be updated after application
            }
            
            # Insert into optimization insights
            result = self.db_client.insert("optimization_insights", insight_data, "shared")
            
            if result:
                # Send notification message
                self.send_message(
                    to_project=self.other_project,
                    message_type="optimization",
                    title=f"New Optimization: {title}",
                    content=f"Shared optimization insight: {description}",
                    priority="medium",
                    metadata={
                        "insight_type": insight_type,
                        "estimated_savings": estimated_savings,
                        "insight_id": result.get("id")
                    }
                )
                
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error sharing optimization insight: {e}")
            return False
    
    def _get_current_commit(self) -> str:
        """Get current Git commit hash"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                cwd="/home/ubuntu/my_manus_knowledge"
            )
            return result.stdout.strip()[:8] if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"
    
    def perform_coordination_cycle(self) -> Dict[str, Any]:
        """Perform a complete coordination cycle"""
        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "project": self.project_name,
                "actions_performed": [],
                "messages_processed": 0,
                "coordination_needed": False
            }
            
            # Update our project status
            status_updated = self.update_project_status()
            if status_updated:
                results["actions_performed"].append("updated_project_status")
            
            # Check coordination requirements
            coord_check = self.check_coordination_requirements()
            results["coordination_needed"] = coord_check.get("coordination_needed", False)
            
            if coord_check.get("coordination_needed"):
                # Perform suggested actions
                for action in coord_check.get("suggested_actions", []):
                    if action == "coordinate_credit_usage":
                        if self.coordinate_credit_usage():
                            results["actions_performed"].append("coordinated_credit_usage")
                    elif action == "process_critical_messages":
                        processed = self._process_critical_messages()
                        results["messages_processed"] += processed
                        results["actions_performed"].append(f"processed_{processed}_critical_messages")
            
            # Process unread messages
            unread_messages = self.get_unread_messages(10)
            for message in unread_messages:
                if self._process_message(message):
                    self.mark_message_read(message.message_id)
                    results["messages_processed"] += 1
            
            return results
            
        except Exception as e:
            print(f"❌ Error in coordination cycle: {e}")
            return {"error": str(e)}
    
    def _process_critical_messages(self) -> int:
        """Process critical messages"""
        unread_messages = self.get_unread_messages(50)
        critical_messages = [msg for msg in unread_messages if msg.priority == "critical"]
        
        processed = 0
        for message in critical_messages:
            if self._process_message(message):
                self.mark_message_read(message.message_id)
                processed += 1
        
        return processed
    
    def _process_message(self, message: CoordinationMessage) -> bool:
        """Process a coordination message"""
        try:
            print(f"📨 Processing {message.message_type} message from {message.from_project}: {message.title}")
            
            if message.message_type == "optimization":
                # Handle optimization insights
                insight_id = message.metadata.get("insight_id")
                if insight_id:
                    print(f"💡 Received optimization insight: {message.title}")
                    # Could implement automatic application of optimizations here
            
            elif message.message_type == "coordination":
                # Handle coordination requests
                action = message.metadata.get("action")
                if action == "redistribute_workload":
                    print(f"⚖️ Workload redistribution requested: {message.content}")
                    # Could implement workload redistribution logic here
            
            elif message.message_type == "warning":
                # Handle warnings
                print(f"⚠️ Warning from {message.from_project}: {message.content}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            return False

# Global coordinator instance
_coordinators = {}

def get_coordinator(project_name: str = "smart_layer") -> ProjectCoordinator:
    """Get a project coordinator instance"""
    if project_name not in _coordinators:
        _coordinators[project_name] = ProjectCoordinator(project_name)
    
    return _coordinators[project_name]

# Convenience functions
def update_project_status(commit_hash: str = None, health_score: float = None,
                         active_operations: int = None, project_name: str = "smart_layer") -> bool:
    """Update project status in manifest"""
    coordinator = get_coordinator(project_name)
    return coordinator.update_project_status(commit_hash, health_score, active_operations)

def get_system_status(project_name: str = "smart_layer") -> Dict[str, Any]:
    """Get system status for both projects"""
    coordinator = get_coordinator(project_name)
    return coordinator.get_system_status()

def send_coordination_message(to_project: str, message_type: str, title: str,
                            content: str, priority: str = "medium",
                            project_name: str = "smart_layer") -> bool:
    """Send coordination message to other project"""
    coordinator = get_coordinator(project_name)
    return coordinator.send_message(to_project, message_type, title, content, priority)

def perform_coordination_cycle(project_name: str = "smart_layer") -> Dict[str, Any]:
    """Perform coordination cycle"""
    coordinator = get_coordinator(project_name)
    return coordinator.perform_coordination_cycle()

if __name__ == "__main__":
    # Test coordination system
    coordinator = get_coordinator("test_project")
    
    print("🤝 Testing Project Coordination...")
    
    # Test status update
    status_updated = coordinator.update_project_status(health_score=0.85, active_operations=3)
    print(f"Status update: {'✅' if status_updated else '❌'}")
    
    # Test system status
    system_status = coordinator.get_system_status()
    if "error" not in system_status:
        print(f"System health: {system_status.get('system_health', 'unknown')}")
        print(f"Combined usage: {system_status.get('combined_credit_usage', 0):.1f}%")
    
    # Test coordination check
    coord_check = coordinator.check_coordination_requirements()
    print(f"Coordination needed: {coord_check.get('coordination_needed', False)}")
    
    # Test message sending
    message_sent = coordinator.send_message(
        to_project="manus_origin",
        message_type="test",
        title="Test Message",
        content="This is a test coordination message",
        priority="low"
    )
    print(f"Message sent: {'✅' if message_sent else '❌'}")
    
    print("✅ Coordination system test complete")

