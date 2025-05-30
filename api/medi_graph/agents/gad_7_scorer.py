import json

from typing import List, Dict
from enum import Enum
from pydantic import BaseModel
from langgraph.graph import (
    END,
)
from langgraph.prebuilt import (
    create_react_agent,
)

from pydantic import BaseModel
from typing import List

from ..llm import llm_model
from ..utils import extract_json_from_message
from ..types import MetricEnum, ProgressEnum


class GAD7Item(str, Enum):
    nervous = "nervous"
    uncontrollable_worry = "uncontrollable_worry"
    worrying_too_much = "worrying_too_much"
    trouble_relaxing = "trouble_relaxing"
    restlessness = "restlessness"
    irritability = "irritability"
    fear_of_something_awful = "fear_of_something_awful"


class TherapySession(BaseModel):
    therapy_session_number: int
    estimated_scores: Dict[GAD7Item, int]
    total_score: int
    justification: str


class GAD7AgentOutput(BaseModel):
    client_id: str
    sessions: List[TherapySession]
    progress_summary: str
    progress_status: ProgressEnum


gad_7_scorer_agent = create_react_agent(
    model=llm_model,
    tools=[],
    prompt=(
        """
        You are a psychological assessment agent specializing in estimating GAD-7 anxiety scores based on therapist session notes.

        **Objective:**
        For each therapy session, estimate the GAD-7 anxiety score using the client’s described symptoms. Then compare scores across sessions to assess changes in anxiety severity.

        **Instructions:**
        1. **Analyze Sessions Individually:** Use `therapy_session_number` to identify and assess each session independently. Carefully interpret all described symptoms and context.
        2. **Score Each GAD-7 Item (0–3):** Evaluate the client’s state using the 7 GAD-7 items:
        - 0 = Not at all
        - 1 = Several days
        - 2 = More than half the days
        - 3 = Nearly every day  
        Use judgment based on intensity, frequency, and duration. If an item isn’t explicitly mentioned but is reasonably implied (e.g., “feeling overwhelmed” → “worrying too much”), infer with justification. Otherwise, score 0.
        3. **Total Score:** Sum all 7 items to compute the total GAD-7 score for each session.
        4. **Justification:** Provide a brief justification per session, referencing key quotes or observations that explain the chosen scores.
        5. **Progress Evaluation:** Compare total scores across sessions to determine progress:
        - **Improving:** Significant decrease (e.g., 15 → 5)
        - **Plateau:** Minimal or no change (e.g., 10 → 11)
        - **Deteriorating:** Significant increase (e.g., 5 → 15)

        **Output Format:**
        ```json
        {
        "client_id": "client1",
        "sessions": [
            {
            "therapy_session_number": 1,
            "estimated_scores": {
                "nervous": 2,
                "uncontrollable_worry": 2,
                "worrying_too_much": 2,
                "trouble_relaxing": 1,
                "restlessness": 0,
                "irritability": 1,
                "fear_of_something_awful": 1
            },
            "total_score": 9,
            "justification": "Client described moderate anxiety for six weeks, feeling overwhelmed due to procrastination and workload. Trouble relaxing inferred from stress. Irritability and mild fear inferred from context. No signs of restlessness."
            },
            {
            "therapy_session_number": 2,
            "estimated_scores": {
                "nervous": 1,
                "uncontrollable_worry": 1,
                "worrying_too_much": 1,
                "trouble_relaxing": 0,
                "restlessness": 0,
                "irritability": 0,
                "fear_of_something_awful": 0
            },
            "total_score": 3,
            "justification": "Client reported reduced anxiety, better task management, and increased confidence. Items 1–3 scored mildly. No evidence of other symptoms."
            }
        ],
        "progress_status": "Improving",
        "progress_summary": "GAD-7 score decreased from 9 (moderate anxiety) to 3 (minimal anxiety), indicating strong therapeutic progress and symptom reduction."
        }
    """
    ),
    name="gad_7_scorer_agent",
    response_format=GAD7AgentOutput.model_json_schema()
)


def gad_7_scorer_node(state):
    """
    GAD-7 Scorer node that uses the GAD-7 agent to score therapy sessions.
    """
    all_therapy_sessions = state.all_therapy_sessions
    new_messages = state.messages.copy()
    if not all_therapy_sessions:
        return END

    combined_data = []

    for data in all_therapy_sessions:

        symptoms = [
            {
                "description": s["Description"],
                "onset": s["Onset"],
                "frequency": s["Frequency"],
                "ascendance": s["Ascendance"],
                "intensity": s["Intensity"],
                "duration": s["Duration"],
                "quote": s["Quote (Symptom)"]
            }
            for s in data["Psychological Factors"]["Symptoms"].values()
        ]

        diagnosis = [
            {
                "dsm_5_diagnosis": d["Description"],
                "dsm_5_code": d.get("DSM- Code", "NA"),
                "icd_10_code": d.get("ICD- Code", "NA"),
            } for d in data["Clinical Assessment"]["Diagnosiss"].values()
        ]

        anxiety_json = {
            "therapy_session_number": data["therapy_session_number"],
            "client_id": data["client_id"],
            "chief_complaint": data["Presentation"]["Chief Complaint"],
            "symptoms": symptoms,
            "sleep": data["Biological Factors"]["Sleep"],
            "physical_activity": data["Biological Factors"]["Physical Activity"],
            "mood_and_affect": data["Mental Status Exam"]["Mood and Affect"],
            "thought_process_and_content": data["Mental Status Exam"]["Thought Process and Content"],
            "cognition": data["Mental Status Exam"]["Cognition"],
            "speech_and_language": data["Mental Status Exam"]["Speech and Language"],
            "risk_quote": data["Risk Assessment"]["Quote (Risk)"],
            "diagnosis": diagnosis
        }

        combined_data.append(anxiety_json)

    if not combined_data:
        return END

    prompt = f"""
    {json.dumps(combined_data, indent=2)}
    """
    res = gad_7_scorer_agent.invoke({
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })
    if res.get("error"):
        print(f"Error in GAD-7 Scorer node: {res['error']}")
        return END

    if not res.get("structured_response"):
        last_msg = res["messages"][-1].content if res.get("messages") else ""
        parsed = extract_json_from_message(last_msg)
        if parsed:
            gad_7_output = GAD7AgentOutput.model_validate(parsed)
        else:
            print("No valid JSON found in message content.")
            return END
    else:
        gad_7_output = GAD7AgentOutput.model_validate(
            res["structured_response"])

    state.output = gad_7_output
    state.metric = MetricEnum.gad_7
    new_messages.extend(
        res["messages"] if res["messages"] else []
    )

    return state.model_copy(
        update={
            "messages": new_messages
        }
    )
