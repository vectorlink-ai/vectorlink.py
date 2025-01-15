import datafusion as df
import pyarrow as pa
import numpy as np
import pandas as pd
import ctypes
from datafusion import DataFrame, SessionContext
from typing import Optional, Dict
import torch
from torch import Tensor
from .utils import torch_type_to_ctype, name_to_torch_type


def dataframe_to_tensor(df: DataFrame, tensor: Tensor):
    stream = df.execute_stream()
    offset = 0
    dtype = tensor.dtype
    ctype = torch_type_to_ctype(dtype)
    (_, dim) = tensor.size()
    for batch in stream:
        embeddings = batch.to_pyarrow().column(0)
        embeddings_ptr = ctypes.cast(
            embeddings.buffers()[3].address, ctypes.POINTER(ctype)
        )
        embeddings_tensor = torch.tensor(
            np.ctypeslib.as_array(embeddings_ptr, (len(embeddings), dim))
        )
        array_slice = tensor.narrow(0, offset, len(embeddings))
        array_slice.copy_(embeddings_tensor)
        offset += len(embeddings)


def write_field_averages(
    ctx: SessionContext,
    template_source: str,
    key: str,
    vector_source: str,
    destination: str,
):
    fv = field_vectors(ctx, f"{template_source}/{key}/", vector_source)
    average = torch.mean(fv, 1).numpy()
    dataframe = pd.DataFrame({"template": [key], "average": [average]})
    df.from_pandas(dataframe).write_parquet(destination)


def field_vectors(
    ctx: SessionContext,
    source: str,
    vector_source: str,
    configuration: Optional[Dict] = None,
) -> Tensor:
    if configuration is None:
        # defaults to OpenAI dimensions / datatype
        configuration = {"dimensions": 1536, "field_type": "float32"}
    template_df: DataFrame = ctx.read_parquet(source)
    vector_df: DataFrame = ctx.read_parquet(vector_source).select(
        df.col("hash").alias("embedding_hash"), df.col("embedding")
    )
    result = template_df.join(
        vector_df, left_on="hash", right_on="embedding_hash", how="inner"
    ).select(df.col("embedding"))
    size = result.count()
    dim = configuration["dimensions"]
    field_type = configuration["field_type"]
    dtype = name_to_torch_type(field_type)
    tensor = torch.empty((size, dim), dtype=dtype)
    dataframe_to_tensor(result, tensor)
    return tensor
