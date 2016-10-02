from operator import itemgetter

import funcy
import rx

from service.github import GithubService


class HireableFinder:
    """
    Finds hireable Github users.

    :param GithubService github_service: Github service
    """
    def __init__(self, github_service):
        self.github = github_service

    def rx_find_hireable(self, initial_user):
        return self.github.rx_starred_repositories(initial_user) \
            .map(funcy.partial(funcy.lpluck, 'full_name')) \
            .flat_map_latest(self.__contributors) \
            .map(funcy.rpartial(funcy.without, initial_user)) \
            .map(self.__sort) \
            .flat_map_latest(self.__hireable)

    def __contributors(self, repos):
        contributors = list(map(self.github.rx_contributors, repos))

        return rx.Observable.concat(contributors) \
            .buffer_with_count(len(repos)) \
            .map(funcy.flatten) \
            .map(funcy.partial(funcy.pluck, 'login'))

    def __sort(self, contributors):
        contribs = funcy.count_by(None, contributors).items()
        sorted_contribs = sorted(contribs, key=itemgetter(1), reverse=True)

        return funcy.lmap(0, sorted_contribs)

    def __hireable(self, logins):
        return rx.Observable.concat(
            list(map(self.github.rx_user_details, logins))) \
            .buffer_with_count(len(logins)) \
            .map(funcy.partial(funcy.where, hireable=True)) \
            .map(funcy.partial(funcy.lpluck, 'login'))
