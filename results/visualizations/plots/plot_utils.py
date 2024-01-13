import os

import numpy as np
import pandas as pd

from src.core.workspace_context import get_results_dir


def get_data(filter_criteria, group_criteria, subgroup_criteria=None):
    combined_data = pd.DataFrame()
    folder_path = get_results_dir()

    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]
    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        df = pd.read_csv(file_path)

        mask = np.ones(len(df), dtype=bool)
        for filter_key, filter_value in filter_criteria.items():
            mask &= df[filter_key] == filter_value

        filtered_data = df[mask]
        combined_data = pd.concat([combined_data, filtered_data], ignore_index=True)

        group_criteria = get_merged_group_criteria(group_criteria, subgroup_criteria)

        combined_data.loc[
            combined_data["embeddings_strategy"]
            == "tf-idf-embedding--standard-tokenizer",
            "embeddings_strategy",
        ] = "tf-embedding--standard-tokenizer"

        combined_data.loc[
            combined_data["embeddings_strategy"]
            == "tf-idf-embedding--subword-tokenizer",
            "embeddings_strategy",
        ] = "tf-embedding--subword-tokenizer"

        for group_key, group_values in group_criteria.items():
            combined_data = combined_data[combined_data[group_key].isin(group_values)]

        if "term_strategy" in group_criteria:
            term_strategy_values = group_criteria.get("term_strategy", [])
            if "meta_ast_text" in term_strategy_values:
                combined_data = combined_data[
                    (combined_data["term_strategy"] != "meta_ast_text")
                    | (
                        (combined_data["term_strategy"] == "meta_ast_text")
                        & (combined_data["meta_strategy"] == "ast-lg")
                    )
                ]

        combined_data = combined_data.rename(
            columns=lambda x: "codebert" if "codebert" in x else x
        )

        grouped_data = (
            combined_data.groupby(list(group_criteria.keys()))
            .apply(custom_aggregation)
            .reset_index()
        )
    return grouped_data


def get_merged_group_criteria(group_criteria, subgroup_criteria):
    if subgroup_criteria is not None:
        merged_group_criteria = group_criteria.copy()
        merged_group_criteria.update(subgroup_criteria)
        return merged_group_criteria
    else:
        return group_criteria


def custom_aggregation(group):
    mean_value = np.mean(group["mean"])
    std_value = np.std(group["mean"])
    var_value = np.var(group["mean"])
    return pd.Series({"Mean": mean_value, "Std": std_value, "Var": var_value})


def get_formatted_identifier(identifier):
    format = {
        "iluwatar__java-design-patterns": "java-\ndesign-\npatterns",
        "reactive_x___rx_java": "RxJava",
        "eugenp__tutorials": "tutorials",
        "airbnb__lottie-android": "lottie-\nandroid",
        "bumptech__glide": "glide",
        "apolloconfig__apollo": "apollo",
        "selenium_hq__selenium": "selenium",
        "alibaba__nacos": "nacos",
        "netty__netty": "netty",
        "apache__dubbo": "dubbo",
    }
    return format[identifier]


def get_identifiers():
    return [
        "iluwatar__java-design-patterns",
        "reactive_x___rx_java",
        "apache__dubbo",
        "eugenp__tutorials",
        "airbnb__lottie-android",
        "bumptech__glide",
        "netty__netty",
        "apolloconfig__apollo",
        "selenium_hq__selenium",
        "alibaba__nacos",
    ]


def get_formatted_label(label):
    format_label = {
        "window_size": "Window Size",
        "k": "Top-K",
        "meta_strategy": "Code Feature Set",
        "embeddings_concept": "Vectorization Technique",
        "W": "Window Size",
        "V": "Vectorization Technique",
        "C": "Code Change Information",
        "T": "Tokenization Technique",
        "K": "Top-K",
        "term_strategy": "Code Change Information",
        "repository_identifier": "CodeBERT Transformation",
    }
    return format_label[label] if label in format_label else label


def get_formatted_item(item):
    format_item = {
        "window_size": "W",
        "k": "K",
        "meta_strategy": "Set",
        "embeddings_concept": "V",
        "tf_idf": "TF-IDF",
        "tf": "TF",
        "term_strategy": "C",
        "tf-embedding--standard-tokenizer": "Standard",
        "tf-embedding--subword-tokenizer": "Subword",
        "repository_identifier": "CodeBERT T",
    }
    return format_item[item] if item in format_item else item


def get_formatted_value(value):
    format_value = {
        "ast-lg": "LG",
        "ast-md": "MD",
        "ast-sm": "SM",
        "tf": "TF",
        "tf_idf": "TF-IDF",
        "tf-embedding--standard-tokenizer": "Standard",
        "tf-embedding--subword-tokenizer": "Subword",
        "codebert": "CodeBERT",
        "diff_text": "Diff",
        "diff_text/meta_ast_text": "Combined",
        "meta_ast_text": "AST",
        "meta_ast_code": "AST",
        "codebert-embedding": "Flattening",
        "codebert-summed-embedding": "Sum Pooling",
    }
    return format_value[value] if value in format_value else value
