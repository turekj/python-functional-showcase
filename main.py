from logic.hireable import HireableFinder
from service.github import GithubService


printed_hireable_count = 0


def main():
    github_service = GithubService()
    hireable_finder = HireableFinder(github_service)

    login = input("Provide user login: ")

    print("Hireable: \n")
    hireable_finder.rx_find_hireable(login).subscribe(
        on_next=print_hireable,
        on_completed=on_hireables_printed)


def print_hireable(hireable):
    global printed_hireable_count
    print("{0}. {1}\n".format(printed_hireable_count + 1, hireable))
    printed_hireable_count += 1


def on_hireables_printed():
    global printed_hireable_count
    printed_hireable_count = 0


if __name__ == '__main__':
    main()
