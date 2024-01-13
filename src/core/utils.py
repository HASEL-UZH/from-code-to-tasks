import hashlib
import json
import re


def group_by(items, property):
    grouped_data = {}

    accessor = None
    if isinstance(property, str):
        accessor = lambda d: d.get(property)
    elif callable(property):
        accessor = property

    if not accessor:
        raise RuntimeError("Illegal property accessor")

    for item in items:
        key = accessor(item)
        if key not in grouped_data:
            grouped_data[key] = []
        grouped_data[key].append(item)

    return grouped_data


def camel_to_snake(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def remove_cr_lf(s):
    return s.replace("\n", "").replace("\r", "")


def truncate_string(s, max_length=1000):
    if len(s) > max_length:
        return s[:max_length] + "…"
    else:
        return s


def split_string(s):
    if s is None:
        return []
    s = re.sub("[-_]", " ", s)
    s = re.sub(r"(?<!^)(?=[A-Z])", " ", s)
    return [part for part in s.split(" ") if part]


def hash_string(s):
    if s is None:
        s = ""
    md5_hash = hashlib.md5(s.encode()).hexdigest()
    return md5_hash


def hash_object(obj):
    return hash_string(json.dumps(obj))


def is_date(d):
    return type(d).__name__ == "date"


def accessor(obj, *keys):
    if not obj:
        return None
    for key in keys:
        try:
            obj = obj.get(key) if obj is not None else None
        except AttributeError:
            return None
    return obj


def get_date_string(d):
    if not is_date(d):
        return None
    return d.strftime("%Y-%m-%d")
