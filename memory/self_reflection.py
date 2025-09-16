#!/usr/bin/env python3

import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
import csv

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from memory.trajectory_tracker import get_tracker, TrajectoryTracker
    from memory.supabase_client import get_client
except ImportError as e:
    print(f"Warning: Import error: {e}")

class SelfReflectionEngine:
    """Handles AI self-reflection and continuous improvement"""
    
    def __init__(self):
        self.reflection_log_path = "/home/ubuntu/my_manus_knowledge/logs/self_reflection.csv"
        self.insights_path = "/home/ubuntu/my_manus_knowledge/logs/insights.json"
        self.performance_history = []
        
    def conduct_reflection(self, time_period_hours: int = 24) -> Dict[str, Any]:
        """Conduct a comprehensive self-reflection session"""
        
        reflection_data = {
            "timestamp": int(time.time()),
            "period_hours": time_period_hours,
            "reflection_id": f"reflection_{int(time.time())}",
            "insights": {},
            "action_items": [],
            "performance_score": 0.0
        }
        
        # Analyze trajectory data
        tracker = get_tracker()
        performance_analysis = tracker.analyze_performance_trends()
        
        # Generate insights based on performance
        insights = self._generate_insights(performance_analysis)
        reflection_data["insights"] = insights
        
        # Create action items for improvement
        action_items = self._create_action_items(insights, performance_analysis)
        reflection_data["action_items"] = action_items
        
        # Calculate overall performance score
        performance_score = self._calculate_performance_score(performance_analysis)
        reflection_data["performance_score"] = performance_score
        
        # Log reflection
        self._log_reflection(reflection_data)
        
        # Generate reflection report
        report = self._generate_reflection_report(reflection_data)
        
        return {
            "reflection_data": reflection_data,
            "report": report,
            "recommendations": self._generate_recommendations(reflection_data)
        }
    
    def _generate_insights(self, performance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from performance analysis"""
        insights = {}
        
        if "action_statistics" in performance_analysis:
            # Analyze action efficiency
            action_stats = performance_analysis["action_statistics"]
            most_efficient_action = None
            least_efficient_action = None
            best_efficiency = 0
            worst_efficiency = float('inf')
            
            for action, stats in action_stats.items():
                efficiency = stats["avg_score"] / max(stats["avg_tokens"], 1)
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    most_efficient_action = action
                if efficiency < worst_efficiency:
                    worst_efficiency = efficiency
                    least_efficient_action = action
            
            insights["action_efficiency"] = {
                "most_efficient": most_efficient_action,
                "least_efficient": least_efficient_action,
                "efficiency_ratio": best_efficiency / max(worst_efficiency, 0.001)
            }
        
        # Credit efficiency insights
        if "credit_efficiency" in performance_analysis:
            credit_eff = performance_analysis["credit_efficiency"]
            insights["credit_management"] = {
                "efficiency_score": credit_eff,
                "status": "excellent" if credit_eff > 0.8 else "good" if credit_eff > 0.6 else "needs_improvement",
                "total_tokens": performance_analysis.get("total_tokens_used", 0)
            }
        
        # Task completion insights
        if "average_score" in performance_analysis:
            avg_score = performance_analysis["average_score"]
            insights["task_performance"] = {
                "average_score": avg_score,
                "performance_level": "excellent" if avg_score > 0.8 else "good" if avg_score > 0.6 else "needs_improvement",
                "total_actions": performance_analysis.get("total_actions", 0)
            }
        
        return insights
    
    def _create_action_items(self, insights: Dict[str, Any], performance_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create actionable improvement items"""
        action_items = []
        
        # Credit efficiency improvements
        if "credit_management" in insights:
            credit_info = insights["credit_management"]
            if credit_info["status"] == "needs_improvement":
                action_items.append({
                    "priority": "high",
                    "category": "credit_efficiency",
                    "action": "Optimize token usage by implementing better caching and reducing redundant API calls",
                    "target_metric": "credit_efficiency",
                    "target_value": 0.8
                })
        
        # Task performance improvements
        if "task_performance" in insights:
            task_info = insights["task_performance"]
            if task_info["performance_level"] == "needs_improvement":
                action_items.append({
                    "priority": "medium",
                    "category": "task_quality",
                    "action": "Improve task completion strategies and error handling",
                    "target_metric": "average_score",
                    "target_value": 0.8
                })
        
        # Action efficiency improvements
        if "action_efficiency" in insights:
            eff_info = insights["action_efficiency"]
            if eff_info["least_efficient"]:
                action_items.append({
                    "priority": "medium",
                    "category": "action_optimization",
                    "action": f"Optimize {eff_info['least_efficient']} action for better token efficiency",
                    "target_metric": "action_efficiency",
                    "target_value": eff_info["efficiency_ratio"] * 1.2
                })
        
        return action_items
    
    def _calculate_performance_score(self, performance_analysis: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        scores = []
        weights = []
        
        # Credit efficiency (40% weight)
        if "credit_efficiency" in performance_analysis:
            scores.append(performance_analysis["credit_efficiency"])
            weights.append(0.4)
        
        # Task completion (40% weight)
        if "average_score" in performance_analysis:
            scores.append(performance_analysis["average_score"])
            weights.append(0.4)
        
        # Activity level (20% weight) - based on number of actions
        if "total_actions" in performance_analysis:
            activity_score = min(1.0, performance_analysis["total_actions"] / 10)  # Normalize to 10 actions
            scores.append(activity_score)
            weights.append(0.2)
        
        if not scores:
            return 0.0
        
        # Calculate weighted average
        total_weight = sum(weights)
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        
        return weighted_sum / total_weight
    
    def _log_reflection(self, reflection_data: Dict[str, Any]):
        """Log reflection data to CSV and Supabase"""
        
        # Log to CSV
        try:
            file_exists = os.path.exists(self.reflection_log_path)
            with open(self.reflection_log_path, 'a', newline='') as csvfile:
                fieldnames = ['timestamp', 'reflection_id', 'performance_score', 'insights', 'action_items']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow({
                    'timestamp': reflection_data['timestamp'],
                    'reflection_id': reflection_data['reflection_id'],
                    'performance_score': reflection_data['performance_score'],
                    'insights': json.dumps(reflection_data['insights']),
                    'action_items': json.dumps(reflection_data['action_items'])
                })
                
        except Exception as e:
            print(f"❌ Error logging reflection to CSV: {e}")
        
        # Try to log to Supabase
        try:
            supabase = get_client()
            supabase.table("self_reflection").insert({
                "reflection_text": f"Reflection {reflection_data['reflection_id']}",
                "insights": reflection_data['insights'],
                "action_items": reflection_data['action_items'],
                "performance_score": reflection_data['performance_score'],
                "timestamp": reflection_data['timestamp']
            }).execute()
            
        except Exception as e:
            print(f"❌ Error logging reflection to Supabase: {e}")
    
    def _generate_reflection_report(self, reflection_data: Dict[str, Any]) -> str:
        """Generate a human-readable reflection report"""
        
        timestamp = datetime.fromtimestamp(reflection_data['timestamp'])
        score = reflection_data['performance_score']
        insights = reflection_data['insights']
        action_items = reflection_data['action_items']
        
        report = f"""
# Self-Reflection Report
**Date:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Overall Performance Score:** {score:.2f}/1.00

## Key Insights

"""
        
        # Add insights
        for category, insight in insights.items():
            report += f"### {category.replace('_', ' ').title()}\n"
            if isinstance(insight, dict):
                for key, value in insight.items():
                    report += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            else:
                report += f"- {insight}\n"
            report += "\n"
        
        # Add action items
        if action_items:
            report += "## Action Items\n\n"
            for i, item in enumerate(action_items, 1):
                report += f"{i}. **{item['category'].replace('_', ' ').title()}** ({item['priority']} priority)\n"
                report += f"   - Action: {item['action']}\n"
                report += f"   - Target: {item['target_metric']} = {item['target_value']}\n\n"
        
        return report
    
    def _generate_recommendations(self, reflection_data: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations for improvement"""
        recommendations = []
        
        score = reflection_data['performance_score']
        insights = reflection_data['insights']
        
        if score < 0.6:
            recommendations.append("Consider implementing more aggressive caching strategies to improve credit efficiency")
            recommendations.append("Review and optimize the most token-intensive operations")
        
        if "credit_management" in insights:
            credit_info = insights["credit_management"]
            if credit_info["status"] == "needs_improvement":
                recommendations.append("Implement request batching to reduce API call overhead")
                recommendations.append("Add more intelligent caching for frequently accessed data")
        
        if "task_performance" in insights:
            task_info = insights["task_performance"]
            if task_info["performance_level"] == "needs_improvement":
                recommendations.append("Implement better error handling and retry mechanisms")
                recommendations.append("Add more comprehensive input validation")
        
        return recommendations
    
    def get_reflection_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent reflection history"""
        reflections = []
        
        try:
            with open(self.reflection_log_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    reflections.append({
                        'timestamp': int(row['timestamp']),
                        'reflection_id': row['reflection_id'],
                        'performance_score': float(row['performance_score']),
                        'insights': json.loads(row['insights']),
                        'action_items': json.loads(row['action_items'])
                    })
            
            # Sort by timestamp and return most recent
            reflections.sort(key=lambda x: x['timestamp'], reverse=True)
            return reflections[:limit]
            
        except Exception as e:
            print(f"❌ Error reading reflection history: {e}")
            return []

# Global reflection engine instance
_global_reflection_engine = None

def get_reflection_engine() -> SelfReflectionEngine:
    """Get or create global reflection engine"""
    global _global_reflection_engine
    if _global_reflection_engine is None:
        _global_reflection_engine = SelfReflectionEngine()
    return _global_reflection_engine

def conduct_daily_reflection() -> Dict[str, Any]:
    """Convenience function for daily reflection"""
    engine = get_reflection_engine()
    return engine.conduct_reflection(24)

# Example usage and testing
if __name__ == "__main__":
    # Test the self-reflection engine
    engine = SelfReflectionEngine()
    
    print("Conducting self-reflection...")
    result = engine.conduct_reflection(24)
    
    print(f"Performance Score: {result['reflection_data']['performance_score']:.2f}")
    print(f"Number of insights: {len(result['reflection_data']['insights'])}")
    print(f"Number of action items: {len(result['reflection_data']['action_items'])}")
    
    print("\nReflection Report:")
    print(result['report'])
    
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"- {rec}")

