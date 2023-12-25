from typing import Protocol, Optional, List


class ITokenizer(Protocol):
    name: str

    def tokenize(self, text: str) -> [str]:
        ...

    def tokenize_corpus_texts(
        self, texts: Optional[List[str]] = None
    ) -> Optional[List[str]]:
        ...
