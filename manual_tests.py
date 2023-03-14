import query
from requests import post
from pprint import pprint


if __name__ == "__main__":

    print("Enter an access token: ", end="")
    auth = input()

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    preliminary_query = """
    {
        repository(name: "flutter", owner: "flutter") {
            issue(number: 1831) {
                comments(first:100) {
                    edges {
                        node {
                            author {
                                login
                            }
                            bodyText
                            createdAt
                        }
                    }
                    pageInfo {
                        endCursor
                    }
                }
            }
        }  
    }
    """

    request = post("https://api.github.com/graphql", json={"query": preliminary_query}, headers=headers)
    trimmed_request = request.json()["data"]["repository"]["issue"]["comments"]

    trimmed_request["edges"] += query.get_other_comments(1831, trimmed_request["pageInfo"]["endCursor"],
                                                "flutter", "flutter", "issue", headers)

    pprint(trimmed_request)
    print(len(trimmed_request["edges"]))
