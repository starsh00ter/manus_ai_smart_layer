#!/usr/bin/env python3

import json
import hashlib
import pathlib
import time
import subprocess as sp
import datetime
import uuid
import sys
import os

# Add manus_core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from manus_core.utils.credits import get_credit_manager, check_credits, reserve_credits, update_credits
from manus_core.routing.coordinator import get_coordinator
from manus_core.config import get_config

KEY_FILE = pathlib.Path("memory/.r1_key")
COST_LOG_FILE = pathlib.Path("logs/cost.csv")

# Initialize shared components
config = get_config()
credit_manager = get_credit_manager("smart_layer")
coordinator = get_coordinator("smart_layer")

# Legacy compatibility
DAILY_CREDIT_LIMIT = config.credit.daily_limit
_used_today = 0
_last_reset_day = datetime.date.today()

def _reset_daily_credits():
    """Legacy function for backward compatibility"""
    global _used_today, _last_reset_day
    current_day = datetime.date.today()
    if current_day != _last_reset_day:
        _used_today = 0
        _last_reset_day = current_day

def spend(estimated_cost: int) -> bool:
    """Enhanced spend function using shared credit management"""
    try:
        # Use shared credit management system
        user_id = "system"
        
        # Check credit availability using shared system
        availability = credit_manager.check_credit_availability(user_id, estimated_cost)
        
        if not availability.get("allowed", False):
            remaining = availability.get("remaining_balance", 0)
            usage_pct = availability.get("usage_percentage", 100)
            print(f"❌ Credit Gatekeeper: Estimated cost ({estimated_cost}T) exceeds available credits.")
            print(f"   Remaining: {remaining}T, Usage: {usage_pct:.1f}%")
            
            # Send coordination message if usage is high
            if usage_pct > 90:
                coordinator.send_message(
                    to_project="manus_origin",
                    message_type="warning",
                    title="High Credit Usage Alert",
                    content=f"Smart layer project at {usage_pct:.1f}% credit usage",
                    priority="high"
                )
            
            return False
        
        # Reserve credits for the operation
        session_id = f"session_{int(time.time())}"
        operation_id = str(uuid.uuid4())
        
        reserved = credit_manager.reserve_credits(
            user_id=user_id,
            session_id=session_id,
            operation_id=operation_id,
            operation_type="LLM_CALL",
            estimated_tokens=estimated_cost
        )
        
        if not reserved:
            print(f"❌ Failed to reserve credits for operation")
            return False
        
        # Store operation ID for later actual cost update
        _store_operation_id(operation_id)
        
        # Update legacy counter for backward compatibility
        global _used_today
        _reset_daily_credits()
        _used_today += estimated_cost
        
        return True
        
    except Exception as e:
        print(f"❌ Error in spend function: {e}")
        # Fallback to legacy behavior
        return _legacy_spend(estimated_cost)

def _legacy_spend(estimated_cost: int) -> bool:
    """Legacy spend function as fallback"""
    _reset_daily_credits()
    global _used_today

    if _used_today + estimated_cost > DAILY_CREDIT_LIMIT:
        print(f"❌ Credit Gatekeeper: Estimated cost ({estimated_cost}T) exceeds daily limit. Used today: {_used_today}T. Remaining: {DAILY_CREDIT_LIMIT - _used_today}T.")
        return False
    
    return True

def _store_operation_id(operation_id: str):
    """Store operation ID for later cost updates"""
    try:
        op_file = pathlib.Path("memory/.current_operation")
        with open(op_file, "w") as f:
            f.write(operation_id)
    except Exception as e:
        print(f"⚠️ Could not store operation ID: {e}")

def _get_stored_operation_id() -> str:
    """Get stored operation ID"""
    try:
        op_file = pathlib.Path("memory/.current_operation")
        if op_file.exists():
            with open(op_file, "r") as f:
                return f.read().strip()
    except Exception:
        pass
    return None

def _log_cost(tokens_spent, action_name):
    """Enhanced cost logging with shared credit management"""
    try:
        # Update actual usage in shared system
        operation_id = _get_stored_operation_id()
        if operation_id:
            success = credit_manager.update_actual_usage(
                operation_id=operation_id,
                actual_tokens=tokens_spent,
                metadata={"action_name": action_name, "timestamp": time.time()}
            )
            
            if success:
                print(f"💳 Updated actual usage: {tokens_spent}T for {action_name}")
            else:
                print(f"⚠️ Failed to update actual usage in shared system")
        
        # Update legacy counter
        global _used_today
        _reset_daily_credits()
        _used_today += tokens_spent
        
        # Log to CSV for backward compatibility
        with open(COST_LOG_FILE, "a") as f:
            f.write(f"{time.time()},{tokens_spent},{action_name}\n")
        
        # Update project status in coordination system
        coordinator.update_project_status(
            health_score=0.8,  # Could be calculated based on recent performance
            active_operations=1
        )
        
    except Exception as e:
        print(f"❌ Error logging cost: {e}")
        # Fallback to legacy logging
        _reset_daily_credits()
        global _used_today
        _used_today += tokens_spent
        with open(COST_LOG_FILE, "a") as f:
            f.write(f"{time.time()},{tokens_spent},{action_name}\n")

def call_r1(messages, max_tokens=150):
    cache_key = hashlib.md5(json.dumps(messages).encode()).hexdigest()
    cache_file = pathlib.Path(f"memory/cache/{cache_key}.json")

    if cache_file.exists():
        _log_cost(0, "cached_r1_call")
        return json.loads(cache_file.read_text())

    # Estimate cost for the API call (rough estimate for prompt + expected response)
    # A more accurate estimate would involve tokenizing the messages
    estimated_api_cost = len(json.dumps(messages).split()) + max_tokens # Rough estimate
    if not spend(estimated_api_cost):
        raise Exception("Credit limit reached for API call.")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set in environment variables.")

    # Prepare the curl command for DeepSeek API
    data_payload = json.dumps({
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": max_tokens
    })
    
    test_cmd = [
        "curl", "-s", "-X", "POST", "https://api.deepseek.com/v1/chat/completions",
        "-H", "Authorization: Bearer " + api_key,
        "-H", "Content-Type: application/json",
        "-d", data_payload
    ]

    try:
        result = sp.run(test_cmd, capture_output=True, text=True, timeout=10)
        result.check_returncode()
        response_data = json.loads(result.stdout)

        # Parse actual tokens spent from API response
        actual_tokens_spent = response_data.get("usage", {}).get("total_tokens", estimated_api_cost)
        _log_cost(actual_tokens_spent, "deepseek_api_call")

        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(response_data))
        return response_data

    except sp.CalledProcessError as e:
        print(f"❌ DeepSeek API call failed with error: {e.stderr}")
        raise
    except json.JSONDecodeError:
        print(f"❌ Failed to decode JSON response: {result.stdout}")
        raise
    except Exception as e:
        print(f"❌ An unexpected error occurred during DeepSeek API call: {e}")
        raise

# Ensure logs directory exists and cost.csv has header
COST_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
if not COST_LOG_FILE.exists():
    with open(COST_LOG_FILE, "w") as f:
        f.write("timestamp,tokens_spent,action_name\n")


