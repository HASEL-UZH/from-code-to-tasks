import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from src.strategies.tokenization.commons import is_number
from src.strategies.tokenization.defs import ITokenizer

"""
# Setup

## NLTK

```bash
pip install nltk
python -m nltk.downloader punkt stopwords
```
"""

stop_words = set(stopwords.words("english"))


class NltkTokenizer(ITokenizer):
    name = "nltk-word-tokenize"

    def tokenize(self, text: str) -> [str]:
        tokens = sorted([w.lower() for w in word_tokenize(text)])
        return tokens


class NltkTokenizerOptimized(ITokenizer):
    name = "nltk-word-tokenize-optimized"

    def tokenize(self, text: str) -> [str]:
        base = word_tokenize(text)
        unique = list(set(base))
        unique_lower = [
            d.lower().strip() for d in unique
        ]  # FIXME clean tokens, remove punctuations, special characters

        tokens = sorted(
            [
                d
                for d in unique_lower
                if len(d) > 1 and d not in stop_words and accept_fn(d)
            ]
        )
        return tokens


exclusions = set(list(string.punctuation))


def accept_fn(s):
    # Return True if `s` is not in the exclusion set
    return s not in exclusions and not is_number(s)
