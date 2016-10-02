from collections import OrderedDict

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
        return rx.Observable.concat(
            list(map(self.github.rx_contributors, repos))) \
            .buffer_with_count(len(repos)) \
            .map(funcy.flatten) \
            .map(funcy.partial(funcy.pluck, 'login'))

    def __sort(self, contributors):
        return OrderedDict(
            sorted(funcy.count_by(funcy.identity, contributors).items(),
                   key=lambda i: i[1], reverse=True)).keys()

    def __hireable(self, logins):
        return rx.Observable.concat(
            list(map(self.github.rx_user_details, logins))) \
            .buffer_with_count(len(logins)) \
            .map(funcy.partial(funcy.where, hireable=True)) \
            .map(funcy.partial(funcy.lpluck, 'login'))
