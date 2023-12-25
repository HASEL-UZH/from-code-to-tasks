from src.core.profiler import Profiler
from src.core.utils import group_by
from src.github.defs import RepositoryIdentifier
from src.store.object_factory import ObjectFactory
from src.store.mdb_store import db
from src.strategies.terms.diff_text import create_diff_text
from src.strategies.terms.meta_ast_code import create_meta_ast_code
from src.strategies.terms.meta_ast_text import create_meta_ast_text
from src.tasks.pipeline_context import PipelineContext, DEFAULT_PIPELINE_CONTEXT


def change_term_creator_task(context: PipelineContext):
    ast_strategies = [
        {"id": "meta_ast_text", "type": "text", "handler": create_meta_ast_text},
        {"id": "meta_ast_code", "type": "java", "handler": create_meta_ast_code},
    ]
    diff_strategies = [
        {"id": "diff_text", "type": "text", "handler": create_diff_text},
    ]

    profiler = Profiler("change_term_creator_task")
    count = 0
    meta_resources = db.find_resources(
        context.create_resource_criteria(
            {
                "kind": "change",
            }
        )
    )
    for resource in meta_resources:
        count += 1
        profiler.debug(f"Count: {count}, resource: {resource['filename']}")
        for strategy in ast_strategies:
            commit = db.find_object(resource["@container"])
            content = strategy["handler"](resource) or ""
            term_resource = create_term_resource(
                commit,
                content,
                tpe=strategy["type"],
                meta_strategy=resource["strategy"]["meta"],
                term_strategy=strategy["id"],
            )
            db.save_resource(term_resource, commit)

    diff_resources = db.find_resources(
        context.create_resource_criteria({"kind": "diff"})
    )
    diff_groups = group_by(diff_resources, "@container")
    for commit_id, diff_group_resources in diff_groups.items():
        commit = db.find_object(commit_id)
        for strategy in diff_strategies:
            content = strategy["handler"](diff_group_resources) or ""
            term_resource = create_term_resource(
                commit,
                content,
                tpe="text",
                meta_strategy=None,
                term_strategy=strategy["id"],
            )
            db.save_resource(term_resource, commit)


def create_term_resource(commit, content, tpe, meta_strategy, term_strategy):
    return ObjectFactory.resource(
        commit,
        {
            "name": "change-repr",
            "type": tpe,
            "kind": "term",
            "version": None,
            "content": content,
            "strategy": {"meta": meta_strategy, "terms": term_strategy},
        },
    )


if __name__ == "__main__":
    change_term_creator_task(DEFAULT_PIPELINE_CONTEXT)
