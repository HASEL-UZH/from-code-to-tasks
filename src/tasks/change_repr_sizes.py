from statistics import mean

from src.core.logger import log
from src.store.mdb_store import db, Collection


def create_term_repr_size(context):
    resources = list(
        db.find_resources(
            context.create_resource_criteria(
                {
                    "kind": "term",
                }
            )
        )
    )
    total = len(resources)
    data = []
    for i, resource in enumerate(resources):
        log.info(f"{i}/{total}")
        size = db.get_resource_size(resource)
        resource_data = {
            "kind": resource.get("kind", ""),
            "strategy": resource.get("strategy", ""),
            "type": resource.get("type", ""),
            "size": size,
        }
        data.append(resource_data)
    Collection.term_repr_size.insert_many(data)


def create_term_size_statistics():
    categories = [
        {"terms": "diff_text", "meta": None},
        {"terms": "meta_ast_text", "meta": "ast-sm"},
        {"terms": "meta_ast_text", "meta": "ast-md"},
        {"terms": "meta_ast_text", "meta": "ast-lg"},
        {"terms": "meta_ast_code", "meta": "ast-sm"},
        {"terms": "meta_ast_code", "meta": "ast-md"},
        {"terms": "meta_ast_code", "meta": "ast-lg"},
    ]

    mean_sizes = {}

    for category_info in categories:
        meta = category_info["meta"]
        terms = category_info["terms"]
        meta_strategy_query = {"strategy": {"meta": meta, "terms": terms}}
        resources = list(Collection.term_repr_size.find(meta_strategy_query))
        sizes = [resource.get("size", 0) for resource in resources]
        mean_size = mean(sizes) if sizes else 0
        mean_sizes[f"{terms} {meta}"] = mean_size

    mean_sizes_kB = {
        category: mean_size / 1024 for category, mean_size in mean_sizes.items()
    }
    for category_info in categories:
        meta = category_info["meta"]
        terms = category_info["terms"]
        print(
            f"Mean size for {terms} {meta}: {mean_sizes_kB[f'{terms} {meta}']:.2f} kB"
        )


if __name__ == "__main__":
    create_term_size_statistics()
