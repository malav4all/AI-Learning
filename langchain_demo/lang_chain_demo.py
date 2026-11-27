import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder,PromptTemplate

load_dotenv()


OPENAI_MODEL = "gpt-4o-mini"
LOCAL_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
RUN_LOCAL_MODEL = True


def header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def get_openai_llm(tem = 0):
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=OPENAI_MODEL,temperature=tem)


# 1. WHAT IS LANGCHAIN: one common interface for every model
def section1_langchain_basic():
    header("1 LangChain Basic:llm.invoke()")

    llm = get_openai_llm()

    response = llm.invoke("what is the capital of india? one line")
    #AI Message
    print("Type of response:",type(response).__name__)

    print("Text:",response.content)

    response = llm.invoke([
        ("system","You answer in exactly 5 word"),
        ("human","what is machine learning")
    ])


    print("with System Role:",response.content)


# 2. HUGGING FACE PIPELINE: tokenize + model + decode in one line
_hf_pipe_cache  = {}
def get_hf_pipeline(**generation_kwargs):
    """Load the local model once,reuse it every section"""
    from transformers import pipeline

    if "pipe" not in _hf_pipe_cache:
        print(f"Loading {LOCAL_MODEL} (First time download -1GB)...")
        _hf_pipe_cache["pipe"] = pipeline('text-generation',model=LOCAL_MODEL)
    return _hf_pipe_cache["pipe"]


def section2_hf_pipeline():
    header("2. HUGGING FACE PIPELINE (no LangChain yet)")

    pipe = get_hf_pipeline()


    tokenizer = pipe.tokenizer
    text = "The capital of india is"
    tokenids = tokenizer.encode(text)
    print("text:",text)
    print("Token ids:",tokenids)
    print("Tokens:",tokenizer.convert_ids_to_tokens(tokenids))

    #  One call does tokenize -> generate -> decode

    result = pipe(text,max_new_tokens = 15,do_sample=False,return_full_text=False)
    print("\nGenerated:", result[0]["generated_text"])

    # Chat style: the pipeline applies the model's chat template for you

    chat = [{"role":"user","content":"Explain AI in one simple line."}]
    result = pipe(chat,max_new_tokens=40,do_sample=False)
    print("Chat_reply:",result[0]["generated_text"][-1]["content"])


# 3. INTEGRATING HF PIPELINE WITH LANGCHAIN: the "adapter"


def section3_hf_in_langchain():
    header("3. HuggingFacePipeline + ChatHuggingFace (LangChain adapter)")

    from langchain_huggingface import ChatHuggingFace,HuggingFacePipeline

    llm = HuggingFacePipeline(
        pipeline=get_hf_pipeline(),
        pipeline_kwargs={
            "max_new_tokens":60,
            "do_sample":False,
            "return_full_text":False
        }
    )

    print("Plain LLM (text in ,textout)")

    print(" ",llm.invoke("Q:What is Python?\na").strip())

    # Wrap it as a chat model: now roles work and the chat template is applied
    chat_llm = ChatHuggingFace(llm=llm)
    reply = chat_llm.invoke([
        ("system","You are a friendly Teacher,answer in one line."),
        ("human","What is a neural network?")
    ])

    print("\chat models with roles:")
    print(" ,",reply.content.strip())


# 5. WHAT IS A PROMPT TEMPLATE (no LLM needed)

def section5_prompt_template_basics():
    header("5. PROMPT TEMPLATE BASICS (no API needed)")
    template = PromptTemplate.from_template(
        "Explain {topic} to a {audience}. in {n} simple lines."
    )

    print("Varibale Found:",template.input_variables)

    for topic,audience in [("overfitting","10-year-old"),("RAG","manager")]:
        print("->",template.format(topic=topic,audience=audience,n=3))


    try:
        template.format(topic="LLMs")
    except KeyError as e:
        print("\n Missing variable error",e)

    for_kids = template.partial(audience="10-year-old",n=2)
    print("\n partial template still needs:",for_kids.input_variables)
    print("->",for_kids.format(topic="the internet"))

# 6. CODING PROMPT TEMPLATES: chains with the | pipe (LCEL)

def build_explain_chain(llm):
    template = PromptTemplate.from_template(
        "Explain {topic} to a {audience} in {n} simple lines"
    )

    return template | llm | StrOutputParser()


def build_fewshot_chain(llm):
     template = PromptTemplate.from_template(
        "Classify the review. Answer with one word only.\n\n"
        '"Fast delivery, great quality" -> Positive\n'
        '"It broke in two days" -> Negative\n'
        '"It\'s okay, nothing special" -> Neutral\n\n'
        '"{review}" ->'
    )

     return template | llm | StrOutputParser()


def section6_template_chains():
    header("6. PROMPT TEMPLATE CHAINS: template | llm | parser")
    llm = get_openai_llm()
    chain  = build_explain_chain(llm)
    print(chain.invoke({"topic":"overfitting","audience":"10-year-old","n":3}))
    print("\nFew-shot template, run on many reviews with .batch():")
    reviews = ["The packaging was torn", "Best phone I ever bought", "Works, I guess"]
    results = build_fewshot_chain(llm).batch([{"review": r} for r in reviews])
    for r, label in zip(reviews, results):
        print(f"  {r:<28} -> {label.strip()}")

    print("\nNotice: .invoke() = one input, .batch() = many inputs at once.")


# ---------------------------------------------------------------------------
# 7. ROLES WITH CHAT PROMPT TEMPLATE
# ---------------------------------------------------------------------------
PERSONA_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "You are a {persona}. Answer in {language} in at most 3 lines."),
    ("human", "{question}"),
])


def section7a_chat_template_basics():
    header("7a. CHAT PROMPT TEMPLATE: roles (no API needed)")
    messages = PERSONA_TEMPLATE.format_messages(
        persona="friendly teacher", language="Hinglish", question="What is overfitting?"
    )
    for m in messages:
        print(f"{type(m).__name__:<14} | {m.content}")

    print("\nRole names: LangChain 'human' = OpenAI 'user', 'ai' = 'assistant'.")


def section7b_personas():
    header("7b. ONE CHAT TEMPLATE, THREE PERSONAS")
    chain = PERSONA_TEMPLATE | get_openai_llm() | StrOutputParser()
    for persona in ["friendly teacher for kids", "senior ML engineer", "strict interviewer"]:
        print(f"\n--- {persona} ---")
        print(chain.invoke({
            "persona": persona,
            "language": "English",
            "question": "What is overfitting?",
        }))


def section7c_history():
    header("7c. CHAT HISTORY WITH MessagesPlaceholder")
    template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Keep answers to one line."),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ])
    chain = template | get_openai_llm() | StrOutputParser()

    history = []  # the API is stateless, so WE keep the memory
    for question in ["My name is Malav.", "I am learning LangChain.", "What is my name and what am I learning?"]:
        answer = chain.invoke({"history": history, "question": question})
        print(f"You: {question}\nBot: {answer}\n")
        history += [("human", question), ("ai", answer)]

if __name__ == "__main__":
    # Always runs: no key, no download
    section5_prompt_template_basics()
    section7a_chat_template_basics()

    if os.environ.get("OPENAI_API_KEY"):
        # section1_langchain_basics()
        section6_template_chains()
        section7b_personas()
        section7c_history()
    else:
        print("\nOPENAI_API_KEY not set: skipped sections 1, 6, 7b, 7c.")

    if RUN_LOCAL_MODEL:
        try:
            import langchain_huggingface  # noqa: F401
            import transformers  # noqa: F401
        except ImportError:
            print("\nSkipped sections 2-4. Install: pip install langchain-huggingface transformers torch")
        else:
            section2_hf_pipeline()
            section3_hf_in_langchain()
            # section4_parameters()
