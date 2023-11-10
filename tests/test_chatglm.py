
import openai
from langchain.adapters.openai import convert_message_to_dict
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

if __name__ == "__main__":
    system_message_prompt = SystemMessagePromptTemplate.from_template("你是一个导游")
    human_message_prompt = HumanMessagePromptTemplate.from_template("{text}")
    chat_prompt_template = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

    endpoint_url = "http://localhost:8000/v1"
    question = "北京和上海两座城市有什么不同？"

    openai.api_base = endpoint_url
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [convert_message_to_dict(m) for m in chat_prompt_template.format_messages(text=question)]
    )
    print(response)