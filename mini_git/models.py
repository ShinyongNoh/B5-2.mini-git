"""커밋 그래프의 노드 정의."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Commit:
    """생성 후 변경되지 않는 커밋. parents는 여러 부모를 표현할 수 있다."""

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: tuple[str, ...] = ()
