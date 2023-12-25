from src.ast.create_ast_change_model import create_ast_change_model
from src.core.profiler import Profiler
from src.core.utils import group_by, accessor
from src.github.defs import RepositoryIdentifier
from src.store.object_factory import ObjectFactory
from src.store.mdb_store import db
from src.tasks.pipeline_context import PipelineContext, DEFAULT_PIPELINE_CONTEXT


def change_model_creator_task(context: PipelineContext):
    db.delete_resources_where(
        context.create_resource_criteria({"kind": "change", "type": "json"})
    )

    profiler = Profiler("change_model_creator_task")

    meta_resources = list(
        db.find_resources(
            context.create_resource_criteria(
                {
                    "kind": "meta",
                }
            )
        )
    )
    group_key_lambda = lambda x: x.get("strategy").get("meta")
    grouped_meta_resources = group_by(meta_resources, group_key_lambda)

    for meta_key in grouped_meta_resources:
        meta_ast_group = grouped_meta_resources[meta_key]
        profiler.info(f"create change model for: {meta_key}")

        count = 0
        commit_groups = group_by(meta_ast_group, "@container")
        for commit_key, commit_resources in commit_groups.items():
            commit = db.find_object(commit_key)

            profiler.debug(f"Commit: {commit['id']}")

            resource_dict = {}
            resource_groups = group_by(commit_resources, "name")
            for resource_name, file_resources in resource_groups.items():
                resource_before = next(
                    (d for d in file_resources if d.get("version") == "before"), None
                )
                resource_after = next(
                    (d for d in file_resources if d.get("version") == "after"), None
                )
                meta_before = db.get_resource_content(resource_before)
                meta_after = db.get_resource_content(resource_after)
                resource_dict[resource_name] = (meta_before, meta_after)

            change_object = create_ast_change_model(resource_dict, commit)
            change_resource = ObjectFactory.resource(
                commit,
                {
                    "name": "change-model",
                    "type": "json",
                    "kind": "change",
                    "version": None,
                    "content": change_object,
                    "strategy": {"meta": meta_key},
                },
            )
            db.save_resource(change_resource, commit)
            count += 1
            if count % 10 == 0:
                profiler.debug(f"Change model progress: {count}")

        # }
        profiler.info(f"change_model_creator_task done: {count}")


# }


if __name__ == "__main__":
    change_model_creator_task(DEFAULT_PIPELINE_CONTEXT)
