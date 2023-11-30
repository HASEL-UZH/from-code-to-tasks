import json
from typing import TypedDict, Optional, Any, List, Dict
from datetime import datetime

from src.core.logger import log
from src.core.utils import hash_string
from src.github.defs import RepositoryIdentifier
from src.store.mdb_store import Collection
from src.strategies.defs import ICommitInfo, IEmbeddingConcept
from src.strategies.embeddings.defs import IEmbeddingStrategy


class PipelineOptions(TypedDict):
    repositories: Optional[List[str]]
    log_accuracy_flag: Optional[bool]


class PipelineContext:
    def __init__(self, opts: Optional[PipelineOptions]):
        self._context_id = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self._opts = opts or {}
        self._opts_str = json.dumps(self._opts or None)
        self._errors = []
        self._scope = None
        self._repositories = ",".join(self._opts.get("repositories", []))
        self._log_accuracy_flag = self._opts.get("log_accuracy_flag", False)
        self._log_cache = {}

    def _create_db_filter_criteria(self, field: str, criteria: Optional[dict] = None):
        if not criteria:
            criteria = {}

        repositories = self._opts.get("repositories", [])
        if len(repositories) == 1:
            _criteria = {field: repositories[0]}
        elif len(repositories) > 1:
            _criteria = {field: {"$in": repositories}}
        else:
            _criteria = {}

        _criteria = {**criteria, **_criteria}
        return _criteria

    def create_repository_criteria(self, criteria: Optional[dict] = None):
        criteria = self._create_db_filter_criteria("identifier", criteria)
        return criteria

    def create_commit_criteria(self, criteria: Optional[dict] = None):
        criteria = self._create_db_filter_criteria("repository_identifier", criteria)
        return criteria

    def create_resource_criteria(self, criteria: Optional[dict] = None):
        criteria = self._create_db_filter_criteria("repository_identifier", criteria)
        return criteria

    def create_issue_criteria(self, criteria: Optional[dict] = None):
        criteria = self._create_db_filter_criteria("identifier", criteria)
        return criteria

    def get_opts(self):
        return self._opts.copy()

    def error(self, scope: str = None, message: str = None, data: dict = None):
        log.error(f"scope: {scope}, message: {message}")
        self._errors.append(
            {
                "context": self._context_id,
                "opts": self._opts_str,
                "scope": scope,
                "message": message,
                "data": data,
            }
        )

    def set_scope(self, scope: Any):
        self._scope = scope
        self._log_cache = {}

    def _get_log_tokens(self, embedding_strategy, text):
        text_hash = hash_string(text)
        tokens = self._log_cache.get(text_hash)
        if tokens is None:
            tokens = set([d.lower() for d in embedding_strategy.get_tokens(text)])
            self._log_cache[text_hash] = tokens
        return tokens

    # the accuracies are sorted in descending order
    def log_accuracy(
        self,
        pr_commit: ICommitInfo,
        sliding_window_index: int,
        sliding_window_items: Dict[str, ICommitInfo],
        match: bool,
        accuracies: Dict[str, float],
        top_keys: [str],
    ):
        log_accuracy_flag = self._opts.get("log_accuracy_flag", False)
        if log_accuracy_flag:
            embedding_concept: IEmbeddingConcept = self._scope["embedding_concept"]
            embedding_strategy: IEmbeddingStrategy = self._scope["embedding_strategy"]
            pr_tokens = self._get_log_tokens(
                embedding_strategy, pr_commit["pull_request_text"]
            )
            text_tokens = self._get_log_tokens(
                embedding_strategy, pr_commit["change_text"]
            )
            pr_common_tokens = pr_tokens.intersection(text_tokens)
            entry = {
                "context_id": self._context_id,
                "repositories": self._repositories,
                "embedding_concept": embedding_concept.name,
                "embedding_strategy": embedding_strategy.name,
                "content_meta_strategy": self._scope["content_strategy"]["meta"],
                "content_terms_strategy": self._scope["content_strategy"]["terms"],
                "window_size": self._scope["window_size"],
                "k": self._scope["k"],
                "sliding_window_index": sliding_window_index,
                "match": match,
                "pr_commit": pr_commit["commit_hash"],
                "pr_tokens": ", ".join(sorted(list(pr_tokens))),
                "text_tokens": ", ".join(sorted(list(text_tokens))),
                "common_tokens": ", ".join(sorted(list(pr_common_tokens))),
                "common_tokens_count": len(pr_common_tokens),
                "accuracy": accuracies[pr_commit["commit_hash"]],
                "accuracy_rank": top_keys.index(pr_commit["commit_hash"]),
                "accuracies": accuracies,
                "top_keys": top_keys,
            }
            if not match:
                mismatch_commit = sliding_window_items[top_keys[0]]
                mismatch_pr_tokens = self._get_log_tokens(
                    embedding_strategy, mismatch_commit["pull_request_text"]
                )
                mismatch_text_tokens = self._get_log_tokens(
                    embedding_strategy, mismatch_commit["change_text"]
                )
                mismatch_pr_common_tokens = mismatch_pr_tokens.intersection(text_tokens)
                entry["mismatch_pr_commit"] = mismatch_commit["commit_hash"]
                entry["mismatch_pr_tokens"] = ", ".join(
                    sorted(list(mismatch_pr_tokens))
                )
                entry["mismatch_text_tokens"] = ", ".join(
                    sorted(list(mismatch_pr_tokens))
                )
                entry["mismatch_text_tokens"] = ", ".join(
                    sorted(list(mismatch_text_tokens))
                )
                entry["mismatch_common_tokens"] = ", ".join(
                    sorted(list(mismatch_pr_common_tokens))
                )
                entry["mismatch_common_token_count"] = len(mismatch_pr_common_tokens)
                entry["mismatch_accuracy"] = accuracies[mismatch_commit["commit_hash"]]

            Collection.accuracy.insert_one(entry)


DEFAULT_PIPELINE_CONTEXT = PipelineContext(
    opts={
        "repositories": [RepositoryIdentifier.iluwatar__java_design_patterns],
        "log_accuracy_flag": False,
    }
)
