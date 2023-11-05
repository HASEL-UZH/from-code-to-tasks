import re
from collections import defaultdict

# grouped = group_by(data, "age")
#
# for key, group in grouped.items():
#     print(f"Group {key}:")
#     for item in group:
#         print(f"  {item}")
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
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def is_date(d):
    return type(d).__name__ == "date"

# example accessor(customer, "address", "street")
def accessor(obj, *keys):
    if not obj:
        return None
    for key in keys:
        try:
            # Attempt to get the key if the object is not None
            obj = obj.get(key) if obj is not None else None
        except AttributeError:
            # If obj does not have .get (it's not a dict), return None
            return None
    return obj

def get_date_string(d):
    if not is_date(d):
        return None
    return d.strftime('%Y-%m-%d')


