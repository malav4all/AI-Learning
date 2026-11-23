from dataclasses import dataclass
from openai import OpenAI

import os 

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Provider:
    name:str
    env_var:str
    is_free:bool
    base_url:str | None
    model:str

PROVIDERS = [
    Provider(
        name="OpenAI",
        env_var="OPENAI_API_KEY",
        is_free=False,
        base_url=None,
        model="gpt-4o-mini"
    )
]

def select_provider()-> Provider:
    for provider in PROVIDERS:
        if os.getenv(provider.env_var):
            return provider
    raise RuntimeError(f"No Provider Found")


def get_client_and_model()->tuple[OpenAI,str,Provider]:
    provider = select_provider()
    api_key  = os.getenv(provider.env_var)
    if provider.base_url in None:
        client = OpenAI(api_key=api_key)
    else:
        client = OpenAI(api_key=api_key,base_url=provider.base_url)
    return client,provider.model,provider
