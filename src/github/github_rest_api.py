from src.github.github_api import (
    GitHubApi,
    GITHUB_TOKEN,
    parse_link_header,
    get_query_parameter,
)


class GitHubRestApi(GitHubApi):
    def __init__(self, token=None, headers=None):
        # Call the superclass constructor
        super().__init__(token, headers)

    # https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories
    def find_repositories(self, n, criteria=None):
        params = {}  # we may use some base criteria in the future
        if isinstance(criteria, dict):  # add additional optional criteria parameters
            params = {**criteria, **params}

        def _provider(page, page_size):
            _params = {**params, **{"page": page, "per_page": page_size}}
            _result = self.get_request("/search/repositories", _params)
            _items = _result["data"]["items"] if _result["ok"] else []
            return _items

        items = self.use_paging(_provider, n, page_size=100)
        return items

    # issues (open and closed) excluding pull requests
    # options?: {
    #     "type": "issue" | "pr"
    # }
    def get_issue_count(self, repo_owner: str, repo_name: str, opts=None) -> int:
        _params = {"state": "all", "per_page": 1}
        total_issues = 0
        path = "pulls" if opts and opts.get("type") == "pr" else "issues"
        endpoint = f"/repos/{repo_owner}/{repo_name}/{path}"
        result = self.get_request(endpoint, _params)
        headers = result["headers"]
        if "link" in headers:
            links = headers["link"].split(", ")
            last_page_url = next(
                parse_link_header(link)
                for link in links
                if get_query_parameter(link, "rel") == "last"
            )
            if last_page_url:
                last_page_str = get_query_parameter(last_page_url["url"], "page")
                total_issues = int(last_page_str or 0)
            else:
                # If there's no "last" link, we're on the only page
                total_issues = len(result["data"])
        else:
            # If the response has no 'Link' header, there is only one page of results
            total_issues = len(result["data"])
        return total_issues

    # n = -1 means unlimited fetch
    def use_paging(self, provider_fn, n, page_size):
        items = []
        current_page = 1
        while len(items) < n or n < 0:
            # Fetch the next page of items
            page_items = provider_fn(page=current_page, page_size=page_size)
            if (
                not page_items
            ):  # cancel if the provider does not return items (e.g., because of an error)
                return items
            if isinstance(page_items, list):
                items.extend(page_items[: n - len(items)])
                if len(page_items) < page_size:
                    break  # No more items available
            # Increment the page number for the next call
            current_page += 1
        return items


github_rest_api = GitHubRestApi(GITHUB_TOKEN)
