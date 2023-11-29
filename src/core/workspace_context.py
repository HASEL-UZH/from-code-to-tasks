import os
import csv
import json
from openpyxl import Workbook
from src.core.logger import log

STORE_ROOT = os.path.abspath("./_store")
RESULTS_DIR = os.path.abspath("./results")


def get_store_dir(path=None):
    full_path = STORE_ROOT
    if path:
        full_path = os.path.join(STORE_ROOT, path)
    return get_or_create_dir(full_path)


def get_results_dir():
    return get_or_create_dir(RESULTS_DIR)


def get_results_file(filepath):
    return os.path.join(get_results_dir(), filepath)


def get_cache_dir():
    return get_store_dir(".cache")


# --- Check file type


def is_java_file(file_name):
    return file_name.endswith(".java")


def is_ast_file(file_name):
    return file_name.endswith("ast.json") and not file_name.endswith("meta_ast.json")


def is_ast_meta_file(file_name):
    return file_name.endswith("meta_ast.json")


# returns the file extensions including the '.'
def get_file_ext(file_name):
    _, ext = os.path.splitext(file_name)
    return ext


# returns the file extensions without the '.'
def get_file_ext_name(file_name):
    _, ext = os.path.splitext(file_name)
    return ext[1:]


def get_file_base_name(file_name):
    base, _ = os.path.splitext(file_name)
    return base


# --- File IO


def get_or_create_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)
    return dir_name


# Load json
def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
        return data


def read_text_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
        return content


# Write json
def write_json_file(file_path, file_content, format=True):
    with open(file_path, "w") as json_file:
        json.dump(file_content, json_file, indent=4 if format else 0)


def write_text_file(file_path, file_content, opts={}):
    #  log.debug(f"write_text_file: {file_path}")
    if opts and opts["no_empty_file"] and file_content is None:
        return
    with open(file_path, "w") as file:
        file.write(file_content)


def write_csv_file(file_path: str, rows: [dict], opts=None):
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        for item in rows:
            writer.writerow(item)


def write_xlsx_file(file_path: str, rows: [dict], opts=None):
    wb = Workbook()
    ws = wb.active

    if rows:
        headers = list(rows[0].keys())
        ws.append(headers)
        for obj in rows:
            ws.append([obj.get(header) for header in headers])
    wb.save(file_path)


def get_pull_request(file_path):
    commit_info_file_path = os.path.join(file_path, "commit_info.json")
    data = read_json_file(commit_info_file_path)
    return data["pull request"]
