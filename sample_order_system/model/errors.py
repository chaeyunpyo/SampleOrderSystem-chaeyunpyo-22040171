from __future__ import annotations


class DataIntegrityError(Exception):
    """data/ 아래 JSON 파일이 손상되었거나(JSON 문법 오류), 예상 구조와 다르거나
    (필드 누락, 타입 불일치), 값 자체가 파싱 불가능한 경우(잘못된 날짜/상태 문자열)
    발생한다. 리포지토리의 로드 경로에서 원본 예외를 이걸로 감싸 던져,
    호출부(main.py)가 한 곳에서 일관되게 사용자에게 안내할 수 있게 한다."""
