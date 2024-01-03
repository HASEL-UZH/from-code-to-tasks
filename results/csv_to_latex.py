import os

import pandas as pd

from src.core.workspace_context import get_results_dir


def get_formatted_column_header(column):
    format_dict = {
        "k": "K",
        "window_size": "W",
        "embeddings_concept": "V",
        "embeddings_strategy": "T",
        "meta_strategy": "C",
        "term_strategy": "R",
        "mean": "Mean Accuracy",
    }

    return format_dict.get(column, column)


def get_formatted_value(column, value):
    format_dict = {
        "tf": "TF",
        "tf_idf": "TF-IDF",
        "window_size": "W",
        "tf-idf-embedding--standard-tokenizer": "Standard",
        "tf-idf-embedding--subword-tokenizer": "Subword",
        "tf-embedding--standard-tokenizer": "Standard",
        "tf-embedding--subword-tokenizer": "Subword",
        "meta_ast_text": "Text",
        "diff_text": "Text",
        "diff_text/meta_ast_text": "Text",
        "meta_ast_code": "Code",
        "ast-lg": "Source (LG)",
        "ast-md": "Source (MD)",
        "ast-sm": "Source (SM)",
        "None/ast-lg": "Combined",
        "nan": "Diff",
        "codebert-embedding": "-",
        "codebert-summed-embedding": "-",
        "codebert": "CodeBERT (Flattening)",
        "codebert-summed": "CodeBERT (Sum Pooling)",
    }
    if column == "mean":
        float_value = float(value)
        return "{:.2f}".format(float_value)
    else:
        return format_dict.get(value, value)


def csv_to_latex(csv_filename, caption, label):
    # Read CSV file into a DataFrame
    df = pd.read_csv(csv_filename)

    selected_rows = df[
        ((df["k"] == 1) & (df["window_size"] == 10))
        | ((df["k"] == 2) & (df["window_size"] == 10))
        | ((df["k"] == 3) & (df["window_size"] == 10))
        | ((df["k"] == 1) & (df["window_size"] == 20))
        | ((df["k"] == 1) & (df["window_size"] == 50))
    ]

    # Selected columns for the LaTeX table
    selected_columns = [
        "k",
        "window_size",
        "embeddings_concept",
        "embeddings_strategy",
        "meta_strategy",
        "term_strategy",
        "mean",
    ]

    # Generate LaTeX table string
    latex_table = (
        "\\begin{longtable}{|" + "|".join(["c"] * (len(selected_columns))) + "|}\n"
    )
    latex_table += "\\hline\n"
    latex_table += (
        " & ".join([get_formatted_column_header(col) for col in selected_columns])
        + " \\\\\n"
    )
    latex_table += "\\hline\n"
    latex_table += "\\endfirsthead\n"
    latex_table += "\\caption[]{Continued from previous page} \\\\\n"
    latex_table += "\\hline\n"
    latex_table += (
        " & ".join([get_formatted_column_header(col) for col in selected_columns])
        + " \\\\\n"
    )
    latex_table += "\\hline\n"
    latex_table += "\\endhead\n"
    latex_table += "\\hline\n"
    latex_table += (
        "\\multicolumn{"
        + str(len(selected_columns))
        + "}{r}{Continued on next page} \\\\\n"
    )
    latex_table += "\\endfoot\n"
    latex_table += "\\hline\n"
    latex_table += "\\caption{" + caption + "} \n"
    latex_table += "\\label{" + label + "}\n"
    latex_table += "\\endlastfoot\n"

    # Add table data
    for _, row in selected_rows.iterrows():
        values = [get_formatted_value(col, str(row[col])) for col in selected_columns]
        latex_table += " & ".join(values) + " \\\\\n"
        latex_table += "\\hline\n"

    # Complete the table
    latex_table += "\\end{longtable}\n"

    return latex_table


def generate_and_save_latex_tables(folder_path, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)

        caption_dict = {
            "results_airbnb__lottie-android.csv": "Result Runs for lottie-android by airbnb",
            "results_alibaba__nacos.csv": "Result Runs for nacos by alibaba",
            "results_apolloconfig__apollo.csv": "Result Runs for apollo by apolloconfig",
            "results_bumptech__glide.csv": "Result Runs for glide by bumptech",
            "results_eugenp__tutorials.csv": "Result Runs for tutorials by eugenp",
            "results_iluwatar__java-design-patterns.csv": "Result Runs for java-design-patterns by iluwatar",
            "results_reactive_x___rx_java.csv": "Result Runs for RxJava by ReactiveX",
            "results_selenium_hq__selenium.csv": "Result Runs for selenium by SeleniumHQ",
            "results_apache__dubbo.csv": "Result Runs for dubbo by apache",
            "results_netty__netty.csv": "Result Runs for netty by netty",
        }

        label_dict = {
            "results_airbnb__lottie-android.csv": "result-runs-lottie-android-airbnb",
            "results_alibaba__nacos.csv": "result-runs-nacos-alibaba",
            "results_apolloconfig__apollo.csv": "result-runs-apollo-apolloconfig",
            "results_bumptech__glide.csv": "result-runs-glide-bumptech",
            "results_eugenp__tutorials.csv": "result-runs-tutorials-eugenp",
            "results_iluwatar__java-design-patterns.csv": "result-runs-java-design-patterns-iluwatar",
            "results_reactive_x___rx_java.csv": "result-runs-rxjava-reactivex",
            "results_selenium_hq__selenium.csv": "result-runs-selenium-seleniumhq",
            "results_apache__dubbo.csv": "result-runs-dubbo-apache",
            "results_netty__netty.csv": "result-runs-netty-netty",
        }

        caption = caption_dict[csv_file]
        label = label_dict[csv_file]

        latex_table_string = csv_to_latex(file_path, caption, label)

        # Save the LaTeX table string to a text file in the output folder
        txt_filename = os.path.join(output_folder, f"{label_dict[csv_file]}-table.tex")
        with open(txt_filename, "w") as txt_file:
            txt_file.write(latex_table_string)


if __name__ == "__main__":
    folder_path = get_results_dir()
    output_folder = "latex-results"  # Change to the desired output folder
    generate_and_save_latex_tables(folder_path, output_folder)
