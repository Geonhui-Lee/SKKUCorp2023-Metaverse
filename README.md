# SKKUCorp2023_Metaverse

2023학년도 성균관대학교 소프트웨어융합대학 산학협력프로젝트 웅진씽크빅 메타버스 프로젝트의 백엔드 애플리케이션입니다.

## 폴더 구조
- mv_backend: 핵심 백엔드 애플리케이션 (Django)
- mv_backend_cefr: 어휘 기반 CEFR 레벨 평가용 백엔드 애플리케이션 (NestJS)

## mv_backend 실행방법
1. 코어 백엔드 애플리케이션은 Django 기반으로 개발되어 있어 Pip (파이썬 패키지 매니저) 및 Django를 셋업해야 합니다.
  - pip 셋업: https://pip.pypa.io/
  - venv (가상화된 파이썬 환경) 셋업: https://docs.python.org/3/tutorial/venv.html
  - Django Documentation: https://docs.djangoproject.com/en/5.0/topics/install/#installing-official-release

2. Django 기반 백엔드 애플리케이션에 포함된 파이썬 모듈을 설치합니다.
````
cd mv_backend
pip install -r requirements.txt
````

3. [초기 설정] 코어 백엔드 애플리케이션은 OpenAI API Key, MongoDB 데이터베이스 등 외부적인 요소도 활용하므로 환경변수 설정을 해야 합니다. mv_backend 내에 환경변수 탬플릿 파일(`.env.template`)을 복사하여 환경변수 파일을 생성한 뒤 (`.env`), 아래와 같이 수정합니다.
````
OPENAI_API_KEY=(OPENAI API 키 입력)
MONGODB_CONNECTION_STRING=mongodb+srv://(MongoDB 연결 스트링 입력 )
````
  
4. 아래와 같은 명령어로 백엔드 애플리케이션을 실행할 수 있습니다.
````
python manage.py runserver
````

## mv_backend 내부구조
- `api`: 프론트엔드/백엔드 간 통신을 위한 코드가 포함되어 있습니다.
  - `load.py`: 각 프로세스 함수가 정의된 요청 디렉토리를 한 곳에 관리하는 곳입니다.
  - `function/***`: 백엔드 애플리케이션 내 핵심 기능이 구현된 함수가 포함된 곳입니다. 
- `lib`: Database, CommonChatOpenAI 등 공통적으로 사용되는 설정 및 클래시가 포함되어 있습니다.

## mv_backend_cefr 실행방법
1. CEFR 레벨 평가용 백엔드 애플리케이션은 NestJS 기반으로 개발되어 있어 Node.js 및 NestJS을 셋업해야 합니다.
  - Node.js 설치: https://nodejs.org/en (LTS 버전 설치)
  - NestJS: Node.js 설치 후 NestJS 초기 설정 페이지 참고 (https://docs.nestjs.com/)
    - 참고: Node.js가 이미 설치되어 있는 경우 `npm i -g @nestjs/cli`를 터미널 상 입력하여 바로 NestJS를 설치할 수 있습니다.
2. [초기 설정] 아래와 같은 명령어로 백엔드 애플리케이션 실행을 위한 자바/타입스크립트 모듈을 설치합니다. 
````
cd mv_backend_cefr
npm install
````
3. 아래와 같은 명령어로 백엔드 애플리케이션을 실행할 수 있습니다.
````
npm run start
````
