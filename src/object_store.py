import os
import uuid

from src.object_factory import ObjectFactory
from src.workspace_context import get_workspace_dir, get_or_create_dir, get_repository_dir, OBJECT_INF_FILE, \
    write_json_file, get_store_dir, read_json_file, get_commit_dir, write_text_file, get_store_path, read_text_file


# Base file system structure
# workspace (root)
#   datasets/
#       commit_data/
#           repository_{repo_id}/   // use name instead
#               {commit_id}/
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
#   repositories/
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
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
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
                        file_base_data = _decode_resource_name(base_name)
                        file_object = ObjectFactory.resource(container_object, file_base_data)
                        file_object["_location"] = fs_element
                        node["_object"] = file_object
                        self.nodes.append(node)
                except Exception as e:
                    pass
            return node

        self.root = scan(self.workspace_dir,None, None,0)
        self.set_dirty(False, "sync")
        for node in self.nodes:
            obj = node.get("_object")
            if obj:
                oid = obj.get("id")
                if (oid):
                    self.objects[oid] = obj

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

    def find_object(self, oid):
        pass


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
        _nodes = self._get_nodes()
        nodes = [
            obj for obj in _nodes
            if obj and "_object" in obj and ObjectFactory.is_resource(obj["_object"])
        ]
        commits = [obj["_object"] for obj in nodes if "_object" in obj]
        return commits


    # repository: IRepository
    def save_repository(self, repository):
        directory = get_or_create_dir(get_repository_dir(repository["id"]))
        info_file = os.path.join(directory, OBJECT_INF_FILE)
        repository["_location"] = os.path.relpath(directory, get_store_dir())
        write_json_file(info_file, repository)
        self.invalidate()

    def save_commit(self, commit):
        repo_dir = get_repository_dir()
        directory = get_or_create_dir(get_commit_dir(commit["repository_id"], commit["id"]))
        info_file = os.path.join(directory, OBJECT_INF_FILE)
        commit["_location"] = os.path.relpath(directory, get_store_dir())
        write_json_file(info_file, commit)
        self.invalidate()

    def save_resource(self, resource, container=None):
        location = resource.get("_location")
        if not location:
            if container and container.get("_location"):
                directory = container.get("_location")
                file_name = _encode_resource_name(resource)
                location = os.path.join(directory, file_name)
                resource["_location"] = location
            else:
                # FIXME try o locate the container by it's container oid (@container)
                raise Exception("Cannot determine location for resource: "+resource.get("oid"))

        file_path = get_store_path(location)
        if resource["type"] == "json":
            write_json_file(file_path, resource.get("content"))
        else:
            write_text_file(file_path, resource.get("content"))

    # commit_id: string; // uid of commit (e.g., iluwatar/java-design-patterns|0ad44ced247191cc631100010ca40b4baa84d161)
    def get_commit(self, commit_id):
        pass


    def get_resource(self, resource_id):
        pass


    def load_resource(self, resource, force = False):
        if not resource.get("content") or force:
            file_path = resource.get("_location")
            if file_path and os.path.exists(file_path):
                content = None
                if resource.get("type")=="json":
                    content = read_json_file(file_path)
                else:
                    content = read_text_file(file_path)
                resource["content"] = content

    def delete(self):
        pass


def _encode_resource_name(resource):
    base_template = "{name}--{kind}--{version}"
    strategy_template = "{meta}--{terms}--{embedding}"

    base_part = base_template.format(
        name = resource.get("name", "undefined") or "",
        kind = resource.get("kind", "") or "",
        version = resource.get("version", "") or "",
    )
    strategy = resource.get("strategy")
    if strategy:
        strategy_part = strategy_template.format(
            meta=strategy.get("meta","") or "",
            terms=strategy.get("terms","") or "",
            embedding=strategy.get("embedding","") or ""
        )
        base_part = "@".join([base_part, strategy_part])

    name = ".".join([base_part, resource.get("type", "txt")])
    return name

def _decode_resource_name(resource_name):
    root, ext = os.path.splitext(resource_name)
    type = ext[1:]
    parts = root.split("@")
    base_part = parts[0]
    base_parts = base_part.split("--")
    strategy_part = parts[1] if 1 < len(parts) else None
    obj = {
        "name": base_parts[0] or None,
        "kind": base_parts[1] or None,
        "version": base_parts[2] or None,
        "type": type
    }
    if strategy_part:
        strategy_parts = strategy_part.split("--")
        obj["strategy"] = {
            "meta": strategy_parts[0] or None,
            "terms": strategy_parts[1] or None,
            "embedding": strategy_parts[2]or None,
        }
    return obj


ws = get_workspace_dir()
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

