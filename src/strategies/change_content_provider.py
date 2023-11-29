from typing import Iterator, TypedDict
from src.store.mdb_store import db
from src.strategies.defs import IContentStrategy
from src.tasks.pipeline_context import PipelineContext


class ChangeContentProvider:
    _context: PipelineContext
    _content_strategy: IContentStrategy
    _cursor: Iterator[dict]

    def __init__(self, context: PipelineContext, content_strategy: IContentStrategy):
        self._context = context
        self._content_strategy = content_strategy

    def __iter__(self):
        self._cursor = self._get_db_cursor()
        return self

    def __next__(self):
        while True:
            item = self._get_next()
            if item is not None:
                return item

    def _get_db_cursor(self):
        file_type = "text"
        if self._content_strategy["terms"] == "meta_ast_code":
            file_type = "java"

        criteria = self._context.create_resource_criteria(
            {
                "strategy.meta": self._content_strategy["meta"],
                "kind": "term",
                "type": file_type,
                "strategy.terms": self._content_strategy["terms"],
            }
        )
        change_resources = db.find_resources(criteria)
        return change_resources

    def _get_next(self):
        change_resource = next(self._cursor)
        item = self._get_commit_info(change_resource)
        return item

    def _get_commit_info(self, change_resource):
        change_content = db.get_resource_content(change_resource, volatile=True)
        change_text = change_content.strip() if change_content else ""
        commit = db.find_object(change_resource.get("@container"))
        pull_request_text = (
            commit.get("pull_request_title", "")
            + " "
            + commit.get("pull_request_text", "")
        )
        commit_info = {
            "commit_hash": commit.get("commit_hash"),
            "commit_date": commit.get("commit_date"),
            "pull_request_text": pull_request_text,
            "change_text": change_text,
            "commit_message_text": commit.get("commit_message"),
            "filename": change_resource["filename"],
            "resource": change_resource,
        }
        return commit_info if change_text else None
