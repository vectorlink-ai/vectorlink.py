import pyarrow as pa
import datafusion as df

CHUNK_RANGE_TYPE = pa.struct(
    [
        pa.field("start", pa.uint64(), nullable=False),
        pa.field("end", pa.uint64(), nullable=False),
    ]
)

CHUNK_SCHEMA = pa.schema(
    [
        pa.field(
            "chunk_range",
            CHUNK_RANGE_TYPE,
            nullable=False,
        ),
        pa.field("text", pa.string_view(), nullable=False),
        # pa.field("hash", pa.string_view(), nullable=False),
    ]
)
