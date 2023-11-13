def filter_json(root, accept_fn, sort=True):
    """
    Filter a JSON structure, calling a function for each value to determine if it should be included in the result.

    Args:
    - root (any): The JSON data.
    - accept_fn (function): A function to call for each value in the JSON structure, returns True to keep or
        False to discard the given value
        - Args:
            - value (any) the current value
            - parent (any) the parent object
            - parent_key (string|number|null) the parent key or index
            - level (number) the level of nesting
    """

    def _filter(node, parent, parent_key, level):
        if isinstance(node, dict):
            if sort:
                node = dict(sorted(node.items()))
            return {
                key: _filter(value, node, key, level + 1)
                for key, value in node.items()
                if accept_fn(value, node, key, level)
            }

        if isinstance(node, list):
            return [
                _filter(value, node, index, level + 1)
                for index, value in enumerate(node)
                if accept_fn(value, node, index, level)
            ]

        return node

    return _filter(root, None, None, 0)


def traverse_json(root, visitor_fn):
    """
    Traverse a JSON structure, calling a function for each value.

    Args:
    - root (any): The JSON data.
    - visitor_fn (function): A function to call for each value in the JSON structure.
        - Args:
            - value (any) the current value
            - parent (any) the parent object
            - parent_key (string|number|null) the parent key or index
            - level (number) the level of nesting
    """

    def _traverse(node, parent, parent_key, level):
        visitor_fn(node, parent, parent_key, level)

        if isinstance(node, dict):
            for key, value in node.items():
                _traverse(value, node, key, level + 1)

        elif isinstance(node, list):
            for index, value in enumerate(node):
                _traverse(value, node, index, level + 1)

    _traverse(root, None, None, 0)


def traverse_json_with_context(root, enter_fn, exit_fn=None, context=None):
    def _traverse(node, parent, parent_key, level):
        enter_fn(node, parent, parent_key, level, context)

        if isinstance(node, dict):
            for key, value in node.items():
                _traverse(value, node, key, level + 1)

        elif isinstance(node, list):
            for index, value in enumerate(node):
                _traverse(value, node, index, level + 1)

        if exit_fn:
            exit_fn(node, parent, parent_key, level, context)

        return context

    return _traverse(root, None, None, 0)
