from src.core.utils import group_by
from src.store.object_factory import ObjectFactory
from src.store.object_store import db
from src.strategies.terms.diff_text import create_diff_text
from src.strategies.terms.meta_ast_code import create_meta_ast_code
from src.strategies.terms.meta_ast_text import create_meta_ast_text


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


def change_term_creator_task():
    ast_strategies = [
        {"id": "meta_ast_text", "type": "text", "handler": create_meta_ast_text},
        {"id": "meta_ast_code", "type": "java", "handler": create_meta_ast_code},
    ]
    diff_strategies = [
        {"id": "diff_text", "type": "text", "handler": create_diff_text},
    ]

    meta_resources = db.find_resources({"kind": "change"})
    for resource in meta_resources:
        for strategy in ast_strategies:
            commit = db.find_object(resource["@container"])
            content = strategy["handler"](resource)
            term_resource = create_term_resource(
                commit,
                content,
                tpe=strategy["type"],
                meta_strategy=resource["strategy"]["meta"],
                term_strategy=strategy["id"],
            )
            db.save_resource(term_resource, invalidate=False)

    diff_resources = db.find_resources({"kind": "diff"})
    diff_groups = group_by(diff_resources, "@container")
    for key, diff_group_resources in diff_groups.items():
        for strategy in diff_strategies:
            commit = db.find_object(resource["@container"])
            content = strategy["handler"](diff_group_resources)
            term_resource = create_term_resource(
                commit,
                content,
                tpe="text",
                meta_strategy=None,
                term_strategy=strategy["id"],
            )
            db.save_resource(term_resource, invalidate=False)


if __name__ == "__main__":
    change_term_creator_task()
