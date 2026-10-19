"""표준 정렬 API나 그래프 라이브러리를 사용하지 않는 알고리즘."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Mapping
from typing import TypeVar

from .models import Commit

T = TypeVar("T")
K = TypeVar("K")


def merge_sort(items: Iterable[T], key: Callable[[T], K]) -> list[T]:
    """key 기준 오름차순의 안정 병합 정렬. 시간 O(n log n), 공간 O(n)."""
    source = list(items)
    size = len(source)
    if size < 2:
        return source

    # 반복형 bottom-up 방식은 긴 입력에서도 재귀 깊이 제한을 받지 않는다.
    source_keys = [key(item) for item in source]
    target = source.copy()
    target_keys = source_keys.copy()
    width = 1
    while width < size:
        for start in range(0, size, width * 2):
            middle = min(start + width, size)
            end = min(start + width * 2, size)
            left, right = start, middle
            for output in range(start, end):
                # 동률에서는 왼쪽 원소를 선택하므로 입력 순서가 유지된다.
                if right >= end or (
                    left < middle and source_keys[left] <= source_keys[right]
                ):
                    target[output] = source[left]
                    target_keys[output] = source_keys[left]
                    left += 1
                else:
                    target[output] = source[right]
                    target_keys[output] = source_keys[right]
                    right += 1
        source, target = target, source
        source_keys, target_keys = target_keys, source_keys
        width *= 2
    return source


def topological_order(commits: Mapping[str, Commit]) -> list[Commit]:
    """Kahn 알고리즘으로 전체 DAG의 부모를 자식보다 먼저 반환한다. O(V+E)."""
    indegree = {commit_hash: len(commit.parents) for commit_hash, commit in commits.items()}
    children: dict[str, list[str]] = {commit_hash: [] for commit_hash in commits}
    for commit_hash, commit in commits.items():
        for parent in commit.parents:
            if parent not in commits:
                raise ValueError(f"Missing parent: {parent}")
            children[parent].append(commit_hash)

    ready = deque(commit_hash for commit_hash, degree in indegree.items() if degree == 0)
    result: list[Commit] = []
    while ready:
        commit_hash = ready.popleft()
        result.append(commits[commit_hash])
        for child in children[commit_hash]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)

    if len(result) != len(commits):
        raise ValueError("Commit graph contains a cycle")
    return result


def shortest_path(
    adjacency: Mapping[str, Iterable[str]], start: str, end: str
) -> list[str] | None:
    """무방향 그래프에서 최단 경로 중 '->' 연결 문자열이 최소인 경로. O(V+E)."""
    # 도착점에서 BFS하여 각 노드가 도착점까지 가는 최소 간선 수를 구한다.
    distance = {end: 0}
    queue = deque([end])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)
    if start not in distance:
        return None

    # 거리가 1씩 감소하는 이웃만 고른다. 그중 사전순 최소를 고르면
    # 최단 길이를 보존하면서 전체 경로 문자열도 사전순 최소가 된다.
    path = [start]
    current = start
    while current != end:
        best: str | None = None
        best_key: str | None = None
        for neighbor in adjacency[current]:
            if distance.get(neighbor) == distance[current] - 1:
                candidate_key = neighbor + ("->" if neighbor != end else "")
                if best_key is None or candidate_key < best_key:
                    best, best_key = neighbor, candidate_key
        if best is None:
            raise ValueError("Inconsistent undirected graph")
        path.append(best)
        current = best
    return path


def ancestor_hashes(commits: Mapping[str, Commit], start: str) -> list[str]:
    """반복형 DFS로 자기 자신을 제외한 모든 조상을 중복 없이 반환한다."""
    visited = {start}
    stack = list(reversed(commits[start].parents))
    result: list[str] = []
    while stack:
        commit_hash = stack.pop()
        if commit_hash in visited:
            continue
        visited.add(commit_hash)
        result.append(commit_hash)
        stack.extend(reversed(commits[commit_hash].parents))
    return result
