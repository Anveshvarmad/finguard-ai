#!/bin/bash

set -e

API_URL="${API_URL:-http://localhost:8000}"

echo "Testing FinGuard AI backend at $API_URL"
echo

echo "1. Health check"
curl -s "$API_URL/health" | python -m json.tool
echo

echo "2. Database health"
curl -s "$API_URL/health/database" | python -m json.tool
echo

echo "3. Redis health"
curl -s "$API_URL/health/redis" | python -m json.tool
echo

echo "4. System status"
curl -s "$API_URL/system/status" | python -m json.tool
echo

echo "5. Seed sample data"
curl -s -X POST "$API_URL/seed/sample-data?force=true" | python -m json.tool
echo

echo "6. Generate simulated transactions"
curl -s -X POST "$API_URL/simulate/batch?count=10" > /tmp/finguard_simulation.json
python -m json.tool /tmp/finguard_simulation.json > /dev/null
echo "Generated 10 simulated transactions"
echo

echo "7. Index transactions"
curl -s -X POST "$API_URL/index/transactions?limit=500" | python -m json.tool
echo

echo "8. Semantic search"
curl -s -X POST "$API_URL/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "suspicious wire transfers with missing approvals",
    "top_k": 5
  }' | python -m json.tool
echo

echo "9. Analytics summary"
curl -s "$API_URL/analytics/summary" | python -m json.tool
echo

echo "Smoke test completed successfully."
