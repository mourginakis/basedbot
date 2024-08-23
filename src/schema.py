from typing import Optional, Literal
import pydantic
from pydantic import BaseModel, Field

assert pydantic.__version__.startswith("2.")

# Notes:
# - The `Literal` type is used to restrict the possible values of a string.
# - Setting a parameter equal to something sets the default value, but it can still
#   be changed unless combined with Literal
# - Field() can also be used to set the default, and also additional constraints, 
#   like min_length, max_length, frozen, etc.
#

class DalleRequest(BaseModel):
    """Generic request for a dalle model"""
    model: Literal["dall-e-3", "dall-e-2"]
    prompt: str
    size: Optional[Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]]
    quality: Literal["standard", "hd"]
    cost: float
    response_format: Optional[Literal["url", "b64_json"]]

class DalleRequestHigh(DalleRequest):
    """Request a high quality dalle model (expensive)"""
    model: Literal["dall-e-3"] = "dall-e-3"
    prompt: str
    size: Literal["1792x1024"] = "1792x1024"
    quality: Literal["hd"] = "hd"
    cost: float = 0.12
    response_format: Optional[Literal["url", "b64_json"]]

class DalleRequestLow(DalleRequest):
    """Request a low quality dalle model (cheap)"""
    model: Literal["dall-e-2"] = "dall-e-2"
    prompt: str
    size: Literal["1024x1024"] = "1024x1024"
    quality: Literal["standard"] = "standard"
    cost: float = 0.02
    response_format: Optional[Literal["url", "b64_json"]]

class ImageResponse(BaseModel):
    """Dalle image response"""
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None
    url: Optional[str] = None

# TODO: can discord display base64 images?
