import os

from src.core.utils import camel_to_snake


class Classifier:
    repository = "repository"
    commit = "commit"
    resource = "resource"


class ObjectFactory:
    # obj: dict | string (id)
    @staticmethod
    def _get_classifier(obj):
        if not obj:
            return
        classifier = None
        if type(obj).__name__ == "string":
            classifier = obj
        elif type(obj).__name__ == "dict":
            classifier = obj.get("classifier")
        return classifier

    # obj: dict | string (id)
    @staticmethod
    def is_container(obj):
        return ObjectFactory.is_repository(obj) or ObjectFactory.is_commit(obj)

    @staticmethod
    def is_repository(obj):
        classifier = ObjectFactory._get_classifier(obj)
        return classifier == Classifier.repository

    @staticmethod
    def is_commit(obj):
        classifier = ObjectFactory._get_classifier(obj)
        return classifier == Classifier.commit

    @staticmethod
    def is_pr(obj):
        classifier = ObjectFactory._get_classifier(obj)
        return classifier == Classifier.pr

    @staticmethod
    def is_resource(obj):
        classifier = ObjectFactory._get_classifier(obj)
        return classifier == Classifier.resource

    @staticmethod
    def repository(url, data=None):
        if data is None:
            data = {}
        repo_id = get_repository_identifier(url)
        classifier = Classifier.repository
        id = get_object_id(classifier, repo_id)
        _object = {
            "id": id,
            "classifier": classifier,
            "identifier": repo_id,
            "repository_url": url,
        }
        _object = {**_object, **data, **_object}
        return _object

    @staticmethod
    def commit(data=None):
        if data is None:
            data = {}
        identifier = data["commit_hash"]
        classifier = Classifier.commit
        id = get_object_id(classifier, identifier)
        repo_identifier = get_repository_identifier(data["repository_url"])
        repo_id = get_object_id(Classifier.repository, repo_identifier)
        _object = {
            "id": id,
            "classifier": classifier,
            "identifier": identifier,
            "repository_identifier": repo_identifier,
            "@repository": repo_id,
        }
        _object = {**_object, **data, **_object}
        return _object

    @staticmethod
    def resource(container, data):
        requirements = ["name", "type", "kind"]
        if not all(key in data for key in requirements):
            raise Exception("Instantiation error for class 'Resource'")

        if not container:
            pass

        filename = encode_resource_name(data)
        identifier = "#".join([container["identifier"], filename])
        classifier = Classifier.resource
        id = get_object_id(classifier, identifier)
        _object = {
            "id": id,
            "classifier": classifier,
            "identifier": identifier,
            "filename": filename,
            "@container": container.get("id"),
            "repository_identifier": container.get("repository_identifier"),
        }
        _object = {**_object, **data, **_object}
        if not "content" in _object:
            _object["content"] = None
        return _object


# --- Utilities


def get_object_id(classifier, _id):
    return "::".join([classifier, _id])


def get_repository_identifier(repository_url):
    # Remove the prefix
    id = repository_url.replace("https://github.com/", "")
    # Replace "/" with "__"
    id = id.replace("/", "__")
    id = camel_to_snake(id)
    return id


def get_resource_id(container_id, identifier):
    id = "/".join([container_id or "", identifier])
    return id


def encode_resource_name(resource):
    base_template = "{name}--{kind}--{version}"
    strategy_template = "{meta}--{terms}--{embedding}"

    base_part = base_template.format(
        name=resource.get("name", "undefined") or "",
        kind=resource.get("kind", "") or "",
        version=resource.get("version", "") or "",
    )
    strategy = resource.get("strategy")
    if strategy:
        strategy_part = strategy_template.format(
            meta=strategy.get("meta", "") or "",
            terms=strategy.get("terms", "") or "",
            embedding=strategy.get("embedding", "") or "",
        )
        base_part = "@".join([base_part, strategy_part])

    name = ".".join([base_part, resource.get("type", "txt")])
    return name


def decode_resource_name(resource_name):
    root, ext = os.path.splitext(resource_name)
    type = ext[1:]
    parts = root.split("@")
    base_part = parts[0]
    base_parts = base_part.split("--")
    strategy_part = parts[1] if 1 < len(parts) else None
    obj = {
        "filename": resource_name,
        "name": base_parts[0] or None,
        "kind": base_parts[1] or None,
        "version": base_parts[2] or None,
        "type": type,
    }
    if strategy_part:
        strategy_parts = strategy_part.split("--")
        obj["strategy"] = {
            "meta": strategy_parts[0] or None,
            "terms": strategy_parts[1] or None,
            "embedding": strategy_parts[2] or None,
        }
    return obj
