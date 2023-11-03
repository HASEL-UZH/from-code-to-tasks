import re

# grouped = group_by(data, "age")
#
# for key, group in grouped.items():
#     print(f"Group {key}:")
#     for item in group:
#         print(f"  {item}")
def group_by(items, property_name):
    grouped_data = {}

    for item in items:
        key = item.get(property_name)
        if key not in grouped_data:
            grouped_data[key] = []
        grouped_data[key].append(item)

    return grouped_data


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def is_date(d):
    return type(d).__name__ == "date"


def get_date_string(d):
    if not is_date(d):
        return None
    return d.strftime('%Y-%m-%d')
