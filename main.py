from logic.hireable import HireableFinder
from service.github import GithubService


def main():
    github_service = GithubService()
    hireable_finder = HireableFinder(github_service)

    login = input("Provide user login: ")

    print("\nCalculating hireables...\n")

    hireable_finder.rx_find_hireable(login).subscribe(on_next=print_hireables)


def print_hireables(hireables):
    hireables_str = '\n'.join(
        map(lambda l: '{0}. {1}'.format(l[0] + 1, l[1]),
            enumerate(hireables)))

    print(hireables_str)


if __name__ == '__main__':
    main()
