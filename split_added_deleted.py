
def get_added_deleted_lines():
    added_lines = ""
    deleted_lines = ""

    #TODO remove
    diff_file = 'data_collection/commit_data/commit_0b042dad43b7065c12f38980c90a0ad6bb823ccc/Commandbanip.java.diff'

    with open(diff_file, 'r') as f:
        for line in f:
            if line.startswith('+'):
                added_lines += line[1:].strip() + '\n'
            elif line.startswith('-'):
                deleted_lines += line[1:].strip() + '\n'
    return added_lines, deleted_lines

def main():
    added_lines, deleted_lines = get_added_deleted_lines()
    print(added_lines)
    print(deleted_lines)

if __name__ == "__main__":
    main()