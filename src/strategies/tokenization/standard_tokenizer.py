import re
from src.strategies.tokenization.defs import ITokenizer
from src.strategies.tokenization.commons import remove_numbers, is_number


class StandardTokenizer(ITokenizer):
    name = "standard"

    def tokenize(self, text: str) -> [str]:
        # split_by_whitespace_and_punctuation
        tokens = re.findall(r"\b\w+\b", text)
        return tokens


class StandardTokenizerNoNumbers(StandardTokenizer):
    name = "standard-no-numbers"

    def tokenize(self, text: str) -> [str]:
        tokens = super().tokenize(text)
        tokens = [d for d in tokens if not is_number(d)]
        return tokens
