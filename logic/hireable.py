from operator import itemgetter

import funcy
import rx

from service.github import GithubService


# noinspection PyMethodMayBeStatic
class HireableFinder:
    """
    Finds hireable Github users.

    :param GithubService github_service: Github service
    """
    def __init__(self, github_service):
        self.github = github_service

    def rx_find_hireable(self, initial_user):
        return self.starred_repo_names(initial_user) \
            .flat_map_latest(self.contributor_logins) \
            .map(funcy.rpartial(funcy.without, initial_user)) \
            .map(self.contributors_sorted_by_repos_contributed_in) \
            .flat_map_latest(self.filter_hireable_users)

    def starred_repo_names(self, user):
        return self.github.rx_starred_repositories(user) \
            .map(funcy.partial(funcy.lpluck, 'full_name'))

    def contributor_logins(self, repos):
        contributors = funcy.lmap(self.github.rx_contributors, repos)

        return rx.Observable.concat(contributors) \
            .buffer_with_count(len(repos)) \
            .map(funcy.flatten) \
            .map(funcy.partial(funcy.pluck, 'login'))

    def contributors_sorted_by_repos_contributed_in(self, contributors):
        users_by_repos = funcy.count_by(None, contributors).items()
        sorted_users = sorted(users_by_repos, key=itemgetter(1), reverse=True)

        return funcy.lmap(0, sorted_users)

    def filter_hireable_users(self, users):
        return rx.Observable.concat(
            list(map(self.github.rx_user_details, users))) \
            .buffer_with_count(len(users)) \
            .map(funcy.partial(funcy.where, hireable=True)) \
            .map(funcy.partial(funcy.lpluck, 'login'))
