# SKKUCorp2023_Metaverse

2023학년도 성균관대학교 소프트웨어융합대학 산학협력프로젝트 웅진씽크빅 메타버스 프로젝트의 백엔드 애플리케이션입니다.

## 데모 영상

- A1 level (GPT 3.5 Turbo)

## [![Video Label](http://img.youtube.com/vi/G8IFECU7Q6k/0.jpg)](https://youtu.be/G8IFECU7Q6k?si=9RODhlfOSECArWhE)

- A1 level (GPT 4)

## [![Video Label](http://img.youtube.com/vi/KTXqJFn-iWE/0.jpg)](https://youtu.be/KTXqJFn-iWE?si=6-3DD1L4wRXTHyVy)

- Customizing NPC

[![Video Label](http://img.youtube.com/vi/K7FkbBDxkEM/0.jpg)](https://youtu.be/K7FkbBDxkEM?si=BlLAKwhonpZFR2PH)

## 폴더 구조

- mv_backend: 핵심 백엔드 애플리케이션 (Django)
- mv_backend_cefr: 어휘 기반 CEFR 레벨 평가용 백엔드 애플리케이션 (NestJS)

## mv_backend 실행방법

1. 코어 백엔드 애플리케이션은 Django 기반으로 개발되어 있어 Pip (파이썬 패키지 매니저) 및 Django를 셋업해야 합니다.

- pip 셋업: https://pip.pypa.io/
- venv (가상화된 파이썬 환경) 셋업: https://docs.python.org/3/tutorial/venv.html
- Django Documentation: https://docs.djangoproject.com/en/5.0/topics/install/#installing-official-release

2. Django 기반 백엔드 애플리케이션에 포함된 파이썬 모듈을 설치합니다.

```
cd mv_backend
pip install -r requirements.txt
```

3. [초기 설정] 코어 백엔드 애플리케이션은 OpenAI API Key, MongoDB 데이터베이스 등 외부적인 요소도 활용하므로 환경변수 설정을 해야 합니다. mv_backend 내에 환경변수 탬플릿 파일(`.env.template`)을 복사하여 환경변수 파일을 생성한 뒤 (`.env`), 아래와 같이 수정합니다.

```
OPENAI_API_KEY=(OPENAI API 키 입력)
MONGODB_CONNECTION_STRING=mongodb+srv://(MongoDB 연결 스트링 입력 )
```

4. 아래와 같은 명령어로 백엔드 애플리케이션을 실행할 수 있습니다.

```
python manage.py runserver
```

## mv_backend/mv_backend 내부구조

- `api`: 프론트엔드/백엔드 간 통신을 위한 코드가 포함되어 있습니다.
  - `load.py`: 각 프로세스 함수가 정의된 요청 디렉토리를 한 곳에 관리하는 곳입니다.
  - `function/***`: 백엔드 애플리케이션 내 핵심 기능이 구현된 함수가 포함된 곳입니다.
    - `cefr_simplified.py`: 활용 어휘를 기반으로 CEFR 점수가 계산되는 기능
    - `cefr.py`: GPT를 통해 CEFR 점수가 산출되는 기능
    - `change_model.py`: CommonChatOpenAI의 모델을 변경하는 기능
    - `chat.py`: user 정보를 기반으로 NPC가 맞춤형 대화하는 기능
    - `current.py`: 현재 retrieve, reflect, cefr 결과를 가져오는 기능
    - `custom_persona.py`: wikipedia 정보를 통해 NPC persona를 생성하는 기능
    - `fix_json_format.py`: quiz가 잘못된 json 형식이면 수정하는 기능
    - `profile.py`: 지금까지의 interest, conversation style, retrieve, cefr 결과를 가져오는 기능
    - `quiz_generator.py`: user 정보를 기반으로 퀴즈 생성하는 기능
    - `reflect.py`: reflect(user 특성 찾기) 기능
    - `retrieve.py`: retrieve(user 미진 사항 찾기) 기능
    - `session_end.py`: 대화 세션이 종료되면 대화 내용에 대해 retrieve, reflect, cefr 단계를 수행하는 기능
- `lib`: Database, CommonChatOpenAI 등 공통적으로 사용되는 설정 및 클래시가 포함되어 있습니다.
  - `common.py`: CommonChatOpenAI의 모델
  - `database.py`: database class 정의 (API 문서 - mv_backend.lib.database)
- `settings.py`: Django 환경 설정 파일
- `urls.py`: URL 구성 관련 파일

## 프론트엔드(유니티) 실행방법

1. Unity Hub 다운로드

- Unity 프로젝트를 실행할 수 있는 Unity Hub를 다운로드합니다(https://unity.com/kr/download)

2. Unity 에디터 다운로드

- 저희 프로젝트는 Unity 2022.3.9f1으로 개발됐습니다. 해당 버전의 유니티 에디터를 다운해줍니다.(https://unity.com/releases/editor/whats-new/2022.3.9)

3. 빈 프로젝트 생성 및 패키지 불러오기

- Unity Hub로 빈 3D 프로젝트를 하나 생성합니다.
- 첨부된 unitypackage 파일을 실행하고, 모두 import 합니다(https://drive.google.com/file/d/1_UTHz_s-KAknqiW6L9XNl1x3PIJNhLXD/view?usp=sharing).

4. 프로그램 실행

- 상단의 실행 버튼을 누르고, Game 화면을 한번 클릭하면 프로그램을 플레이 가능합니다.

### 유니티 조작법

- `WASD`: 움직임
- `Shift + WASD`: 달리기
- `Mouse Left Click`: UI를 마우스 왼쪽 클릭 시, 키고 끄기 가능

## mv_backend_cefr 실행방법

1. CEFR 레벨 평가용 백엔드 애플리케이션은 NestJS 기반으로 개발되어 있어 Node.js 및 NestJS을 셋업해야 합니다.

- Node.js 설치: https://nodejs.org/en (LTS 버전 설치)
- NestJS: Node.js 설치 후 NestJS 초기 설정 페이지 참고 (https://docs.nestjs.com/)
  - 참고: Node.js가 이미 설치되어 있는 경우 `npm i -g @nestjs/cli`를 터미널 상 입력하여 바로 NestJS를 설치할 수 있습니다.

2. [초기 설정] 아래와 같은 명령어로 백엔드 애플리케이션 실행을 위한 자바/타입스크립트 모듈을 설치합니다.

```
cd mv_backend_cefr
npm install
```

3. 아래와 같은 명령어로 백엔드 애플리케이션을 실행할 수 있습니다.

```
npm run start
```

## [API 문서](https://dotgeon-kingo.notion.site/eb449a2cf045442d85a3cf3c65c75e7c?v=a945cf7ef8d940e7aa20a35fe26c23d4)
