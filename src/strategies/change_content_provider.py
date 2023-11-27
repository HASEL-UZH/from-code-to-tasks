from src.github.defs import RepositoryIdentifier
from src.store.mdb_store import db
from src.strategies.embeddings.defs import ContentStrategy


# FIXME use iterator
def get_commit_infos(content_strategy: ContentStrategy) -> [dict]:
    file_type = "text"
    if content_strategy["terms"] == "meta_ast_code":
        file_type = "java"

    change_resources = db.find_resources(
        {
            "strategy.meta": content_strategy["meta"],
            "kind": "term",
            "type": file_type,
            "strategy.terms": content_strategy["terms"],
            "repository_identifier": RepositoryIdentifier.iluwatar__java_design_patterns,
        }
    )
    commit_infos = []
    for change_resource in change_resources:
        commit = db.find_object(change_resource.get("@container"))
        change_text = db.get_resource_content(change_resource)
        pull_request_text = commit["pull_request_title"]
        commit_info = {
            "commit_hash": commit.get("commit_hash"),
            "commit_date": commit.get("commit_date"),
            "pull_request_text": pull_request_text,
            "change_text": change_text,
            "commit_message_text": commit.get("commit_message"),
            "filename": change_resource["filename"],
            "resource": change_resource,
        }
        if change_text:
            commit_infos.append(commit_info)
    return commit_infos


def get_change_content_infos(content_strategy: ContentStrategy):
    return get_commit_infos(content_strategy)
