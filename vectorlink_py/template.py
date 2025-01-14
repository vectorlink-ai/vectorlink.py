import datafusion as df
from pybars import Compiler
from typing import Callable, Optional, List, Union
import pyarrow as pa
import pandas

from datafusion import DataFrame


def clean_record(record):
    return {k: v if v and not v.isspace() else None for k, v in record.items()}


def generate_template_udf(
    compiled_template: Callable, names: List[str], template_name: Optional[str] = None
) -> df.ScalarUDF:

    def template_udf(*args: pa.StringArray) -> pa.StringArray:
        templated_strings = []
        for record in (
            pa.RecordBatch.from_arrays(list(args), names)
            .to_pandas()
            .to_dict(orient="records")
        ):
            record = clean_record(record)
            result = compiled_template(record)
            if result.isspace():
                # force whitespace results to be the empty s tring
                result = ""

            templated_strings.append(result)

        return pa.array(templated_strings)

    input_types = [pa.string() for _ in names]
    return df.udf(template_udf, input_types, pa.string(), "stable", name=template_name)


def template_frame(
    input_frame: DataFrame,
    template: Union[Callable, str],
    id_column: str = "id",
    columns_of_interest: Optional[List[str]] = None,
) -> DataFrame:
    if isinstance(template, str):
        compiled_template = Compiler().compile(template)
    else:
        compiled_template = template

    if columns_of_interest is None:
        columns_of_interest = [
            name for name in input_frame.schema().names if name != id_column
        ]

    template_udf = generate_template_udf(compiled_template, columns_of_interest)
    columns = [df.col(col) for col in columns_of_interest]
    return input_frame.select(
        df.col(id_column), template_udf(*columns).alias("templated")
    )
