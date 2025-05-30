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
from ..types import ProgressEnum


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
    You are a highly analytical psychological assessment agent specializing in depression scoring based on therapist notes.
    Your primary function is to estimate a PHQ-9 depression score (Patient Health Questionnaire-9) for a client based on provided therapy session notes.
    You will then compare the scores from two or more consecutive sessions and report the change in depression levels.

    **Instructions:**
    1.  **Analyze Each Therapy Session Individually:** Use the `therapy_session_number` as a reference to the therapy session number. For each therapy session provided, carefully read all the fields.
    2.  **Estimate PHQ-9 Score per Session:** Map the described client's state and symptoms to the 9 PHQ-9 items. Assign a score (0-3) for each item based on the *intensity*, *frequency*, and *duration* described in the notes.
        -   **0 = Not at all**
        -   **1 = Several days**
        -   **2 = More than half the days**
        -   **3 = Nearly every day**
        If an item is not explicitly mentioned but can be *reasonably inferred* from other descriptions (e.g., "lack of motivation" might infer "little interest or pleasure in doing things"), make that inference and justify it. If no reasonable inference can be made, score 0.
    3.  **Calculate Total PHQ-9 Score:** Sum the scores for all 9 items for each therapy session.
    4.  **Justify Scores:** Provide a concise justification for the total score of each session, referencing specific details (quotes if available, or paraphrased observations) from the notes that led to your score.
    5.  **Structured Output:** Return the scores and justifications in a structured JSON format for each therapy session. Include the overall progress summary crafted based on score changes and carefully determine progress status based on the score changes and overall clinical context:
        -   **Improving**: If the total score decreased significantly (e.g., from 15 to 5), indicating a positive response to treatment.
        -   **Plateau**: If the total score remained stable (e.g., 10 to 11), indicating no significant change in symptoms.
        -   **Deteriorating**: If the total score increased (e.g., from 5 to 15), indicating worsening symptoms or response to treatment.

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
        "justification": "The client reported feeling 'constantly sad and lacking motivation for the past few weeks,' which supports high scores for feeling down (3) and little interest (2). She mentioned 'difficulty falling asleep most nights' (2) and feeling 'drained of energy' (2). Appetite was 'somewhat reduced' (1). She expressed 'guilt about not doing enough' (2). Concentration was 'a bit off' (1). No explicit mention of psychomotor changes or self-harm thoughts, so scored 0. Overall symptoms suggest moderately severe depression."
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
        "justification": "The client reported feeling 'better and more engaged in activities,' with 'some lingering sadness on a few days,' supporting mild scores for little interest (1) and feeling down (1). Sleep has 'improved but still occasionally restless' (1), and energy levels are 'better but still not fully restored' (1). No mention of appetite issues, self-worth issues, or concentration problems, so scored 0 for these. No indication of psychomotor changes or self-harm thoughts. Overall symptoms suggest minimal depression, indicating good progress."
        }
    ],
    "progress_status": "<Improving | Plateau | Deteriorating>",
    "progress_summary": "The client's PHQ-9 score decreased from 13 (moderately severe depression) in session 1 to 4 (minimal depression) in session 2, indicating significant improvement in depressive symptoms and positive response to therapeutic interventions."
    }
    ```
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
    print("PHQ 9 response:")
    print(res)
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
    new_messages.extend(
        res["messages"] if res["messages"] else []
    )

    return state.model_copy(
        update={
            "messages": new_messages
        }
    )
