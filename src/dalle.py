from typing import Union

from openai import OpenAI
from openai import AsyncOpenAI
from openai.types import Image, ImageModel, ImagesResponse

from src.load_config import OPENAI_PROJECT_API_KEY, OPENAI_PROJECT_NAME
from src.schema import DalleRequest, DalleResponse

openai_client = OpenAI(api_key=OPENAI_PROJECT_API_KEY,
                       project=OPENAI_PROJECT_NAME)


# check billing here:
# https://platform.openai.com/settings/organization/billing/overview
# TODO: is there an API call for this?




def run_dalle_1(request: DalleRequest) -> DalleResponse:
    pass


async def run_dalle(model="dall-e-3", prompt="", size="1792x1024", quality="hd"):
    """
    dalle-3 limit is 7 images per minute
    dalle-2 limit is 50 images per minute
    urls will expire after 1 hour
    https://platform.openai.com/docs/guides/images/usage
    https://platform.openai.com/settings/organization/limits
    1024x1024, 1792x1024, or 1024x1792 for DALL·E-3
    """
    assert prompt, "Error: no prompt"
    response = openai_client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality, # or "hd"
        n=1,
    )
    revised_prompt = response.data[0].revised_prompt
    image_url = response.data[0].url
    return revised_prompt, image_url

