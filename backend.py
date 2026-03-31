from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import requests 

# Initialize the API
app = FastAPI(title="Dumbo V2 - Cloud Bridge Edition")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
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

# --- Persistent Storage (JSON Memory) ---
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

load_memory()

# --- Hugging Face Transformer Bridge ---
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "") 
API_URL = "https://router.huggingface.co/hf-inference/models/distilgpt2"
headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def query_transformer(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        
        # If Hugging Face returns weird text instead of JSON, catch it!
        try:
            return response.json()
        except ValueError:
            return {"error": f"Hugging Face returned weird data: {response.status_code} - {response.text[:100]}"}
            
    except Exception as e:
        # Catch severe server crashes like timeouts
        return {"error": f"Python Server Crash: {str(e)}"}

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "Dumbo's Cloud Bridge is Online!"}

@app.post("/chat")
def chat_with_dumbo(msg: Message):
    user_text = msg.text.lower().strip()
    
    # 1. First, check your custom JSON Memory Bank (Exportable)
    for subject, fact in memory_bank.items():
        if subject in user_text:
            return {
                "response": f"My memory bank remembers this: {fact['subject'].capitalize()} {fact['verb']} {fact['property']}.",
                "source": "JSON Memory Bank"
            }

    # 2. Check if Token Exists
    if not HUGGINGFACE_TOKEN:
        return {
            "response": f"I heard '{msg.text}'. (But I am missing my Hugging Face Token in Render's Environment Variables!)",
            "source": "Python Bridge Server"
        }

    # 3. Bridge over to the Transformer Supercomputer!
    transformer_reply = query_transformer({"inputs": msg.text})
    
    if transformer_reply:
        # Check if the AI generated text successfully
        if isinstance(transformer_reply, list) and len(transformer_reply) > 0 and 'generated_text' in transformer_reply[0]:
            clean_text = transformer_reply[0]['generated_text'].replace('\n', ' ').strip()
            return {
                "response": clean_text,
                "source": "Hugging Face Transformer"
            }
        # THIS IS NEW: It will now tell you EXACTLY what failed!
        elif isinstance(transformer_reply, dict) and 'error' in transformer_reply:
            return {
                "response": f"Diagnostic Report: '{transformer_reply['error']}'",
                "source": "Hugging Face Diagnostic"
            }

    # 4. Fallback
    return {
        "response": f"I tried to think about '{msg.text}', but my connection failed completely.",
        "source": "Python Bridge Server Error"
    }

@app.post("/learn")
def learn_fact(fact: Fact):
    memory_bank[fact.subject.lower()] = {
        "subject": fact.subject,
        "verb": fact.verb,
        "property": fact.property
    }
    save_memory() 
    return {"status": "success", "message": f"Python saved: {fact.subject} {fact.verb} {fact.property}"}