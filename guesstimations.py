# Most repos are public
# Guesstimate by hand calling the API
num_repos = 13000000


def hours_to_download_repos():
    # GitHub's API limit
    # Need to use auth
    # https://developer.github.com/v3/#rate-limiting
    max_requests_per_hour = 5000
    max_requests_per_second = max_requests_per_hour / 3600
    # approx 1.3888888888888888

    # page limit
    repos_per_request = 100
    max_repos_per_second = repos_per_request * max_requests_per_second
    min_crawl_time_in_seconds = num_repos / max_repos_per_second
    min_crawl_time_in_hours = min_crawl_time_in_seconds / 3600
    # it'll take 26 hours

    return min_crawl_time_in_hours


def size_of_repos_in_gb():
    kb = num_repos * 5 # ~5kb pretty printed json
    mb = kb / 1000
    gb = mb / 1000
    return gb



print('{} hours to dl'.format(hours_to_download_repos()))
print('{} gb to download'.format(size_of_repos_in_gb()))

