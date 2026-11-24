from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from weather_agent.schemas import tool_catalog

# folder this file lives in: .../weather_agent/prompts/ (where the .jinja files are)
TEMPLATES_DIR = Path(__file__).resolve().parent

_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=False,          # prompts are plain text, not HTML
    undefined=StrictUndefined, # raise an error if a template uses a variable you didn't pass
)


def render_template(name: str, **context) -> str:
    return _env.get_template(name).render(**context)


def build_system_prompt(*, extra_guidance: str = "") -> str:
    return render_template(
        "system.jinja",
        tools=tool_catalog(),
        extra_guidance=extra_guidance,
    )


def build_greeting_prompt() -> str:
    return render_template("greeting.jinja")