import re

from nltk import word_tokenize
from nltk.corpus import stopwords

from src.strategies.tokenization.commons import is_number
from src.strategies.tokenization.defs import ITokenizer

stop_words = set(stopwords.words("english"))


class BasicTestTokenizer(ITokenizer):
    name = "basic-test-tokenizer"

    def tokenize(self, text: str) -> [str]:
        words = word_tokenize(text)
        filtered_words = [
            word for word in words if word.lower() not in stopwords.words("english")
        ]
        return filtered_words

    def tokenize_corpus_texts(self, texts: [str]):
        filtered_texts = []
        for text in texts:
            words = word_tokenize(text)
            filtered_words = [
                word for word in words if word.lower() not in stopwords.words("english")
            ]
            filtered_text = " ".join(filtered_words)
            filtered_texts.append(filtered_text)
        return filtered_texts


class SubwordTestTokenizer(BasicTestTokenizer):
    name = "subword-test-tokenizer"

    def tokenize(self, text: str) -> [str]:
        text_removed_stopwords = " ".join(super().tokenize(text))
        text_split_subwords = self.split_subwords(text_removed_stopwords)
        return text_split_subwords

    def tokenize_corpus_texts(self, texts: [str]) -> [str]:
        texts_removed_stopwords = super().tokenize_corpus_texts(texts)
        texts_split_subwords = []
        for text in texts_removed_stopwords:
            texts_split_subwords.append(" ".join(self.split_subwords(text)))
        return texts_split_subwords

    def split_subwords(self, text):
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


class RemovedNumberTestTokenizer(SubwordTestTokenizer):
    name = "removed-number-test-tokenizer"

    def tokenize(self, text: str) -> [str]:
        text_removed_stopwords = super().tokenize(text)
        text_removed_numbers = [d for d in text_removed_stopwords if not is_number(d)]
        return text_removed_numbers

    def tokenize_corpus_texts(self, texts: [str]) -> [str]:
        texts_removed_stopwords = super().tokenize_corpus_texts(texts)
        texts_removed_numbers = []
        for text in texts_removed_stopwords:
            texts_removed_numbers.append([d for d in text if not is_number(d)])
        return texts_removed_stopwords
