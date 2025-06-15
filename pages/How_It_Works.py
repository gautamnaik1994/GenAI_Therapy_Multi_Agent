import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="How It Works", layout="wide")
st.title("How this app works")

st.markdown("""
## Overview

**Therapy Agent** is an advanced system for analyzing medical and therapy sessions. It processes session transcripts, automatically scores mental health assessments (GAD-7, PHQ-9), and visualizes client progress over time.

---
""")

st.markdown("""
## Key Features

- **Session Parsing:** Efficiently reads and processes semi-structured session transcripts.
- **Agentic Reasoning:** Employs a graph of specialized agents (scorers, supervisors) for modular, extensible analysis.
- **Automated Assessment Scoring:** Accurately scores GAD-7 and PHQ-9 assessments directly from session text.
- **Visualization:** Presents client progress, assessment trends, and therapy insights in an interactive UI.

---
""")

st.markdown("""
## How to Use

### Upload multiple therapy session files

   You can upload a file containing multiple therapy session data. The file should be in JSON format and contain an array of session objects in the following format.  
   Open the following file to see an example of a therapy session data. For this demo app we are using a sample session files from the `medi_graph/sample_data` directory.
""")

sample_path1 = Path("./medi_graph/sample_data/client3_session1.txt")
with open(sample_path1, "r") as f:
    session_data = json.load(f)
st.text("Session 1")
st.json(session_data, expanded=False)

sample_path2 = Path("./medi_graph/sample_data/client3_session2.txt")
with open(sample_path2, "r") as f:
    session_data = json.load(f)
st.text("Session 2")
st.json(session_data, expanded=False)

sample_path3 = Path("./medi_graph/sample_data/client3_session3.txt")
with open(sample_path3, "r") as f:
    session_data = json.load(f)
st.text("Session 3")
st.json(session_data, expanded=False)


st.markdown("""
### Data is processed by AI Agent

   The uploaded data is processed by a modular agentic framework. The architecture is shown below:
""")

img_path = "./img/agents_graph.png"
if Path(img_path).exists():
    st.image(img_path, caption="AI Agent Architecture", width=500)
else:
    st.info("Architecture diagram not found (img/agents_graph.png).")

st.markdown("""
- The **Supervisor Agent** receives the therapy session data and tries to determine the diagnosis by keyword search.
- If the diagnosis is not clear, the agent consults the LLM API for further insights.
- Depending on the diagnosis (anxiety or depression), the agent routes to the appropriate specialist agent (GAD-7 or PHQ-9 scorer).
- The specialist agent analyzes all session data and generates a summary of the client's progress, which is displayed in the frontend.

---
""")

st.markdown("""
### Output

The output of the Therapy Agent includes:

- **Automated Assessment Scores:** GAD-7 and PHQ-9 scores are automatically calculated and presented.
- **Client Progress Visualizations:** Interactive charts and graphs show client progress over time.
- **Session Summaries:** Key insights and summaries from each therapy session are provided.
            
""")

sample_response = Path("./medi_graph/sample_data/sample_response.json")
with open(sample_response, "r") as f:
    response_data = json.load(f)
st.text("Response from the Agent")
st.json(response_data, expanded=False)


st.markdown("""
## Research and Design

- **Project Objective:** Track and analyze mental health assessments across multiple therapy sessions, extracting and quantifying clinical information from free-text data using LLMs.
- **Domain Exploration:** In-depth research into GAD-7 and PHQ-9 assessments, their clinical significance, and scoring criteria.
- **System Design:** Chose an agentic reasoning framework (LangGraph) for modularity and extensibility, enabling seamless integration of new assessments and agents.
- **Prompt Engineering:** Prompts are engineered to focus on transcript sections most relevant to assessment criteria, improving accuracy and efficiency.
- **Hybrid Diagnosis:** Combines brute-force keyword search with LLM-based reasoning for efficient and accurate diagnosis.
- **Output Structuring:** Uses Pydantic models to ensure consistent, actionable, and user-friendly results, including summaries, symptom highlights, and detailed score breakdowns.
- **Model Evaluation:** Benchmarked open-source (Llama 3) and proprietary (GPT-4.1) LLMs; GPT-4.1 is recommended for production.

---
""")

st.markdown("""
## Challenges and Lessons Learned

- **Data Complexity:** Extracting structured insights from nuanced, free-text clinical notes required careful prompt engineering and iterative refinement.
- **Token Efficiency:** Managing LLM context windows and minimizing unnecessary input was critical for performance and cost.
- **User-Centric Design:** Structuring outputs for real-world clinical utility involved close consideration of therapist workflows and information needs.

---
""")

st.markdown("""
## Scope for Improvement

- **Session Count Limitation:** Current implementation tested on up to 3 sessions per client. Scaling to more sessions will require batching and summarization strategies.
- **Extending Agent Capabilities:** Future work could include additional assessments (e.g., PTSD, OCD) and more complex reasoning agents.
- **Enhanced Visualization:** More advanced data visualizations (e.g., heatmaps, trend analysis) can provide deeper insights into client progress.

---
""")

st.markdown("""
## Demo Video

[![Demo Video](http://img.youtube.com/vi/-9N9Gt9KL6E/0.jpg)](http://www.youtube.com/watch?v=-9N9Gt9KL6E "Demo Video")

---
""")
