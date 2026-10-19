# Mini Git

커밋 그래프, 브랜치, 탐색, 직접 구현한 정렬과 역색인을 학습하는 CLI 프로그램입니다.
과제 PDF의 필수 요구사항을 구현했습니다. **5번 보너스 과제(Diff, Merge 명령, 정렬 성능 비교)는 제외했습니다.**

## 실행

Python **3.10 이상**이면 실행할 수 있습니다. 외부 패키지 설치는 필요하지 않습니다.
프로젝트 폴더에서 다음 명령을 실행합니다.

```bash
python main.py
```

환경에 따라 `python` 대신 `python3`를 사용합니다.
과제의 개발 환경은 Python 3.10 이상입니다. 다만 macOS의 기본 `python3`가 Python 3.9를 가리키는 경우에도
실행할 수 있도록 타입 힌트의 평가를 지연했으며, Python 3.9.6에서도 실행을 확인했습니다.
버전은 `python3 --version`으로 확인할 수 있습니다. 설치된 Python 3.14를 직접 사용하려면 `python3.14 main.py`로 실행합니다.
`mini-git> ` 프롬프트에서 명령을 입력하고 `exit` 또는 `quit`으로 종료합니다.
EOF(Ctrl+D, Windows에서는 Ctrl+Z 후 Enter)와 Ctrl+C도 정상 종료합니다.
커밋 메타데이터는 메모리에만 저장되므로 프로그램 종료 시 사라집니다.

## 명령어

명령어 이름은 대소문자를 구분하지 않습니다. 공백을 포함하는 인자는 큰따옴표 또는 작은따옴표로 감쌉니다.
사용자명, 메시지, 브랜치명은 입력한 대소문자를 유지합니다. 옵션 이름과 값은 아래 표기를 사용합니다.

| 명령 | 동작 |
| --- | --- |
| `INIT <user_name>` | 저장소를 초기화하고 `main` 브랜치와 현재 작성자를 설정 |
| `BRANCH <branch_name>` | 현재 HEAD를 가리키는 새 브랜치 생성 |
| `SWITCH <branch_name>` | 현재 브랜치와 HEAD 전환 |
| `COMMIT <message>` | 현재 HEAD를 부모로 하는 커밋 생성 및 역색인 갱신 |
| `LOG` | **전체 브랜치**의 커밋을 부모가 자식보다 먼저 나오도록 출력 |
| `LOG --sort-by=date` | timestamp 기준 오름차순 출력 |
| `LOG --sort-by=author` | 작성자 이름 기준 사전순 오름차순 출력 |
| `PATH <commit1> <commit2>` | 부모 연결을 무방향 간선으로 보는 최단 경로 출력 |
| `ANCESTORS <commit_hash>` | 모든 조상을 중복 없이 출력. 자기 자신은 제외 |
| `SEARCH <keyword>` | 소문자로 정규화한 메시지 토큰 역색인 검색 |
| `SEARCH --author=<name>` | 작성자 이름 완전 일치 역색인 검색 |
| `exit` / `quit` | 프로그램 종료 |

빈 입력은 무시합니다. 명령의 인자 수가 틀리거나 따옴표가 닫히지 않으면 `Invalid args`를 출력하고 입력을 계속 받습니다.
브랜치 생성은 현재 브랜치를 바꾸지 않으며, 커밋 생성은 현재 브랜치의 끝만 이동시킵니다.
첫 커밋 이전에 브랜치를 만들 수도 있습니다. 각각 첫 커밋을 만들면 서로 연결되지 않은 루트들이 생길 수 있습니다.

`INIT`을 다시 실행하면 기존 커밋, 브랜치, 역색인을 지우고 지정한 작성자로 새 저장소를 시작합니다.
커밋 ID 카운터는 초기화하지 않으므로 같은 프로그램 세션에서 삭제된 커밋의 hash도 재사용하지 않습니다.
과제에서 증가 카운터를 허용하므로 hash는 `00000001`, `00000002`, …처럼 증가하는 16진수 식별자입니다.
작성자 변경 전용 명령은 과제에 없으므로 한 저장소의 CLI 커밋은 `INIT`에서 정한 작성자를 사용합니다.

## 실행 예시

아래는 새 프로그램 세션에서의 입력 순서입니다. 날짜는 실제 커밋 생성 시각입니다.

```text
mini-git> init "Alice Kim"
Initialized repository.
Current branch: main
Current user: Alice Kim
mini-git> commit "Initial commit"
[main 00000001] Initial commit
mini-git> branch feature
Created branch: feature
mini-git> switch feature
Switched to branch: feature
mini-git> commit "Add login feature"
[feature 00000002] Add login feature
mini-git> switch main
Switched to branch: main
mini-git> commit "Add payment feature"
[main 00000003] Add payment feature
mini-git> path 00000002 00000003
Path: 00000002 -> 00000001 -> 00000003
mini-git> search "login"
Found 1 commit:
commit 00000002 (Alice Kim, 2026-10-09T02:00:00.000000+00:00)
    Add login feature
mini-git> quit
Bye.
```

프로그램을 종료하기 전에 추가로 확인할 수 있는 명령입니다.

```text
LOG
LOG --sort-by=date
LOG --sort-by=author
ANCESTORS 00000003
SEARCH "login feature"
SEARCH --author="Alice Kim"
```

목록 출력에는 항상 hash, author, timestamp, message를 표시합니다. timestamp는 UTC이며 `+00:00`으로 시간대를 표시합니다.
`LOG`에는 예시의 세 커밋이 모두 나오며 `00000001`은 두 자식보다 먼저 나옵니다.
`ANCESTORS 00000003`의 조상은 `00000001`입니다. 형제 브랜치의 `00000002`는 조상이 아닙니다.

## 검색 규칙

메시지를 `lower().split()`으로 토큰화하여 **keyword → hash 목록**에 등록합니다.
한 메시지에 같은 토큰이 여러 번 있어도 해당 hash는 한 번만 등록합니다.
**author → hash 목록**도 별도로 유지합니다.

- `SEARCH LOGIN`은 `login` 토큰을 찾습니다. `log`는 `login`에 일치하지 않습니다.
- 최소 토큰화 기준을 그대로 적용하므로 `login,`과 `login`은 서로 다른 토큰입니다.
- `SEARCH "login feature"`처럼 공백이 있으면 연속된 토큰 구문을 검색합니다. 관련 토큰들의 역색인 교집합으로 후보를 좁힌 후, 후보 메시지만 검사합니다.
- 구문 검색은 대소문자와 토큰 사이 공백 개수를 무시합니다. `login new feature`는 `"login feature"`에 일치하지 않습니다.
- `SEARCH --author="Alice Kim"`은 작성자 이름 전체의 대소문자까지 일치해야 합니다.
- 검색 결과는 커밋 생성 순서이며 결과가 없으면 `Found 0 commits:`를 출력합니다.

## 구조

```text
main.py                    실행 진입점
mini_git/
    __init__.py            공개 클래스
    models.py              불변 Commit 노드
    repository.py          커밋/브랜치/HEAD 상태와 명령 기능
    algorithms.py          병합 정렬, 위상 정렬, BFS 최단 경로, DFS 조상 탐색
    index.py               메시지 토큰 및 작성자 역색인
    cli.py                 따옴표 파싱, 오류 처리, 결과 출력, REPL
```

## 핵심 자료구조와 알고리즘

`Commit`은 `hash`, `message`, `author`, `timestamp`, `parents`를 갖는 변경 불가능한 노드입니다.
`parents`는 튜플이므로 0개 이상의 부모를 표현할 수 있습니다. 필수 `COMMIT` 명령은 부모를 0개 또는 1개 생성하지만,
위상 정렬과 조상 탐색은 여러 부모를 갖는 일반 DAG도 처리하도록 구현했습니다.

커밋은 `dict[hash, Commit]`, 브랜치는 `dict[branch_name, hash 또는 None]`으로 저장합니다.
HEAD는 현재 브랜치가 가리키는 커밋으로 계산합니다. 별도로 저장하지 않아 브랜치와 HEAD의 값이 어긋나지 않습니다.
`adjacency`는 PATH용 양방향 인접 리스트이고, 원본 커밋의 `parents`는 방향성을 그대로 유지합니다.

### DAG와 기본 LOG

방향 간선은 자식에서 부모로 향합니다. 새 커밋은 이미 존재하는 HEAD만 부모로 삼고 기존 커밋을 수정하지 않습니다.
따라서 부모를 따라갈수록 먼저 생성된 커밋으로 이동하며 자기 자신으로 돌아오는 순환이 생기지 않습니다.
브랜치는 커밋을 가리키는 포인터이므로 브랜치 생성/전환도 그래프에 순환을 만들지 않습니다.

기본 LOG는 **Kahn 위상 정렬**을 사용합니다. 출력 목적에서는 부모 → 자식 관계를 구성하고,
각 노드의 아직 출력되지 않은 부모 수를 계산합니다. 부모가 없는 노드를 큐에서 출력한 뒤 자식의 부모 수를 줄입니다.
그 수가 0이 된 자식만 큐에 넣으므로 모든 부모가 자식보다 먼저 나옵니다.
여러 노드가 준비되면 딕셔너리의 삽입 순서와 FIFO 큐 순서를 사용합니다.
옵션 LOG는 지정된 key 자체로 정렬하며 기본 LOG의 위상 순서를 강제하지 않습니다.

### PATH와 ANCESTORS

PATH는 도착점에서 **BFS**하여 최소 간선 수를 계산합니다. 시작점이 방문되지 않았으면 `No path`입니다.
이후 시작점부터 거리가 1씩 감소하는 이웃 중 사전순 최소 hash를 선택합니다.
같은 길이의 경로는 첫 번째로 다른 hash에서 사전순이 결정되므로,
`hash1->hash2->...` 문자열이 최소인 최단 경로를 얻습니다. 같은 커밋끼리의 경로는 해당 hash 하나입니다.

ANCESTORS는 스택을 사용하는 **반복형 DFS**입니다. 모든 부모를 따라가고 방문 집합으로 중복을 제거합니다.
공통 조상이 있더라도 한 번만 출력합니다. 재귀를 사용하지 않아 긴 이력에서도 재귀 깊이 제한을 피합니다.
루트 커밋은 `No ancestors`를 출력합니다.

### 직접 구현한 정렬

`merge_sort`는 너비 1, 2, 4, …의 구간을 합치는 반복형 **병합 정렬**입니다.
날짜와 작성자 등 비교 기준은 `key` 함수로 전달합니다. key는 원소당 한 번 계산합니다.
평균/최악 시간복잡도는 모두 **O(n log n)**, 보조 공간은 **O(n)**입니다.
동률일 때 왼쪽 구간의 원소를 먼저 선택하여 **안정 정렬**을 보장합니다.
LOG의 정렬 옵션에서 날짜/작성자가 같으면 커밋 생성 순서를 유지합니다.
Python의 `sorted()`, `list.sort()`와 정렬 관련 라이브러리는 사용하지 않습니다.

### 역색인과 시간복잡도

V는 커밋 수, E는 부모 간선 수, k는 검색 결과 수입니다. 딕셔너리/집합 조회는 평균 O(1)을 기준으로 합니다.

| 기능 | 시간복잡도 | 추가 공간 |
| --- | --- | --- |
| hash로 커밋 조회 / 브랜치 생성·전환 | 평균 O(1) | O(1) |
| 커밋 생성과 색인 갱신 | 메시지 길이 L 기준 O(L) | O(L) 이내 |
| 기본 LOG (위상 정렬) | O(V+E) | O(V+E) |
| 정렬 LOG (병합 정렬) | O(V log V) | O(V) |
| PATH (BFS + 경로 복원) | O(V+E) | O(V) |
| ANCESTORS (반복 DFS) | 방문한 조상 및 간선에 비례 | 방문한 조상 및 간선에 비례 |
| 단일 토큰/작성자 검색 | 질의 처리 + O(k) | O(k) |

전체 순회 검색은 결과가 없어도 V개 커밋을 모두 확인합니다.
역색인은 키로 hash 목록을 바로 얻으므로 단일 토큰/작성자 검색은 결과에 해당하는 커밋만 조회합니다.
공백 포함 구문 검색은 각 토큰의 후보 목록과 교집합 후보 메시지를 처리합니다. 후보가 모든 커밋이라면 모두 검사할 수 있지만,
관련 없는 커밋 전체를 무조건 순회하지 않습니다.

## 오류 처리

| 상황 | 출력 |
| --- | --- |
| 인자 수/옵션/따옴표 오류, 빈 문자열 | `Invalid args` |
| INIT 이전 저장소 명령 | `Repository not initialized` |
| 존재하지 않는 브랜치 | `Unknown branch: <name>` |
| 존재하지 않는 커밋 | `Unknown commit: <hash>` |
| 이미 존재하는 브랜치 생성 | `Branch already exists: <name>` |
| 지원하지 않는 명령 | `Unknown command: <COMMAND>` |

## 직접 기능 확인

`python3 main.py`로 시작하여 위 실행 예시의 브랜치 분기까지 입력한 뒤,
종료 전에 아래 명령의 결과를 확인합니다. 별도의 검사 코드를 작성할 필요는 없습니다.

| 명령 | 확인할 결과 |
| --- | --- |
| `LOG` | 세 커밋이 모두 나오고 `00000001`이 두 자식보다 먼저 출력됨 |
| `PATH 00000002 00000003` | `00000002 -> 00000001 -> 00000003` |
| `ANCESTORS 00000003` | `00000001`만 출력됨 |
| `SEARCH LOGIN` | 로그인 커밋 한 개가 나옴 |
| `SEARCH --author="Alice Kim"` | 세 커밋이 모두 나옴 |
| `LOG --sort-by=date` / `LOG --sort-by=author` | 해당 기준의 오름차순이며 동률이면 생성 순서를 유지함 |
| `SWITCH missing` | `Unknown branch: missing` 후 다음 입력을 받음 |
| `QUIT` | 정상 종료하며, 다시 실행하면 빈 저장소에서 시작함 |

위 hash는 새 프로그램 세션에서 예시를 순서대로 입력했을 때의 값입니다.
연결되지 않은 두 커밋의 PATH는 `No path`, 존재하지 않는 hash는 `Unknown commit: <hash>`입니다.

파일 내용 추적과 네트워크 통신은 없으며, 저장소의 디스크 영속성도 구현하지 않습니다.
