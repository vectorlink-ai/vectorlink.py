from typing import List


class Range:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class Chunker:
    def generate_chunks(self, text: str) -> List[Range]: ...
