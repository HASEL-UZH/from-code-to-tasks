import re

from src.analytics.pr_statistics import get_pr_statistics
from src.store.mdb_store import db, Collection
from src.strategies.defs import IContentStrategy, ICommitInfo
from src.tasks.pipeline_context import PipelineContext


class ChangeContentProvider:
    def get_content(
        self, context: PipelineContext, content_strategy: IContentStrategy
    ) -> [ICommitInfo]:
        file_type = "text"
        if content_strategy["terms"] == "meta_ast_code":
            file_type = "java"

        criteria = context.create_resource_criteria(
            {
                "strategy.meta": content_strategy["meta"],
                "kind": "term",
                "type": file_type,
                "strategy.terms": content_strategy["terms"],
            }
        )
        change_resources = db.find_resources(criteria)
        commit_infos: [ICommitInfo] = []
        for change_resource in change_resources:
            commit_info = self._get_commit_info(context, change_resource)
            if commit_info is not None:
                pr_filter = PrFilter(context)
                if pr_filter.accept_commit_info(commit_info["commit_hash"]):
                    commit_infos.append(commit_info)
        return commit_infos

    def _get_commit_info(
        self, context: PipelineContext, change_resource
    ) -> ICommitInfo:
        change_content = db.get_resource_content(change_resource, volatile=True)
        change_text = change_content.strip() if change_content else ""
        commit = db.find_object(change_resource.get("@container"))
        pull_request_title = commit.get("pull_request_title", "")
        pull_request_text = commit.get("pull_request_text", "")
        issue_text = ""
        numbers = [int(d) for d in re.findall(r"\d+", pull_request_title)]
        if len(numbers):
            issues = list(
                Collection.github_issue.find(
                    context.create_issue_criteria({"number": {"$in": numbers}})
                )
            )
            issue_items = []
            for issue in issues:
                issue_items.append(issue["title"])
                # issue_items.append(issue["bodyText"])
            issue_text = " ".join(issue_items)

        pull_request_text = " ".join(
            [pull_request_title, pull_request_text, issue_text]
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


class PrFilter:
    def __init__(self, context):
        # TODO fix repository identifier
        self._pr_statistics = get_pr_statistics("iluwatar__java-design-patterns")
        self._lookup = self.create_lookup_dict(context)

    def accept_commit_info(self, commit_id) -> bool:
        pr_info = self._lookup[commit_id]
        # Remove PRs with duplicate title
        if pr_info["duplicate_title"]:
            return False
        # # Remove PRs where majority of files are test files
        if pr_info["number_test_files"] / pr_info["number_source_files"] > 0.5:
            return False
        # Remove PRs with too many or too little files
        if (
            pr_info["number_source_files"] > self._pr_statistics["src_files_max"]
            or pr_info["number_source_files"] < self._pr_statistics["src_files_min"]
        ):
            return False
        if (
            pr_info["number_lines"] > self._pr_statistics["lines_max"]
            or pr_info["number_lines"] < self._pr_statistics["lines_min"]
        ):
            return False
        return True

    def create_lookup_dict(self, context):
        lookup_dict = {
            pr_info["pr"]["commit_hash"]: {
                k: v for k, v in pr_info.items() if k != "pr"
            }
            for pr_info in self._pr_statistics["pr_infos"]
        }
        return lookup_dict
