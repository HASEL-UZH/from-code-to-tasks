import re
from src.strategies.tokenization.defs import ITokenizer
from src.strategies.tokenization.commons import remove_numbers, is_number


class SubwordTokenizer(ITokenizer):
    name = "subword"

    def tokenize(self, text: str) -> [str]:
        words = re.findall(r"[A-Za-z]+", text)
        transformed_words = []
        for word in words:
            separators = ["_", "-"]
            for separator in separators:
                if separator in word:
                    subwords = word.split(separator)
                    transformed_words.extend(subwords)
                    break
            else:
                subwords = re.findall(r"[a-z]+|[A-Z][a-z]*", word)
                transformed_words.extend(subwords)
        return transformed_words


class SubwordTokenizerNoNumbers(SubwordTokenizer):
    name = "subword-no-numbers"

    def tokenize(self, text: str) -> [str]:
        tokens = super().tokenize(text)
        tokens = [d for d in tokens if not is_number(d)]
        return tokens
