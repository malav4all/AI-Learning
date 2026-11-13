import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal


load_dotenv()


Model ="gpt-4o-mini"

_client  = None


def get_client():
    """Create the Open AI client only when and API Section actually runs"""
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI()
    return _client



def ask(prompt,system=None,temperature = 0):
    """Send One prompt and return the reply text."""
    messages = []
    if system:
        messages.append({"role":"system","content":system})
    messages.append({"role":"user","content":prompt})
    response = get_client().chat.completions.create(
        model=Model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content.strip()


def parse(message,schema):
    """Structure Output with a pydantic schema. Work on new and older openai SDK"""
    client  = get_client()
    try:
        response = client.chat.completions.parse(
            model=Model,
            messages=message,
            response_format=schema
        )
    except AttributeError:
        response = client.chat.completions.parse(
            model=Model,
            messages=message,
            response_format=schema
        )
    return response.choices[0].message.parsed


def header(title):
    print("\n" + "="* 70)
    print(title)
    print("=" * 70)



# ---------------------------------------------------------------------------
# 1. PERSONA-BASED PROMPTING
#    Same question, three personas -> three different styles of answer.
# ---------------------------------------------------------------------------


PERSONAS = {
    "Teacher for kids": (
        "You are a friendly school teacher explaining to a 10-year-old. "
        "Use very simple words and one fun example. Max 3 sentences."
    ),
    "Senior ML engineer": (
        "You are a senior ML engineer with 10 years of experience, talking to "
        "a fellow engineer. Be precise and technical. Max 3 sentences."
    ),
    "Strict interviewer": (
        "You are a strict technical interviewer. Do not explain the answer. "
        "Ask the candidate 2 sharp follow-up questions about the topic."
    ),
}


def demo_persona():
    header("1. Persona-based Prompting")
    question = "What is Overfitting?"
    print("Question:",question)
    for name,persona in PERSONAS.items():
        print(f"\n---Persona:{name}-----")
        print(ask(question,system=persona))
    print("\nNotice: same question, different tone, depth and even task.")
    print("The persona changes style and focus, not the model's knowledge.")



# ---------------------------------------------------------------------------
# 2. STRUCTURED OUTPUT: three levels
# ---------------------------------------------------------------------------

REVIEW = "The delivery was late and the packaging was torn,but the phone work fine."

def demo_structured_level1_prompt_only():
    header("2a. Structure Output level 1: just ask for json in the prompt")
    reply = ask(
        'Extract from this review. Return only JSON Like',
        '{"sentiment":".....","issue":"...","rating":1-5}\n\n'+ REVIEW
    )
    print("Raw Reply:\n",reply)
    try:
        data = json.loads(reply)
        print("Parsed Ok:",data)
    except json.JSONDecodeError:
              print("json.loads FAILED. The model probably added ```json or extra text.")
    print("Notice: usually works, but nothing guarantees it.")



def demo_structure_level2_json_mode():
    header("2b. Structure Output level 2: JSON Mode")
    response = get_client().chat.completions.create(
        model=Model,
        response_format={"type":"json_object"},
        temperature=0,
        messages=[
            {
                "role":"system",
                "content":"Extract review details. Reply in JSON With keys:"
                "sentiment,issue,rating(1-5)."
            },
            {
                "role":"user",
                "content":REVIEW
            }
        ]
    )

    data = json.loads(response.choices[0].message.content)
    print("Parsed:",data)
    print("sentiment--->",data.get("sentiment"))



class Review(BaseModel):
    sentiment:Literal["Postive","Negative","Mixed"]
    issues:list[str]
    rating:int

def demo_structured_level3_schema():
    header("2c. STRUCTURED OUTPUT, LEVEL 3: Pydantic schema")
    review = parse(
        [
            {"role": "system", "content": "Extract review details. Rating is 1-5."},
            {"role": "user", "content": REVIEW},
        ],
        Review,
    )

    print("Python object:", review)
    print("sentiment:", review.sentiment)
    print("issues:   ", review.issues)
    print("rating:   ", review.rating)
    print("As JSON:  ", review.model_dump_json())
    print("Notice: exact keys and types, no json.loads needed.")

def demo_structured_batch():
    header("2d. REAL USE: turn messy reviews into a clean table")
    reviews = [
        "Amazing battery life, totally worth the price!",
        "Screen cracked in a week. Customer care never replied.",
        "Camera is good but the phone heats up while gaming.",
    ]
    print(f"{'Sentiment':<10} | {'Rating':<6} | Issues")
    print("-" * 60)
    for text in reviews:
        r = parse(
            [
                {"role": "system", "content": "Extract review details. Rating is 1-5."},
                {"role": "user", "content": text},
            ],
            Review,
        )
        print(f"{r.sentiment:<10} | {r.rating:<6} | {', '.join(r.issues) or '-'}")


# ---------------------------------------------------------------------------
# 3. CoT + STRUCTURED OUTPUT
#    Reasoning field FIRST, answer field LAST. Order matters.
# ---------------------------------------------------------------------------

QUESTION = (
    "A bakery had 23 cookies. 20 were sold in the morning. The baker made 6 more. "
    "4 more were sold in the afternoon. Each cookie costs $3. "
    "How much money did the bakery make today?"
)


class AnswerWithReasoning(BaseModel):
    steps:list[str] #1. Think first 
    final_answere:int #2. Answere last


class AnswerFirst(BaseModel):
    final_answer: int  # answer is written before any reasoning
    steps: list[str]

def demo_cot_structured():
    header("3. CoT + STRUCTURED OUTPUT")
    system = "Solve the problem. Show your reasoning in 'steps'."
 
    good = parse(
        [{"role": "system", "content": system}, {"role": "user", "content": QUESTION}],
        AnswerWithReasoning,
    )
    print("(a) steps FIRST, answer LAST")
    for i, s in enumerate(good.steps, 1):
        print(f"   {i}. {s}")
    print("final_answer:", good.final_answere)
 
    bad = parse(
        [{"role": "system", "content": system}, {"role": "user", "content": QUESTION}],
        AnswerFirst,
    )
    print("\n(b) answer FIRST, steps LAST")
    print("   final_answer:", bad.final_answer)
    for i, s in enumerate(bad.steps, 1):
        print(f"   {i}. {s}")
 
    print("\nCorrect answer: (20 + 4) x 3 = 72")
    print("Notice: in (b) the answer is written before any thinking, so the steps")
    print("can only justify it afterwards. Bigger models may still get it right;")
    print("try a harder question or a smaller model to see the difference clearly.")

        
if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("\OPENAI_API_KEY is not set, so sections 1-3 were skipped.")
        print("Add it to your .env file and run again.")
    else:
        demo_cot_structured()
