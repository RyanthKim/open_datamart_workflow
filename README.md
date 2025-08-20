# open_datamart_workflow

> ⚠️ **이 프로젝트는 포트폴리오 목적으로 원본 프로젝트를 복제하여 만든 예시입니다. 실제 운영 환경에서는 사용하지 마세요.**

## 소개
이 프로젝트는 Google Spreadsheet, Redash, Redshift, 형태소 분석(Komoran)을 활용하여 문서 및 템플릿의 카테고리 자동 분류 및 데이터 동기화를 자동화하는 워크플로우입니다.

## 폴더 구조
- `main.py`: 전체 워크플로우 실행 스크립트
- `workflow_list.py`: 쿼리, 시트, 카테고리 관련 설정
- `resource/`: 사용자 정의 함수, 형태소 사전, 카테고리 매핑 JSON, requirements.txt 등 리소스 파일
- `resource/custom_functions.py`: DB, Redash, 형태소 분석 등 주요 기능 구현

## 설치 방법
1. Python 3.10 이상 설치
2. 필요한 패키지 설치:
    ```sh
    pip install -r resource/requirements.txt
    ```
3. Google Spreadsheet API 인증 파일(`resource/project-gsheet-input-cf916fb9860d.json`) 준비

## 사용법
1. `main.py`를 실행하면 아래 작업이 자동으로 수행됩니다.
    - Google Spreadsheet에서 데이터 읽어 Redshift 테이블 갱신
    - Redash 쿼리 실행 및 결과 반영
    - 문서/템플릿 타이틀 형태소 분석 및 카테고리 분류 후 DB 저장
    - Slack 알림 전송

    ```sh
    python main.py
    ```

## 주요 기능
- Google Spreadsheet ↔ Redshift 데이터 동기화
- Redash 쿼리 자동 실행
- Komoran 기반 형태소 분석 및 사용자 사전 적용
- 문서/템플릿 타이틀 카테고리 자동 분류
- Slack 알림 연동

## 환경 변수 및 설정
- DB, Redash, Slack 등 주요 정보는 `resource/custom_functions.py`에서 설정

## 참고
- 형태소 사전 및 카테고리 매핑은 `resource/documentCategoryJson/`, `resource/formCategoryJson/` 폴더 참고

---
문의: 담당자에게 연락