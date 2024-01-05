import sys

from src.store.mdb_store import Collection
from src.tasks.foundation.insert_github_issues import insert_github_issues
from src.tasks.foundation.insert_github_pr import insert_github_pr
from src.tasks.foundation.insert_pr_info import insert_pr_info
from src.tasks.foundation.insert_pydriller_commit import insert_pydriller_commit


def main():
    if len(sys.argv) != 3:
        print("Usage: python do_it.py <action> <repository>")
        sys.exit(1)

    action = sys.argv[1]
    repo = sys.argv[2]
    repository = list(
        Collection.github_repository.find(
            {
                "identifier": repo,
            }
        )
    )

    if action == "insert_github_pr":
        insert_github_pr(repository)
    elif action == "insert_github_issues":
        insert_github_issues(repository)
    elif action == "insert_pydriller_commit":
        insert_pydriller_commit(repository)
    elif action == "insert_pr_info":
        insert_pr_info(repository)
    else:
        print(
            "Invalid action. Supported actions: insert_github_pr, insert_github_issues, insert_pydriller_commit, insert_pr_info"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
