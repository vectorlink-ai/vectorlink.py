import datafusion as df
from datafusion import DataFrame


def dedup_dataframe(dataframe: DataFrame, dedup_field: str) -> DataFrame:
    return (
        dataframe.select(df.col(dedup_field), df.functions.md5(df.col(dedup_field)))
        .aggregate(
            df.col(dedup_field),
            [
                df.functions.first_value(df.functions.md5(df.col(dedup_field))).alias(
                    "hash"
                )
            ],
        )
        .select(df.col("hash"), df.col(dedup_field))
    )
