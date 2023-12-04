import os

from langdetect import detect, DetectorFactory
from pydriller import Repository

from src.core.logger import log
from src.core.profiler import Profiler
from src.core.workspace_context import get_results_dir, write_csv_file, write_xlsx_file
from src.github.github_grapghql_api import github_graphql_api
from src.store.mdb import mdb
from src.store.mdb_store import Collection
from src.store.object_factory import get_repository_identifier

api = github_graphql_api


# Creates entries in github_repository collection
def insert_github_repositories():
    profiler = Profiler()
    result = api.find_top_java_repositories(n=100, max_pages=100) or []
    query_result = result.get("query")
    if True or result["ok"]:
        data = result.get("data")
        entries = []
        log.info(f"Insert {len(data)} repositories")
        base = {
            "quid": result.get("quid"),
            "timestamp": result.get("timestamp"),
        }
        for repository in result.get("data"):
            identifier = get_repository_identifier(repository["url"])
            repository["owner"] = repository.get("owner", {}).get("login", None)
            entry = {**({"identifier": identifier}), **base, **repository}

            entry.pop(
                "stargazers", None
            )  # remove nested stargazer property as we already stargazerCount
            entry["primaryLanguage"] = entry.get("primaryLanguage", {}).get(
                "name", None
            )
            entries.append(entry)

        Collection.github_repository.delete_many({})
        Collection.github_repository.insert_many(entries)

        Collection.github_query.insert_one(
            {
                **base,
                **(
                    {
                        "query": query_result["template"],
                        "variable": query_result["variables"],
                        "response_count": query_result["response_count"],
                    }
                ),
            }
        )

    else:
        log.error("insert_github_repositories failed")
    profiler.info("insert_github_repositories")


def _update_top_repositories_with_language():
    profiler = Profiler("update_top_repositories_with_language")
    repositories = list(Collection.github_repository.find())

    for d in repositories:
        profiler.debug(d.get("url"))
        lang_info = _get_text_language_info(d.get("description"))
        d["language"] = lang_info.get("language")
        d["languages"] = lang_info.get("languages")

        Collection.github_repository.update_one({"_id": d["_id"]}, {"$set": d})
    # }
    profiler.info("done")


def _update_top_repositories_with_stats():
    profiler = Profiler("update_top_repositories_with_stats")
    repositories = list(Collection.github_repository.find())

    max_disk_usage = max(d["diskUsage"] for d in repositories)
    max_fork_count = max(d["forkCount"] for d in repositories)
    max_stargazer_count = max(d["stargazerCount"] for d in repositories)

    for d in repositories:
        profiler.debug(d.get("url"))
        d["diskUsagePercent"] = (
            (d["diskUsage"] / max_disk_usage) if max_disk_usage != 0 else 0
        )
        d["forkCountPercent"] = (
            (d["forkCount"] / max_fork_count) if max_fork_count != 0 else 0
        )
        d["stargazerCountPercent"] = (
            (d["stargazerCount"] / max_stargazer_count)
            if max_stargazer_count != 0
            else 0
        )
        Collection.github_repository.update_one({"_id": d["_id"]}, {"$set": d})
    # }
    profiler.info("done")


def _update_top_repositories_with_pr_count():
    profiler = Profiler("update_top_repositories_with_pr_count")
    repositories = list(Collection.github_repository.find())
    for d in repositories:
        profiler.debug(d.get("url"))
        result = github_graphql_api.get_pull_request_count(
            owner=d["owner"], repository_name=d["name"]
        )
        if result["ok"]:
            d["pr_count"] = (
                result["data"]
                .get("repository", {})
                .get("pullRequests", {})
                .get("totalCount")
            )
            Collection.github_repository.update_one({"_id": d["_id"]}, {"$set": d})
    # }
    profiler.info("update_top_repositories_with_pr_count")


DetectorFactory.seed = 0


def _get_text_language_info(s):
    def get_language(text):
        try:
            return detect(text)
        except:
            return "unknown"

    def contains_chinese(text):
        if not text:
            return False
        for char in text:
            if "\u4e00" <= char <= "\u9fff":
                return True
        return False

    info = {
        "language": "unknown",
        "languages": None,
    }

    languages = []

    if s:
        info["language"] = get_language(s)
        if contains_chinese(s):
            languages.append(info["language"])
            languages.append("zh")
            if info["language"].startswith("zh"):
                log.info("Chinese")
            else:
                log.info("Mixed")

    if languages:
        info["languages"] = ", ".join(languages)
    return info


def _generate_top_repositories_stats():
    profiler = Profiler()
    repositories = list(Collection.github_repository.find())
    rows = []
    for d in repositories:
        # Calculating lastUpdate
        last_update_year = d["updatedAt"][:4] if "updatedAt" in d else ""
        row = {
            "identifier": d.get("identifier", ""),
            "lastUpdateYear": last_update_year,
            "diskUsagePercent": d.get("diskUsagePercent", ""),
            "forkCountPercent": d.get("forkCountPercent", ""),
            "stargazerCountPercent": d.get("stargazerCountPercent", ""),
        }
        rows.append(row)

    filepath = os.path.join(get_results_dir(), "repository_stats.csv")
    write_csv_file(filepath, rows)
    filepath_xslx = os.path.join(get_results_dir(), "repository_stats_gen.xlsx")
    write_xlsx_file(filepath_xslx, rows)

    profiler.info("_generate_top_repositories_stats")


def _verify_commit_consistencies(owner: str, repository_name: str):
    profiler = Profiler()
    repo_url = f"https://github.com/{owner}/{repository_name}"
    log.info(f"Get commits for repository: {repo_url}")
    # git_repository = Repository(repo_url, only_modifications_with_file_types=[".java"])
    git_repository = Repository(repo_url)
    commits = []
    for commit in git_repository.traverse_commits():
        commits.append(commit)
    profiler.debug(
        f"Total commits in repository '{repo_url}': {len(commits)} (PyDriller)"
    )

    query = """
      {
        repository(owner: "{owner}", name: "{repository_name}") {
          defaultBranchRef {
            target {
              ... on Commit {
                history {
                  totalCount
                }
              }
            }
          }
        }
      }
    """
    query = query.replace("{owner}", owner)
    query = query.replace("{repository_name}", repository_name)

    result = api.execute_grapqhql_query(query)
    count = result["data"]["repository"]["defaultBranchRef"]["target"]["history"][
        "totalCount"
    ]
    profiler.debug(f"Total commits in repository '{repo_url}': {count} (GrapghQL)")
    commits_map = {d.hash: d for d in commits}

    pr_count = 0
    merge_count = 0
    match_count = 0
    nonmatch_count = 0

    def check_commit(commit_id):
        nonlocal match_count
        nonlocal nonmatch_count
        c = commits_map.get(commit_id)
        if c:
            match_count += 1
        else:
            nonmatch_count += 1

    c_pr = mdb["pr"]
    prs = c_pr.find()
    for pr in prs:
        pr_count += 1
        merge_commit = pr.get("mergeCommit")
        if merge_commit:
            merge_count += 1
            check_commit(merge_commit["oid"])
        commits = pr.get("commits")
        if commits:
            for c in commits:
                check_commit(c["oid"])

    # }
    profiler.info(
        f"Commit consistency check, pr_count: {pr_count}, merge_comit_count: {merge_count}, match: '{match_count}', non matched: {nonmatch_count}"
    )


if __name__ == "__main__":
    print(f"Rate limit: {api.get_rate_limit()}")
    insert_github_repositories()
    print("Done.")
