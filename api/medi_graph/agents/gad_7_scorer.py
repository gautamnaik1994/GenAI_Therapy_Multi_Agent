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
from ..types import ProgressEnum


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
    You are a highly analytical psychological assessment agent specializing in anxiety scoring based on therapist notes.
    Your primary function is to estimate a GAD-7 anxiety score (Generalized Anxiety Disorder 7-item scale) for a client based on provided therapy session notes.
    You will then compare the scores from two or more consecutive sessions and report the change in anxiety levels. 

    **Instructions:**
    1.  **Analyze Each Therapy Session Individually:** Use the `therapy_session_number` as a reference to the therapy session number. For each therapy session provided, carefully read all the fields.
    2.  **Estimate GAD-7 Score per Session:** Map the described client's state and symptoms to the 7 GAD-7 items. Assign a score (0-3) for each item based on the *intensity*, *frequency*, and *duration* described in the notes.If an item is not explicitly mentioned but can be *reasonably inferred* from other descriptions (e.g., "overwhelmed" might infer "worrying too much"), make that inference and justify it. If no reasonable inference can be made, score 0.
    3.  **Calculate Total GAD-7 Score:** Sum the scores for all 7 items for each therapy session.
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
            "nervous": 2,
            "uncontrollable_worry": 2,
            "worrying_too_much": 2,
            "trouble_relaxing": 1,
            "restlessness": 0,
            "irritability": 1,
            "fear_of_something_awful": 1
        },
        "total_score": 9,
        "justification": "The client reported 'feeling anxious and stressed recently,' with symptoms described as moderate and lasting approximately six weeks. He felt 'overwhelmed' due to procrastination and taking on too many tasks, which supports moderate scores for items 1-3. Trouble relaxing is inferred from feeling overwhelmed (score 1). No evidence of restlessness (score 0). Some irritability is inferred from stress and overwhelm (score 1). Mild fear of something awful is inferred from the anxiety context (score 1). No mention of severe or persistent symptoms for higher scores."
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
        "justification": "The client reported a 'significant reduction in anxiety and stress,' with symptoms now described as mild and occasional. He feels more confident and is managing tasks better, indicating improvement in items 1-3 (score 1 each). No evidence of trouble relaxing, restlessness, irritability, or fear, so these are scored 0. The overall tone is positive, and the client is actively using coping strategies."
        }
    ],
    "progress_summary": "The client's GAD-7 score decreased from 9 (moderate anxiety) in session 1 to 3 (minimal anxiety) in session 2, indicating significant improvement in anxiety symptoms and effective response to therapy interventions."
    }
    ```
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
    print("GAD-7 Scorer response:")
    print(res)
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
    new_messages.extend(
        res["messages"] if res["messages"] else []
    )

    return state.model_copy(
        update={
            "messages": new_messages
        }
    )
