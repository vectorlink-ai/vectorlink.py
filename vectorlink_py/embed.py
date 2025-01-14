import datafusion as df
import pyarrow as pa
from datafusion import DataFrame, SessionContext


embed_table_schema = pa.schema(
    [
        pa.field("hash", pa.string_view(), nullable=False),
        pa.field("embedding", pa.list_(pa.float32(), 1536), nullable=False),
    ]
)


def get_unembedded(ctx: SessionContext, source: str, destination: str) -> DataFrame:
    already_vectorized = ctx.read_parquet(
        destination, schema=embed_table_schema
    ).select(df.col("hash"))
    return ctx.read_parquet(source).join(
        already_vectorized, left_on="hash", right_on="hash", how="anti"
    )
