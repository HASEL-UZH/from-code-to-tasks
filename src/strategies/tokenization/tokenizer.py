import re

from nltk import word_tokenize
from nltk.corpus import stopwords

from src.strategies.tokenization.defs import ITokenizer

stop_words = set(stopwords.words("english"))


class StandardTokenizer(ITokenizer):
    name = "standard-tokenizer"

    def tokenize(self, text: str) -> [str]:
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in stop_words]
        return filtered_words

    def tokenize_corpus_texts(self, texts: [str]):
        filtered_texts = []
        for text in texts:
            words = word_tokenize(text)
            filtered_words = [word for word in words if word.lower() not in stop_words]
            filtered_text = " ".join(filtered_words)
            filtered_texts.append(filtered_text)
        return filtered_texts


class SubwordTokenizer(StandardTokenizer):
    name = "subword-tokenizer"

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
        words = re.findall(r"([a-z]+|[A-Z][a-z]+|[a-z]+_[a-z]+)", text)
        words = [word.split("-") for word in words]
        words = [subword for sublist in words for subword in sublist]
        words = [word.split(".") for word in words]
        words = [subword for sublist in words for subword in sublist]
        words = [
            subword.lower() for word in words for subword in re.split("[-.]", word)
        ]
        words = list(filter(None, words))
        return words
