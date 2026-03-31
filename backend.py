from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

# Initialize the API
app = FastAPI(title="Dumbo V2 Python Brain")

# Crucial: This allows your React frontend to talk to this Python backend without security blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows any frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class Message(BaseModel):
    text: str

class Fact(BaseModel):
    subject: str
    verb: str
    property: str

# --- Persistent Storage ---
# Look for a special cloud folder (Volume), otherwise save in the current folder
DATA_DIR = os.getenv("DATA_DIR", ".")
MEMORY_FILE = os.path.join(DATA_DIR, "dumbo_persistent_memory.json")
memory_bank = {}

def load_memory():
    global memory_bank
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory_bank = json.load(f)

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_bank, f, indent=4)

# Load memory when the server starts
load_memory()

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "Dumbo's Python Brain is Online!"}

@app.post("/chat")
def chat_with_dumbo(msg: Message):
    user_text = msg.text.lower().strip()
    
    # 1. Check Python Memory
    for subject, fact in memory_bank.items():
        if subject in user_text:
            return {
                "response": f"My Python brain remembers this: {fact['subject'].capitalize()} {fact['verb']} {fact['property']}.",
                "source": "Python Memory Bank"
            }

    # 2. THE UPGRADE ZONE
    # This is where you can eventually import libraries like 'transformers', 'nltk', 
    # or text-generation models to make Dumbo highly intelligent!
    
    # For now, it echoes back to prove the connection works.
    return {
        "response": f"I processed '{msg.text}' on my Python backend! Ready for you to add ML models here.",
        "source": "Python NLP Engine"
    }

@app.post("/learn")
def learn_fact(fact: Fact):
    memory_bank[fact.subject.lower()] = {
        "subject": fact.subject,
        "verb": fact.verb,
        "property": fact.property
    }
    save_memory() # Saves to the JSON file immediately!
    return {"status": "success", "message": f"Python saved: {fact.subject} {fact.verb} {fact.property}"}