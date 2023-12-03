from typing import TypedDict, Callable, Any, List, Protocol

from src.strategies.embeddings.defs import IEmbeddingStrategyFactory


class IContentStrategy(TypedDict):
    meta: str
    terms: str


class IEmbeddingConcept(Protocol):
    name: str
    embedding_strategies: [IEmbeddingStrategyFactory]
    calculate_similarity: Callable[..., Any]
    content_strategies: List[IContentStrategy]


class ICommitInfo(TypedDict):
    commit_hash: str
    commit_date: str
    pull_request_text: str
    change_text: str
    commit_message_text: str
    filename: str
    resource: str


# Enum


class CacheStrategy:
    Memory = "memory"
    Npy = "npy"


class ContentStrategies:
    TfxAll = [
        {"meta": "ast-sm", "terms": "meta_ast_text"},
        {"meta": "ast-md", "terms": "meta_ast_text"},
        {"meta": "ast-lg", "terms": "meta_ast_text"},
        {"meta": None, "terms": "diff_text"},
    ]
    TfxCore = [
        {"meta": "ast-lg", "terms": "meta_ast_text"},
        {"meta": None, "terms": "diff_text"},
    ]

    TfxCombined = [
        {
            "$or": [
                {
                    "$and": [
                        {"strategy.meta": "ast-lg"},
                        {"strategy.terms": "meta_ast_text"},
                    ]
                },
                {
                    "$and": [
                        {"strategy.meta": None},
                        {"strategy.terms": "diff_text"},
                    ]
                },
            ]
        }
    ]

    CodeBERT = [
        {"meta": "ast-sm", "terms": "meta_ast_code"},
        {"meta": "ast-md", "terms": "meta_ast_code"},
        {"meta": "ast-lg", "terms": "meta_ast_code"},
    ]
