import openai as oa
import datafusion as df
import pyarrow as pa
from datafusion import DataFrame, SessionContext
from typing import Dict, Optional, Literal
from . import openai_vectorize


def embedding_schema(dimension=1536):
    embed_table_schema = pa.schema(
        [
            pa.field("hash", pa.string_view(), nullable=False),
            pa.field("embedding", pa.list_(pa.float32(), dimension), nullable=False),
        ]
    )
    return embed_table_schema


HASH_SCHEMA = pa.schema(
    [
        pa.field("hash", pa.string_view(), nullable=False),
    ]
)


def get_unembedded_from_df(source: DataFrame, destination: DataFrame) -> DataFrame:
    return source.join(destination, left_on="hash", right_on="hash", how="anti")


def get_unembedded(
    ctx: SessionContext, source: df.DataFrame, destination: str
) -> DataFrame:
    already_vectorized = ctx.read_parquet(destination, schema=HASH_SCHEMA)
    return get_unembedded_from_df(source, already_vectorized)


def vectorize(
    ctx: df.SessionContext,
    source: df.DataFrame,
    destination: str,
    model: Literal[
        "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"
    ] = "text-embedding-3-small",
):
    dimension = openai_vectorize.model_dimensions(model)
    unembedded = get_unembedded(ctx, source, destination)

    # TODO this is now very specific for openai. However, all the
    # openai specific stuff is just about what UDF is used.
    client = oa.Client()
    udf = openai_vectorize.generate_embedding_udf(client, model)

    unembedded.select(
        df.col("hash"), udf(df.col("text")).alias("embedding")
    ).write_parquet(destination)
