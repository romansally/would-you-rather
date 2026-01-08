#!/usr/bin/env bash
set -euo pipefail

# Default to your Render URL (change if needed)
BASE_URL="${BASE_URL:-https://would-you-rather-demo.onrender.com}"

# Check for Token
if [[ -z "${ADMIN_TOKEN:-}" ]]; then
  echo "❌ ERROR: ADMIN_TOKEN environment variable is not set."
  echo "Usage: export ADMIN_TOKEN='your_token' && ./seed_production.sh"
  exit 1
fi

# Function to post a poll
post_poll () {
  echo "Creating poll: $1..."
  curl -sS -L -X POST "$BASE_URL/polls/" \
    -H "Content-Type: application/json" \
    -H "X-Admin-Token: $ADMIN_TOKEN" \
    -d "$1"
  echo ""
}

echo "🌱 Seeding production database at $BASE_URL..."
echo "-----------------------------------------------"

# Poll 1
post_poll '{
  "question":"Would you rather have the ability to fly or be invisible?",
  "option_a":"Fly through the sky",
  "option_b":"Become invisible",
  "category":"superpowers"
}'

# Poll 2
post_poll '{
  "question":"Would you rather live in the mountains or by the beach?",
  "option_a":"Mountains",
  "option_b":"Beach",
  "category":"lifestyle"
}'

# Poll 3
post_poll '{
  "question":"Would you rather always be 10 minutes late or 20 minutes early?",
  "option_a":"10 minutes late",
  "option_b":"20 minutes early",
  "category":"general"
}'

echo "-----------------------------------------------"
echo "✅ Done! Verify at $BASE_URL/play"