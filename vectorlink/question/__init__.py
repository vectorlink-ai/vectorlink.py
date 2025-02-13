from typing import List
from openai import Client
import json
import openai
import backoff


@backoff.on_exception(
    backoff.constant,
    (json.decoder.JSONDecodeError,),
    max_tries=3,
    interval=0.01,
)
def generate_questions(text: str, examples: List[str] = []) -> List[str]:
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You generate questions based on given text. You generate 100 questions. Generate as a JSON list of questions. It is VERY important that it is JSON. Like, super important. Really, don't give anything back that is not JSON. Do NOT use markdown.\nExample output: ["Who went to the store?", "Where did Luke go?"]""",
            },
            {"role": "user", "content": text},
        ],
    )

    return json.loads(response.choices[0].message.content)
