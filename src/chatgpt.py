from openai import OpenAI
from devtools import debug
from collections import deque

from src.load_config import OPENAI_PROJECT_API_KEY, OPENAI_PROJECT_NAME, DEV_MESSAGE

# https://platform.openai.com/docs/guides/text-generation?example=completions

client = OpenAI(api_key=OPENAI_PROJECT_API_KEY,
                       project=OPENAI_PROJECT_NAME)


devmessage = DEV_MESSAGE
print(f"devmessage={devmessage}")

messages = deque(maxlen=20)


def gpt4o(s) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": devmessage},
            {"role": "user", "content": s}
        ]
    )
    # debug(completion)
    msg = completion.choices[0].message.content
    return msg


# TODO: put this in a class
def gpt4o_memory(s) -> str:
    # "system" was replaced with "developer" in the API
    messages.append({"role": "user", "content": s})
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": devmessage},
            *messages
        ]
    )
    response_str = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": response_str})
    return response_str


def gpt4o1_memory(s) -> str:
    # o1 does not accept the “developer” role, nor does it accept “system". 
    # This may change.
    messages.append({"role": "user", "content": s})
    completion = client.chat.completions.create(
        model="o1-mini",
        messages=[
            *messages
        ]
    )
    response_str = completion.choices[0].message.content
    return response_str