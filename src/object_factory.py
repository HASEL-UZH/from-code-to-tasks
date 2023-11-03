from src.utils.utils import camel_to_snake


class ObjectFactory:
    CLASSIFIERS = {
        "repository": "repository",
        "commit": "commit",
        "resource": "resource",
    }

    @staticmethod
    def is_repository(obj):
        if obj:
            classifier = obj["classifier"]
            return classifier == ObjectFactory.CLASSIFIERS["repository"]
        return False

    @staticmethod
    def is_commit(obj):
        if obj:
            classifier = obj["classifier"]
            return classifier == ObjectFactory.CLASSIFIERS["commit"]
        return False

    @staticmethod
    def is_resource(obj):
        if obj:
            classifier = obj["classifier"]
            return classifier == ObjectFactory.CLASSIFIERS["resource"]
        return False


    @staticmethod
    def repository(url, data=None):
        if data is None:
            data = {}
        repo_id = get_repository_id(url)
        classifier = ObjectFactory.CLASSIFIERS["repository"]
        oid = get_object_id(classifier, repo_id)
        _object = {
            "classifier": classifier,
            "oid": oid,
            "id": repo_id,
            "repository_url": url,
        }
        _object = {**_object, **data, **_object}
        return _object

    @staticmethod
    def commit(data=None):
        if data is None:
            data = {}
        id = data["commit_hash"]
        classifier = ObjectFactory.CLASSIFIERS["commit"]
        oid = get_object_id(classifier, id)
        repo_id = get_repository_id(data["repository_url"])
        repo_classifier = ObjectFactory.CLASSIFIERS["repository"]
        repo_oid = get_object_id(repo_classifier, repo_id)
        _object = {
            "classifier": classifier,
            "oid": oid,
            "id": id,
            "repository_id": repo_id,
            "@repository": repo_oid
        }
        _object = {**_object, **data, **_object}
        return _object

    @staticmethod
    def resource(container, data):
        if data is None:
            data = {}
        id = data.get("id")
        full_name = data.get("name", "undefined")
        if data.get("name") and data.get("type"):
            full_name = ".".join([data.get("name"), data.get("type")])
        if not id:
            id = "/".join([container.get("id", "undefined"), full_name])
        classifier = ObjectFactory.CLASSIFIERS["resource"]
        oid = get_object_id(classifier, id)
        _object = {
            "classifier": classifier,
            "oid": oid,
            "id": id,
            "@container": container.get("oid"),
        }
        _object = {**_object, **data, **_object}
        if not "content" in _object:
            _object["content"] = None
        return _object


# --- Utilities

def get_object_id(classifier, _id):
   return "::".join([classifier,_id])

def get_repository_id(repository_url):
    # Remove the prefix
    id = repository_url.replace("https://github.com/", "")
    # Replace "/" with "__"
    id = id.replace("/", "__")
    id = camel_to_snake(id)
    return id

def get_resource_id(container_id, name):
    id = "/".join([container_id or "", name])
    return id
