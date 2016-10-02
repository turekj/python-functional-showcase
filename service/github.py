from rx_extensions.requests import rx_get_json


class GithubService:
    def rx_user_details(self, username):
        return rx_get_json('https://api.github.com/users/{0}'.format(username))
