#!/usr/bin/env python3

"""
Automated Idea Management System

Inspired by the manus_origin project's blueprint update mechanism and 
deferred idea management, this system provides structured idea ingestion,
processing, and integration into the project blueprint.
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Import from manus_core
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'manus_core'))

from manus_core.db.client import get_shared_client
from manus_core.cache.manager import get_cache_manager
from manus_core.routing.coordinator import get_coordinator
from manus_core.config import get_config

@dataclass
class Idea:
    """Represents a single idea in the system"""
    id: str
    title: str
    description: str
    category: str  # 'optimization', 'feature', 'bug_fix', 'research', 'infrastructure'
    priority: str  # 'low', 'medium', 'high', 'critical'
    status: str    # 'new', 'processing', 'approved', 'implemented', 'rejected', 'deferred'
    source: str    # 'user_input', 'brother_project', 'self_reflection', 'automated_analysis'
    created_at: datetime
    updated_at: datetime
    estimated_effort: int  # Hours
    estimated_impact: float  # 0.0 to 1.0
    dependencies: List[str]  # List of idea IDs this depends on
    tags: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Idea':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

class IdeaManager:
    """Manages the automated idea processing system"""
    
    def __init__(self, project_name: str = "smart_layer"):
        self.project_name = project_name
        self.config = get_config()
        self.db_client = get_shared_client(project_name)
        self.cache = get_cache_manager(project_name)
        self.coordinator = get_coordinator(project_name)
        
        # Local storage paths
        self.ideas_dir = Path("ideas")
        self.ideas_dir.mkdir(exist_ok=True)
        
        self.blueprint_file = Path("system_blueprint_v2.md")
        self.deferred_ideas_file = Path("ideas/deferred_ideas.md")
        self.processed_ideas_file = Path("ideas/processed_ideas.json")
        
        # Processing settings
        self.auto_process_interval = 3600  # 1 hour
        self.last_auto_process = 0
        
    def submit_idea(self, title: str, description: str, category: str = "feature",
                   priority: str = "medium", source: str = "user_input",
                   tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Submit a new idea to the system"""
        try:
            # Generate unique ID
            idea_id = hashlib.md5(f"{title}_{description}_{time.time()}".encode()).hexdigest()[:12]
            
            # Create idea object
            idea = Idea(
                id=idea_id,
                title=title,
                description=description,
                category=category,
                priority=priority,
                status="new",
                source=source,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                estimated_effort=0,  # To be estimated during processing
                estimated_impact=0.0,  # To be estimated during processing
                dependencies=[],
                tags=tags or [],
                metadata=metadata or {}
            )
            
            # Store in database
            success = self.db_client.insert("ideas", idea.to_dict(), "shared")
            
            if success:
                # Cache for quick access
                self.cache.set(f"idea_{idea_id}", idea.to_dict(), namespace="ideas")
                
                # Log to local file as backup
                self._log_idea_locally(idea)
                
                print(f"💡 Submitted idea: {title} (ID: {idea_id})")
                
                # Send coordination message if high priority
                if priority in ["high", "critical"]:
                    self.coordinator.send_message(
                        to_project="manus_origin",
                        message_type="insight",
                        title=f"High Priority Idea: {title}",
                        content=f"New {priority} priority idea submitted: {description}",
                        priority="medium",
                        metadata={"idea_id": idea_id, "category": category}
                    )
                
                return idea_id
            else:
                print(f"❌ Failed to submit idea: {title}")
                return None
                
        except Exception as e:
            print(f"❌ Error submitting idea: {e}")
            return None
    
    def get_idea(self, idea_id: str) -> Optional[Idea]:
        """Retrieve an idea by ID"""
        try:
            # Check cache first
            cached = self.cache.get(f"idea_{idea_id}", namespace="ideas")
            if cached:
                return Idea.from_dict(cached)
            
            # Check database
            results = self.db_client.select(
                table="ideas",
                columns="*",
                filters={"id": idea_id},
                schema="shared",
                limit=1
            )
            
            if results:
                idea_data = results[0]
                idea = Idea.from_dict(idea_data)
                
                # Cache for future use
                self.cache.set(f"idea_{idea_id}", idea.to_dict(), namespace="ideas")
                
                return idea
            
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving idea {idea_id}: {e}")
            return None
    
    def list_ideas(self, status: str = None, category: str = None, 
                  priority: str = None, limit: int = 50) -> List[Idea]:
        """List ideas with optional filtering"""
        try:
            filters = {}
            if status:
                filters["status"] = status
            if category:
                filters["category"] = category
            if priority:
                filters["priority"] = priority
            
            results = self.db_client.select(
                table="ideas",
                columns="*",
                filters=filters,
                schema="shared",
                order_by="-created_at",
                limit=limit
            )
            
            ideas = []
            for result in results:
                try:
                    idea = Idea.from_dict(result)
                    ideas.append(idea)
                except Exception as e:
                    print(f"⚠️ Error parsing idea: {e}")
                    continue
            
            return ideas
            
        except Exception as e:
            print(f"❌ Error listing ideas: {e}")
            return []
    
    def process_idea(self, idea_id: str) -> bool:
        """Process a single idea through the evaluation pipeline"""
        try:
            idea = self.get_idea(idea_id)
            if not idea:
                print(f"❌ Idea {idea_id} not found")
                return False
            
            if idea.status != "new":
                print(f"⚠️ Idea {idea_id} already processed (status: {idea.status})")
                return True
            
            print(f"🔄 Processing idea: {idea.title}")
            
            # Update status to processing
            self.update_idea_status(idea_id, "processing")
            
            # Estimate effort and impact
            effort, impact = self._estimate_idea_metrics(idea)
            
            # Analyze dependencies
            dependencies = self._analyze_dependencies(idea)
            
            # Determine approval status
            approval_status = self._evaluate_idea_approval(idea, effort, impact)
            
            # Update idea with analysis results
            updates = {
                "estimated_effort": effort,
                "estimated_impact": impact,
                "dependencies": dependencies,
                "status": approval_status,
                "updated_at": datetime.now().isoformat()
            }
            
            success = self.db_client.update(
                table="ideas",
                data=updates,
                filters={"id": idea_id},
                schema="shared"
            )
            
            if success:
                # Clear cache to force refresh
                self.cache.delete(f"idea_{idea_id}", namespace="ideas")
                
                # Log processing result
                self._log_processing_result(idea, approval_status, effort, impact)
                
                # If approved, consider for blueprint integration
                if approval_status == "approved":
                    self._consider_blueprint_integration(idea)
                
                print(f"✅ Processed idea {idea_id}: {approval_status}")
                return True
            else:
                print(f"❌ Failed to update idea {idea_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error processing idea {idea_id}: {e}")
            return False
    
    def update_idea_status(self, idea_id: str, new_status: str) -> bool:
        """Update the status of an idea"""
        try:
            updates = {
                "status": new_status,
                "updated_at": datetime.now().isoformat()
            }
            
            success = self.db_client.update(
                table="ideas",
                data=updates,
                filters={"id": idea_id},
                schema="shared"
            )
            
            if success:
                # Clear cache
                self.cache.delete(f"idea_{idea_id}", namespace="ideas")
                print(f"📝 Updated idea {idea_id} status to: {new_status}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error updating idea status: {e}")
            return False
    
    def auto_process_ideas(self) -> Dict[str, Any]:
        """Automatically process new ideas"""
        try:
            current_time = time.time()
            
            # Check if it's time for auto-processing
            if current_time - self.last_auto_process < self.auto_process_interval:
                return {"skipped": True, "reason": "Too soon for auto-processing"}
            
            # Get new ideas
            new_ideas = self.list_ideas(status="new", limit=20)
            
            if not new_ideas:
                self.last_auto_process = current_time
                return {"processed": 0, "message": "No new ideas to process"}
            
            results = {
                "processed": 0,
                "approved": 0,
                "rejected": 0,
                "deferred": 0,
                "errors": 0
            }
            
            for idea in new_ideas:
                try:
                    if self.process_idea(idea.id):
                        results["processed"] += 1
                        
                        # Get updated status
                        updated_idea = self.get_idea(idea.id)
                        if updated_idea:
                            if updated_idea.status == "approved":
                                results["approved"] += 1
                            elif updated_idea.status == "rejected":
                                results["rejected"] += 1
                            elif updated_idea.status == "deferred":
                                results["deferred"] += 1
                    else:
                        results["errors"] += 1
                        
                except Exception as e:
                    print(f"⚠️ Error processing idea {idea.id}: {e}")
                    results["errors"] += 1
            
            self.last_auto_process = current_time
            
            # Send summary to brother project if significant activity
            if results["processed"] > 5:
                self.coordinator.send_message(
                    to_project="manus_origin",
                    message_type="insight",
                    title="Idea Processing Summary",
                    content=f"Processed {results['processed']} ideas: {results['approved']} approved, {results['rejected']} rejected, {results['deferred']} deferred",
                    priority="low",
                    metadata=results
                )
            
            return results
            
        except Exception as e:
            print(f"❌ Error in auto-processing: {e}")
            return {"error": str(e)}
    
    def _estimate_idea_metrics(self, idea: Idea) -> tuple[int, float]:
        """Estimate effort (hours) and impact (0.0-1.0) for an idea"""
        # Simple heuristic-based estimation
        # In a real system, this could use ML or more sophisticated analysis
        
        effort = 1  # Default 1 hour
        impact = 0.1  # Default low impact
        
        # Estimate based on category
        category_effort = {
            "bug_fix": 2,
            "optimization": 4,
            "feature": 8,
            "infrastructure": 16,
            "research": 12
        }
        
        category_impact = {
            "bug_fix": 0.3,
            "optimization": 0.6,
            "feature": 0.7,
            "infrastructure": 0.8,
            "research": 0.4
        }
        
        effort = category_effort.get(idea.category, effort)
        impact = category_impact.get(idea.category, impact)
        
        # Adjust based on priority
        priority_multipliers = {
            "low": 0.7,
            "medium": 1.0,
            "high": 1.3,
            "critical": 1.6
        }
        
        multiplier = priority_multipliers.get(idea.priority, 1.0)
        effort = int(effort * multiplier)
        impact = min(1.0, impact * multiplier)
        
        # Adjust based on description length (more detailed = potentially more complex)
        if len(idea.description) > 500:
            effort = int(effort * 1.2)
            impact = min(1.0, impact * 1.1)
        
        return effort, impact
    
    def _analyze_dependencies(self, idea: Idea) -> List[str]:
        """Analyze potential dependencies for an idea"""
        dependencies = []
        
        # Simple keyword-based dependency detection
        # In a real system, this could use NLP or knowledge graphs
        
        description_lower = idea.description.lower()
        
        # Check for infrastructure dependencies
        if any(keyword in description_lower for keyword in ["database", "schema", "migration"]):
            # Look for infrastructure ideas
            infra_ideas = self.list_ideas(category="infrastructure", status="approved")
            dependencies.extend([i.id for i in infra_ideas[:3]])
        
        # Check for feature dependencies
        if "api" in description_lower and idea.category != "infrastructure":
            # Look for API-related infrastructure
            api_ideas = self.list_ideas(category="infrastructure")
            api_ideas = [i for i in api_ideas if "api" in i.description.lower()]
            dependencies.extend([i.id for i in api_ideas[:2]])
        
        return dependencies
    
    def _evaluate_idea_approval(self, idea: Idea, effort: int, impact: float) -> str:
        """Evaluate whether an idea should be approved, rejected, or deferred"""
        
        # Calculate effort-to-impact ratio
        if effort == 0:
            ratio = 0
        else:
            ratio = impact / effort
        
        # Decision thresholds
        if ratio > 0.1 and impact > 0.5:
            return "approved"
        elif ratio < 0.02 or impact < 0.1:
            return "rejected"
        elif effort > 20:  # High effort ideas


            return "deferred"
        else:
            return "approved"
    
    def _consider_blueprint_integration(self, idea: Idea):
        """Consider integrating approved idea into system blueprint"""
        try:
            if not self.blueprint_file.exists():
                print(f"⚠️ Blueprint file not found: {self.blueprint_file}")
                return
            
            # Read current blueprint
            blueprint_content = self.blueprint_file.read_text()
            
            # Simple integration - add to appropriate section
            integration_section = self._determine_blueprint_section(idea)
            
            if integration_section:
                # Create integration note
                integration_note = f"""

### {idea.title} (Idea #{idea.id})

**Category:** {idea.category}  
**Priority:** {idea.priority}  
**Estimated Effort:** {idea.estimated_effort} hours  
**Estimated Impact:** {idea.estimated_impact:.2f}  

{idea.description}

**Implementation Status:** Approved for development  
**Dependencies:** {', '.join(idea.dependencies) if idea.dependencies else 'None'}  
**Tags:** {', '.join(idea.tags) if idea.tags else 'None'}  

---
"""
                
                # Find insertion point in blueprint
                section_marker = f"## {integration_section}"
                if section_marker in blueprint_content:
                    # Insert after section header
                    parts = blueprint_content.split(section_marker, 1)
                    if len(parts) == 2:
                        updated_content = parts[0] + section_marker + integration_note + parts[1]
                        
                        # Write updated blueprint
                        self.blueprint_file.write_text(updated_content)
                        print(f"📋 Integrated idea {idea.id} into blueprint section: {integration_section}")
                        
                        # Update idea status
                        self.update_idea_status(idea.id, "implemented")
                        
                        return
                
                print(f"⚠️ Could not find section '{integration_section}' in blueprint")
            else:
                print(f"⚠️ Could not determine blueprint section for idea {idea.id}")
                
        except Exception as e:
            print(f"❌ Error integrating idea into blueprint: {e}")
    
    def _determine_blueprint_section(self, idea: Idea) -> Optional[str]:
        """Determine which blueprint section an idea belongs to"""
        category_sections = {
            "infrastructure": "Infrastructure Components",
            "feature": "Core Features",
            "optimization": "Performance Optimizations",
            "bug_fix": "Bug Fixes and Improvements",
            "research": "Research and Development"
        }
        
        return category_sections.get(idea.category)
    
    def _log_idea_locally(self, idea: Idea):
        """Log idea to local file as backup"""
        try:
            log_file = self.ideas_dir / "idea_log.jsonl"
            
            with open(log_file, "a") as f:
                f.write(json.dumps(idea.to_dict()) + "\n")
                
        except Exception as e:
            print(f"⚠️ Could not log idea locally: {e}")
    
    def _log_processing_result(self, idea: Idea, status: str, effort: int, impact: float):
        """Log processing results"""
        try:
            result = {
                "idea_id": idea.id,
                "title": idea.title,
                "category": idea.category,
                "priority": idea.priority,
                "status": status,
                "effort": effort,
                "impact": impact,
                "processed_at": datetime.now().isoformat()
            }
            
            log_file = self.ideas_dir / "processing_log.jsonl"
            
            with open(log_file, "a") as f:
                f.write(json.dumps(result) + "\n")
                
        except Exception as e:
            print(f"⚠️ Could not log processing result: {e}")
    
    def generate_ideas_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report on ideas"""
        try:
            all_ideas = self.list_ideas(limit=1000)
            
            # Statistics
            stats = {
                "total": len(all_ideas),
                "by_status": {},
                "by_category": {},
                "by_priority": {},
                "by_source": {},
                "total_effort": 0,
                "average_impact": 0.0
            }
            
            for idea in all_ideas:
                # Count by status
                stats["by_status"][idea.status] = stats["by_status"].get(idea.status, 0) + 1
                
                # Count by category
                stats["by_category"][idea.category] = stats["by_category"].get(idea.category, 0) + 1
                
                # Count by priority
                stats["by_priority"][idea.priority] = stats["by_priority"].get(idea.priority, 0) + 1
                
                # Count by source
                stats["by_source"][idea.source] = stats["by_source"].get(idea.source, 0) + 1
                
                # Sum effort and impact
                stats["total_effort"] += idea.estimated_effort
                stats["average_impact"] += idea.estimated_impact
            
            if all_ideas:
                stats["average_impact"] /= len(all_ideas)
            
            # Recent activity
            recent_ideas = [i for i in all_ideas if (datetime.now() - i.created_at).days <= 7]
            stats["recent_activity"] = {
                "new_ideas_this_week": len(recent_ideas),
                "processed_this_week": len([i for i in recent_ideas if i.status != "new"])
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error generating ideas report: {e}")
            return {"error": str(e)}

def main():
    """Main function for testing the idea management system"""
    manager = IdeaManager()
    
    print("🚀 Testing Automated Idea Management System")
    print("=" * 50)
    
    # Test idea submission
    idea_id = manager.submit_idea(
        title="Implement Advanced Caching Layer",
        description="Add a multi-tier caching system with Redis backend and intelligent cache invalidation to improve system performance and reduce database load.",
        category="optimization",
        priority="high",
        tags=["performance", "caching", "redis"],
        metadata={"estimated_complexity": "medium"}
    )
    
    if idea_id:
        print(f"✅ Submitted test idea: {idea_id}")
        
        # Test idea processing
        if manager.process_idea(idea_id):
            print(f"✅ Processed test idea: {idea_id}")
            
            # Retrieve and display processed idea
            processed_idea = manager.get_idea(idea_id)
            if processed_idea:
                print(f"📋 Processed Idea Details:")
                print(f"   Status: {processed_idea.status}")
                print(f"   Effort: {processed_idea.estimated_effort} hours")
                print(f"   Impact: {processed_idea.estimated_impact:.2f}")
                print(f"   Dependencies: {processed_idea.dependencies}")
    
    # Test auto-processing
    print("\n🔄 Testing auto-processing...")
    results = manager.auto_process_ideas()
    print(f"📊 Auto-processing results: {results}")
    
    # Generate report
    print("\n📈 Generating ideas report...")
    report = manager.generate_ideas_report()
    print(f"📋 Ideas Report: {json.dumps(report, indent=2)}")
    
    print("\n✅ Automated Idea Management System test completed!")

if __name__ == "__main__":
    main()

