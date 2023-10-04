
import requests

def get_stargazers_mapping(candidate_repository_urls):
    stargazers_mapping = {}
    for repository_url in candidate_repository_urls:
        request_url = f"https://api.github.com/repos/{repository_url[19:]}"
        response = requests.get(request_url)
        if response.status_code == 200:
            repo_info = response.json()
            stargazers_count = repo_info["stargazers_count"]
            stargazers_mapping[repository_url] = stargazers_count
    return stargazers_mapping

def get_ten_most_popular(stargazers_mapping):
    sorted_repos = sorted(stargazers_mapping.items(), key=lambda x: x[1], reverse=True)
    top_10_repos = sorted_repos[:10]
    top_10_repo_urls = [repo[0] for repo in top_10_repos]
    return top_10_repo_urls


def main():
    candidate_repository_urls = [
    "https://github.com/iluwatar/java-design-patterns",
    "https://github.com/spring-projects/spring-framework",
    "https://github.com/NationalSecurityAgency/ghidra",
    "https://github.com/square/retrofit",
    "https://github.com/bumptech/glide",
    "https://github.com/SeleniumHQ/selenium",
    "https://github.com/TeamNewPipe/NewPipe",
    "https://github.com/apache/skywalking",
    "https://github.com/libgdx/libgdx",
    "https://github.com/mybatis/mybatis-3",
    "https://github.com/OpenAPITools/openapi-generator",
    "https://github.com/iBotPeaches/Apktool",
    "https://github.com/openzipkin/zipkin",
    "https://github.com/material-components/material-components-android",
    "https://github.com/thingsboard/thingsboard",
    "https://github.com/mockito/mockito",
    "https://github.com/elastic/logstash",
    "https://github.com/deeplearning4j/deeplearning4j",
    "https://github.com/Netflix/zuul",
    "https://github.com/apache/druid",
    "https://github.com/questdb/questdb",
    "https://github.com/quarkusio/quarkus",
    "https://github.com/google/guice",
    "https://github.com/LSPosed/LSPosed",
    "https://github.com/Netflix/eureka",
    "https://github.com/codecentric/spring-boot-admin",
    "https://github.com/apache/dolphinscheduler"]
    stargazers_mapping = get_stargazers_mapping(candidate_repository_urls)
    print(stargazers_mapping)
    ten_most_popular_repositories = get_ten_most_popular(stargazers_mapping)
    print(ten_most_popular_repositories)


if __name__ == "__main__":
    main()
