from openai import OpenAI
from devtools import debug
from collections import deque
import base64

from src.load_config import OPENAI_PROJECT_API_KEY, OPENAI_PROJECT_NAME, DEV_MESSAGE

# https://platform.openai.com/docs/guides/text-generation?example=completions

client = OpenAI(api_key=OPENAI_PROJECT_API_KEY,
                       project=OPENAI_PROJECT_NAME)


devmessage = DEV_MESSAGE
print(f"devmessage={devmessage}")

messages = deque(maxlen=20)


def gptimage1(prompt: str, quality="medium") -> str:
    """
    https://platform.openai.com/docs/guides/image-generation
    https://platform.openai.com/docs/models/gpt-image-1
    """
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size="auto",
        quality="medium" # high, auto
    )
    # Available sizes:
    #   - 1024x1024  (square)
    #   - 1536x1024  (landscape)
    #   - 1024x1536  (portrait)
    #   - auto       (default)
    #
    # Quality options:
    #   - low
    #   - medium
    #   - high
    #   - auto       (default)
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    return image_bytes


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