# di_dups65 — 의약품 정보 시스템

Django + MySQL 기반 의약품 정보 웹 사이트입니다.

## 주요 기능

1. **의약품 중복성분 보기** — 약품을 선택하여 중복 성분을 비교
2. **의약정보 보기** — 성분/회사/효능별 검색, 상세 정보 확인
3. **회원 기능** — 회원가입, 로그인, 로그아웃, 회원정보 수정
4. **게시판** — 게시글 작성/조회/수정/삭제
5. **About Us** — 의약품 중복 사용 검토 전문회사 소개

---

## 개발 환경 설정

### 1. 의존성 설치

```bash
pip install django mysqlclient python-dotenv
```

### 2. 데이터베이스 설정

#### SQLite (기본 — 로컬 개발용)

별도 설정 없이 바로 사용할 수 있습니다.

#### MySQL (운영 환경)

프로젝트 루트에 `.env` 파일을 만들고 아래 내용을 설정하세요:

```env
USE_MYSQL=True
DB_NAME=medsite
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=3306
SECRET_KEY=your-secret-key
```

MySQL에서 데이터베이스를 미리 생성해두어야 합니다:

```sql
CREATE DATABASE medsite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 마이그레이션

```bash
python manage.py migrate
```

### 4. 슈퍼유저 생성

```bash
python manage.py createsuperuser
```

### 5. 샘플 데이터 입력

```bash
python manage.py seed_data
```

### 6. 개발 서버 실행

```bash
python manage.py runserver
```

브라우저에서 <http://127.0.0.1:8000/> 으로 접속하세요.

---

## 프로젝트 구조

```
di_dups65/
├── medsite/          # 프로젝트 설정
├── medicines/        # 의약품 중복성분 / 의약정보 앱
├── accounts/         # 회원 기능 앱
├── board/            # 게시판 앱
├── templates/        # HTML 템플릿
└── manage.py
```

## 관리자 페이지

<http://127.0.0.1:8000/admin/> 에서 데이터를 직접 관리할 수 있습니다.
