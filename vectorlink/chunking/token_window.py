from protocol import *
from typing import List


import tiktoken


class Tokenizer:
    def encode(self, text: str) -> List: ...
    def decode(self, encoded: List) -> str: ...


class TiktokenTokenizer(Tokenizer):
    def __init__(self, style="o200k_base"):
        self.encoding = tiktoken.get_encoding(style)

    def encode(self, text: str) -> List:
        return self.encoding.encode(text)

    def decode(self, encoded: List) -> str:
        return self.encoding.decode(encoded)


def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


class TokenWindowChunker(Chunker):
    def __init__(self, tokenizer: Tokenizer, token_window_size: int):
        self.tokenizer = tokenizer
        self.token_window_size = token_window_size

    def generate_chunks(self, text: str) -> List[Range]:
        encoded = self.tokenizer.encode(text)
        chunks = list(chunk_list(encoded, self.token_window_size))
        result = []
        offset = 0
        for chunk in chunks:
            decoded = self.tokenizer.decode(chunk)
            result.append(Range(offset, offset + len(decoded)))
            offset += len(decoded)

        return result
