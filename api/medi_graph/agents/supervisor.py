import json

from typing import List
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

# from api.langgraph.graph import Route
from ..types import Route

from ..llm import get_chat_together_llm
from ..utils import extract_json_from_message


class ClassificationEnum(str, Enum):
    anxiety = "Anxiety"
    depression = "Depression"
    # both = "Both"
    neither = "Neither"


class ClassificationResult(BaseModel):
    classification: ClassificationEnum
    confidence: str
    reasoning: str
    supporting_symptoms: List[str] = []


supervisor = create_react_agent(
    model=get_chat_together_llm(),
    tools=[],
    prompt=(
        """
        You are a clinical classification assistant trained to detect anxiety and depression from structured therapy session data. Your task is to review psychological symptoms, mental status, client quotes, and other clinical observations to determine whether the patient likely has:

        - Anxiety
        - Depression
        - Neither

        Base your reasoning on the GAD-7 and PHQ-9 criteria.

        Return your output as a structured JSON object with the following fields:
        {
        "classification": "<Anxiety | Depression | Neither>",
        "confidence": "<Low | Medium | High>",
        "reasoning": "<A concise explanation of why this classification was made>",
        "supporting_symptoms": ["<brief symptom 1>", "<brief symptom 2>", ...]
        }
        Do not hallucinate diagnoses. Only rely on information present in the input.
    """
    ),
    name="supervisor",
    response_format=ClassificationResult.model_json_schema()
)


def supervisor_node(state):
    """
    Supervisor node that uses the supervisor agent to classify the therapy session data.
    """
    all_therapy_sessions = state.all_therapy_sessions
    new_messages = state.messages.copy()
    if not all_therapy_sessions:
        return END
    data = all_therapy_sessions[0]
    conceptualization = data["Clinical Assessment"]["Clinical Conceptualization"].lower(
    )

    depression_keywords = [
        "depression", "depressed", "dysthymia", "low mood", "sadness", "hopeless",
        "anhedonia", "tearful", "worthless", "guilt", "fatigue", "loss of interest",
        "loss of pleasure", "suicidal", "self-harm", "insomnia", "withdrawn",
        "pessimism", "self-blame", "helpless", "depressive"
    ]

    anxiety_keywords = [
        "anxiety", "anxious", "panic", "worry", "worried", "nervous", "restless",
        "fear", "phobia", "obsessive", "compulsive", "rumination", "hypervigilant",
        "irritability", "tension", "avoidance", "social anxiety", "panic attack",
    ]

    if any(word in conceptualization for word in depression_keywords):
        state.route = Route.depression
        print("Depression detected in clinical conceptualization, routing to depression.")
        return state

    if any(word in conceptualization for word in anxiety_keywords):
        state.route = Route.anxiety
        print("Anxiety detected in clinical conceptualization, routing to anxiety.")
        return state

    relevant_data = {
        "chief_complaint": data["Presentation"]["Chief Complaint"],
        "symptoms": data["Psychological Factors"]["Symptoms"],
        "mood_and_affect": data["Mental Status Exam"]["Mood and Affect"],
        "thought_content": data["Mental Status Exam"]["Thought Process and Content"],
        "cognition": data["Mental Status Exam"]["Cognition"],
        "hopelessness": data["Risk Assessment"]["Hopelessness"],
        "suicidal_thoughts": data["Risk Assessment"]["Suicidal Thoughts or Attempts"],
        "sleep": data["Biological Factors"]["Sleep"],
        # fixed key here
        "diagnosis": data["Clinical Assessment"]["Diagnosiss"],
        "client_quotes": {
            "chief_complaint_quote": data["Presentation"].get("Quote (Chief Complaint)", ""),
            "symptom_quotes": [s.get("Quote (Symptom)", "") for s in data["Psychological Factors"]["Symptoms"].values()],
            "risk_quote": data["Risk Assessment"].get("Quote (Risk)", "")
        }
    }
    prompt = f"""
    {json.dumps(relevant_data, indent=2)}
    """

    res = supervisor.invoke({
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })
    print("Supervisor response:")
    print(res)
    if res.get("error"):
        print(f"Error in supervisor node: {res['error']}")
        return END

    if not res.get("structured_response"):
        last_msg = res["messages"][-1].content if res.get("messages") else ""
        parsed = extract_json_from_message(last_msg)
        if parsed:
            classification = ClassificationResult.model_validate(parsed)
        else:
            print("No valid JSON found in message content.")
            return END
    else:
        classification = ClassificationResult.model_validate(
            res["structured_response"])

    diagnosis = classification.classification
    if diagnosis == ClassificationEnum.anxiety:
        state.route = Route.anxiety
    elif diagnosis == ClassificationEnum.depression:
        state.route = Route.depression
    # elif diagnosis == ClassificationEnum.both:
    #     state.route = Route.anxiety
    else:
        state.route = "end"

    state.diagnosis = diagnosis
    new_messages.extend(
        res["messages"] if res["messages"] else []
    )

    return state.model_copy(
        update={
            "messages": new_messages
        }
    )
