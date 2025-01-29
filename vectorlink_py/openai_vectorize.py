import openai as oa
import datafusion as df
import pyarrow as pa
from typing import Dict, Optional, Literal
import json
import backoff


def embeddings_pylist_to_table(
    ids,
    embeddings,
    dimension: int = 1536,
):
    embeddings = pa.array(embeddings, type=pa.list_(pa.float32(), dimension))
    schema = pa.schema(
        [
            pa.field("hash", pa.string_view(), nullable=False),
            pa.field(
                "embedding",
                pa.list_(pa.float32(), dimension),
                nullable=False,
            ),
        ]
    )
    return pa.Table.from_pydict({"hash": ids, "embedding": embeddings}, schema=schema)


def write_batched_embeddings(ctx, batched_ids, batched_strings, destination, **kwargs):
    embedding_kwargs = {key: value for key, value in kwargs.items() if key in ["model"]}
    embeddings = get_embedding(batched_strings, **embedding_kwargs)
    table_kwargs = {key: value for key, value in kwargs.items() if key in ["dimension"]}
    table = embeddings_pylist_to_table(batched_ids, embeddings, **table_kwargs)
    ctx.from_arrow_table(table).write_parquet(destination)


# TODO this should take an openai client as an argument so we can mock
@backoff.on_exception(backoff.constant, oa.RateLimitError, interval=60)
def get_embedding(
    strings,
    model: Literal[
        "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"
    ] = "text-embedding-3-small",
):
    try:
        response = oa.embeddings.create(input=strings, model=model)
    except Exception as e:
        print(f"Unable to embed the following strings: {strings}")
        raise e
    return [embedding.embedding for embedding in response.data]


# TODO make this accept a dataframe rather than a stream
def vectorize(
    ctx: df.SessionContext,
    stream: df.RecordBatchStream,
    destination: str,
    model: Literal[
        "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"
    ] = "text-embedding-3-small",
    dimension=1536,
    batch_size=1000,
):
    batched_ids = []
    batched_strings = []
    for result in stream:
        for element in result.to_pyarrow().to_pylist():
            batched_ids.append(element["hash"])
            batched_strings.append(element["templated"])
            if len(batched_strings) == batch_size:
                write_batched_embeddings(
                    ctx,
                    batched_ids,
                    batched_strings,
                    destination,
                    dimension=dimension,
                    model=model,
                )
                batched_ids = []
                batched_strings = []
    if len(batched_ids) > 0:
        write_batched_embeddings(
            ctx,
            batched_ids,
            batched_strings,
            destination,
            dimension=dimension,
            model=model,
        )
