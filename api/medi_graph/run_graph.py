
from .graph import medic_graph
import sys
import os
import json
import re
from pathlib import Path


def run_langgraph_agent(all_therapy_sessions):

    result = medic_graph.invoke({
        "messages": [],
        "all_therapy_sessions": all_therapy_sessions,
        "diagnosis": "",
        "metric": None,
    })
    out = {}
    if isinstance(result, dict) and "output" in result:
        out = json.loads(result["output"].model_dump_json())
        out["diagnosis"] = result["diagnosis"].value
        out["metric"] = result["metric"].value

    return out


def run_langgraph_agent_using_sample_data(client_id: str = "client3"):

    base_path = Path(__file__).parent / "sample_data"

    if client_id == "client3":
        files = [
            base_path / f"{client_id}_session1.txt",
            base_path / f"{client_id}_session2.txt",
            base_path / f"{client_id}_session3.txt",
        ]
    else:
        files = [
            base_path / f"{client_id}_session1.txt",
            base_path / f"{client_id}_session2.txt",
        ]

    all_therapy_sessions = []

    for file_path in files:
        with open(file_path, "r") as f:
            print(f"Reading file: {file_path.resolve()}")
            session_data = json.load(f)
            base = file_path.name
            match = re.match(r'(client\d+)_session(\d+)\.txt$', base)
            if match:
                client_id = match.group(1)
                session_number = int(match.group(2))
            else:
                client_id = "NA"
                session_number = "NA"
            session_data["client_id"] = client_id
            session_data["therapy_session_number"] = session_number
            all_therapy_sessions.append(session_data)

    result = run_langgraph_agent(all_therapy_sessions)
    return result
