import datafusion as df
import pyarrow as pa


class Index:
    def __init__(self, context) -> Index:
        self.context = context

    @classmethod
    def generate(cls, frame: df.DataFrame) -> Index:
        """Generate an index from a frame with columns 'vector_id' and 'vector'"""
        ...

    def to_dataframe(self, ctx: df.SessionContext) -> df.DataFrame:
        """returns the inner state of this indexer as a dataframe"""
        ...

    @classmethod
    def from_dataframe(cls, frame: df.DataFrame) -> Index:
        """Reconstructs the index from a dataframe with the columns as produced by `to_dataframe`"""
        ...

    def search(self, ctx: df.SessionContext, search_vectors: df.DataFrame) -> pa.Array:
        """"""
        ...
