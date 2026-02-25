# 프로젝트 구조

이 문서는 Wavoscope 저장소의 디렉토리 구조와 각 구성 요소의 목적을 설명합니다.

## 디렉토리 개요

-   **`audio/`**: 핵심 오디오 엔진을 포함합니다.
    -   `audio_backend.py`: 메인 오디오 백엔드 퍼사드(facade).
    -   `chord_analyzer.py`: 코드 플래그를 위한 크로마(Chroma) 기반 코드 감지.
    -   `ringbuffer.py`: 오디오 스트리밍을 위한 스레드 안전 링 버퍼.
    -   `spectrum_analyzer.py`: FFT 및 스펙트럼 데이터 계산 로직.
    -   `synth.py`: 메트로놈 클릭 및 코드 들어보기를 위한 실시간 합성.
    -   `waveform_cache.py`: 효율적인 표시를 위한 파형 데이터 생성 및 캐싱 관리.
    -   **`engine/`**: 저수준 오디오 처리 구성 요소.
        -   `playback.py`: 핵심 재생 로직 및 스트림 관리.
        -   `processing.py`: 오디오 스트레칭(TSM) 및 버퍼 관리.
        -   `metronome.py`: 메트로놈 클릭 타이밍 및 생성.
        -   `filters.py`: 실시간 바이쿼드(biquad) 필터링(대역 통과).
-   **`backend/`**: 현대적인 FastAPI 기반 웹 백엔드.
    -   `main.py`: FastAPI 서버의 진입점으로, API 엔드포인트 및 프론트엔드 자산을 제공합니다.
    -   `state.py`: 공유 글로벌 상태(활성화된 `Project` 인스턴스).
    -   `routers/`: 오디오, 재생, 프로젝트 등 다양한 API 도메인을 위한 모듈형 FastAPI 라우터.
-   **`cli/`**: 명령줄 인터페이스 유틸리티를 포함합니다.
    -   `flag_cli.py`: 터미널을 통해 플래그를 관리하기 위한 유틸리티.
-   **`config/`**: 애플리케이션의 설정 파일 및 기본 설정.
-   **`docs/`**: 작업 로드맵 및 구조 가이드를 포함한 프로젝트 문서.
-   **`frontend/`**: React 기반 그래픽 사용자 인터페이스.
    -   `src/components/`: React 구성 요소(Waveform, Spectrum, Timeline, PlaybackBar).
    -   `src/store/`: 프론트엔드 상태 관리(Zustand).
    -   `dist/`: 빌드된 프로덕션 자산.
-   **`resources/`**: 아이콘(SVG), 테마(JSON) 및 애플리케이션 리소스와 같은 정적 자산.
-   **`scripts/`**: 자동화 및 유틸리티 스크립트(예: 스크린샷 생성).
-   **`session/`**: 프로젝트 지속성 및 고수준 상태를 처리합니다.
    -   `project.py`: 오디오, 메타데이터(플래그) 및 캐싱을 하나로 묶는 `Project` 클래스.
    -   `manager.py`: `.oscope` 사이드카 파일 I/O 및 스크러빙(scrubbing)을 처리합니다.
    -   `flags.py`: 리듬 및 코드 플래그 리스트를 관리합니다.
    -   `looping.py`: 다양한 루프 모드(전체, 섹션, 마커, 가사)의 로직.
    -   `export.py`: MusicXML 내보내기 생성.
    -   `chord_utils.py`: 코드 이름 파싱 및 검증을 위한 헬퍼.
-   **`utils/`**: 일반적인 헬퍼 함수 및 공유 유틸리티.

## 루트 파일

-   **`run.sh` / `run.bat`**: 환경을 설정하고 애플리케이션을 실행하는 스크립트.
-   **`main.py`**: 애플리케이션의 진입점. 이제 FastAPI + pywebview를 실행합니다.
-   **`AGENTS.md`**: 프로젝트에서 작업하는 AI 에이전트를 위한 지침 및 로드맵.
-   **`Readme.md`**: 일반적인 프로젝트 개요 및 설정 지침.
-   **`LICENSE`**: 프로젝트의 MIT 라이선스 약관.
-   **`SECURITY.md`**: 보안 취약점 보고를 위한 정책.
-   **`requirements.txt`**: Python 의존성.
