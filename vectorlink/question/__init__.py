from typing import List, Dict
from openai import Client
import json
import openai
import backoff
import datafusion as df
import pyarrow as pa


@backoff.on_exception(
    backoff.constant,
    (json.decoder.JSONDecodeError,),
    max_tries=3,
    interval=0.01,
)
def generate_questions(text: str, examples: List[str] = []) -> List[str]:
    # TODO: make examples do something
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


def rate_content_relevance(prompt: str, fragment: str) -> Dict:
    client = Client()
    result = (
        client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You score relevance of a fragment of text to answering a given question. Score should be between 1 and 10. Give reasons for the scoring. A fragment with false information should still be considered relevant. Score should be on the last line with nothing else on it. This is very important. Also, do not use any markdown.",
                },
                {
                    "role": "user",
                    "content": f"question: {prompt}\ntext fragment: {fragment}",
                },
            ],
        )
        .choices[0]
        .message.content
    )

    return {"response": result, "score": int(result.split("\n")[-1])}


def generate_questions_udf_fn(chunks: pa.Array) -> pa.Array:
    results = []
    for chunk in chunks:
        result = generate_questions(str(chunk))
        print(result)
        results.append(result)
    return pa.array(results, type=pa.list_(pa.string_view()))


generate_questions_udf = df.udf(
    generate_questions_udf_fn,
    [pa.string_view()],
    pa.list_(pa.string_view()),
    "stable",
    name="generate_questions",
)
