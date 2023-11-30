import statistics
from typing import TypedDict, Any

from src.core.utils import group_by
from src.store.mdb_store import Collection


class IPrInfo(TypedDict):
    pr: Any
    number_source_files: int
    number_unique_files: int
    number_test_files: int
    duplicate_title: bool
    number_of_lines: int


class IPrStatistics(TypedDict):
    repository_identifier: str
    pr_infos: [IPrInfo]
    src_files_max: int
    src_files_min: int
    lines_max: int
    lines_min: int


def get_pr_statistics(repository_identifier: str) -> IPrStatistics:
    pr_statistics: IPrStatistics = {
        "repository_identifier": repository_identifier,
        "pr_infos": [],
        "src_files_max": 0,
        "src_files_min": 0,
        "lines_max": 0,
        "lines_min": 0,
    }
    resources = Collection.resource.find(
        {"kind": "source", "repository_identifier": repository_identifier}
    )
    resource_groups = group_by(resources, "@container")
    pr_title_statistics = {}
    for commit_id, resource_group in resource_groups.items():
        pr = Collection.commit.find_one({"id": commit_id})
        pr_title = pr["pull_request_title"]
        pr_entry = pr_title_statistics.get(pr_title)
        if not pr_entry:
            pr_title_statistics[pr_title] = 0
        pr_title_statistics[pr_title] += 1

    for commit_id, resource_group in resource_groups.items():
        pr = Collection.commit.find_one({"id": commit_id})
        pr_title = pr["pull_request_title"]
        added_deleted_lines = pr["added_lines"] + pr["deleted_lines"]
        unique_file_names = list(set([d["name"] for d in resource_group]))
        pr_info: IPrInfo = {
            "pr": pr,
            "number_source_files": len(resource_group),
            "number_unique_files": len(unique_file_names),
            "number_test_files": len(
                [d for d in unique_file_names if "test" in d.lower()]
            ),
            "duplicate_title": pr_title_statistics[pr_title] > 1,
            "number_of_lines": added_deleted_lines,
        }
        pr_statistics["pr_infos"].append(pr_info)

    # TODO modify bandwidth of accepted src files
    src_files_values = [
        pr_info.get("number_source_files", 0) for pr_info in pr_statistics["pr_infos"]
    ]
    src_files_average_value = statistics.mean(src_files_values)
    src_files_std_deviation = statistics.stdev(src_files_values)
    src_files_max = src_files_average_value + 0.2 * src_files_std_deviation
    src_files_min = src_files_average_value - 0.2 * src_files_std_deviation

    # TODO modify bandwidth of accepted lines
    lines_values = [
        pr_info.get("number_of_lines", 0) for pr_info in pr_statistics["pr_infos"]
    ]
    lines_average_value = statistics.mean(lines_values)
    lines_std_deviation = statistics.stdev(lines_values)
    lines_max = lines_average_value + 0.2 * lines_std_deviation
    lines_min = lines_average_value - 0.2 * lines_std_deviation

    files_within_bandwidth = sum(
        1
        for num_files in src_files_values
        if src_files_min <= num_files <= src_files_max
    )

    total_files = len(src_files_values)
    print(
        f"Files within bandwidth ({src_files_min} to {src_files_max}): {files_within_bandwidth} out of {total_files}"
    )

    pr_statistics["src_files_max"] = src_files_max
    pr_statistics["src_files_min"] = src_files_min
    pr_statistics["lines_max"] = lines_max
    pr_statistics["lines_min"] = lines_min

    return pr_statistics
