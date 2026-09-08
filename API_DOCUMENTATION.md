# NexusCore State Engine - API Documentation

Complete reference for all REST API endpoints with examples, request/response schemas, and use cases.

---

## 🔗 Base URL

```
http://127.0.0.1:8000/api
```

---

## 📋 Endpoints Overview

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/state` | Fetch current engine state | None |
| POST | `/message` | Add message to working memory | None |
| POST | `/checkpoint` | Create a state checkpoint | None |
| POST | `/rollback` | Rollback to previous checkpoint | None |
| POST | `/step` | Execute a transactional step | None |
| GET | `/history` | View step execution history | None |
| POST | `/reset` | Reset entire state engine | None |

---

## 📍 1. GET /api/state

**Description**: Fetch the current state of the NexusCore engine, including working memory, paged memory, system state, and active checkpoints.

### Request

```http
GET /api/state HTTP/1.1
Host: 127.0.0.1:8000
Accept: application/json
```

### cURL Example

```bash
curl -X GET "http://127.0.0.1:8000/api/state" \
  -H "Accept: application/json"
```

### JavaScript/Fetch Example

```javascript
fetch('http://127.0.0.1:8000/api/state')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Response (200 OK)

```json
{
  "working_memory": [
    {
      "role": "user",
      "content": "Hello, what can you help me with?"
    },
    {
      "role": "assistant",
      "content": "I can help with code, writing, analysis, math, and more!"
    }
  ],
  "paged_memory": [
    {
      "id": "a1b2c3d4",
      "role": "system",
      "content": "You are a helpful AI assistant.",
      "paged_at": "2026-09-08T21:30:45.123456"
    },
    {
      "id": "e5f6g7h8",
      "role": "user",
      "content": "This is an older message that was evicted from active memory",
      "paged_at": "2026-09-08T21:31:10.654321"
    }
  ],
  "state_payload": {
    "status": "initialized",
    "timestamp": "2026-09-08T21:25:06.000000",
    "version": "1.0.0",
    "context_size": 2,
    "paged_count": 2,
    "step_count": 3,
    "last_step": "DatabaseMigration",
    "last_step_status": "success",
    "last_checkpoint": "stable-v1",
    "checkpoint_count": 1,
    "updated_at": "2026-09-08T21:32:15.789012"
  },
  "checkpoints": [
    "stable-v1",
    "backup-v2",
    "production"
  ]
}
```

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `working_memory` | Array[Object] | Active messages in RAM |
| `paged_memory` | Array[Object] | Evicted messages in storage |
| `state_payload` | Object | Current system state & metrics |
| `checkpoints` | Array[String] | Available checkpoint names |

### Use Cases

- **Dashboard Refresh**: Get full state for UI updates
- **State Monitoring**: Track memory usage and step execution
- **Debugging**: Inspect working & paged memory contents
- **Audit Trail**: Monitor state payload history

---

## 💬 2. POST /api/message

**Description**: Add a new message to the working memory. Messages automatically page out when memory limit is exceeded.

### Request

```http
POST /api/message HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "role": "user",
  "content": "What is the capital of France?"
}
```

### Request Body

```json
{
  "role": "user|assistant|system",
  "content": "Message text content here..."
}
```

### cURL Example

```bash
curl -X POST "http://127.0.0.1:8000/api/message" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "Please help me refactor this authentication module"
  }'
```

### JavaScript/Fetch Example

```javascript
const message = {
  role: "assistant",
  content: "I'd be happy to help refactor your authentication code. Let's start by reviewing the current implementation."
};

fetch('http://127.0.0.1:8000/api/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(message)
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### Python Example

```python
import requests

message = {
    "role": "user",
    "content": "Explain how virtual context paging works"
}

response = requests.post(
    'http://127.0.0.1:8000/api/message',
    json=message
)
print(response.json())
```

### Response (200 OK)

```json
{
  "status": "message added",
  "working_memory_size": 3
}
```

### Error Responses

**400 Bad Request** - Invalid message format
```json
{
  "detail": "validation error in request body"
}
```

**422 Unprocessable Entity** - Missing required fields
```json
{
  "detail": [
    {
      "loc": ["body", "role"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `role` | string | Yes | Message sender: `user`, `assistant`, or `system` |
| `content` | string | Yes | Message text content (any length) |

### Auto-Paging Behavior

When `working_memory_size` exceeds the configured limit (default: 5):
1. Oldest message is removed from working memory
2. Message is added to paged memory with UUID
3. Paged memory receives `paged_at` timestamp
4. State payload updates: `paged_count` increments, `context_size` adjusts

### Use Cases

- **Conversation Flow**: Add user/assistant messages for multi-turn dialogue
- **Context Injection**: Insert system prompts and context
- **State Simulation**: Load messages for testing memory paging
- **Long-running Sessions**: Handle unlimited conversation length via auto-paging

---

## 📌 3. POST /api/checkpoint

**Description**: Create a named checkpoint of the current engine state. Useful for creating save points before risky operations.

### Request

```http
POST /api/checkpoint HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "checkpoint_id": "pre-refactor-v1"
}
```

### Request Body

```json
{
  "checkpoint_id": "string (name/tag for this checkpoint)"
}
```

### cURL Example

```bash
curl -X POST "http://127.0.0.1:8000/api/checkpoint" \
  -H "Content-Type: application/json" \
  -d '{"checkpoint_id": "before-database-migration"}'
```

### JavaScript/Fetch Example

```javascript
const checkpoint = {
  checkpoint_id: "stable-production-state"
};

fetch('http://127.0.0.1:8000/api/checkpoint', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(checkpoint)
})
  .then(response => response.json())
  .then(data => console.log('Checkpoint created:', data));
```

### Python Example

```python
import requests

response = requests.post(
    'http://127.0.0.1:8000/api/checkpoint',
    json={"checkpoint_id": "v1.2.0"}
)
print(response.json())
```

### Response (200 OK)

```json
{
  "status": "checkpoint created",
  "checkpoint_id": "pre-refactor-v1"
}
```

### Checkpoint Data Stored

Each checkpoint captures:
```json
{
  "checkpoint_id": "pre-refactor-v1",
  "timestamp": "2026-09-08T21:35:22.123456",
  "working_memory": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "paged_memory": [
    {"id": "abc123", "role": "system", "content": "...", "paged_at": "..."}
  ],
  "state_payload": {
    "status": "...",
    "context_size": 2,
    "paged_count": 1,
    ...
  }
}
```

### Naming Conventions

```
✅ Good checkpoint names:
- "v1.0"
- "stable-2026-09-08"
- "before-refactor"
- "production-backup"
- "test-run-001"

❌ Avoid:
- Empty strings
- Very long names (200+ chars)
- Special characters (use hyphens instead of spaces)
```

### Error Responses

**400 Bad Request** - Duplicate checkpoint ID
```json
{
  "detail": "Checkpoint 'v1.0' already exists"
}
```

### Use Cases

- **Version Control**: Save state before major changes
- **Testing**: Create baseline for test scenarios
- **Recovery**: Create backups before risky operations
- **A/B Testing**: Create separate checkpoints for different paths
- **Audit Trail**: Timestamped snapshots for compliance

---

## ↩️ 4. POST /api/rollback

**Description**: Restore the engine to a previously saved checkpoint state. All current state is lost; replaced with checkpoint data.

### Request

```http
POST /api/rollback HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "checkpoint_id": "pre-refactor-v1"
}
```

### Request Body

```json
{
  "checkpoint_id": "string (name of checkpoint to restore)"
}
```

### cURL Example

```bash
curl -X POST "http://127.0.0.1:8000/api/rollback" \
  -H "Content-Type: application/json" \
  -d '{"checkpoint_id": "before-database-migration"}'
```

### JavaScript/Fetch Example

```javascript
const rollbackRequest = {
  checkpoint_id: "stable-production-state"
};

fetch('http://127.0.0.1:8000/api/rollback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(rollbackRequest)
})
  .then(response => response.json())
  .then(data => {
    console.log('Rolled back to:', data.checkpoint_id);
    // Refresh UI to show restored state
    fetchState();
  });
```

### Python Example

```python
import requests

response = requests.post(
    'http://127.0.0.1:8000/api/rollback',
    json={"checkpoint_id": "v1.0"}
)
print(f"Restored state: {response.json()}")
```

### Response (200 OK)

```json
{
  "status": "rolled back",
  "checkpoint_id": "pre-refactor-v1"
}
```

### State After Rollback

```json
{
  "working_memory": [
    // ... restored from checkpoint
  ],
  "paged_memory": [
    // ... restored from checkpoint
  ],
  "state_payload": {
    "rolled_back_to": "pre-refactor-v1",
    "rollback_timestamp": "2026-09-08T21:40:15.654321",
    // ... other checkpoint state
  }
}
```

### Error Responses

**404 Not Found** - Checkpoint doesn't exist
```json
{
  "detail": "Checkpoint 'non-existent' not found"
}
```

### Important Notes

⚠️ **Rollback is Destructive**
- All current state after the checkpoint is lost
- Cannot undo a rollback (would need another checkpoint)
- Checkpoint data remains available for future rollbacks

### Use Cases

- **Error Recovery**: Revert to last known good state
- **Testing**: Reset state between test runs
- **Experimentation**: Try different paths, rollback if needed
- **Multi-scenario Simulation**: Restore different baseline states

---

## ⚙️ 5. POST /api/step

**Description**: Execute a named transactional step. Each step can succeed or fail, updating the system state payload accordingly.

### Request

```http
POST /api/step HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "step_name": "RefactorAuthentication",
  "action_type": "success",
  "payload_key": "module",
  "payload_val": "oauth2-provider"
}
```

### Request Body

```json
{
  "step_name": "string (name of the step)",
  "action_type": "success|fail",
  "payload_key": "string (state key)",
  "payload_val": "string (state value)"
}
```

### cURL Example

```bash
# Successful step
curl -X POST "http://127.0.0.1:8000/api/step" \
  -H "Content-Type: application/json" \
  -d '{
    "step_name": "DatabaseMigration",
    "action_type": "success",
    "payload_key": "migration_version",
    "payload_val": "v2.0.0"
  }'

# Failed step
curl -X POST "http://127.0.0.1:8000/api/step" \
  -H "Content-Type: application/json" \
  -d '{
    "step_name": "ValidateSchema",
    "action_type": "fail",
    "payload_key": "error_code",
    "payload_val": "SCHEMA_VALIDATION_FAILED"
  }'
```

### JavaScript/Fetch Example

```javascript
// Success case
const step = {
  step_name: "DeployToProduction",
  action_type: "success",
  payload_key: "deployment_id",
  payload_val: "deploy-20260908-001"
};

fetch('http://127.0.0.1:8000/api/step', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(step)
})
  .then(response => response.json())
  .then(data => console.log('Step executed:', data));

// Failure case
const failedStep = {
  step_name: "SendNotification",
  action_type: "fail",
  payload_key: "failure_reason",
  payload_val: "email_service_unavailable"
};

fetch('http://127.0.0.1:8000/api/step', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(failedStep)
})
  .then(response => response.json())
  .then(data => console.log('Step failed:', data));
```

### Python Example

```python
import requests

# Success
response = requests.post(
    'http://127.0.0.1:8000/api/step',
    json={
        "step_name": "BackupDatabase",
        "action_type": "success",
        "payload_key": "backup_location",
        "payload_val": "s3://backups/db-20260908.bak"
    }
)
print(response.json())

# Failure
response = requests.post(
    'http://127.0.0.1:8000/api/step',
    json={
        "step_name": "CompileCode",
        "action_type": "fail",
        "payload_key": "error_message",
        "payload_val": "Syntax error at line 42"
    }
)
print(response.json())
```

### Response (200 OK)

```json
{
  "status": "step executed",
  "step_name": "RefactorAuthentication",
  "action_type": "success"
}
```

### Step History Entry Created

Each step creates a history record:
```json
{
  "step_name": "RefactorAuthentication",
  "action_type": "success",
  "status": "completed",
  "timestamp": "2026-09-08T21:45:30.123456",
  "payload": {
    "module": "oauth2-provider"
  }
}
```

### State Payload Updates

On success:
```json
{
  "last_step": "RefactorAuthentication",
  "last_step_status": "success",
  "step_RefactorAuthentication": "oauth2-provider",
  "step_count": 5,
  "updated_at": "2026-09-08T21:45:30.123456"
}
```

On failure:
```json
{
  "last_step": "ValidateSchema",
  "last_step_status": "failed",
  "step_count": 6,
  "updated_at": "2026-09-08T21:45:45.654321"
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `step_name` | string | Yes | Identifier for this step (e.g., `DatabaseMigration`) |
| `action_type` | string | Yes | Either `success` or `fail` |
| `payload_key` | string | Yes | Key for state data (e.g., `version`) |
| `payload_val` | string | Yes | Value for state data (e.g., `2.0.0`) |

### Error Responses

**400 Bad Request** - Invalid action_type
```json
{
  "detail": "action_type must be 'success' or 'fail'"
}
```

### Use Cases

- **Workflow Execution**: Track multi-step processes
- **Error Handling**: Log failures with context
- **State Mutation**: Update state based on operations
- **Audit Logging**: Create timestamped execution records
- **Rollback Planning**: Know which steps led to current state

---

## 📊 6. GET /api/history

**Description**: Retrieve the complete execution history of all transactional steps run in this session.

### Request

```http
GET /api/history HTTP/1.1
Host: 127.0.0.1:8000
Accept: application/json
```

### cURL Example

```bash
curl -X GET "http://127.0.0.1:8000/api/history" \
  -H "Accept: application/json"
```

### JavaScript/Fetch Example

```javascript
fetch('http://127.0.0.1:8000/api/history')
  .then(response => response.json())
  .then(data => {
    console.log(`Executed ${data.history.length} steps:`);
    data.history.forEach((step, index) => {
      console.log(`${index + 1}. ${step.step_name} - ${step.status}`);
    });
  });
```

### Python Example

```python
import requests

response = requests.get('http://127.0.0.1:8000/api/history')
history = response.json()

print(f"Total steps: {len(history['history'])}")
for step in history['history']:
    print(f"  - {step['step_name']}: {step['status']}")
```

### Response (200 OK)

```json
{
  "history": [
    {
      "step_name": "AuthenticationSetup",
      "action_type": "success",
      "status": "completed",
      "timestamp": "2026-09-08T21:35:15.123456",
      "payload": {
        "provider": "oauth2"
      }
    },
    {
      "step_name": "DatabaseMigration",
      "action_type": "success",
      "status": "completed",
      "timestamp": "2026-09-08T21:35:45.654321",
      "payload": {
        "version": "2.0.0"
      }
    },
    {
      "step_name": "ValidateSchema",
      "action_type": "fail",
      "status": "failed",
      "timestamp": "2026-09-08T21:36:10.987654",
      "payload": {
        "error_code": "SCHEMA_VALIDATION_FAILED"
      }
    },
    {
      "step_name": "DeployToProduction",
      "action_type": "success",
      "status": "completed",
      "timestamp": "2026-09-08T21:36:50.111111",
      "payload": {
        "deployment_id": "prod-001"
      }
    }
  ]
}
```

### History Entry Structure

| Field | Type | Description |
|-------|------|-------------|
| `step_name` | string | Name of the executed step |
| `action_type` | string | Either `success` or `fail` |
| `status` | string | Either `completed` or `failed` |
| `timestamp` | string | ISO 8601 timestamp of execution |
| `payload` | object | Key-value data from the step |

### Empty History Response

```json
{
  "history": []
}
```

### Use Cases

- **Audit Trail**: Review all operations performed
- **Debugging**: Identify which step caused an issue
- **Analytics**: Analyze step success/failure rates
- **Documentation**: Generate execution logs
- **Replay**: Use history to reproduce workflows

---

## 🔄 7. POST /api/reset

**Description**: Completely reset the engine to initial state. Clears all messages, checkpoints, and step history.

### Request

```http
POST /api/reset HTTP/1.1
Host: 127.0.0.1:8000
```

### cURL Example

```bash
curl -X POST "http://127.0.0.1:8000/api/reset"
```

### JavaScript/Fetch Example

```javascript
fetch('http://127.0.0.1:8000/api/reset', {
  method: 'POST'
})
  .then(response => response.json())
  .then(data => {
    console.log('Engine reset:', data);
    // Refresh UI
    fetchState();
  });
```

### Python Example

```python
import requests

response = requests.post('http://127.0.0.1:8000/api/reset')
print(response.json())
```

### Response (200 OK)

```json
{
  "status": "state engine reset"
}
```

### What Gets Reset

✅ **Cleared:**
- All working memory messages
- All paged memory messages
- All checkpoints
- All step history
- State payload (reset to defaults)

❌ **Note:** This cannot be undone. Create a checkpoint before resetting!

### Error Handling

There are no error cases for reset - it always succeeds.

### Use Cases

- **Fresh Start**: Start a new session
- **Testing**: Reset between test runs
- **Cleanup**: Free memory between major operations
- **Demo Reset**: Return to initial state for presentations

---

## 🔐 Authentication

Currently, **all endpoints require no authentication**. For production use, consider adding:

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/api/state")
async def get_state(credentials: HTTPAuthCredentials = Depends(security)):
    # Validate JWT or API key
    pass
```

---

## 📈 Rate Limiting

No rate limiting is currently implemented. For production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/message")
@limiter.limit("100/minute")
async def add_message(payload: MessagePayload):
    pass
```

---

## 🚨 Error Handling

All errors follow this format:

```json
{
  "detail": "Error description"
}
```

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Message added, step executed |
| 400 | Bad Request | Invalid JSON, missing fields |
| 404 | Not Found | Checkpoint doesn't exist |
| 422 | Validation Error | Field type mismatch |
| 500 | Server Error | Unexpected exception |

---

## 📝 Request/Response Examples

### Complete Workflow Example

```javascript
// 1. Get initial state
const state1 = await fetch('/api/state').then(r => r.json());
console.log('Initial state:', state1);

// 2. Add some messages
await fetch('/api/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ role: 'user', content: 'Hello!' })
});

// 3. Create checkpoint before risky operation
await fetch('/api/checkpoint', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ checkpoint_id: 'safe-point' })
});

// 4. Execute a step
await fetch('/api/step', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    step_name: 'ProcessData',
    action_type: 'success',
    payload_key: 'records',
    payload_val: '1000'
  })
});

// 5. Check history
const history = await fetch('/api/history').then(r => r.json());
console.log('Execution history:', history);

// 6. If something went wrong, rollback
if (history.history.some(s => s.status === 'failed')) {
  await fetch('/api/rollback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ checkpoint_id: 'safe-point' })
  });
}

// 7. Get final state
const stateFinal = await fetch('/api/state').then(r => r.json());
console.log('Final state:', stateFinal);
```

---

## 🧪 Testing with cURL

```bash
# 1. Get state
curl http://127.0.0.1:8000/api/state

# 2. Add message
curl -X POST http://127.0.0.1:8000/api/message \
  -H "Content-Type: application/json" \
  -d '{"role":"user","content":"Test message"}'

# 3. Create checkpoint
curl -X POST http://127.0.0.1:8000/api/checkpoint \
  -H "Content-Type: application/json" \
  -d '{"checkpoint_id":"v1"}'

# 4. Execute step
curl -X POST http://127.0.0.1:8000/api/step \
  -H "Content-Type: application/json" \
  -d '{
    "step_name":"TestStep",
    "action_type":"success",
    "payload_key":"test_key",
    "payload_val":"test_value"
  }'

# 5. Get history
curl http://127.0.0.1:8000/api/history

# 6. Rollback
curl -X POST http://127.0.0.1:8000/api/rollback \
  -H "Content-Type: application/json" \
  -d '{"checkpoint_id":"v1"}'

# 7. Reset
curl -X POST http://127.0.0.1:8000/api/reset
```

---

## 📚 Resources

- **Dashboard**: `index.html` - Interactive UI
- **Backend Code**: `app.py` - FastAPI implementation
- **README**: `README.md` - Full documentation
- **Compose File**: `docker-compose.yml` - Docker setup

---

## ❓ FAQ

**Q: Does the API persist data?**
A: No, all data is in-memory. Restart the server to clear everything. Use checkpoints to save state within a session.

**Q: Can I query specific messages?**
A: Not directly. Use `/api/state` to get all messages, then filter client-side.

**Q: Is there pagination for history?**
A: No, `/api/history` returns all entries. Filter client-side as needed.

**Q: Can I delete individual checkpoints?**
A: No, checkpoints persist until reset. Use `/api/reset` to clear all.

**Q: What's the message content size limit?**
A: No enforced limit, but practical limit ~32KB per request body.

---

Last Updated: 2026-09-08
