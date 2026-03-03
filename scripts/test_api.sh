#!/bin/bash

# Test script for EC2-Automator API endpoints

BASE_URL="http://localhost:8000"

echo "=== EC2-Automator API Tests ==="
echo ""

# Test health check
echo "1. Testing health check endpoint..."
curl -s "$BASE_URL/health" | jq . || echo "Health check failed"
echo ""

# Test get options
echo "2. Testing GET /options endpoint..."
curl -s "$BASE_URL/options" | jq . || echo "Get options failed"
echo ""

# Test launch instance
echo "3. Testing POST /launch endpoint..."
LAUNCH_RESPONSE=$(curl -s -X POST "$BASE_URL/launch" \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name": "test-web-01",
    "instance_type": "t3.micro",
    "app_name": "nginx",
    "owner": "test-team"
  }')

echo "$LAUNCH_RESPONSE" | jq . || echo "Launch instance failed"

# Extract task_id
TASK_ID=$(echo "$LAUNCH_RESPONSE" | jq -r '.task_id' 2>/dev/null)

if [ ! -z "$TASK_ID" ] && [ "$TASK_ID" != "null" ]; then
  echo ""
  echo "4. Testing GET /status/{task_id} endpoint (task_id: $TASK_ID)..."
  curl -s "$BASE_URL/status/$TASK_ID" | jq . || echo "Get status failed"
else
  echo "Could not extract task_id from launch response"
fi

echo ""
echo "5. Testing DELETE /terminate endpoint..."
curl -s -X DELETE "$BASE_URL/terminate/i-1234567890abcdef0" | jq . || echo "Terminate instance failed"

echo ""
echo "=== Tests Complete ==="
