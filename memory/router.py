import os
import json
import hashlib
import pathlib
import time
import subprocess as sp
import datetime

KEY_FILE = pathlib.Path("memory/.r1_key")
COST_LOG_FILE = pathlib.Path("logs/cost.csv")
DAILY_CREDIT_LIMIT = 300000 # 300 credits * 1000 tokens/credit

_used_today = 0
_last_reset_day = datetime.date.today()

def _reset_daily_credits():
    global _used_today, _last_reset_day
    current_day = datetime.date.today()
    if current_day != _last_reset_day:
        _used_today = 0
        _last_reset_day = current_day
        # Optionally, re-read cost.csv for today's actual spend if needed for robustness

def spend(estimated_cost: int) -> bool:
    _reset_daily_credits()
    global _used_today

    # Validate against in-memory counter
    if _used_today + estimated_cost > DAILY_CREDIT_LIMIT:
        print(f"❌ Credit Gatekeeper: Estimated cost ({estimated_cost}T) exceeds daily limit. Used today: {_used_today}T. Remaining: {DAILY_CREDIT_LIMIT - _used_today}T.")
        return False
    
    # For more robust validation, one could parse cost.csv here for today's actual spend
    # However, to save tokens, we rely on the in-memory counter for real-time checks
    # and assume _log_cost updates _used_today accurately.

    return True

def _log_cost(tokens_spent, action_name):
    global _used_today
    _reset_daily_credits()
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


