#!/usr/bin/env python3

"""
Manus AI Smart Layer - Main System Orchestrator

This module provides a unified interface for the entire self-improving,
credit-efficient personal management system.
"""

import json
import time
import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from memory.router import call_r1, spend
    from memory.trajectory_tracker import get_tracker, log_action
    from memory.self_reflection import get_reflection_engine, conduct_daily_reflection
    from memory.learning_integration import get_learning_integration, enhanced_call_r1
    from memory.supabase_client import get_client
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")

class ManusSmartLayer:
    """Main orchestrator for the Manus AI Smart Layer system"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"smart_layer_{int(time.time())}"
        self.start_time = time.time()
        self.version = "1.0.0"
        self.credit_limit_daily = 300000  # 300K tokens per day
        self.credit_warning_threshold = 0.8  # Warn at 80% usage
        
        # Initialize components
        self.tracker = get_tracker(self.session_id)
        self.reflection_engine = get_reflection_engine()
        self.learning_integration = get_learning_integration()
        
        print(f"🚀 Manus AI Smart Layer v{self.version} initialized")
        print(f"📊 Session ID: {self.session_id}")
        
    def smart_call(self, prompt: str, model: str = "deepseek-r1", **kwargs) -> Dict[str, Any]:
        """
        Enhanced LLM call with full smart layer capabilities:
        - Credit management and tracking
        - Trajectory logging
        - Performance scoring
        - Automatic reflection triggers
        """
        
        # Check credit limits before making call
        if not self._check_credit_limits():
            raise Exception("Daily credit limit exceeded. Please wait for reset or optimize usage.")
        
        try:
            # Use enhanced call with learning integration
            result = enhanced_call_r1(prompt, model, **kwargs)
            
            # Log successful smart call
            self._log_smart_action("smart_call", {
                "prompt_length": len(prompt),
                "model": model
            }, {
                "success": True,
                "result_available": True
            }, score=1.0)
            
            return result
            
        except Exception as e:
            # Log failed smart call
            self._log_smart_action("smart_call_failed", {
                "prompt_length": len(prompt),
                "model": model,
                "error": str(e)
            }, {
                "success": False,
                "error_type": type(e).__name__
            }, score=0.0)
            
            raise e
    
    def _check_credit_limits(self) -> bool:
        """Check if we're within daily credit limits"""
        try:
            # Read current credit usage from cost.csv
            cost_file = "/home/ubuntu/my_manus_knowledge/logs/cost.csv"
            if not os.path.exists(cost_file):
                return True
            
            today = datetime.now().strftime("%Y-%m-%d")
            daily_usage = 0
            
            with open(cost_file, 'r') as f:
                lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        date_str = parts[0][:10]  # Extract date part
                        if date_str == today:
                            try:
                                tokens = int(parts[2])
                                daily_usage += tokens
                            except ValueError:
                                continue
            
            usage_ratio = daily_usage / self.credit_limit_daily
            
            if usage_ratio >= 1.0:
                print(f"❌ Daily credit limit exceeded: {daily_usage}/{self.credit_limit_daily} tokens")
                return False
            elif usage_ratio >= self.credit_warning_threshold:
                print(f"⚠️ Credit warning: {daily_usage}/{self.credit_limit_daily} tokens ({usage_ratio:.1%} used)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking credit limits: {e}")
            return True  # Allow operation if check fails
    
    def _log_smart_action(self, action: str, input_data: Dict[str, Any], 
                         output_data: Dict[str, Any], score: float = 0.0):
        """Log an action with smart layer metadata"""
        log_action(
            action=action,
            input_data=input_data,
            output_data=output_data,
            cost_tokens=0,
            score=score,
            metadata={
                "smart_layer_version": self.version,
                "session_id": self.session_id,
                "timestamp": time.time()
            }
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        # Get learning stats
        learning_stats = self.learning_integration.get_learning_stats()
        
        # Get trajectory analysis
        performance_analysis = self.tracker.analyze_performance_trends()
        
        # Get recent reflections
        recent_reflections = self.reflection_engine.get_reflection_history(3)
        
        # Calculate session metrics
        session_duration = time.time() - self.start_time
        
        # Check credit status
        credit_status = self._get_credit_status()
        
        return {
            "system_info": {
                "version": self.version,
                "session_id": self.session_id,
                "uptime_minutes": session_duration / 60,
                "status": "operational"
            },
            "credit_management": credit_status,
            "performance": performance_analysis,
            "learning": {
                "trajectory_length": learning_stats["current_trajectory_length"],
                "recent_reflections_count": len(recent_reflections),
                "next_reflection_minutes": learning_stats["next_reflection_in_minutes"]
            },
            "recent_reflections": recent_reflections[:2] if recent_reflections else []
        }
    
    def _get_credit_status(self) -> Dict[str, Any]:
        """Get current credit usage status"""
        try:
            cost_file = "/home/ubuntu/my_manus_knowledge/logs/cost.csv"
            if not os.path.exists(cost_file):
                return {"status": "no_data", "daily_usage": 0, "limit": self.credit_limit_daily}
            
            today = datetime.now().strftime("%Y-%m-%d")
            daily_usage = 0
            
            with open(cost_file, 'r') as f:
                lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        date_str = parts[0][:10]
                        if date_str == today:
                            try:
                                tokens = int(parts[2])
                                daily_usage += tokens
                            except ValueError:
                                continue
            
            usage_ratio = daily_usage / self.credit_limit_daily
            
            status = "healthy"
            if usage_ratio >= 1.0:
                status = "limit_exceeded"
            elif usage_ratio >= self.credit_warning_threshold:
                status = "warning"
            
            return {
                "status": status,
                "daily_usage": daily_usage,
                "limit": self.credit_limit_daily,
                "usage_ratio": usage_ratio,
                "remaining": self.credit_limit_daily - daily_usage
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def force_reflection(self) -> Dict[str, Any]:
        """Force a self-reflection session"""
        print("🤔 Forcing self-reflection session...")
        
        try:
            result = conduct_daily_reflection()
            
            # Log the forced reflection
            self._log_smart_action("forced_reflection", {
                "trigger": "manual"
            }, {
                "performance_score": result['reflection_data']['performance_score'],
                "insights_count": len(result['reflection_data']['insights']),
                "action_items_count": len(result['reflection_data']['action_items'])
            }, score=result['reflection_data']['performance_score'])
            
            print(f"✅ Reflection completed. Score: {result['reflection_data']['performance_score']:.2f}")
            
            return result
            
        except Exception as e:
            print(f"❌ Reflection failed: {e}")
            return {"error": str(e)}
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Run performance optimization based on recent reflections"""
        
        print("🔧 Running performance optimization...")
        
        # Get recent reflections for optimization insights
        recent_reflections = self.reflection_engine.get_reflection_history(5)
        
        optimization_actions = []
        
        if recent_reflections:
            latest_reflection = recent_reflections[0]
            action_items = latest_reflection.get('action_items', [])
            
            for item in action_items:
                if item['priority'] == 'high':
                    optimization_actions.append({
                        "action": item['action'],
                        "category": item['category'],
                        "implemented": False  # Would implement actual optimizations here
                    })
        
        # Log optimization attempt
        self._log_smart_action("performance_optimization", {
            "reflections_analyzed": len(recent_reflections),
            "action_items_found": len(optimization_actions)
        }, {
            "optimizations_planned": len(optimization_actions),
            "success": True
        }, score=0.8)
        
        return {
            "optimization_actions": optimization_actions,
            "reflections_analyzed": len(recent_reflections),
            "timestamp": time.time()
        }
    
    def export_session_data(self, format: str = "json") -> str:
        """Export current session data"""
        
        session_data = {
            "session_info": {
                "session_id": self.session_id,
                "start_time": self.start_time,
                "duration_minutes": (time.time() - self.start_time) / 60,
                "version": self.version
            },
            "system_status": self.get_system_status(),
            "trajectory_data": self.tracker.get_recent_trajectories(50),
            "reflection_history": self.reflection_engine.get_reflection_history(10)
        }
        
        if format == "json":
            filename = f"/home/ubuntu/my_manus_knowledge/exports/session_{self.session_id}.json"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            print(f"📁 Session data exported to: {filename}")
            return filename
        
        return json.dumps(session_data, indent=2)

# Global smart layer instance
_global_smart_layer = None

def get_smart_layer(session_id: Optional[str] = None) -> ManusSmartLayer:
    """Get or create global smart layer instance"""
    global _global_smart_layer
    if _global_smart_layer is None or (session_id and _global_smart_layer.session_id != session_id):
        _global_smart_layer = ManusSmartLayer(session_id)
    return _global_smart_layer

def smart_call(prompt: str, model: str = "deepseek-r1", **kwargs) -> Dict[str, Any]:
    """Convenience function for smart LLM calls"""
    smart_layer = get_smart_layer()
    return smart_layer.smart_call(prompt, model, **kwargs)

# Example usage and testing
if __name__ == "__main__":
    # Test the smart layer system
    smart_layer = ManusSmartLayer("test_session")
    
    print("\n📊 System Status:")
    status = smart_layer.get_system_status()
    print(json.dumps(status, indent=2))
    
    print("\n🔧 Running optimization:")
    optimization = smart_layer.optimize_performance()
    print(json.dumps(optimization, indent=2))
    
    print("\n🤔 Forcing reflection:")
    reflection = smart_layer.force_reflection()
    if "error" not in reflection:
        print(f"Reflection score: {reflection['reflection_data']['performance_score']:.2f}")
    
    print("\n📁 Exporting session data:")
    export_path = smart_layer.export_session_data()
    
    print("\n✅ Smart layer test completed")

