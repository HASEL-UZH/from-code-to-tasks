from typing import Protocol


class ITokenizer(Protocol):
    name: str

    def tokenize(self, text: str) -> [str]:
        ...
