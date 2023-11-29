import json
from typing import TypedDict, Optional, Any, List
from datetime import datetime

from src.core.logger import log
from src.github.defs import RepositoryIdentifier


class PipelineOptions(TypedDict):
    repositories: Optional[List[str]]


class PipelineContext:
    _opts = None
    _opts_str = None
    _errors = []

    def __init__(self, opts: Optional[PipelineOptions]):
        self._context_id = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self._opts = opts or {}
        self._opts_str = json.dumps(self._opts or None)

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


DEFAULT_PIPELINE_CONTEXT = PipelineContext(
    opts={
        "repositories": [RepositoryIdentifier.iluwatar__java_design_patterns],
    }
)
