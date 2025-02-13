# chunking -> embedding -> evaluation
from protocol import *
from token_window import *
from schema import *

import pyarrow as pa


def chunk_text(chunker: Chunker, document_id: str, text: str) -> pa.Table:
    ranges = chunker.generate_chunks(text)
    document_id_array = pa.repeat(
        pa.scalar(document_id, type=pa.string_view()), len(ranges)
    )
    chunk_index_array = pa.array(list(range(0, len(ranges))), type=pa.int32())
    range_array = pa.array(list([r.__dict__ for r in ranges]), type=CHUNK_RANGE_TYPE)
    chunk_array = pa.array(
        list([text[r.start : r.end] for r in ranges]), type=pa.string_view()
    )

    return pa.Table.from_arrays(
        [document_id_array, chunk_index_array, range_array, chunk_array],
        schema=CHUNK_SCHEMA,
    )
