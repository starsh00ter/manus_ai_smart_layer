#!/usr/bin/env bash
# Runs on EVERY commit in BOTH repos – rejects if credit limit exceeded
set -euo pipefail
TOKEN_FILE=".manus/sync-cost.txt"
DAILY_LOG=".manus/daily-tokens.log"

# ---- 1. read today’s spend ----
TODAY=$(date +%F)
TODAY_SPENT=$(awk -F',' -v d="$TODAY" '$1==d{sum+=$2} END{print sum+0}' "$DAILY_LOG")

# ---- 2. estimate this commit ----
if [[ -f "$TOKEN_FILE" ]]; then
    EST=$(cat "$TOKEN_FILE")
else
    EST=$(git diff --cached --numstat | awk '{ words+=$1+$2 } END { printf "%.0f", words*1.3 }')
fi

# ---- 3. gate ----
DAILY_LIMIT=$(yq '.credit.daily_limit' .manus/autosync.yml)
if (( $(echo "$TODAY_SPENT + $EST > $DAILY_LIMIT" | bc -l) )); then
    echo "❌ autosync: $EST tokens would exceed daily limit ($TODAY_SPENT + $EST > $DAILY_LIMIT)"
    exit 77   # git hook convention: reject
fi

# ---- 4. log & allow ----
echo "$(date +%s),$EST,$(git rev-parse --short HEAD)" >> "$DAILY_LOG"
echo "✅ autosync: $EST T approved (today: $((TODAY_SPENT + EST))/$DAILY_LIMIT)"
exit 0


