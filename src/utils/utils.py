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