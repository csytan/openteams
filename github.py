import datetime
import json
import time
import urllib.parse

import peewee
import playhouse.hybrid
import playhouse.migrate
import playhouse.sqlite_ext
import playhouse.apsw_ext
import requests

import secrets




db = playhouse.apsw_ext.APSWDatabase('database.db')
db.connect()


def migrate():
    migrator = playhouse.migrate.SqliteMigrator(db)
    playhouse.migrate.migrate(
        migrator.drop_column('repo', 'issues_per_stars'),
        migrator.add_column('repo', 'issues_per_star', peewee.FloatField(default=0.0)),
        migrator.add_index('repo', ('stars',), False),
        migrator.add_index('repo', ('open_issues',), False),
        migrator.add_index('repo', ('watchers',), False),
        migrator.add_index('repo', ('issues_per_star',), False),
    )
# migrate()


class BaseModel(peewee.Model):
    class Meta:
        database = db


class SearchProgress(BaseModel):
    min_stars = peewee.IntegerField(default=100)

    @classmethod
    def get_progress(cls):
        progress, created = cls.get_or_create(id=1)
        return progress


class Repo(BaseModel):
    github_id = peewee.IntegerField(unique=True)
    fetched = playhouse.apsw_ext.DateTimeField()
    stars = peewee.IntegerField(default=0, index=True)
    open_issues = peewee.IntegerField(default=0, index=True)
    watchers = peewee.IntegerField(default=0, index=True)
    issues_per_star = peewee.FloatField(default=0.0, index=True)
    data = playhouse.sqlite_ext.JSONField()

    def __repr__(self):
        return json.dumps({
            column_name: getattr(self, column_name)
            for column_name in self._meta.columns.keys()
        }, indent=4, separators=(',', ': '), default=str)


db.create_tables([
    SearchProgress,
    Repo
], safe=True)





def fetch_github_api(url):
    print(
        'Fetching {}'.format(url)
    )
    response = requests.get(
        url=url,
        headers={
            'Authorization': 'token ' + secrets.GITHUB_API_TOKEN
        })

    # Keep below the rate limit
    # https://developer.github.com/v3/#rate-limiting
    remaining = response.headers['X-RateLimit-Remaining']
    if not remaining:
        reset_time_seconds = response.headers['X-RateLimit-Reset']
        reset_time = datetime.datetime.utcfromtimestamp(reset_time_seconds)
        now = datetime.datetime.utcnow()
        sleep_seconds = (reset_time - now).seconds
        print(
            'Rate limit reached. Sleeping for {} seconds.'
                .format(sleep_seconds)
        )
        time.sleep(sleep_seconds)

    return response.json()



def fetch_public_repos(start_id):
    # https://developer.github.com/v3/repos/#list-all-public-repositories
    # Example: https://api.github.com/repositories?since=130000000
    return fetch_github_api(
        'https://api.github.com/repositories?since={}'
            .format(start_id)
    )


def search_public_repos(page=0, min_stars=100):
    # https://developer.github.com/v3/search/#search-repositories
    # Example: 
    # https://api.github.com/search/repositories?sort=stars&order=desc&q=stars:%3E100&page=10&per_page=100
    return fetch_github_api(
        'https://api.github.com/search/repositories?' +
        urllib.parse.urlencode({
            'q': 'stars:>={}'.format(min_stars),
            'sort': 'stars',
            'order': 'asc',
            'per_page': 100,
            'page': page
        })
    )



def download_github_public_repos():
    progress = SearchProgress.get_progress()
    next_min_stars = progress.min_stars

    # only the first 1000 results are available
    while True:
        for page in range(1, 11):
            response = search_public_repos(page, progress.min_stars)
            repos_data = response['items']

            # No more results
            if not repos_data:
                print('No repos found. Exiting')
                return

            # Save repos
            for repo_data in repos_data:
                repo_id = repo_data['id']
                repo = (
                    Repo.get_or_none(github_id=repo_id) or 
                    Repo(github_id=repo_id)
                )
                repo.fetched = datetime.datetime.utcnow()
                repo.stars = repo_data['stargazers_count']
                repo.open_issues = repo_data['open_issues_count']
                repo.watchers = repo_data['watchers']
                repo.issues_per_star = repo.open_issues / repo.stars
                repo.data = repo_data
                repo.save()

            next_min_stars = repo.stars
        
        progress.min_stars = next_min_stars
        progress.save()




def download_npm_modules():
    # https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md
    pass


# How many projects are active?
# How many still get new issues?
# How many are on npm?
# How many are dead but still receive plenty of downloads from NPM?
# How many are used by large corporations?






if __name__ == '__main__':
    # download_github_public_repos()

    print('starting')
    query = Repo.select().order_by(Repo.issues_per_star.desc()).limit(100)
    # query = Repo.select()
    for repo in query:
        # repo.issues_per_star = repo.open_issues / repo.stars
        # repo.save()

        print(repo.data['html_url'], repo.issues_per_star)



