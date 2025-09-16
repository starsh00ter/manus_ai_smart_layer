#!/usr/bin/env python3

import csv
import json
import time
import os
import uuid
import sys
from typing import Dict, Any, Optional, List

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from memory.supabase_client import get_client
except ImportError:
    print("Warning: Supabase client not available, using CSV-only mode")
    def get_client():
        raise Exception("Supabase not available")

class TrajectoryTracker:
    """Tracks AI decision-making processes and outcomes for recursive learning"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.csv_path = "/home/ubuntu/my_manus_knowledge/logs/trajectory.csv"
        self.current_trajectory = []
        
    def log_action(self, 
                   action: str, 
                   input_data: Dict[str, Any], 
                   output_data: Dict[str, Any], 
                   cost_tokens: int = 0, 
                   score: float = 0.0,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log an AI action with its inputs, outputs, and performance metrics"""
        
        timestamp = int(time.time())
        entry_id = str(uuid.uuid4())
        
        trajectory_entry = {
            "id": entry_id,
            "timestamp": timestamp,
            "session_id": self.session_id,
            "action": action,
            "input_data": input_data,
            "output_data": output_data,
            "cost_tokens": cost_tokens,
            "score": score,
            "metadata": metadata or {}
        }
        
        # Add to current trajectory
        self.current_trajectory.append(trajectory_entry)
        
        # Log to CSV file
        self._log_to_csv(trajectory_entry)
        
        # Try to log to Supabase (fallback to CSV if fails)
        self._log_to_supabase(trajectory_entry)
        
        return entry_id
    
    def _log_to_csv(self, entry: Dict[str, Any]):
        """Log trajectory entry to CSV file"""
        try:
            file_exists = os.path.exists(self.csv_path)
            with open(self.csv_path, 'a', newline='') as csvfile:
                fieldnames = ['timestamp', 'session_id', 'action', 'input_data', 
                             'output_data', 'cost_tokens', 'score', 'metadata']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow({
                    'timestamp': entry['timestamp'],
                    'session_id': entry['session_id'],
                    'action': entry['action'],
                    'input_data': json.dumps(entry['input_data']),
                    'output_data': json.dumps(entry['output_data']),
                    'cost_tokens': entry['cost_tokens'],
                    'score': entry['score'],
                    'metadata': json.dumps(entry['metadata'])
                })
                
        except Exception as e:
            print(f"❌ Error logging to CSV: {e}")
    
    def _log_to_supabase(self, entry: Dict[str, Any]):
        """Log trajectory entry to Supabase database"""
        try:
            supabase = get_client()
            supabase.table("trajectory").insert({
                "session_id": entry['session_id'],
                "action": entry['action'],
                "input_data": entry['input_data'],
                "output_data": entry['output_data'],
                "cost_tokens": entry['cost_tokens'],
                "score": entry['score'],
                "timestamp": entry['timestamp']
            }).execute()
            
        except Exception as e:
            print(f"❌ Error logging to Supabase: {e}")
    
    def score_trajectory(self, criteria: Dict[str, float]) -> float:
        """Score the current trajectory based on multiple criteria"""
        if not self.current_trajectory:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for criterion, weight in criteria.items():
            if criterion == "credit_efficiency":
                # Score based on tokens used vs. value delivered
                total_tokens = sum(entry['cost_tokens'] for entry in self.current_trajectory)
                efficiency_score = max(0, 1 - (total_tokens / 1000))  # Penalize high token usage
                total_score += efficiency_score * weight
                
            elif criterion == "task_completion":
                # Score based on successful task completion
                completion_score = sum(entry['score'] for entry in self.current_trajectory) / len(self.current_trajectory)
                total_score += completion_score * weight
                
            elif criterion == "response_time":
                # Score based on response time (lower is better)
                if len(self.current_trajectory) > 1:
                    time_diff = self.current_trajectory[-1]['timestamp'] - self.current_trajectory[0]['timestamp']
                    time_score = max(0, 1 - (time_diff / 300))  # Penalize if takes more than 5 minutes
                    total_score += time_score * weight
                else:
                    total_score += 1.0 * weight  # Perfect score for single action
                    
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def get_recent_trajectories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trajectory entries from CSV"""
        trajectories = []
        try:
            with open(self.csv_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    trajectories.append({
                        'timestamp': int(row['timestamp']),
                        'session_id': row['session_id'],
                        'action': row['action'],
                        'input_data': json.loads(row['input_data']),
                        'output_data': json.loads(row['output_data']),
                        'cost_tokens': int(row['cost_tokens']),
                        'score': float(row['score']),
                        'metadata': json.loads(row['metadata'])
                    })
            
            # Sort by timestamp and return most recent
            trajectories.sort(key=lambda x: x['timestamp'], reverse=True)
            return trajectories[:limit]
            
        except Exception as e:
            print(f"❌ Error reading trajectories: {e}")
            return []
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends from trajectory data"""
        trajectories = self.get_recent_trajectories(100)
        
        if not trajectories:
            return {"error": "No trajectory data available"}
        
        # Calculate metrics
        total_tokens = sum(t['cost_tokens'] for t in trajectories)
        avg_score = sum(t['score'] for t in trajectories) / len(trajectories)
        
        # Group by action type
        action_stats = {}
        for t in trajectories:
            action = t['action']
            if action not in action_stats:
                action_stats[action] = {'count': 0, 'total_tokens': 0, 'total_score': 0}
            action_stats[action]['count'] += 1
            action_stats[action]['total_tokens'] += t['cost_tokens']
            action_stats[action]['total_score'] += t['score']
        
        # Calculate averages
        for action in action_stats:
            stats = action_stats[action]
            stats['avg_tokens'] = stats['total_tokens'] / stats['count']
            stats['avg_score'] = stats['total_score'] / stats['count']
        
        return {
            "total_actions": len(trajectories),
            "total_tokens_used": total_tokens,
            "average_score": avg_score,
            "action_statistics": action_stats,
            "credit_efficiency": max(0, 1 - (total_tokens / 10000)),  # Efficiency metric
            "timestamp": int(time.time())
        }

# Global tracker instance
_global_tracker = None

def get_tracker(session_id: Optional[str] = None) -> TrajectoryTracker:
    """Get or create global trajectory tracker"""
    global _global_tracker
    if _global_tracker is None or (session_id and _global_tracker.session_id != session_id):
        _global_tracker = TrajectoryTracker(session_id)
    return _global_tracker

def log_action(action: str, input_data: Dict[str, Any], output_data: Dict[str, Any], 
               cost_tokens: int = 0, score: float = 0.0, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Convenience function to log an action using the global tracker"""
    tracker = get_tracker()
    return tracker.log_action(action, input_data, output_data, cost_tokens, score, metadata)

# Example usage and testing
if __name__ == "__main__":
    # Test the trajectory tracker
    tracker = TrajectoryTracker("test_session")
    
    # Log some test actions
    tracker.log_action(
        action="test_action",
        input_data={"query": "test query"},
        output_data={"response": "test response"},
        cost_tokens=100,
        score=0.8,
        metadata={"test": True}
    )
    
    tracker.log_action(
        action="another_action",
        input_data={"data": "more test data"},
        output_data={"result": "success"},
        cost_tokens=50,
        score=0.9,
        metadata={"test": True}
    )
    
    # Score the trajectory
    score = tracker.score_trajectory({
        "credit_efficiency": 0.4,
        "task_completion": 0.4,
        "response_time": 0.2
    })
    
    print(f"Trajectory score: {score}")
    
    # Analyze performance
    analysis = tracker.analyze_performance_trends()
    print(f"Performance analysis: {json.dumps(analysis, indent=2)}")

