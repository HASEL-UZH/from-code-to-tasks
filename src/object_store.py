import os
from importlib.resources import is_resource

from src.object_factory import ObjectFactory, decode_resource_name
from src.workspace_context import get_or_create_dir, \
    write_json_file, get_store_dir, read_json_file, write_text_file, read_text_file

OBJECT_INF_FILE = "_OBJECT_INF.json"
REPOSITORIES_DIR_NAME = "repositories"
COMMITS_DIR_NAME = "commits"

# Base file system structure
# store (root)
#   repositories/
#       {repository_id}
#           _OBJECT_INF.json
#           commits
#               {commit_id}/
#                   _OBJECT_INF.json
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
#                   commit_info.jsom
#
#
#  object types:
#   java (java source file)
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
#     Commit
#     Resource
#
class ObjectStore:
    def __init__(self, store_dir):
        self.store_dir = store_dir
        self.dirty = True
        self.root = None
        self.nodes = []
        self.objects = {}

    def sync(self, force=False):
        if not force and not self.dirty:
            return

        self.nodes = []
        self.objects = {}
        def scan(fs_element, parent_path, parent, depth):
            """Generate a dictionary that represents the directory structure."""

            is_file = os.path.isfile(fs_element)
            base_name = os.path.basename(fs_element)
            if not self._accept(base_name, is_file):
                return None

            node = {
                "name": base_name,
                "depth": depth,
                "container": False,
                "children": []
            }

            if os.path.isdir(fs_element):
                node["container"] = True,
                self.nodes.append(node)
                inf_file = os.path.join(fs_element, OBJECT_INF_FILE )
                if os.path.exists(inf_file):
                    _object = read_json_file(inf_file)
                    node["_object"] = _object
                items = os.listdir(fs_element)
                sorted_items = sorted(items)
                for item in sorted_items:
                    item_path = os.path.join(fs_element, item)
                    child = scan(item_path, fs_element, node, depth+1)
                    if (child):
                        node['children'].append(child)
            else:
                try:
                    container_object = parent.get("_object")
                    if container_object:
                        file_base_data = decode_resource_name(base_name)
                        resource = ObjectFactory.resource(container_object, file_base_data)
                        location = self.get_resource_location(resource, container_object)
                        resource["_location"] = location
                        _fs_path = self.get_fs_path(location)
                        if _fs_path != fs_element:
                            raise Exception()

                        node["_object"] = resource
                        self.nodes.append(node)

                except Exception as e:
                    pass
            return node

        self.root = scan(self.store_dir,None, None,0)
        self.set_dirty(False, "sync")
        for node in self.nodes:
            obj = node.get("_object")
            if obj:
                id = obj.get("id")
                if (id):
                    self.objects[id] = obj

        pass
    # print(json.dumps(self.root, indent=4))
    pass

    def _accept(self, name, is_file):
        exclusions =[OBJECT_INF_FILE, ".DS_Store", ".gitignore" ]
        if is_file:
            return name not in exclusions
        return True

    def state(self, sync=True):
        if sync:
            self.sync()
        return {
            "root": self.root,
            "nodes": self.nodes
        }

    def _get_root(self):
        return self.state()["root"]

    def _get_nodes(self):
        return self.state()["nodes"]

    def set_dirty(self, dirty, cause=None):
        self.dirty = dirty

    def invalidate(self):
        self.set_dirty(True, "invalidate")

    # --- Query

    def _get_objects(self):
        self.sync()
        return list(self.objects.values())

    def find_object(self, id):
        self.sync()
        obj = self.objects.get(id)
        return obj

    def find_many(self, criteria, objects=None ):
        self.sync()
        objects = objects or self._get_objects()
        if isinstance(criteria, dict):
            return [item for item in objects if all(item.get(k) == v for k, v in criteria.items())]
        elif callable(criteria):
            return [item for item in objects if criteria(item)]
        return objects

    def find_one(self, criteria, objects=None ):
        results = self.find_many(criteria, objects)
        return results[0] if results else None

    def find_resources(self, criteria):
        return self.find_many(criteria, self.get_resources())


    # @returns IRepository
    def get_repositories(self):
        _nodes = self._get_nodes()
        nodes = [
            obj for obj in _nodes
            if obj and "_object" in obj and ObjectFactory.is_repository(obj["_object"])
        ]
        repositories = [obj["_object"] for obj in nodes if "_object" in obj]
        return repositories

    def get_commits(self):
        _nodes = self._get_nodes()
        nodes = [
            obj for obj in _nodes
            if obj and "_object" in obj and ObjectFactory.is_commit(obj["_object"])
        ]
        commits = [obj["_object"] for obj in nodes if "_object" in obj]
        return commits

    def get_resources(self):
        objects = self._get_objects()
        # resources = self.find_many(is_resource, objects)
        resources = self.find_many({"classifier": "resource"}, objects)
        return resources

    # --- IO

    def get_resource_location(self, resource, container=None):
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
    def save_repository(self, repository):
        directory = get_or_create_dir(self.get_repository_dir(repository["identifier"]))
        info_file = os.path.join(directory, OBJECT_INF_FILE)
        repository["_location"] = os.path.relpath(directory, get_store_dir())
        write_json_file(info_file, repository)
        self.invalidate()


    # commit: ICommit
    def save_commit(self, commit):
        directory = get_or_create_dir(self.get_commit_dir(commit["repository_identifier"], commit["identifier"]))
        info_file = os.path.join(directory, OBJECT_INF_FILE)
        commit["_location"] = os.path.relpath(directory, get_store_dir())
        write_json_file(info_file, commit)
        self.invalidate()


    # resource: IResource
    def save_resource(self, resource, container = None):
        file_path = self.get_resource_path(resource, container)
        if resource["type"] == "json":
            write_json_file(file_path, resource.get("content"))
        else:
            write_text_file(file_path, resource.get("content"))
        self.invalidate()

    def load_resource(self, resource, force = False):
        if not resource:
            return None
        if not resource.get("content") or force:
            file_path = self.get_resource_path(resource)
            if file_path and os.path.exists(file_path):
                content = None
                if resource.get("type")=="json":
                    content = read_json_file(file_path)
                else:
                    content = read_text_file(file_path)
                resource["content"] = content
        return resource.get("content")

    # absolute path
    def get_repository_dir(self, repo_id=None):
        paths = [REPOSITORIES_DIR_NAME, repo_id] if repo_id else [REPOSITORIES_DIR_NAME]
        repository_dir =  get_or_create_dir(self.get_fs_path(os.path.join(self.store_dir, *paths)))
        return repository_dir

    # absolute path
    def get_commit_dir(self, repo_id, commit_id):
        repo_dir = self.get_repository_dir(repo_id)
        commit_dir = get_or_create_dir(os.path.join(repo_dir, COMMITS_DIR_NAME, "commit_"+commit_id))
        return commit_dir

    # absolute path
    def get_fs_path(self, location):
        full_path = os.path.abspath(os.path.join(self.store_dir, location))
        return full_path

    def get_resource_path(self, resource, container = None):
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
                raise Exception("Cannot determine location for resource: "+resource.get("id"))

        file_path = self.get_fs_path(location)
        return file_path


ws = get_store_dir()
db = ObjectStore(ws)


if __name__ == "__main__":
    print("object_store DISABLED"); exit(0)
    ws = get_store_dir()
    db = ObjectStore(ws)
    db.sync()

    git_commit = {'repository_url': 'https://github.com/google/guava', 'commit_hash': '1b82532af11ff285c0aaa712a262d4e50bd81099', 'commit_message': 'Fix ByteArrayDataInput javadoc (GitHub pull request #1874).\n-------------\nCreated by MOE: http://code.google.com/p/moe-java\nMOE_MIGRATED_REVID=79122254', 'pull_request': 'Fix ByteArrayDataInput Javadoc', 'commit_author': 'cgdecker', 'commit_date': '2014-11-03', 'in_main_branch': True, 'merge': False, 'added_lines': 1, 'deleted_lines': 1}
    commit = ObjectFactory.commit(git_commit)
    db.save_commit(commit)

    # Generate a random UUID (version 4)
    random_uuid = uuid.uuid4()
    print(random_uuid)

    # Generate a UUID based on the host ID and current timestamp (version 1)
    time_based_uuid = uuid.uuid1()
    print(time_based_uuid)

    # Generate a UUID using a namespace and a name (version 3 and version 5)
    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Sample namespace
    name_based_uuid_v3a = uuid.uuid3(namespace, 'sample_name')  # MD5 based
    name_based_uuid_v3b = uuid.uuid3(namespace, 'sample_name')  # MD5 based
    name_based_uuid_v5 = uuid.uuid5(namespace, 'sample_name')  # SHA-1 based
    print(name_based_uuid_v3a)
    print(name_based_uuid_v5)
    pass

