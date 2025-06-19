from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage
from services.helpers import get_env_value
import os

os.environ["AZURE_OPENAI_API_KEY"] = get_env_value('AZURE_OPENAI_API_KEY')
os.environ["AZURE_OPENAI_ENDPOINT"] = get_env_value('AZURE_OPENAI_ENDPOINT')
OPENAI_API_VERSION = get_env_value('OPENAI_API_VERSION')
AZURE_MODEL_NAME = get_env_value('AZURE_MODEL_NAME')


class OpenAIService:
    def __init__(self):
        self.model = AzureChatOpenAI(azure_deployment=AZURE_MODEL_NAME,
                                     api_version=OPENAI_API_VERSION,
                                     temperature=0,
                                     presence_penalty=0,
                                     frequency_penalty=0)

    async def make_llm_call(self, prompt: str):
        messages = [SystemMessage(content=prompt)]
        response = await self.model.ainvoke(messages)
        parsed_response = response.content.strip()
        return parsed_response

