import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # make `weather_agent` importable

import streamlit as st

from weather_agent.agent import run_agent_turns
from weather_agent.client import get_client_and_model
from weather_agent.prompts import build_greeting_prompt, build_system_prompt

st.set_page_config(page_title="Weather Agent", page_icon="🌤️", layout="centered")

st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem; max-width: 820px;}
      .hero {padding: 1.4rem 1.6rem; border-radius: 16px;
             background: linear-gradient(135deg, #1e3a8a 0%, #0ea5e9 100%);
             color: white; margin-bottom: 1.2rem;}
      .hero h1 {margin: 0; font-size: 1.9rem;}
      .hero p  {margin: .35rem 0 0; opacity: .9;}
      div[data-testid="stChatMessage"] {border-radius: 14px;}
    </style>
    """,
    unsafe_allow_html=True,
)
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

with st.sidebar:
    st.header("🌤️ Weather Agent")
    st.markdown(build_greeting_prompt())
    st.divider()

    st.subheader("Provider")
    try:
        _client, model, provider = get_client_and_model()
        st.success(f"**{provider.name}**  \nModel: `{model}`")
        provider_ok = True
    except RuntimeError as e:
        st.error(f"No provider configured.\n\n{e}")
        provider_ok = False

    st.divider()
    st.subheader("System prompt")
    st.caption("Rendered from `system.jinja`. This is what the agent sees before your messages.")
    with st.expander("Preview rendered prompt"):
        st.code(build_system_prompt(), language="markdown")

    st.divider()
    st.metric("Messages in chat", len(st.session_state.chat_log))
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.chat_log = []
        st.rerun()

st.markdown(
    """
    <div class="hero">
      <h1>🌤️ Live Weather Agent</h1>
      <p>Ask about temperature, wind or sky conditions anywhere in the world.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

EXAMPLES = [
    "What's the weather in New Delhi right now?",
    "Is it windy in London today?",
    "Compare the temperature in Tokyo and Mumbai",
]
if not st.session_state.chat_log:
    st.caption("Try one of these:")
    cols = st.columns(len(EXAMPLES))
    for col, example in zip(cols, EXAMPLES):
        if col.button(example, use_container_width=True):
            st.session_state.pending_prompt = example
            st.rerun()

AVATARS = {"user": "🧑", "assistant": "🌤️"}
for entry in st.session_state.chat_log:
    if entry.get("content"):
        with st.chat_message(entry["role"], avatar=AVATARS.get(entry["role"])):
            st.markdown(entry["content"])

typed = st.chat_input("Ask about the weather…", disabled=not provider_ok)
prompt = typed or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if prompt:
    st.session_state.chat_log.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("Checking the skies…"):
            try:
                # run_agent_turns appends the assistant answer to chat_log itself
                answer = run_agent_turns(st.session_state.chat_log)
                st.markdown(answer)
            except Exception as e:
                st.error("Something went wrong while talking to the agent.")
                with st.expander("Error details"):
                    st.exception(e)