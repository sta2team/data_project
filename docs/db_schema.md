# 📊 DB 스키마

## ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    행정동 ||--o{ 매출 : has
    행정동 ||--o{ 상주인구 : has
    행정동 ||--o{ 유동인구 : has
    행정동 ||--o{ 집객시설 : has
    행정동 ||--o{ 상권변화지표 : has
    행정동 ||--o{ 카페 : has
    행정동 ||--|| xy : generates

    매출 {
        string 기준_년분기_코드 PK
        int 행정동_코드 FK
        string 행정동_코드_명 "표시용"
        string 서비스_업종_코드_명
        float 당월_매출_금액
        float 주중_매출_금액
        float 주말_매출_금액
        float 연령대_10_매출_금액
        float 연령대_20_매출_금액
        float 연령대_30_매출_금액
    }

    면적 {
        string 행정동_코드 PK
        string 행정동_코드_명"표시용"
        float 엑스좌표_값
        float 와이좌표_값
        float 영역_면적
    }

    상주인구 {
        string 기준_년분기_코드 PK
        int 행정동_코드 FK
        string 행정동_코드_명 "표시용"
        int 총_상주인구_수
        int 연령대_10_상주인구_수
        int 연령대_20_상주인구_수
        int 연령대_30_상주인구_수
        int 총_가구_수
    }

    유동인구 {
        string 기준_년분기_코드 PK
        int 행정동_코드 FK
        string 행정동_코드_명 "표시용"
        int 총_유동인구_수
        int 연령대_10_유동인구_수
        int 연령대_20_유동인구_수
        int 연령대_30_유동인구_수
    }

    집객시설 {
        string 기준_년분기_코드 PK
        int 행정동_코드 FK
        string 행정동_코드_명 "표시용"
        int 집객시설_수
        int 지하철_역_수
        int 버스_정거장_수
    }

    상권변화지표 {
        string 기준_년분기_코드 PK
        int 행정동_코드 FK
        string 행정동_코드_명 "표시용"
        string 상권_변화_지표
        float 운영_영업_개월_평균
        float 폐업_영업_개월_평균
    }

    카페 {
        string 기준_년분기_코드 PK
        string 행정동_코드 FK
        string 행정동_코드_명 "표시용"
        int 점포_수
        float 개업_율
        float 폐업_률
    }

    %% 원본 CSV: 피벗 형태 (행=지표, 열=행정동)
    블로그 {
        string district PK "행정동명"
        string 키워드
        int 월_검색량
        int 전체_게시글
        int 월_발행량
        int 상위_블로그_방문자
    }

    %% 원본 CSV: 피벗 형태 (행=날짜, 열=행정동)
    네이버트렌드 {
        date 날짜 PK
        string district PK "행정동명"
        float 검색비율
    }

    %% 원본 CSV: 피벗 형태 (행=날짜, 열=행정동)
    키워드검색량 {
        date 날짜 PK
        string district PK "행정동명"
        int 검색량
    }

    유튜브 {
        string id PK
        string district FK
        string title
        date publishedAt
        int viewCount
        int likeCount
        int commentCount
    }

    xy {
        string 행정동 PK
        int search_23
        int search_24
        int search_25
        float CAGR
        float avg_naver
        int blog_post
        float 하이브리드_점수
    }
```

---

## 테이블 상세

### 서울 열린데이터광장 (상권 데이터)

| 테이블           | 파일명           | 주요 컬럼                                      | 설명                           |
| ---------------- | ---------------- | ---------------------------------------------- | ------------------------------ |
| **매출**         | 매출\_[년도].csv | 행정동\_코드, 당월\_매출\_금액, 연령대별\_매출 | 분기별 매출 데이터 (53개 컬럼) |
| **면적**         | 면적.csv         | 행정동\_코드, 영역\_면적, 좌표                 | 행정동 기본 정보               |
| **상권변화지표** | 상권변화지표.csv | 행정동\_코드, 운영\_영업\_개월\_평균           | 상권 활성화 지표               |
| **상주인구**     | 상주인구.csv     | 행정동\_코드, 총\_상주인구\_수, 연령대별       | 거주 인구                      |
| **유동인구**     | 유동인구.csv     | 행정동\_코드, 총\_유동인구\_수, 연령대별       | 방문 인구                      |
| **집객시설**     | 집객시설.csv     | 행정동\_코드, 집객시설\_수, 지하철\_역\_수     | 시설 인프라                    |
| **카페**         | 카페.csv         | 행정동\_코드, 점포\_수, 개업\_율, 폐업\_률     | 카페 업종 현황                 |

### 외부 데이터 (트렌드)

| 테이블           | 파일명                | 주요 컬럼                        | 설명             |
| ---------------- | --------------------- | -------------------------------- | ---------------- |
| **블로그**       | blog.csv              | district, 행정동별 게시글 수     | 판다랭크         |
| **네이버트렌드** | naver_trend.csv       | 날짜, 행정동별 검색비율          | 네이버 데이터랩  |
| **키워드검색량** | keyword_search_3y.csv | 날짜, 행정동별 검색량            | 판다랭크 (3년치) |
| **유튜브**       | youtube_data.csv      | district, viewCount, publishedAt | YouTube API      |

### 분석 결과

| 테이블       | 파일명 | 주요 컬럼                                 | 설명           |
| ------------ | ------ | ----------------------------------------- | -------------- |
| **분석결과** | xy.csv | 행정동, CAGR, avg_naver, 하이브리드\_점수 | 최종 분석 결과 |

---

## 키 관계

| 관계                  | 설명                              |
| --------------------- | --------------------------------- |
| `행정동_코드`         | 서울 열린데이터 테이블 간 조인 키 |
| `기준_년분기_코드`    | 시계열 데이터 조인 키 (예: 20241) |
| `district` / `행정동` | 외부 데이터와 연결 키             |

---

## 데이터 흐름

```mermaid
graph LR
    subgraph Source [원천 데이터]
        A["서울 열린데이터광장<br/>(매출/유동/상주/집객/카페)"]
        B["판다랭크<br/>(키워드/블로그)"]
        C["네이버 데이터랩<br/>(검색 트렌드)"]
        D["YouTube API<br/>(영상 데이터)"]
    end

    subgraph Process [전처리 및 분석]
        P1[hybrid.ipynb]
        CSV[xy.csv]
        P2[quad.ipynb]
    end

    subgraph Result [분석 결과]
        R1([하이브리드 점수])
        R2([사분면 분류])
    end

    A & B & C & D --> P1
    P1 --> R1
    P1 --> CSV
    CSV --> P2
    P2 --> R2

    %% 스타일 설정 (선택 사항)
    style Source fill:#f9f9f9,stroke:#333
    style Result fill:#e1f5fe,stroke:#01579b
```
