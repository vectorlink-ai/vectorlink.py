import datafusion as df
import pyarrow as pa
from datafusion import DataFrame, SessionContext
from typing import Dict, Optional


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
