from src.store.object_store import db


def create_diff_text(diff_resources):
    additions = []
    deletions = []
    modifications = []
    for diff_resource in diff_resources:
        diff_content = db.get_resource_content(diff_resource)
        diff_additions, diff_deletions, diff_modifications = parse_diff_content(
            diff_content
        )
        additions.extend(diff_additions)
        deletions.extend(diff_deletions)
        modifications.extend(diff_modifications)

    content = "\n".join(additions + modifications + deletions)
    return content


def parse_diff_content(content):
    additions = []
    deletions = []
    modifications = []

    lines = content.split("\n")
    for line in lines:
        if line.startswith("+"):
            additions.append(line[1:])
        elif line.startswith("-"):
            deletions.append(line[1:])
        elif line.startswith("@@"):
            modifications.append(line[2:])

    return additions, deletions, modifications
