import re
import time
import requests
from urllib.parse import urlencode, urlunparse, urlparse, parse_qs
from dotenv import load_dotenv
import os

from src.core.logger import log

load_dotenv()  # This loads the .env file into the environment

# load from .env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_API_GRAPHQL_ENDPOINT = "/graphql"


class GitHubApi:
    def __init__(self, token, headers=None):
        self.token = token
        auth_header = {"Authorization": f"Bearer {token}"} if token else {}
        self.headers = {**auth_header, **(headers or {})}

    def _get_request_heaaders(self, headers=None):
        request_headers = {**self.headers, **(headers or {})}
        return request_headers

    def _get_request_url(self, endpoint="", params=None):
        url = GITHUB_API_BASE_URL.rstrip("/")
        if endpoint:
            url = "/".join([url, endpoint.lstrip("/")])
        url = build_url(url, params)
        return url

    def _get_request_result(self, response):
        if not response:
            return {"ok": False, "data": None, "headers": None, "exception": True}
        data = None
        url = response.url
        ok = 200 <= response.status_code < 300
        if ok:
            data = response.json()
        else:
            print(
                f"Failed to fetch invoke GitHub API {url}. Status code: {response.status_code}"
            )

        result = {"ok": ok, "data": data, "headers": response.headers}
        return result

    def get_request(self, endpoint="", params=None, headers=None):
        request_headers = self._get_request_heaaders()
        url = self._get_request_url(endpoint, params)
        response = requests.get(url, headers=request_headers)
        results = self._get_request_result(response)
        return results

    def post_request(
        self,
        endpoint="",
        data=None,
        json=None,
        params=None,
        headers=None,
        retry_count=0,
        retry_ms=0,
    ):
        request_headers = self._get_request_heaaders()
        url = self._get_request_url(endpoint, params)
        retry_counter = 0
        response = None
        while retry_counter <= retry_count:
            if retry_counter:
                log.warn(f"github_api retry: {retry_counter}")
            try:
                response = requests.post(
                    url, data=data, json=json, headers=request_headers
                )
            except Exception as e:
                response = None
                break
            finally:
                if response.status_code == 502:
                    retry_counter += 1
                    response = None
                    if retry_ms and retry_counter <= retry_count:
                        time.sleep(retry_counter * retry_ms / 1000)
                else:
                    break
        # }

        results = self._get_request_result(response)
        return results


def get_query_parameter(url, property):
    link_url = parse_link_header(url)
    if link_url:
        if property == "rel":
            return link_url.get(property)
        url = link_url.get("url")

    url_elements = urlparse(url)
    url_query = url_elements.query
    query_params = parse_qs(url_query)
    value = query_params.get(property, None)
    if value:
        return value[0]
    return None


def build_url(url, params=None):
    url_parts = list(urlparse(url))
    # Build the query string only if params is not None and not empty
    if params:
        query_string = urlencode(params)
        url_parts[4] = query_string  # Set the query part of the URL

    _url = urlunparse(url_parts)
    return _url


#  RFC 5988, "Web Linking"
def parse_link_header(linke_header):
    # Regular expression pattern to match the URL and rel
    pattern = r'<(?P<url>.+?)>; rel="(?P<rel>.+?)"'
    match = re.match(pattern, linke_header)
    if match:
        # If the pattern matches, return a dictionary with the named groups
        return {"url": match.group("url"), "rel": match.group("rel")}
    else:
        # If the pattern does not match, return None
        return None
