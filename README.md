# NexusCore State Engine Dashboard

A sophisticated Virtual Context Pager & Transactional State Simulator designed for managing LLM context, memory hierarchies, and stateful workflows.

## Features

### 🧠 Memory Management
- **Active Context Memory (RAM)**: Fast access working memory with automatic paging
- **Paged Virtual Memory**: Disk/vector store for evicted context with semantic retrieval capability
- **Automatic Memory Paging**: Intelligently moves old messages to paged storage when memory limits are exceeded

### 📦 Transactional State
- **System State Payload**: Track complex state changes and application context
- **Step Execution**: Run named transactional steps with success/fail outcomes
- **Checkpoint & Rollback**: Create snapshots and rollback to previous states

### 🔄 Context Management
- **Message Injection**: Add user, assistant, or system messages to conversation
- **Virtual Paging**: Automatic context management with configurable thresholds
- **State Persistence**: Full state snapshots for recovery and auditing

## Architecture

```
┌─────────────────────────────────┐
│   Frontend (Tailwind CSS)       │
│   Interactive Dashboard         │
└────────────┬────────────────────┘
             │ REST API (JSON)
             ▼
┌─────────────────────────────────┐
│   FastAPI Backend               │
│   State Engine Core             │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌─────────┐      ┌──────────────┐
│ Working │      │ Paged Memory │
│ Memory  │      │ (Vector Store)│
└─────────┘      └──────────────┘
```

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Gaurav1899/nexuscore-state-engine.git
   cd nexuscore-state-engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the backend server**
   ```bash
   python app.py
   ```
   The API will be available at `http://127.0.0.1:8000`

4. **Open the dashboard**
   ```bash
   # In your browser, open:
   file:///path/to/index.html
   
   # Or serve via HTTP:
   python -m http.server 8080
   # Then visit: http://localhost:8080
   ```

## API Endpoints

### State Management
- **GET** `/api/state` - Fetch current engine state (working memory, paged memory, state payload, checkpoints)

### Message Operations
- **POST** `/api/message` - Add a message to working memory
  ```json
  {
    "role": "user",
    "content": "Your message here..."
  }
  ```

### Checkpoint Operations
- **POST** `/api/checkpoint` - Create a checkpoint
  ```json
  {
    "checkpoint_id": "v1.0"
  }
  ```

- **POST** `/api/rollback` - Rollback to a checkpoint
  ```json
  {
    "checkpoint_id": "v1.0"
  }
  ```

### Step Execution
- **POST** `/api/step` - Execute a transactional step
  ```json
  {
    "step_name": "RefactorAuth",
    "action_type": "success",
    "payload_key": "module",
    "payload_val": "authentication"
  }
  ```

### Utility
- **GET** `/api/history` - Get step execution history
- **POST** `/api/reset` - Reset the entire state engine

## Dashboard Features

### Left Panel
1. **Active Context Memory (RAM)**
   - Shows messages in active working memory
   - Auto-highlighted by message role
   - Scrollable with size limits

2. **Paged Virtual Context**
   - Displays evicted messages
   - Includes paging timestamp and ID
   - Simulates disk/vector store retrieval

3. **Message Injection Control**
   - Select message role (user, assistant, system)
   - Enter message content
   - Send button to add to memory

### Right Panel
1. **System State Payload**
   - Real-time JSON state display
   - Tracks context size, paged count, step history
   - Shows last checkpoint and rollback info

2. **Transactional Step Runner**
   - Enter step name
   - Provide payload key-value pair
   - Run with success or failure outcome

3. **Checkpoints & Rollback**
   - Create named checkpoints (v1.0, backup, etc.)
   - View all active checkpoints
   - Rollback to any checkpoint with one click

## Usage Example

1. **Add messages**
   - Type a message in "Inject Conversation"
   - Click Send
   - Watch as messages fill working memory and auto-page

2. **Create checkpoint**
   - Enter checkpoint name (e.g., "stable-v1")
   - Click Commit
   - State is saved at that moment

3. **Execute steps**
   - Enter step name (e.g., "DatabaseMigration")
   - Add key-value payload (e.g., key="version", value="2.0")
   - Click "Run (Success)" or "Run (Fail)"
   - Watch state payload update

4. **Rollback if needed**
   - Click Rollback button on any checkpoint
   - State returns to that checkpoint instantly

## Configuration

### Working Memory Limit
Edit `app.py` line 60:
```python
self.max_working_memory = 5  # Change this value
```

## Performance Considerations

- **Memory Efficient**: Automatic paging prevents memory bloat
- **Real-time Updates**: Dashboard refreshes on state changes
- **Stateless API**: Each request is independent; state persists in-memory
- **Checkpoint Overhead**: Each checkpoint creates a full state snapshot

## Future Enhancements

- [ ] Persistent storage (SQLite/PostgreSQL)
- [ ] Vector embeddings for semantic retrieval from paged memory
- [ ] Advanced filtering and search in paged memory
- [ ] Export/import state snapshots
- [ ] Real-time WebSocket updates
- [ ] Multi-session management
- [ ] Advanced analytics dashboard

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open a GitHub issue in the repository.
