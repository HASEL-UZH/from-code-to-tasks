import os

import numpy as np
import pandas as pd


def get_data(filter_criteria, group_criteria, subgroup_criteria=None):
    combined_data = pd.DataFrame()
    current_directory = os.getcwd()
    csv_files = [
        file for file in os.listdir(current_directory) if file.endswith(".csv")
    ]

    for csv_file in csv_files:
        file_path = os.path.join(os.getcwd(), csv_file)
        df = pd.read_csv(file_path)

        mask = np.ones(len(df), dtype=bool)
        for filter_key, filter_value in filter_criteria.items():
            mask &= df[filter_key] == filter_value

        filtered_data = df[mask]
        combined_data = pd.concat([combined_data, filtered_data], ignore_index=True)

        grouped_data = (
            combined_data.groupby(list(group_criteria.keys()))
            .apply(custom_aggregation)
            .reset_index()
        )
    return grouped_data


def custom_aggregation(group):
    mean_value = np.mean(group["mean"])
    std_value = np.std(group["mean"])
    var_value = np.var(group["mean"])
    return pd.Series({"Mean": mean_value, "Std": std_value, "Var": var_value})


def get_formatted_identifier(identifier):
    format = {
        "iluwatar__java-design-patterns": "java-design-patterns",
        "reactive_x___rx_java": "RxJava",
        "eugenp__tutorials": "tutorials",
        "airbnb__lottie-android": "lottie-android",
        "bumptech__glide": "glide",
        "apolloconfig__apollo": "apollo",
        "selenium_hq__selenium": "selenium",
        "alibaba__nacos": "nacos",
    }
    return format[identifier]


def get_identifiers():
    return [
        "iluwatar__java-design-patterns",
        "reactive_x___rx_java",
        "eugenp__tutorials",
        "airbnb__lottie-android",
        "bumptech__glide",
        "apolloconfig__apollo",
        "selenium_hq__selenium",
        "alibaba__nacos",
    ]


def get_formatted_label(label):
    format_label = {
        "window_size": "Window Size",
        "k": "Top-K",
        "meta_strategy": "Code Element Set",
    }
    return format_label[label] if label in format_label else label


def get_formatted_item(item):
    format_item = {"window_size": "W", "k": "K", "meta_strategy": "Set"}
    return format_item[item] if item in format_item else item


def get_formatted_value(value):
    format_value = {
        "ast-lg": "Large",
        "ast-md": "Medium",
        "ast-sm": "Small",
    }
    return format_value[value] if value in format_value else value
