from pathlib import Path
import datafusion as df

from vectorlink import embedding, chunking

CONTENT_WINDOW = 1024
OUTPUT = "./my_cool_output/"

# read the transcript
p = Path("./DAY 01 020717 dpc v facebook.txt")
content = p.read_text()

# chunk it
tokenizer = chunking.TiktokenTokenizer()
chunker = chunking.TokenWindowChunker(tokenizer, CONTENT_WINDOW)
chunked = chunking.chunk_text(chunker, content)

# turn it into a table with hashes
ctx = df.SessionContext()
frame = ctx.from_arrow(chunked).with_column("hash", df.functions.md5(df.col("text")))
frame.write_parquet(f"{OUTPUT}chunks/")

# vectorize (todo dedup)
embedding.vectorize(ctx, frame, f"{OUTPUT}vectors/")
