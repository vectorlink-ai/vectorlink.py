import openai as oa
import datafusion as df
import pyarrow as pa
from typing import Dict, Optional, Literal, List
import json
import backoff


def model_dimensions(model_name: str) -> int:
    match model_name:
        case "text-embedding-ada-002" | "text-embedding-3-small":
            return 1536
        case "text-embedding-3-large":
            return 3072
        case _:
            raise ValueError(f"unknown embedding model {model_name}")


def generate_embedding_udf(
    client: oa.Client,
    model: Literal[
        "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"
    ] = "text-embedding-3-small",
):
    dimensions = model_dimensions(model)
    output_type = pa.list_(pa.float32(), dimensions)

    def embedding_udf(inputs: pa.StringViewArray) -> pa.FixedSizeListArray:
        inputs = inputs.to_pylist()
        result = get_embedding(client, inputs, model)
        return pa.array(result, type=output_type)

    return df.udf(
        embedding_udf,
        [pa.string_view()],
        output_type,
        "stable",
        name="generate_embedding",
    )


@backoff.on_exception(backoff.constant, oa.RateLimitError, interval=60)
def get_embedding(
    client: oa.Client,
    strings,
    model: Literal[
        "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"
    ] = "text-embedding-3-small",
) -> List[List[float]]:
    try:
        response = client.embeddings.create(input=strings, model=model)
    except Exception as e:
        print(f"Unable to embed the following strings: {strings}")
        raise e
    return [embedding.embedding for embedding in response.data]
