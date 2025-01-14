import datafusion as df
import pyarrow as pa
from datafusion import DataFrame, SessionContext
from typing import Dict, Optional
from . import openai_vectorize


def embedding_schema(configuration: Optional[Dict]):
    if configuration is not None:
        dimension = configuration["dimension"]
    else:
        dimension = 1536

    embed_table_schema = pa.schema(
        [
            pa.field("hash", pa.string_view(), nullable=False),
            pa.field("embedding", pa.list_(pa.float32(), dimension), nullable=False),
        ]
    )
    return embed_table_schema


def get_unembedded(
    ctx: SessionContext,
    source: str,
    destination: str,
    configuration: Optional[Dict] = None,
) -> DataFrame:
    already_vectorized = ctx.read_parquet(
        destination, schema=embedding_schema(configuration)
    ).select(df.col("hash"))
    return ctx.read_parquet(source).join(
        already_vectorized, left_on="hash", right_on="hash", how="anti"
    )


def vectorize(
    ctx: df.SessionContext,
    source: str,
    destination: str,
    configuration: Optional[Dict] = None,
) -> df.DataFrame:
    if configuration is None:
        configuration = {
            "provider": "OpenAI",
            "max_batch_size": 200 * 2**20,
            "dimension": 1536,
            "model": "text-embedding-3-small",
        }

    df = get_unembedded(ctx, source, destination, configuration)

    if configuration["provider"] == "OpenAI":
        stream = df.execute_stream()
        return openai_vectorize.vectorize(ctx, stream, destination, configuration)
    else:
        raise Exception("No known vectorization provider")
