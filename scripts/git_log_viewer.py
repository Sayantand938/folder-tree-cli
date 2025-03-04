import git
from rich.console import Console
from rich.table import Table


def list_git_commits():
    try:
        repo = git.Repo(".")  # Initialize Git repository in the current directory
        commits = list(repo.iter_commits())  # Fetch all commits

        table = Table(title="Git Commit History", show_lines=True)
        table.add_column("Hash", style="cyan", no_wrap=True)
        table.add_column("Author", style="magenta")
        table.add_column("Date", style="green")
        table.add_column("Message", style="yellow")

        for commit in commits:
            table.add_row(
                commit.hexsha[:7],  # Shortened commit hash
                commit.author.name,
                commit.committed_datetime.strftime("%Y-%m-%d %H:%M"),
                commit.message.strip(),
            )

        console = Console()
        console.print(table)

    except git.exc.InvalidGitRepositoryError:
        print("Not a valid Git repository!")


if __name__ == "__main__":
    list_git_commits()
