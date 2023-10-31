# 01 Data Collection

## Fetch Repositories from GitHub

data_collection/repository_collection/fetch_repositories.py
--> workspace/repositories/candidate_repositories.json

## Rank Repositories

```
data_collection/repository_collection/rank_candidate_repositories.py
--> workspace/repositories/final_repositories.json
```

## Extract commit data and create initial dataset 'commit_data'

```
data_collection/commit_collection/fetch_commit_data.py
--> workspace/datasets/commit_data/commit_{repo_id}_{commit_hash}
```

- commit_info.json
- {file_name}.diff files
- {file_name}_before.java
- {file_name}_after.java

## Create dataset where empty files are removed

```
data_collection/dataset_management/remove_empty_folders.py
--> workspace/datasets/commit_data_removed_empty/commit_{repo_id}_{commit_hash}
```

- commit_info.json
- {file_name}.diff files
- {file_name}_before.java
- {file_name}_after.java

## Create dataset where only comment modifying files are removed

```
data_collection/dataset_management/remove_only_comment.py
--> workspace/datasets/commit_data_removed_empty_and_only_comments/commit_{repo_id}_{commit_hash}
```

- commit_info.json
- {file_name}.diff files
- {file_name}_before.java
- {file_name}_after.java

## ++ Create AST information

### AST Generation

```
ast_generation/ast_creator.py
--> (EXTEND) workspace/datasets/commit_data_removed_empty_and_only_comments/commit_{repo_id}_{commit_hash}
```

- {filename}_before_ast.json
- {filename}_after_ast.json

### AST Meta Generation

```
ast_meta_generation/meta_ast_creator.py
--> (EXTEND) workspace/datasets/commit_data_removed_empty_and_only_comments/commit_{repo_id}_{commit_hash}
```

- {filename}_before_meta_ast.json
- {filename}_after_meta_ast.json

### AST Change Model Generation

```
ast_compare/commit_change_model_generator.py
--> (EXTEND) workspace/datasets/commit_data_removed_empty_and_only_comments/commit_{repo_id}_{commit_hash}
```

- commit_change_object.json (combines all files of the commit)

## Create dataset per repository

```
data_collection/dataset_management/create_dataset_per_repository.py
--> workspace/datasets/commit_data_per_repository/{repo_id}/commit_{repo_id}_{commit_hash}
```

## Create sliding window dataset

```
data_collection/dataset_management/create_sliding_windows.py
--> workspace/datasets/commit_data_slding_window_{window_size}/sliding_window_{window_id}/commit_{repo_id}_{commit_hash}
```

- commit_info.json
- commit_change_object.json

## Create sliding window dataset per repository

```
data_collection/dataset_management/create_sliding_windows_per_repository.py
--> workspace/datasets/commit_data_slding_window_per_repository_{window_size}/{repo_id}/sliding_window_{window_id}/commit_{repo_id}_{commit_hash}```

# 01 Data Collection

# Notes

## <div style="color:red">Problems:</div>

### Some pull request titles are truncated

```json
"repository url": "https://github.com/SeleniumHQ/selenium",
"commit hash": "4efffd5b6409987c538da9b6a325c1614d0bca0e",
"commit message": "SimonStewart: Fix on bug #8. The fix is to only automatically focus on frames and not iframes\n\nr4095",
"pull request": "Enhancement #5078 - Allow :desired_capabilities capabilities to be speci...",
```