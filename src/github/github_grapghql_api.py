import json
import uuid
from src.github.github_api import GitHubApi, GITHUB_TOKEN, GITHUB_API_GRAPHQL_ENDPOINT
from src.core.logger import log
from datetime import datetime
from src.core.workspace_context import write_json_file


# @see https://docs.github.com/en/graphql/guides/forming-calls-with-graphql
# @see https://docs.github.com/en/graphql
# @see https://docs.github.com/en/graphql/overview/explorer
# @see https://medium.com/swlh/introduction-to-graphql-with-github-api-64ee8bb11630
# @see https://github.com/altair-graphql/altair
class GitHubGraphQlApi(GitHubApi):
    def __init__(
        self,
        token=None,
        headers=None,
        retry_count=10,
        retry_ms=100,
    ):
        super().__init__(token, headers)
        self.retry_count = retry_count or 0
        self.retry_ms = retry_ms or 100

    def execute_grapqhql_query(self, query, variables=None, log=False):
        if not variables:
            variables = {}
        payload = {"query": query, "variables": variables}
        result = self.post_request(
            GITHUB_API_GRAPHQL_ENDPOINT,
            json=payload,
            retry_count=self.retry_count,
            retry_ms=self.retry_ms,
        )
        data = result.get("data")
        if data and "data" in data:
            # unpack wrapped data
            result["data"] = data["data"]
        if data and "errors" in data:
            # unpack wrapped data
            result["errors"] = data["errors"]
            result["ok"] = False
            del result["data"]
        return result

    def execute_grapqhql_iteration_query(
        self,
        query,
        variables=None,
        handler=None,
        next_fn=None,
        max_pages=None,
        name=None,
    ):
        if not handler:
            return self.execute_grapqhql_query(query, variables)

        variables = {**(variables or {})}
        context = {
            "query": query,
            "variables": variables,
            "page_count": 0,
        }
        query_info = f" '{name}' " if name else ""
        log.debug(
            f"Execute graphql query{query_info}, max pages: {max_pages}, variables: {json.dumps(variables)})"
        )
        log.debug(f"{query}")
        while True:
            log.debug(f"  page: {context['page_count']}")
            result = self.execute_grapqhql_query(query, variables)
            # data = result.get("data", {}).get("search", {})
            data = result.get("data", {})
            result["data"] = data
            context["page_count"] += 1
            cancel = handler(context, result) == False
            if cancel or (max_pages is not None and context["page_count"] >= max_pages):
                break

            next = next_fn(data)
            if not next or "cursor" not in variables:
                break

            variables["cursor"] = next

        return

    def get_rate_limit(self):
        query = """
            query {
               viewer {
                   login
               }
               rateLimit {
                    limit
                    remaining
                    used
                    resetAt
               }
            }
         """
        result = self.execute_grapqhql_query(query)
        if result["ok"]:
            return result["data"].get("rateLimit")
        return None

    def get_types(self):
        query = """
        query IntrospectionQuery {
          __schema {
            types {
              name
            }
          }
        }
        """
        result = self.execute_grapqhql_query(query)
        if result["ok"]:
            types = result["data"].get("__schema", {}).get("types", [])
            type_names = [t["name"] for t in types if t["name"] is not None]
            return type_names

        return []

    def get_fields(self, object_type):
        query = """
            query IntrospectionQuery($typeName: String!) {
              __type(name: $typeName) {
                name
                kind
                description
                fields {
                  name
                }
              }
            }
        """
        variables = {"typeName": object_type}
        result = self.execute_grapqhql_query(query, variables)
        if result["ok"]:
            type = result["data"].get("__type")
            if type:
                fields = type.get("fields") or []
                names = [d["name"] for d in fields]
                return names
        return []

    def get_schema(self, object_type):
        """
        Retrieves the GraphQL schema for a specified GitHub object type.

        Parameters:
        object_type (str): The type of GitHub object for which the schema is requested.
                           Acceptable values are "Repository" or "Commit".

        Returns:
        dict: The GraphQL schema of the specified object type.
        """

        query = """
            query IntrospectionQuery($typeName: String!) {
              __type(name: $typeName) {
                name
                kind
                fields {
                  name
                  description
                  type {
                    name
                    kind
                    ofType {
                      name
                      kind
                    }
                  }
                  args {
                    name
                    description
                    type {
                      name
                      kind
                      ofType {
                        name
                        kind
                      }
                    }
                    defaultValue
                  }
                }
              }
            }
        """
        variables = {"typeName": object_type}
        result = self.execute_grapqhql_query(query, variables)
        if result["ok"]:
            type = result["data"].get("__type")
            if result["ok"] and type:
                fields = type.get("fields") or []
                schema = {"classifier": type.get("name"), "fields": fields}
                return schema
        return None

    def get_repository(self, owner, name):
        query = """
            query GetRepository($owner: String!, $name: String!) {
              repository(owner: $owner, name: $name) {
                id
                nameWithOwner
                description
                url
              }
            }
        """
        variables = {"owner": owner, "name": name}
        result = self.execute_grapqhql_query(query, variables)
        if result["ok"]:
            return result

        return None

    # n: int, (page size)
    def find_top_java_repositories(self, n=100, max_pages=None):
        def get_query(criteria):
            query = f"language:Java stars:>{2500} {criteria} is:public mirror:false template:false"
            template = """
                query SearchRepos($first: Int!, $query: String!, $cursor: String = null) {
                  search(
                    query: $query,
                    type: REPOSITORY,
                    first: $first
                    after: $cursor
                  ) {
                    repositoryCount
                        pageInfo {
                        endCursor
                        hasNextPage
                    }
                    nodes {
                      ... on Repository {
                        name
                        owner {
                          login
                        }
                        stargazers {
                          totalCount
                        }
                        primaryLanguage {
                          name
                        }
                        url
                        description
                        id
                        name
                        nameWithOwner
                        createdAt
                        updatedAt
                        archivedAt
                        databaseId
                        homepageUrl
                        diskUsage
                        forkCount
                        stargazerCount
                        visibility
                        isDisabled

                        hasDiscussionsEnabled
                        hasIssuesEnabled
                        hasProjectsEnabled
                        hasVulnerabilityAlertsEnabled
                        hasWikiEnabled
                        isArchived
                        isEmpty
                        isFork
                        isLocked
                        isMirror
                        isPrivate
                        isSecurityPolicyEnabled
                        isTemplate
                        isUserConfigurationRepository
                        mergeCommitAllowed
                        mergeCommitMessage
                        mergeCommitTitle
                        mirrorUrl
                        resourcePath
                        securityPolicyUrl
                        sshUrl

                      }
                    }
                  }
                }
            """
            variables = {"first": n, "query": query, "cursor": None}
            return {"query": template, "variables": variables}

        _result = {
            "ok": False,
            "data": [],
            "headers": None,
            "repository_count": None,
        }

        def next(data):
            _next = None
            page_info = data.get("search", {}).get("pageInfo")
            if page_info:
                _next = (
                    page_info.get("endCursor") if page_info.get("hasNextPage") else None
                )
            return _next

        def handler(context, result):
            nonlocal _result
            if result["ok"]:
                if _result["repository_count"] == None:
                    _result["repository_count"] = result["data"].get(
                        "repositoryCount", 0
                    )
                nodes = result["data"].get("search", {}).get("nodes")
                _result["data"].extend(nodes or [])
                _result["headers"] = result["headers"]
                _result["page_count"] = context["page_count"]
            else:
                return None
            pass

        q0 = get_query("")
        base_result = self.execute_grapqhql_query(
            query=q0["query"],
            variables=q0["variables"],
        )

        # We have to divide the query into separate executions because there is a limit of 10 pages, each containing a maximum of 100 entries.
        q1 = get_query("forks:<=1000")
        q2 = get_query("forks:>1000")
        self.execute_grapqhql_iteration_query(
            query=q1["query"],
            variables=q1["variables"],
            handler=handler,
            next_fn=next,
            max_pages=max_pages,
        )
        self.execute_grapqhql_iteration_query(
            query=q2["query"],
            variables=q2["variables"],
            handler=handler,
            next_fn=next,
            max_pages=max_pages,
        )
        _result["timestamp"] = datetime.now().isoformat()
        _result["quid"] = str(uuid.uuid4())
        _result["query"] = {
            "template": q0["query"],
            "variables": q0["variables"],
            "response_count": base_result["data"]["search"]["repositoryCount"],
        }

        return _result

    def get_pull_requests(self, owner, repository_name, n=100, max_pages=None):
        template = """
            query getPullRequests(
              $owner: String!
              $name: String!
              $states: [PullRequestState!]
              $first: Int!
              $cursor: String
            ) {
              repository(owner: $owner, name: $name) {
                url
                pullRequests(first: $first, states: $states, after: $cursor) {
                  totalCount
                  edges {
                    node {
                      title
                      number
                      createdAt
                      mergedAt
                      bodyText
                      state
                      merged
                      mergeCommit {
                         oid
                         message
                      }
                      commits(first: 100) {
                        edges {
                          node {
                            commit {
                              oid
                              messageHeadline
                            }
                          }
                        }
                      }
                    }
                    cursor
                  }
                  pageInfo {
                    endCursor
                    hasNextPage
                  }
                }
              }
            }
        """
        variables = {
            "owner": owner,
            "name": repository_name,
            "states": ["MERGED", "CLOSED"],
            "first": n,
            "cursor": None,
        }
        _result = {
            "ok": False,
            "data": [],
            "headers": None,
            "pr_count": None,
        }

        def next(data):
            _next = None
            page_info = (
                data.get("repository", {}).get("pullRequests", {}).get("pageInfo")
            )
            if page_info:
                _next = (
                    page_info.get("endCursor") if page_info.get("hasNextPage") else None
                )
            return _next

        def handler(context, result):
            nonlocal _result
            if result["ok"]:
                data = result.get("data", {})
                if _result["pr_count"] == None:
                    _result["pr_count"] = (
                        data.get("repository", {})
                        .get("pullRequests", {})
                        .get("totalCount", 0)
                    )
                prs = (
                    data.get("repository", {}).get("pullRequests", {}).get("edges", [])
                )
                _result["url"] = data.get("repository", {}).get("url")
                _result["data"].extend(prs)
                _result["headers"] = result["headers"]
                _result["page_count"] = context["page_count"]
            else:
                return None
            pass

        self.execute_grapqhql_iteration_query(
            query=template,
            variables=variables,
            handler=handler,
            next_fn=next,
            max_pages=max_pages,
        )
        return _result

    def get_pull_request_count(self, owner, repository_name):
        query = """
            query GetPullRequestCount($owner: String!, $name: String!) {
              repository(owner: $owner, name: $name) {
                pullRequests {
                  totalCount
                }
              }
            }
        """
        variables = {"owner": owner, "name": repository_name}
        result = self.execute_grapqhql_query(query, variables)
        if result["ok"]:
            return result

        return None


github_graphql_api = GitHubGraphQlApi(GITHUB_TOKEN)


if __name__ == "__main__":
    api = github_graphql_api
    rate_limit = api.get_rate_limit()
    repository_fields = api.get_fields("Repository")
    commit_fields = api.get_fields("Commit")
    repository_schema = api.get_schema("Repository")
    pr_schema = api.get_schema("PullRequest")
    commit_schema = api.get_schema("Commit")
    object_types = api.get_types()
    react_repository = api.get_repository(owner="facebook", name="react")

    write_json_file(
        "./src/github/docs/github-repository-schema.json", repository_schema
    )
    write_json_file("./src/github/docs/github-commit-schema.json", commit_schema)
    write_json_file("./src/github/docs/github-pr-schema.json", pr_schema)

    write_json_file(
        "./src/github/docs/github-repository-fields.json", repository_fields
    )
    write_json_file("./src/github/docs/github-commit-fields.json", commit_fields)
    write_json_file("./src/github/docs/github-object-types.json", object_types)

    # top_repositories = (
    #     api.find_top_java_repositories(n=100, min_stars=2000, max_pages=1) or []
    # )
    # write_json_file("./docs/github-api/github-object-types.json", object_types)
    # write_json_file(
    #     get_results_file("repositories_stars_1000.json"), top_repositories["data"]
    # )
    # print(f"Repository count: {len(top_repositories)}")
    pass
