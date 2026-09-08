from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid

app = FastAPI(title="NexusCore State Engine")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Models ====================
class Message(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str

class MessagePayload(BaseModel):
    role: str
    content: str

class CheckpointRequest(BaseModel):
    checkpoint_id: str

class RollbackRequest(BaseModel):
    checkpoint_id: str

class StepRequest(BaseModel):
    step_name: str
    action_type: str  # "success" or "fail"
    payload_key: str
    payload_val: str

class StateResponse(BaseModel):
    working_memory: List[Dict[str, Any]]
    paged_memory: List[Dict[str, Any]]
    state_payload: Dict[str, Any]
    checkpoints: List[str]

# ==================== In-Memory State ====================
class StateEngine:
    def __init__(self):
        self.working_memory: List[Message] = []
        self.paged_memory: List[Dict[str, Any]] = []
        self.state_payload: Dict[str, Any] = {
            "status": "initialized",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "context_size": 0,
            "paged_count": 0
        }
        self.checkpoints: Dict[str, Dict[str, Any]] = {}
        self.max_working_memory = 5  # Max items in working memory before paging
        self.step_history: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str) -> None:
        """Add message to working memory, page out if necessary."""
        msg = Message(role=role, content=content)
        self.working_memory.append(msg)
        
        # Auto-page out if working memory exceeds limit
        if len(self.working_memory) > self.max_working_memory:
            paged = self.working_memory.pop(0)
            paged_entry = {
                "id": str(uuid.uuid4())[:8],
                "role": paged.role,
                "content": paged.content,
                "paged_at": datetime.now().isoformat()
            }
            self.paged_memory.append(paged_entry)
            self.state_payload["paged_count"] = len(self.paged_memory)
        
        self.state_payload["context_size"] = len(self.working_memory)
        self.state_payload["last_update"] = datetime.now().isoformat()

    def create_checkpoint(self, checkpoint_id: str) -> None:
        """Create a checkpoint of current state."""
        self.checkpoints[checkpoint_id] = {
            "timestamp": datetime.now().isoformat(),
            "working_memory": [m.dict() for m in self.working_memory],
            "paged_memory": self.paged_memory.copy(),
            "state_payload": self.state_payload.copy()
        }
        self.state_payload["last_checkpoint"] = checkpoint_id
        self.state_payload["checkpoint_count"] = len(self.checkpoints)

    def rollback(self, checkpoint_id: str) -> None:
        """Rollback to a previous checkpoint."""
        if checkpoint_id not in self.checkpoints:
            raise HTTPException(status_code=404, detail=f"Checkpoint '{checkpoint_id}' not found")
        
        cp = self.checkpoints[checkpoint_id]
        self.working_memory = [Message(**m) for m in cp["working_memory"]]
        self.paged_memory = cp["paged_memory"].copy()
        self.state_payload = cp["state_payload"].copy()
        self.state_payload["rolled_back_to"] = checkpoint_id
        self.state_payload["rollback_timestamp"] = datetime.now().isoformat()

    def execute_step(self, step_name: str, action_type: str, payload_key: str, payload_val: str) -> None:
        """Execute a transactional step."""
        step_record = {
            "step_name": step_name,
            "action_type": action_type,
            "timestamp": datetime.now().isoformat(),
            "payload": {payload_key: payload_val}
        }
        
        if action_type == "success":
            # Update state payload with step data
            self.state_payload[f"step_{step_name}"] = payload_val
            self.state_payload["last_step"] = step_name
            self.state_payload["last_step_status"] = "success"
            step_record["status"] = "completed"
        elif action_type == "fail":
            self.state_payload["last_step"] = step_name
            self.state_payload["last_step_status"] = "failed"
            step_record["status"] = "failed"
        
        self.step_history.append(step_record)
        self.state_payload["step_count"] = len(self.step_history)
        self.state_payload["updated_at"] = datetime.now().isoformat()

    def get_state(self) -> StateResponse:
        """Get current state as response object."""
        return StateResponse(
            working_memory=[m.dict() for m in self.working_memory],
            paged_memory=self.paged_memory,
            state_payload=self.state_payload,
            checkpoints=list(self.checkpoints.keys())
        )

# Initialize state engine
state_engine = StateEngine()

# ==================== Routes ====================
@app.get("/")
def root():
    return {"message": "NexusCore State Engine API", "version": "1.0.0"}

@app.get("/api/state", response_model=StateResponse)
def get_state():
    """Fetch current engine state."""
    return state_engine.get_state()

@app.post("/api/message")
def add_message(payload: MessagePayload):
    """Add a message to working memory."""
    state_engine.add_message(payload.role, payload.content)
    return {"status": "message added", "working_memory_size": len(state_engine.working_memory)}

@app.post("/api/checkpoint")
def create_checkpoint(payload: CheckpointRequest):
    """Create a checkpoint."""
    state_engine.create_checkpoint(payload.checkpoint_id)
    return {"status": "checkpoint created", "checkpoint_id": payload.checkpoint_id}

@app.post("/api/rollback")
def rollback(payload: RollbackRequest):
    """Rollback to a checkpoint."""
    state_engine.rollback(payload.checkpoint_id)
    return {"status": "rolled back", "checkpoint_id": payload.checkpoint_id}

@app.post("/api/step")
def execute_step(payload: StepRequest):
    """Execute a transactional step."""
    state_engine.execute_step(
        payload.step_name,
        payload.action_type,
        payload.payload_key,
        payload.payload_val
    )
    return {
        "status": "step executed",
        "step_name": payload.step_name,
        "action_type": payload.action_type
    }

@app.get("/api/history")
def get_history():
    """Get step execution history."""
    return {"history": state_engine.step_history}

@app.post("/api/reset")
def reset_state():
    """Reset the entire state engine."""
    global state_engine
    state_engine = StateEngine()
    return {"status": "state engine reset"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)