import datafusion as df
import pyarrow as pa
from datafusion import DataFrame, SessionContext

templated_table_schema = pa.schema(
    [
        pa.field("hash", pa.string_view(), nullable=False),
        pa.field("templated", pa.string_view(), nullable=False),
    ]
)


def dedup_dataframe(dataframe: DataFrame) -> DataFrame:
    return dataframe.aggregate(
        df.col("templated"),
        [df.functions.first_value(df.col("hash")).alias("hash")],
    ).select(df.col("hash"), df.col("templated"))


def dedup_from_into(ctx: SessionContext, source: str, destination: str):
    source_parquet = ctx.read_parquet(source)
    destination_parquet = ctx.read_parquet(
        destination, schema=templated_table_schema
    ).select(df.col("hash"))
    result = dedup_dataframe(source_parquet).join(
        destination_parquet, left_on="hash", right_on="hash", how="anti"
    )

    result.write_parquet(destination)
