import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


def create_model(model_name: str):
    return ChatOpenAI(
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        model_name=model_name,
    )
