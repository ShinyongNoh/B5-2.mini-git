"""메시지 토큰과 작성자로 커밋 후보를 바로 찾는 역색인."""

from .models import Commit


class InvertedIndex:
    """keyword/author -> 커밋 hash 목록. 목록은 커밋 생성 순서를 유지한다."""

    def __init__(self) -> None:
        self.keywords: dict[str, list[str]] = {}
        self.authors: dict[str, list[str]] = {}

    def add(self, commit: Commit) -> None:
        """split/lower 토큰을 등록하며 같은 메시지의 중복 토큰은 한 번만 넣는다."""
        seen: set[str] = set()
        for keyword in commit.message.lower().split():
            if keyword not in seen:
                self.keywords.setdefault(keyword, []).append(commit.hash)
                seen.add(keyword)
        self.authors.setdefault(commit.author, []).append(commit.hash)

    def by_keyword(self, keyword: str) -> list[str]:
        """단일 토큰은 직접 조회, 여러 토큰은 교집합 후보에서 구문을 검사한다."""
        tokens = keyword.lower().split()
        if not tokens:
            return []
        postings = [self.keywords.get(token, []) for token in tokens]
        if any(not posting for posting in postings):
            return []
        # 가장 작은 후보 목록에서 시작하여 전체 커밋을 순회하지 않는다.
        smallest = min(postings, key=len)
        other_sets = [set(posting) for posting in postings if posting is not smallest]
        return [
            commit_hash for commit_hash in smallest
            if all(commit_hash in posting for posting in other_sets)
        ]

    def by_author(self, author: str) -> list[str]:
        """작성자 이름의 대소문자를 유지한 완전 일치 검색."""
        return list(self.authors.get(author, []))
