from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
import json
import re
import os
from medi_graph.run_graph import run_langgraph_agent, run_langgraph_agent_using_sample_data
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://psytrackr.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})


@app.get("/")
async def root(request: Request):
    return {"message": "Welcome to the Therapy Session Analysis API"}


@app.post("/analyze-sessions/")
@limiter.limit("60/minute")
async def analyze_sessions(request: Request, files: List[UploadFile] = File(...)):
    all_therapy_sessions = []
    for file in files:
        content = await file.read()
        try:
            session_data = json.loads(content)
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Invalid JSON in {file.filename}: {e}"})
        base = os.path.basename(str(file.filename))
        match = re.match(r'(client\d+)_session(\d+)\.txt$', base)
        if match:
            client_id = match.group(1)
            session_number = int(match.group(2))
        else:
            client_id = "client1"
            session_number = "NA"
        session_data["client_id"] = client_id
        session_data["therapy_session_number"] = session_number
        all_therapy_sessions.append(session_data)
    print(f"Total therapy sessions received: {len(all_therapy_sessions)}")
    all_therapy_sessions.sort(key=lambda x: x["therapy_session_number"])

    # dummy_result = {
    #     "all_therapy_sessions": all_therapy_sessions,
    # }
    result = run_langgraph_agent(all_therapy_sessions)
    return JSONResponse(content=result)


@app.get("/analyze-sample-data/{client_id}")
@limiter.limit("60/minute")
async def analyze_sample_data(request: Request, client_id: str):
    """
    Endpoint to run the agent using sample data.
    """
    result = run_langgraph_agent_using_sample_data(client_id=client_id)
    return JSONResponse(content=result)
