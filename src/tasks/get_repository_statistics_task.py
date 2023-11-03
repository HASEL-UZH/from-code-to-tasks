import re
import json
from pydriller import Repository


def get_repository_statistics(repository_url):
    print(f"get_repository_statistics: {repository_url}")
    commit_count = 0
    commit_with_pr_count = 0

    repository = Repository(repository_url, only_modifications_with_file_types=[".java"])
    for commit in repository.traverse_commits():
        commit_count += 1
        if commit_count % 100 == 0:
            print(f"  commit_count: {commit_count}, commit_with_pr_count: {commit_with_pr_count}")

        if _has_pull_request(commit):
            commit_with_pr_count+= 1
        else:
            pass

    statistics = {
        "repository_url": repository_url,
        "statistics": {
            "commit_count": commit_count,
            "commit_with_pr_count": commit_with_pr_count
        }
    }
    return statistics

def _has_pull_request(commit):
    pull_request_number = _get_pull_request_number(commit.msg)
    return pull_request_number is not None

def _get_pull_request_number(commit_msg):
    pattern = r"#(\d+)"
    pull_request_numbers = re.findall(pattern, commit_msg)
    if len(pull_request_numbers) != 1:
        return None
    else:
        pull_request_number = pull_request_numbers[0]
        print("------------------")
        print("    "+commit_msg)
        return pull_request_number

repository_urls = [
    "https://github.com/iluwatar/java-design-patterns",
]
_repository_urls = [
    "https://github.com/Snailclimb/JavaGuide",
    "https://github.com/facebook/react-native",
    "https://github.com/iluwatar/java-design-patterns",
    "https://github.com/spring-projects/spring-boot",
    "https://github.com/elastic/elasticsearch",
    "https://github.com/TheAlgorithms/Java",
    "https://github.com/google/guava",
    "https://github.com/ReactiveX/RxJava",
    "https://github.com/NationalSecurityAgency/ghidra",
    "https://github.com/eugenp/tutorials",
    "https://github.com/dbeaver/dbeaver",
    "https://github.com/airbnb/lottie-android",
    "https://github.com/bumptech/glide",
    "https://github.com/alibaba/arthas",
    "https://github.com/halo-dev/halo",
    "https://github.com/apolloconfig/apollo",
    "https://github.com/alibaba/nacos",
    "https://github.com/alibaba/druid",
    "https://github.com/alibaba/canal",
    "https://github.com/TeamNewPipe/NewPipe",
    "https://github.com/alibaba/fastjson",
    "https://github.com/seata/seata",
    "https://github.com/Netflix/Hystrix",
    "https://github.com/apache/skywalking",
    "https://github.com/libgdx/libgdx",
    "https://github.com/redisson/redisson",
    "https://github.com/google/ExoPlayer",
    "https://github.com/Anuken/Mindustry",
    "https://github.com/oracle/graal",
    "https://github.com/apache/shardingsphere",
    "https://github.com/dianping/cat",
    "https://github.com/keycloak/keycloak",
    "https://github.com/iBotPeaches/Apktool",
    "https://github.com/antlr/antlr4",
    "https://github.com/baomidou/mybatis-plus",
    "https://github.com/prestodb/presto",
    "https://github.com/thingsboard/thingsboard",
    "https://github.com/ben-manes/caffeine",
    "https://github.com/alibaba/DataX",
    "https://github.com/eclipse-vertx/vert.x",
    "https://github.com/arduino/Arduino",
    "https://github.com/elastic/logstash",
    "https://github.com/yuliskov/SmartTube",
    "https://github.com/dataease/dataease",
    "https://github.com/deeplearning4j/deeplearning4j",
    "https://github.com/GoogleContainerTools/jib",
    "https://github.com/pinpoint-apm/pinpoint",
    "https://github.com/questdb/questdb",
    "https://github.com/quarkusio/quarkus",
    "https://github.com/google/guice",
    "https://github.com/neo4j/neo4j"
]

def get_repository_statistics_task():
    statistics = []
    for repo_url in repository_urls:
        repo_statistics = get_repository_statistics(repo_url)
        statistics.append(repo_statistics)
        print(json.dumps(repo_statistics, indent=4))
    pass


if __name__ == "__main__":
    print("TASK DISABLED"); exit(0)
    get_repository_statistics_task()


