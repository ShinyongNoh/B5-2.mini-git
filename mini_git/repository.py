"""브랜치, HEAD, 커밋 저장소를 관리하고 독립 알고리즘을 호출한다."""

from __future__ import annotations

from datetime import datetime, timezone

from .algorithms import ancestor_hashes, merge_sort, shortest_path, topological_order
from .index import InvertedIndex
from .models import Commit


class MiniGitError(Exception):
    """CLI에서 traceback 대신 사용자에게 표시하는 예상 가능한 오류."""


class Repository:
    """세션 내 메모리 저장소. HEAD는 현재 브랜치가 가리키는 커밋이다."""

    def __init__(self) -> None:
        self.author: str | None = None
        self.current_branch: str | None = None
        self.commits: dict[str, Commit] = {}
        self.branches: dict[str, str | None] = {}
        self.adjacency: dict[str, list[str]] = {}
        self.index = InvertedIndex()
        self._next_id = 1

    @property
    def head(self) -> str | None:
        """커밋이 없는 브랜치의 HEAD는 None이다."""
        if self.current_branch is None:
            return None
        return self.branches[self.current_branch]

    def require_initialized(self) -> None:
        """초기화 이전의 저장소 명령을 거부한다."""
        if self.current_branch is None:
            raise MiniGitError("Repository not initialized")

    @staticmethod
    def _require_text(value: str) -> None:
        if not value.strip():
            raise MiniGitError("Invalid args")

    def init(self, author: str) -> None:
        """기존 데이터를 지우고 main을 만든다. 세션 hash 카운터는 유지한다."""
        self._require_text(author)
        self.author = author
        self.current_branch = "main"
        self.commits = {}
        self.branches = {"main": None}
        self.adjacency = {}
        self.index = InvertedIndex()

    def branch(self, name: str) -> None:
        """현재 HEAD를 가리키는 브랜치를 만들며 현재 브랜치는 유지한다."""
        self.require_initialized()
        self._require_text(name)
        if name in self.branches:
            raise MiniGitError(f"Branch already exists: {name}")
        self.branches[name] = self.head

    def switch(self, name: str) -> None:
        """브랜치를 전환하면 HEAD도 해당 브랜치의 마지막 커밋으로 바뀐다."""
        self.require_initialized()
        if name not in self.branches:
            raise MiniGitError(f"Unknown branch: {name}")
        self.current_branch = name

    def commit(self, message: str) -> Commit:
        """현재 HEAD만 부모로 삼는다. 새 노드에서 기존 노드로만 연결하여 DAG를 보장한다."""
        self.require_initialized()
        self._require_text(message)
        commit_hash = f"{self._next_id:08x}"
        parents = () if self.head is None else (self.head,)
        commit = Commit(
            hash=commit_hash,
            message=message,
            author=self.author,
            timestamp=datetime.now(timezone.utc),
            parents=parents,
        )
        self._next_id += 1
        self.commits[commit_hash] = commit
        self.adjacency[commit_hash] = list(parents)
        for parent in parents:
            self.adjacency[parent].append(commit_hash)
        self.index.add(commit)
        self.branches[self.current_branch] = commit_hash
        return commit

    def get_commit(self, commit_hash: str) -> Commit:
        """hash 딕셔너리 조회. 평균 O(1)."""
        self.require_initialized()
        if commit_hash not in self.commits:
            raise MiniGitError(f"Unknown commit: {commit_hash}")
        return self.commits[commit_hash]

    def log(self, sort_by: str | None = None) -> list[Commit]:
        """전체 브랜치 로그. 기본은 위상 순서, 옵션은 해당 key의 안정 오름차순."""
        self.require_initialized()
        if sort_by is None:
            return topological_order(self.commits)
        if sort_by == "date":
            return merge_sort(self.commits.values(), key=lambda commit: commit.timestamp)
        if sort_by == "author":
            return merge_sort(self.commits.values(), key=lambda commit: commit.author)
        raise MiniGitError("Invalid args")

    def path(self, start: str, end: str) -> list[str] | None:
        """부모/자식 모두 이동 가능한 최단 경로를 반환한다."""
        self.get_commit(start)
        self.get_commit(end)
        return shortest_path(self.adjacency, start, end)

    def ancestors(self, commit_hash: str) -> list[Commit]:
        """모든 부모 연결을 따라 조상을 DFS 순서로 반환한다."""
        self.get_commit(commit_hash)
        return [self.commits[parent] for parent in ancestor_hashes(self.commits, commit_hash)]

    def search_keyword(self, keyword: str) -> list[Commit]:
        """단어는 토큰 완전 일치, 공백 포함 인자는 연속된 토큰 구문으로 검색한다."""
        self.require_initialized()
        self._require_text(keyword)
        hashes = self.index.by_keyword(keyword)
        query = keyword.lower().split()
        if len(query) == 1:
            return [self.commits[commit_hash] for commit_hash in hashes]
        result: list[Commit] = []
        for commit_hash in hashes:
            commit = self.commits[commit_hash]
            tokens = commit.message.lower().split()
            if any(tokens[i:i + len(query)] == query for i in range(len(tokens) - len(query) + 1)):
                result.append(commit)
        return result

    def search_author(self, author: str) -> list[Commit]:
        """작성자 역색인에 있는 후보만 hash로 가져온다."""
        self.require_initialized()
        self._require_text(author)
        return [self.commits[commit_hash] for commit_hash in self.index.by_author(author)]
