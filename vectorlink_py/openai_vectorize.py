import openai as oa
import datafusion as df
import pyarrow as pa
from typing import Dict, Optional
import json
import backoff


def embeddings_pylist_to_table(ids, embeddings, configuration):
    embeddings = pa.array(
        embeddings, type=pa.list_(pa.float32(), configuration["dimension"])
    )
    schema = pa.schema(
        [
            pa.field("hash", pa.string_view(), nullable=False),
            pa.field(
                "embedding",
                pa.list_(pa.float32(), configuration["dimension"]),
                nullable=False,
            ),
        ]
    )
    return pa.Table.from_pydict({"hash": ids, "embedding": embeddings}, schema=schema)


def write_batched_embeddings(
    ctx, batched_ids, batched_strings, destination, configuration
):
    embeddings = get_embedding(batched_strings, configuration)
    table = embeddings_pylist_to_table(batched_ids, embeddings, configuration)
    ctx.from_arrow_table(table).write_parquet(destination)


@backoff.on_exception(backoff.constant, oa.RateLimitError, interval=60)
def get_embedding(strings, configuration):
    response = oa.embeddings.create(input=strings, model=configuration["model"])

    return [embedding.embedding for embedding in response.data]


def vectorize(
    ctx: df.SessionContext,
    stream: df.RecordBatchStream,
    destination: str,
    configuration: Dict,
):
    openai_client = oa.Client()
    batched_ids = []
    batched_strings = []
    for result in stream:
        for element in result.to_pyarrow().to_pandas().to_dict(orient="records"):
            batched_ids.append(element["hash"])
            batched_strings.append(element["templated"])
            if len(batched_strings) == 1000:
                write_batched_embeddings(
                    ctx, batched_ids, batched_strings, destination, configuration
                )
                batched_ids = []
                batched_strings = []
    if len(batched_ids) > 0:
        write_batched_embeddings(
            ctx, batched_ids, batched_strings, destination, configuration
        )
