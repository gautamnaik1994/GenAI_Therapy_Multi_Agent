# from langchain_community.cache import InMemoryCache
# from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache
from langchain_openai import ChatOpenAI
from langchain_together import ChatTogether
import os

from dotenv import load_dotenv


# from langchain_google_genai import ChatGoogleGenerativeAI
# set_llm_cache(InMemoryCache())
# from langchain_groq import ChatGroq


load_dotenv()

# set_llm_cache(SQLiteCache(database_path=".langchain.db"))


# def get_google_llm():
#     return ChatGoogleGenerativeAI(
#         temperature=0,
#         max_output_tokens=512,
#         model="gemini-2.0-flash",
#         # model="gemini-2.5-flash-preview-05-20",
#         #  model= "gemini-2.5-pro-preview-05-06",
#         verbose=False,
#     )


# def get_groq_llm():
#     return ChatGroq(
#         model="qwen-qwq-32b",
#         temperature=0,
#     )


def get_chat_together_llm():
    return ChatTogether(
        api_key=os.getenv("TOGETHER_AI_API_KEY"),
        temperature=0.0,
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    )


def get_openai_llm():
    return ChatOpenAI(
        model="gpt-4.1",
        temperature=0.0,
        api_key=os.getenv("OPENAI_API_KEY"),
        verbose=False,
    )


llm_model = get_openai_llm()
