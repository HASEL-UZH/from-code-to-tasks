from src.ast.create_ast_change_model import create_ast_change_model
from src.core.profiler import Profiler
from src.core.utils import group_by, accessor
from src.store.object_factory import ObjectFactory
from src.store.object_store import db


def change_model_creator_task():
    change_model_resources = db.find_resources({"kind": "change", "type": "json"})
    db.delete_resources(change_model_resources)

    profiler = Profiler()

    meta_resources = db.find_resources({"kind": "meta"})
    group_key_lambda = lambda x: x.get("strategy").get("meta")
    grouped_meta_resources = group_by(meta_resources, group_key_lambda)

    for meta_key in grouped_meta_resources:
        meta_ast_group = grouped_meta_resources[meta_key]
        print(f"create change model for: {meta_key}")

        count = 0
        commit_groups = group_by(meta_ast_group, "@container")
        for commit_key, commit_resources in commit_groups.items():
            commit = db.find_object(commit_key)

            meta_strategy_groups = group_by(
                commit_resources, lambda d: accessor(d, "strategy", "meta")
            )
            for (
                meta_strategy_key,
                meta_strategy_resources,
            ) in meta_strategy_groups.items():
                resource_dict = {}
                resource_groups = group_by(meta_strategy_resources, "name")
                for resource_key, file_resources in resource_groups.items():
                    resource_before = db.find_one({"version": "before"}, file_resources)
                    resource_after = db.find_one({"version": "after"}, file_resources)
                    meta_before = db.get_resource_content(resource_before)
                    meta_after = db.get_resource_content(resource_after)
                    resource_dict[resource_key] = (meta_before, meta_after)
                change_object = create_ast_change_model(resource_dict, commit)
                change_resource = ObjectFactory.resource(
                    commit,
                    {
                        "name": "change-model",
                        "type": "json",
                        "kind": "change",
                        "version": None,
                        "content": change_object,
                        "strategy": {"meta": meta_strategy_key},
                    },
                )
                db.save_resource(change_resource, invalidate=False)
                count += 1
                if count % 10 == 0:
                    profiler.checkpoint(f"Change model progress: {count}")

        # }
        profiler.checkpoint(f"change_model_creator_task done: {count}")
        db.invalidate()


# }


if __name__ == "__main__":
    change_model_creator_task()
