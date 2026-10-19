"""따옴표를 지원하는 명령 파서와 mini-git> REPL."""

from __future__ import annotations

import shlex
from collections.abc import Callable

from .models import Commit
from .repository import MiniGitError, Repository


def format_commits(commits: list[Commit]) -> str:
    """모든 목록에서 hash/author/timestamp/message를 식별 가능하게 출력한다."""
    return "\n".join(
        f"commit {commit.hash} ({commit.author}, "
        f"{commit.timestamp.isoformat(timespec='microseconds')})\n    {commit.message}"
        for commit in commits
    )


class CLI:
    """한 명령을 실행하고 결과 문자열을 반환한다. 종료 요청 시 running=False."""

    def __init__(self, repository: Repository | None = None) -> None:
        self.repository = repository if repository is not None else Repository()
        self.running = True

    def execute(self, line: str) -> str:
        """명령어만 대소문자를 무시하며, 문법/저장소 오류는 문자열로 반환한다."""
        try:
            tokens = shlex.split(line)
        except ValueError:
            return "Invalid args"
        if not tokens:
            return ""
        command, args = tokens[0].upper(), tokens[1:]
        try:
            return self._dispatch(command, args)
        except MiniGitError as error:
            return str(error)

    @staticmethod
    def _require_args(args: list[str], count: int) -> None:
        if len(args) != count or any(not arg.strip() for arg in args):
            raise MiniGitError("Invalid args")

    def _dispatch(self, command: str, args: list[str]) -> str:
        repo = self.repository
        if command in {"EXIT", "QUIT"}:
            self._require_args(args, 0)
            self.running = False
            return "Bye."
        if command == "INIT":
            self._require_args(args, 1)
            repo.init(args[0])
            return f"Initialized repository.\nCurrent branch: main\nCurrent user: {repo.author}"
        if command == "BRANCH":
            self._require_args(args, 1)
            repo.branch(args[0])
            return f"Created branch: {args[0]}"
        if command == "SWITCH":
            self._require_args(args, 1)
            repo.switch(args[0])
            return f"Switched to branch: {args[0]}"
        if command == "COMMIT":
            self._require_args(args, 1)
            commit = repo.commit(args[0])
            return f"[{repo.current_branch} {commit.hash}] {commit.message}"
        if command == "LOG":
            if not args:
                commits = repo.log()
            elif len(args) == 1 and args[0].startswith("--sort-by="):
                commits = repo.log(args[0][len("--sort-by="):])
            else:
                raise MiniGitError("Invalid args")
            return format_commits(commits) or "No commits"
        if command == "PATH":
            self._require_args(args, 2)
            path = repo.path(args[0], args[1])
            return "Path: " + " -> ".join(path) if path is not None else "No path"
        if command == "ANCESTORS":
            self._require_args(args, 1)
            return format_commits(repo.ancestors(args[0])) or "No ancestors"
        if command == "SEARCH":
            self._require_args(args, 1)
            if args[0].startswith("--author="):
                commits = repo.search_author(args[0][len("--author="):])
            elif args[0].startswith("--"):
                raise MiniGitError("Invalid args")
            else:
                commits = repo.search_keyword(args[0])
            noun = "commit" if len(commits) == 1 else "commits"
            summary = f"Found {len(commits)} {noun}:"
            return summary + ("\n" + format_commits(commits) if commits else "")
        return f"Unknown command: {command}"


def run_repl(
    read: Callable[[str], str] = input,
    write: Callable[[str], None] = print,
) -> None:
    """명령을 반복 처리하며 exit/quit, EOF, Ctrl+C에서 정상 종료한다."""
    cli = CLI()
    while cli.running:
        try:
            line = read("mini-git> ")
        except (EOFError, KeyboardInterrupt):
            write("\nBye.")
            break
        output = cli.execute(line)
        if output:
            write(output)
