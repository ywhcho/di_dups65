# di_dups65 — 동일성분 찾기 (equiv_ingr) 설정 가이드

## 1. Python 패키지 설치

```bash
pip install -r requirements.txt
```

## 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 만들어 아래 내용을 입력하세요.

```
DJANGO_SECRET_KEY=your-secret-key-here
DB_NAME=di_dups65
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
```

## 3. 데이터베이스 스키마

### 3-1. med_interaction_mfname 테이블에 필드 추가

기존 테이블에 다음 3개 컬럼을 추가합니다.

```sql
ALTER TABLE med_interaction_mfname
  ADD COLUMN ingrnd_t  VARCHAR(255) NOT NULL DEFAULT '' COMMENT '영문성분명',
  ADD COLUMN kingrnd_t VARCHAR(255) NOT NULL DEFAULT '' COMMENT '한글성분명',
  ADD COLUMN cfno      VARCHAR(20)  NOT NULL DEFAULT '' COMMENT '효능분류번호';
```

기존 테이블 구조 (변경 전):
| 컬럼   | 타입        | 설명          |
|--------|-------------|---------------|
| id     | INT PK AUTO | 기본키        |
| wfco   | VARCHAR(20) | 활성성분코드  |
| fname  | VARCHAR(255)| 성분명        |
| igrno1 | VARCHAR(20) | 상호작용번호1 |
| igrno2 | VARCHAR(20) | 상호작용번호2 |
| igrno3 | VARCHAR(20) | 상호작용번호3 |
| igrno4 | VARCHAR(20) | 상호작용번호4 |

추가 후:
| 컬럼      | 타입        | 설명          |
|-----------|-------------|---------------|
| ingrnd_t  | VARCHAR(255)| 영문성분명    |
| kingrnd_t | VARCHAR(255)| 한글성분명    |
| cfno      | VARCHAR(20) | 효능분류번호  |

검색 성능을 위해 인덱스를 추가합니다.

```sql
CREATE INDEX idx_mfname_wfco     ON med_interaction_mfname (wfco);
CREATE INDEX idx_mfname_ingrnd   ON med_interaction_mfname (ingrnd_t(50));
CREATE INDEX idx_mfname_kingrnd  ON med_interaction_mfname (kingrnd_t(50));
CREATE INDEX idx_mfname_cfno     ON med_interaction_mfname (cfno);
```

### 3-2. medicines_medicine 테이블에 필드 추가

기존 테이블에 다음 3개 컬럼을 추가합니다.

```sql
ALTER TABLE medicines_medicine
  ADD COLUMN cfno   VARCHAR(20)  NOT NULL DEFAULT '' COMMENT '효능분류',
  ADD COLUMN deriv2 VARCHAR(100) NOT NULL DEFAULT '' COMMENT '성분계열',
  ADD COLUMN ypri24 VARCHAR(50)  NOT NULL DEFAULT '' COMMENT '연생산실적';
```

기존 테이블 구조 (변경 전):
| 컬럼    | 타입        | 설명         |
|---------|-------------|--------------|
| id      | INT PK AUTO | 기본키       |
| wfco    | VARCHAR(20) | 활성성분코드 |
| htname  | VARCHAR(255)| 제품명       |
| ingred  | VARCHAR(255)| 성분         |
| company | VARCHAR(255)| 회사         |

검색 성능을 위해 인덱스를 추가합니다.

```sql
CREATE INDEX idx_medicine_wfco ON medicines_medicine (wfco);
```

## 4. Django 초기화

```bash
# 마이그레이션 (Django 기본 테이블용 — managed=False 모델은 제외)
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser

# 개발 서버 실행
python manage.py runserver
```

## 5. 사용법

브라우저에서 `http://localhost:8000/` 접속 후:

1. **검색 폼**: 검색 유형(wfco / 영문성분명 / 한글성분명 / 효능분류번호)을 선택하고 검색어 입력 → 검색
2. **Table 1**: 검색 결과 표시. 행을 클릭하면 해당 wfco의 **앞 6자리**로 Table 2 생성.
3. **Table 2**: wfco 앞 6자리가 같은 동일성분 목록. 행을 클릭하면 **wfco 전체**로 Table 3 생성.
4. **Table 3**: `medicines_medicine`에서 해당 wfco와 일치하는 의약품 목록.

모든 테이블은 10건을 초과하면 페이지네이션이 활성화됩니다.
