import time
from typing import Union

from openai import OpenAI
from openai import AsyncOpenAI
from openai.types import Image, ImageModel, ImagesResponse

from src.load_config import OPENAI_PROJECT_API_KEY, OPENAI_PROJECT_NAME
from src.schema import DalleRequest, DalleResponse, DalleRequestTest

openai_client = OpenAI(api_key=OPENAI_PROJECT_API_KEY,
                       project=OPENAI_PROJECT_NAME)


# check billing here:
# https://platform.openai.com/settings/organization/billing/overview
# TODO: is there an API call for this?
# TODO: https://community.openai.com/t/get-the-remaining-credits-via-the-api/18827/13

# base64 is preferred over image urls because the urls expire after 1 hour


def run_dalle_1(request: DalleRequest) -> DalleResponse:
    """Makes a call to the OpenAI API to generate an image."""

    # if it's a test request, return a test response
    if type(request) == DalleRequestTest:
        # TODO: base64?
        time.sleep(1)
        result = DalleResponse(
            b64_json=None,
            revised_prompt="revised prompt for DalleTestRequest",
            url="https://placehold.co/600x400.png",
        )
        return result
    
    try: # try to get the image (content policy violations etc)
        response = openai_client.images.generate(
            model=request.model,
            prompt=request.prompt,
            size=request.size,
            quality=request.quality,
            n=1,
        )

        result = DalleResponse(
            b64_json=None,
            revised_prompt=response.data[0].revised_prompt,
            url=response.data[0].url,
        )

    except Exception as e:
        result = DalleResponse(
            b64_json=None,
            revised_prompt="Error: " + str(e),
            url=None,
        )

    return result


async def run_dalle(model="dall-e-3", prompt="", size="1792x1024", quality="hd"):
    """
    DEPRECATED
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

