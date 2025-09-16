#!/usr/bin/env python3

import json
import time
import os
import sys
from typing import Dict, Any, Optional, Callable
from functools import wraps

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from memory.trajectory_tracker import get_tracker, log_action
    from memory.self_reflection import get_reflection_engine, conduct_daily_reflection
    from memory.router import spend, call_r1
except ImportError as e:
    print(f"Warning: Import error: {e}")

class LearningIntegration:
    """Integrates trajectory tracking, self-reflection, and credit management"""
    
    def __init__(self):
        self.last_reflection_time = 0
        self.reflection_interval = 4 * 3600  # 4 hours in seconds
        self.session_start_time = time.time()
        self.session_id = f"session_{int(self.session_start_time)}"
        
    def enhanced_call_r1(self, prompt: str, model: str = "deepseek-r1", **kwargs) -> Dict[str, Any]:
        """Enhanced version of call_r1 with trajectory tracking and learning"""
        
        start_time = time.time()
        input_data = {
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "model": model,
            "kwargs": kwargs
        }
        
        try:
            # Make the actual API call
            result = call_r1(prompt, model, **kwargs)
            
            # Calculate metrics
            end_time = time.time()
            response_time = end_time - start_time
            
            # Estimate tokens (rough approximation)
            estimated_tokens = len(prompt.split()) * 1.3 + len(str(result).split()) * 1.3
            
            # Score the response (basic scoring)
            score = self._score_response(result, response_time, estimated_tokens)
            
            # Log the action
            output_data = {
                "success": True,
                "response_length": len(str(result)),
                "response_time": response_time,
                "estimated_tokens": estimated_tokens
            }
            
            log_action(
                action="llm_call",
                input_data=input_data,
                output_data=output_data,
                cost_tokens=int(estimated_tokens),
                score=score,
                metadata={
                    "model": model,
                    "session_id": self.session_id
                }
            )
            
            # Check if it's time for reflection
            self._check_reflection_trigger()
            
            return result
            
        except Exception as e:
            # Log failed action
            output_data = {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }
            
            log_action(
                action="llm_call_failed",
                input_data=input_data,
                output_data=output_data,
                cost_tokens=0,
                score=0.0,
                metadata={
                    "model": model,
                    "session_id": self.session_id,
                    "error_type": type(e).__name__
                }
            )
            
            raise e
    
    def _score_response(self, result: Any, response_time: float, estimated_tokens: int) -> float:
        """Score the quality of an LLM response"""
        score = 1.0
        
        # Penalize slow responses
        if response_time > 10:
            score -= 0.2
        elif response_time > 5:
            score -= 0.1
        
        # Penalize high token usage
        if estimated_tokens > 1000:
            score -= 0.2
        elif estimated_tokens > 500:
            score -= 0.1
        
        # Reward successful responses
        if result and len(str(result)) > 10:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _check_reflection_trigger(self):
        """Check if it's time to trigger self-reflection"""
        current_time = time.time()
        
        # Time-based trigger (every 4 hours)
        if current_time - self.last_reflection_time > self.reflection_interval:
            self._trigger_reflection("time_based")
        
        # Action count trigger (every 50 actions)
        tracker = get_tracker()
        if len(tracker.current_trajectory) % 50 == 0 and len(tracker.current_trajectory) > 0:
            self._trigger_reflection("action_count")
    
    def _trigger_reflection(self, trigger_type: str):
        """Trigger a self-reflection session"""
        try:
            print(f"🤔 Triggering self-reflection ({trigger_type})...")
            
            reflection_result = conduct_daily_reflection()
            
            # Log the reflection as an action
            log_action(
                action="self_reflection",
                input_data={"trigger_type": trigger_type},
                output_data={
                    "performance_score": reflection_result['reflection_data']['performance_score'],
                    "insights_count": len(reflection_result['reflection_data']['insights']),
                    "action_items_count": len(reflection_result['reflection_data']['action_items'])
                },
                cost_tokens=0,
                score=reflection_result['reflection_data']['performance_score'],
                metadata={
                    "reflection_id": reflection_result['reflection_data']['reflection_id'],
                    "session_id": self.session_id
                }
            )
            
            self.last_reflection_time = time.time()
            
            # Save reflection report
            self._save_reflection_report(reflection_result)
            
            print(f"✅ Self-reflection completed. Score: {reflection_result['reflection_data']['performance_score']:.2f}")
            
        except Exception as e:
            print(f"❌ Error during self-reflection: {e}")
    
    def _save_reflection_report(self, reflection_result: Dict[str, Any]):
        """Save reflection report to file"""
        try:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            report_path = f"/home/ubuntu/my_manus_knowledge/logs/reflection_report_{timestamp}.md"
            
            with open(report_path, 'w') as f:
                f.write(reflection_result['report'])
                f.write("\n\n## Recommendations\n\n")
                for rec in reflection_result['recommendations']:
                    f.write(f"- {rec}\n")
            
            print(f"📄 Reflection report saved to: {report_path}")
            
        except Exception as e:
            print(f"❌ Error saving reflection report: {e}")
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get current learning and performance statistics"""
        tracker = get_tracker()
        reflection_engine = get_reflection_engine()
        
        # Get trajectory analysis
        performance_analysis = tracker.analyze_performance_trends()
        
        # Get recent reflections
        recent_reflections = reflection_engine.get_reflection_history(5)
        
        # Calculate session stats
        session_duration = time.time() - self.session_start_time
        
        return {
            "session_id": self.session_id,
            "session_duration_minutes": session_duration / 60,
            "current_trajectory_length": len(tracker.current_trajectory),
            "performance_analysis": performance_analysis,
            "recent_reflections": recent_reflections,
            "last_reflection_time": self.last_reflection_time,
            "next_reflection_in_minutes": max(0, (self.reflection_interval - (time.time() - self.last_reflection_time)) / 60)
        }
    
    def force_reflection(self) -> Dict[str, Any]:
        """Force a reflection session regardless of timing"""
        self._trigger_reflection("manual")
        return self.get_learning_stats()

# Global learning integration instance
_global_learning_integration = None

def get_learning_integration() -> LearningIntegration:
    """Get or create global learning integration"""
    global _global_learning_integration
    if _global_learning_integration is None:
        _global_learning_integration = LearningIntegration()
    return _global_learning_integration

def enhanced_call_r1(prompt: str, model: str = "deepseek-r1", **kwargs) -> Dict[str, Any]:
    """Enhanced call_r1 with learning integration"""
    integration = get_learning_integration()
    return integration.enhanced_call_r1(prompt, model, **kwargs)

def learning_decorator(func: Callable) -> Callable:
    """Decorator to add learning capabilities to any function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful function call
            log_action(
                action=f"function_{func.__name__}",
                input_data={"args_count": len(args), "kwargs_keys": list(kwargs.keys())},
                output_data={"success": True, "result_type": type(result).__name__},
                cost_tokens=0,
                score=1.0,
                metadata={"execution_time": time.time() - start_time}
            )
            
            return result
            
        except Exception as e:
            # Log failed function call
            log_action(
                action=f"function_{func.__name__}_failed",
                input_data={"args_count": len(args), "kwargs_keys": list(kwargs.keys())},
                output_data={"success": False, "error": str(e)},
                cost_tokens=0,
                score=0.0,
                metadata={"execution_time": time.time() - start_time, "error_type": type(e).__name__}
            )
            
            raise e
    
    return wrapper

# Example usage and testing
if __name__ == "__main__":
    # Test the learning integration
    integration = LearningIntegration()
    
    print("Testing learning integration...")
    
    # Test enhanced call (this will fail without proper setup, but shows the structure)
    try:
        result = integration.enhanced_call_r1("Test prompt for learning integration")
        print(f"✅ Enhanced call successful: {result}")
    except Exception as e:
        print(f"❌ Enhanced call failed (expected): {e}")
    
    # Get learning stats
    stats = integration.get_learning_stats()
    print(f"\nLearning Stats:")
    print(f"Session ID: {stats['session_id']}")
    print(f"Session Duration: {stats['session_duration_minutes']:.2f} minutes")
    print(f"Current Trajectory Length: {stats['current_trajectory_length']}")
    
    # Test decorator
    @learning_decorator
    def test_function(x, y):
        return x + y
    
    result = test_function(2, 3)
    print(f"\nDecorator test result: {result}")
    
    print("\n✅ Learning integration test completed")

