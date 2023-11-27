from typing import TypedDict, Callable, Any, List


class ContentStrategy(TypedDict):
    meta: str
    terms: str


class ConceptStrategy(TypedDict):
    id: str
    strategies: Any
    calculate_similarity: Callable[..., Any]
    content_strategies: List[ContentStrategy]


# Enum


class CacheStrategy:
    Memory = "memory"
    Npy = "npy"


class ContentStrategies:
    Tfx = [
        {"meta": "ast-sm", "terms": "meta_ast_text"},
        {"meta": "ast-md", "terms": "meta_ast_text"},
        {"meta": "ast-lg", "terms": "meta_ast_text"},
        {"meta": None, "terms": "diff_text"},
    ]
    CodeBERT = [
        {"meta": "ast-sm", "terms": "meta_ast_code"},
        {"meta": "ast-md", "terms": "meta_ast_code"},
        {"meta": "ast-lg", "terms": "meta_ast_code"},
    ]
