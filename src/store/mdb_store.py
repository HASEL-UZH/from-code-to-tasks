import os
import uuid
from datetime import datetime
from typing import Union, Iterable

from src.core.profiler import Profiler
from src.core.logger import log
from src.core.workspace_context import (
    get_or_create_dir,
    read_text_file,
    get_store_dir,
    write_json_file,
    read_json_file,
    write_text_file,
)
from src.store.object_factory import decode_resource_name, ObjectFactory, Classifier
from src.store.mdb import mdb

IDbCursor = Iterable


class StoreFolderName:
    repositories = "repositories"
    commits = "commits"


class Collection:
    repository = mdb.get_collection("repository")
    commit = mdb.get_collection("commit")
    resource = mdb.get_collection("resource")
    accuracy = mdb.get_collection("accuracy")
    github_pr = mdb.get_collection("github_pr")
    github_issue = mdb.get_collection("github_issue")
    github_query = mdb.get_collection("github_query")
    github_repository = mdb.get_collection("github_repository")


# Base file system structure
# store (root)
#   repositories/
#       {repository_id}
#           _OBJECT_INF.json
#           pull_requests
#               pr_{pr_nr}/
#                   FileA_before.java
#                   FileA_after.java
#                   FileA.diff
#                   FileA_before_ast.json
#                   FileA_after_ast.json
#                   FileA_before_meta_ast.json
#                   FileA_after_meta_ast.json
#                   ...
#                   FileX_before.java
#                   FileX_after.java
#                   FileX.diff
#                   ...
#
#
#  object types:
#   java (java source file)
#   text (text file)
#   ast (json ast)
#   meta-ast (json meta ast)
#   diff (git diff file)
#
#  version:
#   "before"
#   "after"
#
#  class types
#     Repository
#     PullRequest
#     Commit
#     Resource
#
class MdbStore:
    def __init__(self, store_dir):
        self.store_dir = store_dir

    def sync(self, force=False):
        log.warning("MdbStore.sync() is a NOP")

    # @deprecated
    def set_dirty(self, dirty, cause=None):
        self.dirty = dirty

    # --- Query

    def _get_collection(self, id: str):
        collection = id.split("::")[0]
        return mdb.get_collection(collection)

    def find_object(self, id: str, logging: bool = False) -> dict:
        profiler = Profiler()
        collection = self._get_collection(id)
        obj = collection.find_one({"id": id})
        logging and profiler.debug("db.find_object")
        return obj

    def find_many(
        self, collection: str, criteria: dict, logging: bool = False
    ) -> IDbCursor:
        profiler = Profiler()
        objects = mdb.get_collection(collection).find(criteria or {})
        logging and profiler.debug("db.find_many")
        return objects

    def find_one(self, collection: str, criteria: dict, logging: bool = False) -> dict:
        profiler = Profiler()
        obj = mdb.get_collection(collection).find_one(criteria or {})
        logging and profiler.checkpoint("db.find_one")
        return obj

    def find_repositories(
        self, criteria: dict = None, logging: bool = False
    ) -> IDbCursor:
        profiler = Profiler()
        objects = Collection.repository.find(criteria or {})
        logging and profiler.debug("db.find_repositories")
        return objects

    def find_commits(self, criteria: dict = None, logging=False) -> IDbCursor:
        profiler = Profiler()
        objects = Collection.commit.find(criteria or {})
        logging and profiler.debug("db.find_commits")
        return objects

    def find_resources(self, criteria: dict, logging: bool = False) -> IDbCursor:
        profiler = Profiler()
        objects = Collection.resource.find(criteria or {})
        logging and profiler.debug("db.find_resources")
        return objects

    def delete_object(self, id: str, logging: bool = False):
        collection = self._get_collection(id)
        profiler = Profiler()
        collection.delete_one({id: id})
        logging and profiler.debug("db.delete_object")

    # --- IO

    def get_resource_location(self, resource: dict, container=None):
        if not ObjectFactory.is_resource(resource):
            return None
        location = resource.get("_location")
        if not location:
            container = container or self.find_object(resource.get("@container"))
            if container:
                location = os.path.join(container["_location"], resource["filename"])
                return location
        raise Exception("Cannot create resource location")

    # repository: IRepository
    def save_repository(self, repository: dict):
        if not ObjectFactory.is_repository(repository):
            raise RuntimeError()
        directory = get_or_create_dir(self.get_repository_dir(repository["identifier"]))
        repository["_location"] = os.path.relpath(directory, get_store_dir())
        Collection.repository.update_one(
            {"id": repository["id"], "classifier": Classifier.repository},
            {"$set": repository},
            upsert=True,
        )

    # commit: ICommit
    def save_commit(self, commit: dict):
        if not ObjectFactory.is_commit(commit):
            raise RuntimeError()
        directory = get_or_create_dir(
            self.get_commit_dir(commit["repository_identifier"], commit["identifier"])
        )
        commit["_location"] = os.path.relpath(directory, get_store_dir())
        Collection.commit.update_one(
            {"id": commit["id"], "classifier": Classifier.commit},
            {"$set": commit},
            upsert=True,
        )

    # resource: IResource
    def save_resource(self, resource, container):
        if not ObjectFactory.is_resource(resource):
            raise RuntimeError()
        file_path = self.get_resource_path(resource, container)
        if resource["type"] == "json":
            write_json_file(file_path, resource.get("content"))
        else:
            write_text_file(file_path, resource.get("content"))

        _resource = resource.copy()
        _resource.pop("content", None)
        Collection.resource.update_one(
            {"id": resource["id"], "classifier": Classifier.resource},
            {"$set": _resource},
            upsert=True,
        )

    def delete_repository(
        self, repository_id, fs_objects: bool = False, recursive: bool = False
    ):
        # TODO file system objects, recursion
        Collection.repository.delete_one({"idt": repository_id})

    def delete_repositories(
        self,
        criteria: dict = None,
        fs_objects: bool = False,
        recursive: bool = False,
        logging=False,
    ):
        # TODO file system objects, recursion
        Collection.repository.delete_many(criteria or {})

    def delete_commit(
        self, commit_id, fs_objects: bool = False, recursive: bool = False
    ):
        # TODO file system objects, recursion
        Collection.commit.delete_one({"idt": commit_id})

    def delete_resource(self, resource_id, fs_remove: bool = True):
        resource = self.find_object(resource_id)
        if resource:
            self.delete_object(resource_id)
            if fs_remove:
                file_path = self.get_resource_path(resource)
                if os.path.exists(file_path):
                    os.remove(file_path)

    def delete_resources_where(self, criteria: dict = None):
        profiler = Profiler()
        result = Collection.resource.delete_many(criteria)
        profiler.debug(
            f"delete_resources_where: {criteria or ''}, count: {result.deleted_count}"
        )

    def delete_resources(self, resources: Union[list, tuple], fs_remove: bool = True):
        if not isinstance(resources, (list, tuple)):
            raise RuntimeError("delete_resources: List required")
        profiler = Profiler()
        count = 0
        for resource in resources:
            if resource:
                self.delete_resource(resource["id"], fs_remove)
                count += 1
        profiler.debug(f"{count} resources deleted")

    def get_resource_content(self, resource, force=False, volatile=True):
        if not resource:
            return None
        content = resource.get("content")
        if not content or force:
            file_path = self.get_resource_path(resource)
            if file_path and os.path.exists(file_path):
                if resource.get("type") == "json":
                    content = read_json_file(file_path)
                else:
                    content = read_text_file(file_path)
                if not volatile:
                    resource["content"] = content
        return content

    def load_resource(self, resource, force=False):
        content = self.get_resource_content(resource, force=force, volatile=False)
        return content

    def unload_resource(self, resource):
        if not resource:
            return None
        resource.pop("content", None)

    # absolute path
    def get_repository_dir(self, repo_id=None):
        paths = (
            [StoreFolderName.repositories, repo_id]
            if repo_id
            else [StoreFolderName.repositories]
        )
        repository_dir = get_or_create_dir(
            self.get_fs_path(os.path.join(self.store_dir, *paths))
        )
        return repository_dir

    # absolute path
    def get_commit_dir(self, repo_id, commit_id):
        repo_dir = self.get_repository_dir(repo_id)
        commit_dir = get_or_create_dir(
            os.path.join(repo_dir, StoreFolderName.commits, "commit_" + commit_id)
        )
        return commit_dir

    # absolute path
    def get_fs_path(self, location):
        full_path = os.path.abspath(os.path.join(self.store_dir, location))
        return full_path

    def get_resource_path(self, resource, container=None):
        location = resource.get("_location")
        if not location:
            container = container or self.find_object(resource.get("@container"))
            if container and container.get("_location"):
                directory = container.get("_location")
                file_name = resource["filename"]
                location = os.path.join(directory, file_name)
                resource["_location"] = location
            else:
                # FIXME try o locate the container by it's container id (@container)
                raise Exception(
                    "Cannot determine location for resource: " + resource.get("id")
                )

        file_path = self.get_fs_path(location)
        return file_path

    def generate_tmp_file(self):
        unique_id = uuid.uuid4()  # Generate a random UUID.
        current_time = datetime.now().strftime(
            "%Y-%d-%m-%H-%M-%S"
        )  # Format the current time.
        tmp_filename = f"{current_time}-{unique_id}.tmp"  # Create the temp filename.
        tmp_dir = get_or_create_dir(
            os.path.abspath(os.path.join(self.store_dir, "tmp"))
        )
        tmp_filepath = os.path.join(tmp_dir, tmp_filename)
        return tmp_filepath


ws = get_store_dir()
db = MdbStore(ws)


if __name__ == "__main__":
    pass
