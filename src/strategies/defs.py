from typing import TypedDict, Callable, Any, List, Protocol, Optional, Union

from src.strategies.embeddings.defs import IEmbeddingStrategyFactory


class IContentStrategy(TypedDict):
    meta: str
    terms: str
    criteria: Optional[dict]


TContentStrategy = Union[IContentStrategy, List[IContentStrategy]]


class IEmbeddingConcept(Protocol):
    name: str
    embedding_strategies: [IEmbeddingStrategyFactory]
    calculate_similarity: Callable[..., Any]
    content_strategies: List[TContentStrategy]


class ICommitInfo(TypedDict):
    commit_hash: str
    commit_date: str
    pull_request_text: str
    change_text: str
    commit_message_text: str
    filename: str
    resource: str


class CacheStrategy:
    Memory = "memory"
    Npy = "npy"


class ContentStrategies:
    TfxAll = [
        {"meta": "ast-sm", "terms": "meta_ast_text"},
        {"meta": "ast-md", "terms": "meta_ast_text"},
        {"meta": "ast-lg", "terms": "meta_ast_text"},
        {"meta": None, "terms": "diff_text"},
        [
            {"meta": None, "terms": "diff_text"},
            {"meta": "ast-lg", "terms": "meta_ast_text"},
        ],
    ]

    CodeBERT = [
        {"meta": "ast-sm", "terms": "meta_ast_code"},
        {"meta": "ast-md", "terms": "meta_ast_code"},
        {"meta": "ast-lg", "terms": "meta_ast_code"},
    ]
