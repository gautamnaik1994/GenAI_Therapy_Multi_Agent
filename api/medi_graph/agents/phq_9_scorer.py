import json

from typing import Dict, List
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


class PHQ9Item(str, Enum):
    little_interest = "little_interest"
    feeling_down = "feeling_down"
    trouble_sleeping = "trouble_sleeping"
    feeling_tired = "feeling_tired"
    poor_appetite = "poor_appetite"
    feeling_bad_about_self = "feeling_bad_about_self"
    trouble_concentrating = "trouble_concentrating"
    slow_or_fast = "slow_or_fast"
    thoughts_of_self_harm = "thoughts_of_self_harm"


class TherapySessionPHQ9(BaseModel):
    therapy_session_number: int
    estimated_scores: Dict[PHQ9Item, int]
    total_score: int
    justification: str


class PHQ9AgentOutput(BaseModel):
    client_id: str
    sessions: List[TherapySessionPHQ9]
    progress_summary: str
    progress_status: ProgressEnum


phq_9_scorer_agent = create_react_agent(
    model=llm_model,
    tools=[],
    prompt=(
        """
        You are a psychological assessment agent specialized in estimating PHQ-9 depression scores from therapist notes.

        **Objective:**
        Analyze therapy session notes and estimate PHQ-9 scores for each session. Then compare scores across sessions to assess changes in depression severity.

        **Instructions:**
        1. **Session Analysis:** For each session (identified by `therapy_session_number`), read and interpret the client's reported state and symptoms.
        2. **Score Estimation (0–3 per item):** Map notes to the 9 PHQ-9 items. Score each based on *frequency*, *intensity*, and *duration*:
        - 0 = Not at all
        - 1 = Several days
        - 2 = More than half the days
        - 3 = Nearly every day  
        If an item is not explicitly mentioned but can be reasonably inferred (e.g., "no motivation" → "little interest"), do so with justification. Otherwise, assign 0.
        3. **Total Score:** Sum the 9 items to compute the PHQ-9 total for each session.
        4. **Justification:** Provide a concise explanation for each session's score, citing key statements or paraphrased descriptions.
        5. **Progress Evaluation:** Compare scores between sessions and determine overall status:
        - **Improving:** Significant decrease (e.g., 15 → 5)
        - **Plateau:** Minimal change (e.g., 10 → 11)
        - **Deteriorating:** Significant increase (e.g., 5 → 15)

        **Output Format:**
        ```json
        {
        "client_id": "client1",
        "sessions": [
            {
            "therapy_session_number": 1,
            "estimated_scores": {
                "little_interest": 2,
                "feeling_down": 3,
                "trouble_sleeping": 2,
                "feeling_tired": 2,
                "poor_appetite": 1,
                "feeling_bad_about_self": 2,
                "trouble_concentrating": 1,
                "slow_or_fast": 0,
                "thoughts_of_self_harm": 0
            },
            "total_score": 13,
            "justification": "Cited consistent sadness, lack of motivation, and low energy. Sleep difficulties and guilt also noted. No mention of psychomotor or self-harm."
            },
            {
            "therapy_session_number": 2,
            "estimated_scores": {
                "little_interest": 1,
                "feeling_down": 1,
                "trouble_sleeping": 1,
                "feeling_tired": 1,
                "poor_appetite": 0,
                "feeling_bad_about_self": 0,
                "trouble_concentrating": 0,
                "slow_or_fast": 0,
                "thoughts_of_self_harm": 0
            },
            "total_score": 4,
            "justification": "Reported increased engagement and energy. Mild lingering sadness. No major issues reported in other areas."
            }
        ],
        "progress_status": "Improving",
        "progress_summary": "The PHQ-9 score dropped from 13 (moderately severe) to 4 (minimal), indicating substantial improvement."
        }
    """
    ),
    name="phq_9_scorer_agent",
    response_format=PHQ9AgentOutput.model_json_schema()
)


def phq_9_scorer_node(state):
    """
    PHQ-9 Scorer node that uses the PHQ-9 agent to score therapy sessions.
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

        depression_json = {
            "therapy_session_number": data["therapy_session_number"],
            "client_id": data["client_id"],
            "chief_complaint": data["Presentation"]["Chief Complaint"],
            "symptoms": symptoms,
            "sleep": data["Biological Factors"]["Sleep"],
            "nutrition": data["Biological Factors"]["Nutrition"],
            "mood_and_affect": data["Mental Status Exam"]["Mood and Affect"],
            "cognition": data["Mental Status Exam"]["Cognition"],
            "hopelessness": data["Risk Assessment"]["Hopelessness"],
            "suicidal_thoughts_or_attempts": data["Risk Assessment"]["Suicidal Thoughts or Attempts"],
            "self_harm": data["Risk Assessment"]["Self Harm"],
            "diagnosis": diagnosis
        }

        combined_data.append(depression_json)

    if not combined_data:
        return END

    prompt = f"""
    {json.dumps(combined_data, indent=2)}
    """
    res = phq_9_scorer_agent.invoke({
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })

    if res.get("error"):
        print(f"Error in PHQ 9 node: {res['error']}")
        return END

    if not res.get("structured_response"):
        last_msg = res["messages"][-1].content if res.get("messages") else ""
        parsed = extract_json_from_message(last_msg)
        if parsed:
            phq_9_output = PHQ9AgentOutput.model_validate(parsed)
        else:
            print("No valid JSON found in message content.")
            return END
    else:
        phq_9_output = PHQ9AgentOutput.model_validate(
            res["structured_response"])

    state.output = phq_9_output
    state.metric = MetricEnum.phq_9
    new_messages.extend(
        res["messages"] if res["messages"] else []
    )

    return state.model_copy(
        update={
            "messages": new_messages
        }
    )
