from . import openai_vectorize
import datafusion as df
from typing import Dict, Optional


def vectorize(
    ctx: df.SessionContext,
    df: df.DataFrame,
    destination: str,
    configuration: Optional[Dict] = None,
) -> df.DataFrame:
    if configuration is None:
        configuration = {
            "provider": "OpenAI",
            "max_batch_size": 200 * 2 ** 20,
            "dimension": 1536,
            "model": "text-embedding-3-small",
        }
o
    if configuration["provider"] == "OpenAI":
        stream = df.execute_stream()
        return openai_vectorize.vectorize(ctx, stream, destination, configuration)
    else:
        raise Exception("No known vectorization provider")
