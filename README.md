# 임베디드 소프트웨어 경진대회 2024

카메라 모듈과 모션 제어를 통합한 파3, 파4에 대한 알고리즘을 제공합니다. 

파3, 파4에서 카메라 및 로봇 동작을 수행하여 완벽한 골프 로직을 수행합니다.

## 프로젝트 구조
```
├── MODULES/
│   ├── Camera/
│   │   ├── calculate.py
│   │   └── camera.py
│   └── Motion/
│       └── robot.py
├── stage/
│   ├── par3.py
│   └── par4.py
├── main.py
├── serialTest.py
└── README.md
```

## 주요 구성 요소

### Camera 모듈
- `calculate.py`: 카메라 관련 계산 로직 구현
- `camera.py`: 카메라 제어 및 기본 기능 구현

### Motion 모듈
- `robot.py`: 로봇 동작 제어 및 관련 기능 구현

### 테스트 환경
- `stage/par3.py`: 파3 테스트 환경 구성
- `stage/par4.py`: 파4 테스트 환경 구성

### 기타 파일
- `main.py`: 프로그램 메인 실행 파일
- `serialTest.py`: 시리얼 통신 스크립트

## 설치 및 실행

1. 의존성 설치
```bash
$ pip install -r requirements.txt
```

2. 프로그램 실행
```bash
$ python main.py
```