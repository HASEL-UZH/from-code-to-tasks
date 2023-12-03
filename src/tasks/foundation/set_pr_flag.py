from src.store.mdb_store import Collection


def set_pr_flag():
    repositories = Collection.github_repository.find(
        {"language": "en", "languages": None}
    ).sort("stargazerCount", -1)
    repositories = repositories[:10]
    for repository in repositories:
        prs = list(
            Collection.github_pr.find({"identifier": repository.get("identifier")})
        )
        pr_commits = {
            d.get("mergeCommit").get("oid"): d for d in prs if d.get("mergeCommit")
        }

        pydriller_commits = Collection.pydriller_commit.find(
            {"repository_identifier": repository.get("identifier")}
        )
        match_count = 0
        nonmatch_count = 0
        flagged_prs = []
        for py_commit in pydriller_commits:
            pr_commit = pr_commits.get(py_commit.hash)
            if not pr_commit:
                nonmatch_count += 1
                continue
            else:
                match_count += 1
            if accept_pr(py_commit):
                py_commit["flag"] = True
            else:
                py_commit["flag"] = False
        Collection.flagged_pr.insert_many(flagged_prs)


def accept_pr(commit):
    # More than 50% test files --> False
    # Duplicate PR title --> False
    pass
