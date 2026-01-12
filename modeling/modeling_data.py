# %% [markdown]
# # DB 업로드(.csv 파일 만들기)

# %%
import os

# 1. 경로 정의 (r 붙이는 거 잊지 마세요!)
data_path = r"C:\Users\Julia\Downloads\sales_data"

# 2. 실제로 그 폴더가 존재하는지 확인
if os.path.exists(data_path):
    print(f"✅ 폴더를 찾았습니다: {data_path}")
else:
    print(f"❌ 폴더를 못 찾았습니다. 경로가 정확한지 확인해 주세요: {data_path}")

# 3. 폴더 안에 뭐가 들어있는지 '무조건' 다 출력해보기
try:
    all_files = os.listdir(data_path)
    print(f"📦 폴더 내 전체 파일 목록 ({len(all_files)}개):")
    for f in all_files:
        print(f" - {f}")
except Exception as e:
    print(f"❌ 폴더 접근 에러: {e}")

# %%
import os
import glob
import pandas as pd

# 1. 파일이 들어있는 로컬 경로 (r을 꼭 붙이세요!)
data_path = r"C:\Users\Julia\Downloads\sales_data" 

# 2. 필터링 조건 (선택하신 정예 멤버들)
target_sectors = [
    '섬유제품', '완구', '운동/경기용품', '화장품', '문구', '서적', 
    '시계및귀금속', '안경', '일반의류', '편의점', '노래방', '미용실', 
    '당구장', '커피-음료', '호프-간이주점', '분식전문점', '치킨전문점', 
    '패스트푸드점', '제과점', '양식음식점', '중식음식점', '한식음식점'
]

cols_to_keep = [
    '기준_년분기_코드', '행정동_코드', '행정동_코드_명', '서비스_업종_코드_명', 
    '당월_매출_금액', '주중_매출_금액', '주말_매출_금액', 
    '연령대_10_매출_금액', '연령대_20_매출_금액', '연령대_30_매출_금액'
]

# 3. 파일 찾기
files = sorted(glob.glob(os.path.join(data_path, "*.csv")))
print(f"📦 총 {len(files)}개의 파일을 찾았습니다.")

combined_list = []

for f in files:
    filename = os.path.basename(f)
    print(f"🔍 {filename} 처리 중...", end=" ")
    
    try:
        # 필요한 컬럼만 읽기 (속도 향상)
        df = pd.read_csv(f, encoding='cp949', usecols=cols_to_keep)
        
        # [필터 1] 기간: 2020년 4분기부터 (20201, 20202, 20203 제외)
        df = df[~df['기준_년분기_코드'].isin([20201, 20202, 20203])]
        
        # [필터 2] 업종: 선택하신 업종만
        df = df[df['서비스_업종_코드_명'].isin(target_sectors)]
        
        combined_list.append(df)
        print(f"-> {len(df)}건 추출 완료")
        
    except Exception as e:
        print(f"-> ❌ 에러 발생: {e}")

# 4. 하나로 합치고 저장
if combined_list:
    final_df = pd.concat(combined_list, ignore_index=True)
    
    # 엑셀에서도 잘 열리도록 'utf-8-sig'로 저장
    output_name = "seoul_sales_1030_refined.csv"
    final_df.to_csv(output_name, index=False, encoding='utf-8-sig')
    
    print("\n" + "="*30)
    print(f"🎉 모든 작업이 끝났습니다!")
    print(f"💾 최종 파일명: {output_name}")
    print(f"📊 총 데이터 행 수: {len(final_df)}개")
    print("="*30)
else:
    print("\n❌ 추출된 데이터가 하나도 없습니다. 경로와 파일 내용을 확인해 주세요.")


# %%
import pandas as pd

# 1. 아까 필터링해서 합쳐둔 파일 읽기
input_file = "seoul_sales_1030_refined.csv" 
df = pd.read_csv(input_file)

# 2. 공식 영문 명칭 매핑 사전 (보내주신 리스트 기준)
official_mapping = {
    '기준_년분기_코드': 'STDR_YYQU_CD',
    '행정동_코드': 'ADSTRD_CD',
    '행정동_코드_명': 'ADSTRD_CD_NM',
    '서비스_업종_코드_명': 'SVC_INDUTY_CD_NM',
    '당월_매출_금액': 'THSMON_SELNG_AMT',
    '당월_매출_건수': 'THSMON_SELNG_CO',
    '주중_매출_금액': 'MDWK_SELNG_AMT',
    '주말_매출_금액': 'WKEND_SELNG_AMT',
    '연령대_10_매출_금액': 'AGRDE_10_SELNG_AMT',
    '연령대_20_매출_금액': 'AGRDE_20_SELNG_AMT',
    '연령대_30_매출_금액': 'AGRDE_30_SELNG_AMT'
}

# 3. 컬럼명 일괄 변경
df_official = df.rename(columns=official_mapping)

# 4. Supabase 업로드용 최종 파일 저장
output_file = "seoul_sales_final_official.csv"
df_official.to_csv(output_file, index=False, encoding='utf-8')

print(f"✅ 변환 완료! 파일명: {output_file}")
print("-" * 30)
print("🚀 바뀐 컬럼 리스트:")
for col in df_official.columns:
    print(f"- {col}")

# %%
import pandas as pd

# 1. 아까 공식 명칭으로 바꾼 파일 읽기
df = pd.read_csv("seoul_sales_final_official.csv")

# 2. 'id'라는 컬럼을 맨 앞에 만들고 1부터 번호 매기기
# df.index + 1 은 0, 1, 2... 대신 1, 2, 3...으로 번호를 만듭니다.
df.insert(0, 'id', range(1, len(df) + 1))

# 3. 최종 저장
df.to_csv("seoul_sales_ready_to_upload.csv", index=False, encoding='utf-8')

print(f"✅ PK 추가 완료! 총 {len(df)}개의 행에 id가 부여되었습니다.")
print(df[['id', 'STDR_YYQU_CD', 'ADSTRD_CD_NM']].head()) # 확인용 출력

# %%
import pandas as pd
import numpy as np

# 1. 통합된 최종 파일 읽기
input_file = "seoul_sales_ready_to_upload.csv"
df = pd.read_csv(input_file)

# 2. 파일을 몇 개로 나눌지 설정
num_files = 4
# 전체 행 수를 4로 나누어 쪼갤 지점 계산
chunks = np.array_split(df, num_files)

print(f"📊 전체 데이터 행 수: {len(df)}개")

# 3. 쪼개진 데이터를 각각 저장
for i, chunk in enumerate(chunks):
    output_name = f"upload_part_{i+1}.csv"
    chunk.to_csv(output_name, index=False, encoding='utf-8')
    
    # 확인을 위해 각 파일의 id 범위를 출력
    start_id = chunk['id'].iloc[0]
    end_id = chunk['id'].iloc[-1]
    print(f"✅ {output_name} 저장 완료! (id: {start_id} ~ {end_id} / 행 수: {len(chunk)})")

print("\n🚀 이제 위 4개 파일을 순서대로 Supabase에 올리시면 됩니다!")

# %% [markdown]
# # 추정매출 연간 증감율 SQL 쿼리문

# %%
-- 1. 기존에 같은 이름의 테이블이 있다면 삭제
-- DROP TABLE IF EXISTS sales_growth;

-- 2. 행정동 코드를 포함하여 새 테이블 생성
CREATE TABLE sales_growth AS
WITH annual_sales AS (
  SELECT
    "ADSTRD_CD", -- 코드 유지
    MAX("ADSTRD_CD_NM") AS "ADSTRD_CD_NM", -- 이름은 대표값으로
    CASE
      WHEN "STDR_YYQU_CD" BETWEEN 20204 AND 20213 THEN '2020Q4_2021Q3'
      WHEN "STDR_YYQU_CD" BETWEEN 20214 AND 20223 THEN '2021Q4_2022Q3'
      WHEN "STDR_YYQU_CD" BETWEEN 20224 AND 20233 THEN '2022Q4_2023Q3'
      WHEN "STDR_YYQU_CD" BETWEEN 20234 AND 20243 THEN '2023Q4_2024Q3'
      WHEN "STDR_YYQU_CD" BETWEEN 20244 AND 20253 THEN '2024Q4_2025Q3'
    END AS sales_year,
    SUM("THSMON_SELNG_AMT") AS total_sales
  FROM sales
  GROUP BY "ADSTRD_CD", sales_year
),
pivot_base AS (
  SELECT
    "ADSTRD_CD", -- 피벗 기준에 코드 추가
    MAX("ADSTRD_CD_NM") AS "행정동명",
    SUM(total_sales) FILTER (WHERE sales_year = '2020Q4_2021Q3') / 100000000.0 AS s1,
    SUM(total_sales) FILTER (WHERE sales_year = '2021Q4_2022Q3') / 100000000.0 AS s2,
    SUM(total_sales) FILTER (WHERE sales_year = '2022Q4_2023Q3') / 100000000.0 AS s3,
    SUM(total_sales) FILTER (WHERE sales_year = '2023Q4_2024Q3') / 100000000.0 AS s4,
    SUM(total_sales) FILTER (WHERE sales_year = '2024Q4_2025Q3') / 100000000.0 AS s5
  FROM annual_sales
  WHERE sales_year IS NOT NULL
  GROUP BY 1
)
SELECT
  "ADSTRD_CD", -- 이제 테이블에 코드가 남습니다.
  "행정동명",
  ROUND(s1, 1) AS "sales_20Q4_21Q3_100M",
  ROUND(s2, 1) AS "sales_21Q4_22Q3_100M",
  ROUND(((s2 - s1) / NULLIF(s1, 0)) * 100, 2) AS "growth_rate_1",
  ROUND(s3, 1) AS "sales_22Q4_23Q3_100M",
  ROUND(((s3 - s2) / NULLIF(s2, 0)) * 100, 2) AS "growth_rate_2",
  ROUND(s4, 1) AS "sales_23Q4_24Q3_100M",
  ROUND(((s4 - s3) / NULLIF(s3, 0)) * 100, 2) AS "growth_rate_3",
  ROUND(s5, 1) AS "sales_24Q4_25Q3_100M",
  ROUND(((s5 - s4) / NULLIF(s4, 0)) * 100, 2) AS "growth_rate_4"
FROM pivot_base
ORDER BY "ADSTRD_CD";

# %% [markdown]
# # 결측치 확인
#  둔촌1동이 null로 나옴 > 재건축이라 2024Q4-2025Q3부터 매출이 잡힌 걸 확인

# %%
SELECT * FROM sales_growth
WHERE "sales_20Q4_21Q3_100M" IS NULL 
   OR "sales_21Q4_22Q3_100M" IS NULL 
   OR "sales_22Q4_23Q3_100M" IS NULL 
   OR "sales_23Q4_24Q3_100M" IS NULL
   OR "sales_24Q4_25Q3_100M" IS NULL;

# %% [markdown]
# # new.csv를 supabase에 업로드하기전 인코딩 문제 해결하기

# %%
import pandas as pd
# 불러올 때 한글 인코딩 설정 (cp949)
df = pd.read_csv('new.csv', encoding='cp949')
# 저장할 때 UTF-8로 저장
df.to_csv('new_utf8.csv', index=False, encoding='utf-8')

# %% [markdown]
# # 회귀분선
# 시장 평균선을 그리고 rising top 10을 찾기

# %%
!uv add plotly

# %%
!uv add scikit-learn

# %%
!uv add nbformat

# %%
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# 1. 데이터 로드
df = pd.read_csv('seoul_4year_alpha_rows.csv')

# 2. 회귀분석 (X: 유동인구, y: 매출)
X = df[['pop_current_weight']].values
y = df['sales_4yr_legacy'].values
model = LinearRegression().fit(X, y)

df['predicted_sales'] = model.predict(X)
df['residual'] = df['sales_4yr_legacy'] - df['predicted_sales']

# 3. 인터랙티브 산점도 (Plotly)
fig = px.scatter(
    df, x='pop_current_weight', y='sales_4yr_legacy',
    hover_name='ADSTRD_CD_NM',
    color='efficiency_dna',
    size='efficiency_dna',
    color_continuous_scale='Portland',
    title='Seoul Commercial Alpha: 4yr Revenue Legacy vs Current Population Weight',
    labels={'pop_current_weight': 'Current Foot Traffic (Weight)', 'sales_4yr_legacy': '4yr Cumulative Sales (Legacy)'}
)

# 회귀선(시장 평균 성장선) 추가
x_range = np.linspace(df['pop_current_weight'].min(), df['pop_current_weight'].max(), 100)
y_range = model.predict(x_range.reshape(-1, 1))
fig.add_trace(go.Scatter(x=x_range, y=y_range, mode='lines', name='Market Average', line=dict(color='gray', dash='dash')))

# Rising Star Top 10 강조 (잔차 기준)
top_10 = df.nlargest(10, 'residual')
for i, row in top_10.iterrows():
    fig.add_annotation(x=row['pop_current_weight'], y=row['sales_4yr_legacy'], text=row['ADSTRD_CD_NM'], showarrow=True, arrowhead=1)

fig.show()

# %%
!uv add statsmodels

# %%
import statsmodels.api as sm
import pandas as pd
import numpy as np

# 1. 데이터 로드
df = pd.read_csv('seoul_4year_alpha_rows.csv')

# 독립변수(인구)와 종속변수(매출) 추출
X = df['pop_current_weight']
y = df['sales_4yr_legacy']

# 상수항 추가 (중요: statsmodels는 Intercept를 자동으로 넣지 않음)
X = sm.add_constant(X)

# 모델 적합
results = sm.OLS(y, X).fit()

# 결과 출력
print(results.summary())

# %%
import pandas as pd
import numpy as np
import statsmodels.api as sm

# 1. 데이터 로드
df = pd.read_csv('seoul_4year_alpha_rows.csv')

# 2. 로그 변환 (데이터가 0일 경우를 대비해 log(1+x) 사용)
# 상권 데이터의 왜도(Skewness)를 줄여 통계적 유의성을 확보합니다.
df['log_pop'] = np.log1p(df['pop_current_weight'])
df['log_sales'] = np.log1p(df['sales_4yr_legacy'])

# 3. 독립변수(X)와 종속변수(y) 설정
X = df['log_pop']
y = df['log_sales']
X = sm.add_constant(X)

# 4. 회귀분석 수행
model_log = sm.OLS(y, X).fit()

# 5. 결과 확인
print(model_log.summary())

# %%
import pandas as pd
import plotly.express as px

df = pd.read_csv('seoul_4year_alpha_rows.csv')

# 평균 매출 성장률과 평균 효율성 계산
avg_sales = df['sales_4yr_legacy'].mean()
avg_efficiency = 1.0  # 투입=산출 기준점

fig = px.scatter(
    df, x='efficiency_dna', y='sales_4yr_legacy',
    hover_name='ADSTRD_CD_NM',
    color='efficiency_dna',
    size='sales_4yr_legacy',
    title="The Alpha Strategy: Efficiency vs Growth",
    labels={'efficiency_dna': 'Efficiency DNA (Quality)', 'sales_4yr_legacy': '4yr Sales Growth (Quantity)'}
)

# 기준점 십자선 추가 (이 선들이 가설의 기준이 됩니다)
fig.add_vline(x=avg_efficiency, line_dash="dash", line_color="red", annotation_text="Efficiency Threshold")
fig.add_hline(y=avg_sales, line_dash="dash", line_color="blue", annotation_text="Avg Sales Growth")

fig.show()

# %%
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

# 1. 데이터 로드
df = pd.read_csv('seoul_4year_alpha_rows.csv')

# 2. 회귀분석 수행
X = df[['pop_current_weight']].values
y = df['sales_4yr_legacy'].values
model = LinearRegression().fit(X, y)
df['predicted'] = model.predict(X)
df['residual'] = df['sales_4yr_legacy'] - df['predicted']

# 3. 전략적 필터링: 회귀선 위에 있는(잔차가 양수인) 지역만 '유효'로 판정
df['is_alpha'] = df['residual'] > 0

# 4. 시각화 (회귀선 아래 지역은 투명하게 처리하거나 'Low Efficiency'로 분류)
fig = px.scatter(
    df, 
    x='pop_current_weight', 
    y='sales_4yr_legacy',
    color='is_alpha', # 회귀선 위/아래 구분
    hover_name='ADSTRD_CD_NM',
    size='efficiency_dna',
    title="<b>Seoul Alpha Analysis: Eliminating the 'Hype' Districts</b>",
    labels={'pop_current_weight': 'Population Weight', 'sales_4yr_legacy': '4yr Sales Legacy'},
    color_discrete_map={True: '#EF553B', False: '#E5ECF6'} # Alpha 지역은 빨강, 비효율은 회색
)

# 회귀선 추가
x_range = np.linspace(df['pop_current_weight'].min(), df['pop_current_weight'].max(), 100)
y_range = model.predict(x_range.reshape(-1, 1))
import plotly.graph_objects as go
fig.add_trace(go.Scatter(x=x_range, y=y_range, mode='lines', name='Market Average Line', line=dict(color='black', dash='dot')))

fig.show()

# %%
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# 1. 데이터 로드
df = pd.read_csv('seoul_4year_alpha_rows.csv')

# 2. 회귀분석 및 잔차(Residual) 계산
X = df[['pop_current_weight']].values
y = df['sales_4yr_legacy'].values
model = LinearRegression().fit(X, y)
df['predicted'] = model.predict(X)
df['residual'] = df['sales_4yr_legacy'] - df['predicted']

# 3. 전략적 필터링 (회귀선 위 & Efficiency DNA 상위 10개)
df_alpha = df[df['residual'] > 0].copy()
top_10 = df_alpha.sort_values(by='efficiency_dna', ascending=False).head(10)

# 4. 시각화 - 전체 배경은 연하게, Top 10은 강렬하게
fig = px.scatter(
    df, x='pop_current_weight', y='sales_4yr_legacy',
    hover_name='ADSTRD_CD_NM',
    opacity=0.3,
    color_discrete_sequence=['gray'],
    title="<b>Seoul Rising Star Top 10: 'The Hidden Alpha'</b>",
    labels={'pop_current_weight': 'Current Population Weight', 'sales_4yr_legacy': '4yr Sales Legacy'}
)

# Top 10 강조 레이어 추가
fig.add_trace(go.Scatter(
    x=top_10['pop_current_weight'],
    y=top_10['sales_4yr_legacy'],
    mode='markers+text',
    marker=dict(size=15, color='red', symbol='star'),
    text=top_10['ADSTRD_CD_NM'],
    textposition="top center",
    name='Top 10 Rising Stars'
))

# 회귀선(평균선) 추가
x_range = np.linspace(df['pop_current_weight'].min(), df['pop_current_weight'].max(), 100)
y_range = model.predict(x_range.reshape(-1, 1))
fig.add_trace(go.Scatter(x=x_range, y=y_range, mode='lines', name='Market Average', line=dict(color='black', dash='dot')))

fig.update_layout(template='plotly_white', showlegend=True)
fig.show()

# 5. 리스트 출력
print("\n" + "="*50)
print("       [월요일 발표용 최종 TOP 10 리스트]       ")
print("="*50)
print(top_10[['ADSTRD_CD_NM', 'sales_4yr_legacy', 'pop_current_weight', 'efficiency_dna']].to_string(index=False))
print("="*50)

# %%
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# 1. 데이터 로드 및 회귀분석
df = pd.read_csv('seoul_4year_alpha_rows.csv')
X = df[['pop_current_weight']].values
y = df['sales_4yr_legacy'].values
model = LinearRegression().fit(X, y)
df['predicted'] = model.predict(X)
df['residual'] = df['sales_4yr_legacy'] - df['predicted']

# 2. 필터링: 회귀선 위(Alpha > 0) 지역 중 효율성 상위 20개
df_alpha = df[df['residual'] > 0].copy()
top_20 = df_alpha.sort_values(by='efficiency_dna', ascending=False).head(20).copy()

# 3. 그룹핑 (인지도 기준 임의 분류 - 발표용)
# 매출 배수가 너무 높으면 '기성 상권', 적당히 높으면서 효율이 극강이면 '붐업 상권'
top_20['type'] = top_20['sales_4yr_legacy'].apply(lambda x: 'Established' if x > 2.1 else 'Boom-up Candidate')

# 4. 시각화
fig = px.scatter(
    top_20, x='pop_current_weight', y='sales_4yr_legacy',
    color='type', size='efficiency_dna',
    hover_name='ADSTRD_CD_NM',
    text='ADSTRD_CD_NM',
    title="<b>Seoul Alpha Top 20: Hidden Gems Beyond the Majors</b>",
    labels={'pop_current_weight': 'Population Weight (Input)', 'sales_4yr_legacy': 'Sales Legacy (Output)'},
    color_discrete_map={'Established': '#636EFA', 'Boom-up Candidate': '#EF553B'}
)

fig.update_traces(textposition='top center')
fig.add_trace(go.Scatter(x=[0.8, 1.4], y=[model.predict([[0.8]])[0], model.predict([[1.4]])[0]], 
                         mode='lines', name='Market Avg', line=dict(color='black', dash='dot')))

fig.show()

# 5. 리스트 출력
print(top_20[['ADSTRD_CD_NM', 'sales_4yr_legacy', 'pop_current_weight', 'efficiency_dna', 'type']].to_string(index=False))

# %%
import plotly.express as px
import plotly.graph_objects as go

# 성수의 수치 추출 (성수2가1동 기준)
seongsu = top_20[top_20['ADSTRD_CD_NM'] == '성수2가1동'].iloc[0]
seongsu_dna = seongsu['efficiency_dna']

# 그래프 그리기
fig = px.scatter(
    top_20, x='pop_current_weight', y='sales_4yr_legacy',
    color='efficiency_dna', size='efficiency_dna',
    hover_name='ADSTRD_CD_NM', text='ADSTRD_CD_NM',
    color_continuous_scale='Viridis',
    title="<b>Next Seongsu Analysis: Who beats Seongsu's Efficiency?</b>"
)

# 성수 기준선 (세로/가로선 혹은 강조 표시)
fig.add_shape(type="circle",
    xref="x", yref="y",
    x0=seongsu['pop_current_weight']-0.02, y0=seongsu['sales_4yr_legacy']-0.05,
    x1=seongsu['pop_current_weight']+0.02, y1=seongsu['sales_4yr_legacy']+0.05,
    line_color="Red", line_width=3
)

fig.add_annotation(x=seongsu['pop_current_weight'], y=seongsu['sales_4yr_legacy'],
            text="BENCHMARK: SEONGSU", showarrow=True, arrowhead=1, ax=50, ay=-40, font=dict(color="red", size=12))

fig.update_layout(template='plotly_white')
fig.show()

# %% [markdown]
# # 결론 - 데이터 셋 부족
# 통계적으로 의미가 없는 결과가 나옴. 원인은 데이터 셋 부족으로 충분히 설명할 수 없다고 판단 더 많은 데이터를 수집할 필요가 있음

# %% [markdown]
# # 데이터 다시 수집
# 서울시 상권분석 서비스 : 상권변화지표 - 행정동
# 서울시 상권분석 서비스 : 집객시설 - 행정동
# 서울시 상권분석 서비스: 상주인구 - 행정동
# 서울시 상권분석 서비스: 길단위인구 - 행정동
# 서울시 상권분석 서비스: 추정매출 - 행정동
# 
# 여기서 길단위인구(유동인구) - 행정동을 기준으로 통합하는 데이터 셋을 만들 것이다.
# 
# 

# %%
import pandas as pd
import glob
import numpy as np
import os  # 로컬 경로 제어를 위해 추가

# [환경설정] 데이터 파일이 있는 폴더 경로로 이동
# 예: r'C:\Users\Documents\Project\Data' (경로 앞에 r을 붙이면 역슬래시 에러 방지)
data_path = r'C:\Users\Julia\Downloads\raw_data'
os.chdir(data_path)

# 1. 선생님이 확정한 업종 및 컬럼 리스트
target_sectors = [
    '섬유제품', '완구', '운동/경기_용품', '화장품', '문구', '서적', 
    '시계및귀금속', '안경', '일반의류', '편의점', '노래방', '미용실', 
    '당구장', '커피-음료', '호프-간이주점', '분식전문점', '치킨전문점', 
    '패스트푸드점', '제과점', '양식음식점', '중식음식점', '한식음식점'
]

cols_to_keep = [
    '기준_년분기_코드', '행정동_코드', '행정동_코드_명', '서비스_업종_코드_명', 
    '당월_매출_금액', '주중_매출_금액', '주말_매출_금액', 
    '연령대_10_매출_금액', '연령대_20_매출_금액', '연령대_30_매출_금액'
]

# 2. 연도별 매출 데이터 통합 (추정매출만 연도별)
print("진행 중: 연도별 추정매출 통합...")
sales_files = sorted(glob.glob('매출_*.csv')) # 파일명 규칙 확인 필요
sales_list = []

for f in sales_files:
    # 불러올 때부터 필요한 컬럼만 추출하여 메모리 확보
    df = pd.read_csv(f, usecols=cols_to_keep, encoding='cp949')
    # 업종 필터링
    df = df[df['서비스_업종_코드_명'].isin(target_sectors)]
    sales_list.append(df)

df_sales = pd.concat(sales_list, ignore_index=True)

# 3. 단일 파일 데이터 로드 (유동인구, 상주인구, 상권지표, 집객시설)
# 각 파일의 컬럼명은 데이터 광장의 표준명칭을 기준으로 했습니다.
print("진행 중: 기타 테이블 병합...")

# [주의] 파일명은 로컬에 저장된 이름과 똑같아야 합니다!
df_pop = pd.read_csv(r'C:\Users\Julia\Downloads\raw_data\유동인구.csv', encoding='cp949')
df_resident = pd.read_csv(r'C:\Users\Julia\Downloads\raw_data\상주인구.csv', encoding='cp949')
df_change = pd.read_csv(r'C:\Users\Julia\Downloads\raw_data\상권변화지표.csv', encoding='cp949')
df_facility = pd.read_csv(r'C:\Users\Julia\Downloads\raw_data\집객시설.csv', encoding='cp949')

# 길단위인구: MZ 유동인구 핵심
df_pop = df_pop[['기준_년분기_코드', '행정동_코드', '총_유동인구_수', '연령대_20_유동인구_수', '연령대_30_유동인구_수']]
df_pop['MZ_유동인구'] = df_pop['연령대_20_유동인구_수'] + df_pop['연령대_30_유동인구_수']

# 상주인구: 베드타운 지수용 
df_resident = df_resident[['기준_년분기_코드', '행정동_코드', '총_상주인구_수', '총_가구_수']]

# 집객시설: 인프라 위주
df_facility = df_facility[['기준_년분기_코드', '행정동_코드', '집객시설_수', '지하철_역_수']]

# 상권변화지표: 역동성 스코어링 포함
df_change = df_change[['기준_년분기_코드', '행정동_코드', '상권_변화_지표_명', '운영_영업_개월_평균']]
# 아까 정한 1~4점 매핑 적용
mapping = {'다이나믹': 4, '상권확장': 3, '정체': 2, '상권축소': 1}
df_change['상권지표_점수'] = df_change['상권_변화_지표_명'].map(mapping).fillna(0)

# 4. 최종 Merge (기준_년분기_코드와 행정동_코드를 키로 활용)
final_df = df_sales.merge(df_pop, on=['기준_년분기_코드', '행정동_코드'], how='left')
final_df = final_df.merge(df_resident, on=['기준_년분기_코드', '행정동_코드'], how='left')
final_df = final_df.merge(df_change, on=['기준_년분기_코드', '행정동_코드'], how='left')
final_df = final_df.merge(df_facility, on=['기준_년분기_코드', '행정동_코드'], how='left')

# 5. 결과 저장
final_df.fillna(0, inplace=True)
final_df.to_csv('final_alpha_data.csv', index=False, encoding='utf-8-sig')
print("축하합니다! 분석용 최종 데이터 셋 생성이 완료되었습니다.")

# %%
# 1. 행 개수 비교
original_rows = len(df_sales)
final_rows = len(final_df)

print(f"--- [1. 데이터 손실 검증] ---")
print(f"매출 데이터 원본 행 수: {original_rows}")
print(f"최종 병합 데이터 행 수: {final_rows}")

if original_rows == final_rows:
    print("✅ 성공: 데이터 누락이나 중복 생성 없이 완벽하게 병합되었습니다.")
else:
    print("⚠️ 주의: 행 개수가 다릅니다. 중복 데이터(Duplication)가 있는지 확인이 필요합니다.")

# %%
print(f"\n--- [2. 주요 지표 결측치(0) 비중 검증] ---")
# 주요 컬럼들 리스트 (선생님 파일의 실제 컬럼명으로 수정 필요)
check_cols = ['총_유동인구_수', '총_상주인구_수', '상권지표_점수', '집객시설수']

for col in check_cols:
    if col in final_df.columns:
        # 0값의 비중 계산
        zero_count = (final_df[col] == 0).sum()
        zero_ratio = (zero_count / len(final_df)) * 100
        print(f"[{col}] 결측치(0) 개수: {zero_count}개 ({zero_ratio:.2f}%)")

# %%
# 1. 데이터 상단 및 구조 확인
print("--- [1. 데이터 기본 구조] ---")
print(final_df.info()) 

# 2. 요약 통계량 확인 (매출, 인구, 지수 등이 상식적인 범위인지)
print("\n--- [2. 주요 지표 요약 통계] ---")
# 분석에 핵심적인 컬럼들만 골라서 봅니다.
key_cols = ['당월_매출_금액', '총_유동인구_수', '총_상주인구_수', 'MZ_유동인구', '상권지표_점수']
# 존재하는 컬럼만 필터링해서 확인
existing_cols = [c for c in key_cols if c in final_df.columns]
print(final_df[existing_cols].describe())

# 3. 데이터 중복 여부 확인
# 동일 분기에 동일 행정동, 동일 업종이 두 번 들어가면 안 됩니다.
duplicate_count = final_df.duplicated(subset=['기준_년분기_코드', '행정동_코드', '서비스_업종_코드_명']).sum()
print(f"\n--- [3. 중복 데이터 체크] ---")
print(f"중복된 행(Row) 개수: {duplicate_count}개")

# 4. '가양동' vs '성수동' 극명한 차이 확인 (Spot Check)
print(f"\n--- [4. 베드타운 vs 핫플레이스 비교 검증] ---")
comparison = final_df[final_df['행정동_코드_명'].isin(['가양1동', '성수2가1동'])].groupby('행정동_코드_명')[existing_cols].mean()
print(comparison)

# %%
# 1. 효율 지표 생성
# 배후 인구(상주인구) 대비 얼마나 외부에서 많이 오나? (상권 효율성)
final_df['상권_유입_강도'] = final_df['총_유동인구_수'] / (final_df['총_상주인구_수'] + 1)

# 2. MZ 타겟팅 지표
# 전체 유동인구 중 MZ(2030)가 차지하는 비율
final_df['MZ_유입_비중'] = (final_df['연령대_20_유동인구_수'] + final_df['연령대_30_유동인구_수']) / (final_df['총_유동인구_수'] + 1)

# 3. 데이터 포인트 최신화 (2025년 1분기 기준)
analysis_2025 = final_df[final_df['기준_년분기_코드'] == 20251].copy()

# %%
# 행정동별로 지표 통합
dong_rank = analysis_2025.groupby('행정동_코드_명').agg({
    '당월_매출_금액': 'sum',
    '상권_유입_강도': 'mean',
    'MZ_유입_비중': 'mean',
    '상권지표_점수': 'mean'
}).reset_index()

# [필터링 조건]
# 1. 상권지표 점수가 2.5점 이상인 곳 (정체된 베드타운 제거)
# 2. MZ 유입 비중이 서울시 평균 이상인 곳
df_filtered = dong_rank[
    (dong_rank['상권지표_점수'] >= 2.5) & 
    (dong_rank['MZ_유입_비중'] >= dong_rank['MZ_유입_비중'].mean())
]

# 최종 '성수 지수' 산출 (유입 강도와 MZ 비중의 조화)
df_filtered['Next_Seongsu_Score'] = (df_filtered['상권_유입_강도'] * 0.5) + (df_filtered['MZ_유입_비중'] * 100 * 0.5)

# 상위 10개 출력
top_10 = df_filtered.sort_values(by='Next_Seongsu_Score', ascending=False).head(10)
print(top_10[['행정동_코드_명', '상권_유입_강도', 'MZ_유입_비중', 'Next_Seongsu_Score']])

# %%
import statsmodels.api as sm
import numpy as np

# 1. 분석용 데이터 정리 (최신 분기 기준)
df_reg = analysis_2025.copy()

# 2. 변수 스케일 조정 (매출액 단위가 너무 크므로 로그를 취하거나 단위를 억으로 변경)
df_reg['매출_억단위'] = df_reg['당월_매출_금액'] / 100000000

# 3. 독립변수(X)와 종속변수(y) 설정
# 상수항(Intercept) 추가 필수
X = df_reg[['MZ_유동인구', '상권_유입_강도', '상권지표_점수', '총_상주인구_수']]
X = sm.add_constant(X) 
y = df_reg['매출_억단위']

# 4. 모델 학습 및 결과 출력
model = sm.OLS(y, X).fit()
print(model.summary())

# %%
# 단위 조정 (가독성 및 통계적 안정성 향상)
df_reg['MZ_유동_천명'] = df_reg['MZ_유동인구'] / 1000
df_reg['상주인구_천명'] = df_reg['총_상주인구_수'] / 1000

# 다시 분석
X_new = df_reg[['MZ_유동_천명', '상권_유입_강도', '상권지표_점수', '상주인구_천명']]
X_new = sm.add_constant(X_new)
model_new = sm.OLS(y, X_new).fit()
print(model_new.summary())

# %%
!uv pip install matplotlib seaborn

# %%
import matplotlib.pyplot as plt
import seaborn as sns

# 회귀계수 데이터 추출 (상수항 제외)
coefs = model_new.params.drop('const')
errors = model_new.bse.drop('const')

# 시각화 설정
plt.figure(figsize=(10, 6))
plt.rc('font', family='Malgun Gothic') # 한글 깨짐 방지
plt.axvline(0, color='red', linestyle='--') # 0점 기준선
coefs.plot(kind='barh', xerr=errors, color='skyblue', edgecolor='black')
plt.title('상권 매출에 미치는 변수별 영향력 (회귀계수)')
plt.xlabel('매출 기여도 (억 단위)')
plt.show()

# %%
import statsmodels.api as sm
import numpy as np

# 1. 전체 데이터 복사 및 클리닝
df_total_reg = final_df.copy()

# 2. 단위 조정 (매출은 억 단위, 인구는 천 명 단위)
df_total_reg['매출_억단위'] = df_total_reg['당월_매출_금액'] / 100000000
df_total_reg['MZ_유동_천명'] = (df_total_reg['연령대_20_유동인구_수'] + df_total_reg['연령대_30_유동인구_수']) / 1000
df_total_reg['상주인구_천명'] = df_total_reg['총_상주인구_수'] / 1000
# 상권_유입_강도 재계산 (원본에 없다면)
df_total_reg['상권_유입_강도'] = df_total_reg['총_유동인구_수'] / (df_total_reg['총_상주인구_수'] + 1)

# 3. 결측치 제거 (전체 데이터는 양이 많아 결측치가 섞여있을 확률이 높음)
cols_to_use = ['MZ_유동_천명', '상권_유입_강도', '상권지표_점수', '상주인구_천명']
df_total_reg = df_total_reg.dropna(subset=cols_to_use + ['매출_억단위'])

# 4. 독립변수(X)와 종속변수(y) 설정
X_total = df_total_reg[cols_to_use]
X_total = sm.add_constant(X_total)
y_total = df_total_reg['매출_억단위']

# 5. 모델 학습 및 결과 출력
model_total = sm.OLS(y_total, X_total).fit()
print(model_total.summary())

# %%
# 코로나 기간(2020~2022)만 따로 떼어내기
corona_df = final_df[final_df['기준_년분기_코드'].between(20201, 20224)].copy()

# 단위 조정
corona_df['매출_억단위'] = corona_df['당월_매출_금액'] / 100000000
corona_df['MZ_유동_천명'] = (corona_df['연령대_20_유동인구_수'] + corona_df['연령대_30_유동인구_수']) / 1000
corona_df['상주인구_천명'] = corona_df['총_상주인구_수'] / 1000
corona_df['상권_유입_강도'] = corona_df['총_유동인구_수'] / (corona_df['총_상주인구_수'] + 1)

# 회귀분석 실행
X_corona = corona_df[['MZ_유동_천명', '상권_유입_강도', '상권지표_점수', '상주인구_천명']]
X_corona = sm.add_constant(X_corona)
y_corona = corona_df['매출_억단위']

model_corona = sm.OLS(y_corona, X_corona).fit()
print(model_corona.summary())

# %%
# 1. 동네(행정동)별로 데이터 합치기 (중복 제거 및 평균값 산출)
final_agg = analysis_2025.groupby('행정동_코드_명').agg({
    '상권_유입_강도': 'mean',
    'MZ_유입_비중': 'mean',
    '상권지표_점수': 'mean'
}).reset_index()

# 2. 다시 정규화 (0~1 사이로 변환)
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
final_agg[['상권_유입_강도', 'MZ_유입_비중', '상권지표_점수']] = scaler.fit_transform(
    final_agg[['상권_유입_강도', 'MZ_유입_비중', '상권지표_점수']]
)

# 3. 넥스트 성수 지수 산출 (가중치 적용)
# MZ 비중에 가장 높은 가중치를 줍니다.
final_agg['넥스트_성수_지수'] = (
    final_agg['MZ_유입_비중'] * 0.4 + 
    final_agg['상권_유입_강도'] * 0.3 + 
    final_agg['상권지표_점수'] * 0.3
) * 100

# 4. 결과 출력 (TOP 10)
result = final_agg.sort_values(by='넥스트_성수_지수', ascending=False).head(10)
print(result[['행정동_코드_명', '넥스트_성수_지수', 'MZ_유입_비중', '상권_유입_강도']])

# %%
# 1. 동네별 매출 규모 파악 (이미 너무 큰 곳을 빼기 위해)
final_agg_with_sales = analysis_2025.groupby('행정동_코드_명').agg({
    '당월_매출_금액': 'sum',
    '상권_유입_강도': 'mean',
    'MZ_유입_비중': 'mean',
    '상권지표_점수': 'mean'
}).reset_index()

# 2. 상위 20% 매출 상권(이미 메이저인 곳) 제외
sales_threshold = final_agg_with_sales['당월_매출_금액'].quantile(0.8)
next_candidates = final_agg_with_sales[final_agg_with_sales['당월_매출_금액'] < sales_threshold].copy()

# 3. 정규화 및 지수 재계산
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
next_candidates[['상권_유입_강도', 'MZ_유입_비중', '상권지표_점수']] = scaler.fit_transform(
    next_candidates[['상권_유입_강도', 'MZ_유입_비중', '상권지표_점수']]
)

# 4. 넥스트 성수 지수 (성장성에 더 비중)
next_candidates['넥스트_성수_지수'] = (
    next_candidates['MZ_유입_비중'] * 0.5 +  # MZ가 모이는 게 제일 중요
    next_candidates['상권_유입_강도'] * 0.3 + 
    next_candidates['상권지표_점수'] * 0.2
) * 100

# 5. 최종 결과 (TOP 10)
final_next_seongsu = next_candidates.sort_values(by='넥스트_성수_지수', ascending=False).head(10)
print(final_next_seongsu[['행정동_코드_명', '넥스트_성수_지수', 'MZ_유입_비중', '상권_유입_강도']])

# %%
# 1. 외부 유입이 너무 적은 곳(단순 자취촌) 필터링
# 상권 유입 강도가 하위 30%인 곳은 과감히 제거 (놀러 오는 사람이 적다는 뜻)
inflow_threshold = next_candidates['상권_유입_강도'].quantile(0.3)
final_hip_candidates = next_candidates[next_candidates['상권_유입_강도'] > inflow_threshold].copy()

# 2. 지수 재산출 (가중치 조정)
# '유입 강도' 비중을 높여서 '놀러 오는 곳'에 가점을 줍니다.
final_hip_candidates['넥스트_성수_지수'] = (
    final_hip_candidates['MZ_유입_비중'] * 0.4 + 
    final_hip_candidates['상권_유입_강도'] * 0.4 + # 외부 유입의 중요도 상승
    final_hip_candidates['상권지표_점수'] * 0.2
) * 100

# 3. 최종 순위 확인
result_final = final_hip_candidates.sort_values(by='넥스트_성수_지수', ascending=False).head(10)
print(result_final[['행정동_코드_명', '넥스트_성수_지수', 'MZ_유입_비중', '상권_유입_강도']])

# %%
# 1. MZ 유동인구 합계 계산
analysis_2025['MZ_유동_수'] = analysis_2025['연령대_20_유동인구_수'] + analysis_2025['연령대_30_유동인구_수']

# 2. 현실적인 필터링 (자취촌 & 재건축지역 제외)
# MZ 유동인구가 너무 적은 곳(하위 20%) 제외 = "사람이 일단 모여야 상권이다"
mz_threshold = analysis_2025['MZ_유동_수'].quantile(0.2)
# 상주인구가 너무 적은 곳(하위 10%) 제외 = "유입강도 수치 왜곡 방지"
resident_threshold = analysis_2025['총_상주인구_수'].quantile(0.1)

valid_df = analysis_2025[
    (analysis_2025['MZ_유동_수'] > mz_threshold) & 
    (analysis_2025['총_상주인구_수'] > resident_threshold)
].copy()

# 3. 이미 너무 커진 메이저 상권 제외 (상위 20% 매출액)
sales_limit = valid_df['당월_매출_금액'].quantile(0.8)
next_step_df = valid_df[valid_df['당월_매출_금액'] < sales_limit].copy()

# 4. 동네별 평균값으로 합치기
final_real = next_step_df.groupby('행정동_코드_명').agg({
    'MZ_유입_비중': 'mean',
    '상권_유입_강도': 'mean',
    '상권지표_점수': 'mean'
}).reset_index()

# 5. 정규화 및 지수 산출 (4:4:2 가중치)
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
final_real[['MZ_유입_비중', '상권_유입_강도', '상권지표_점수']] = scaler.fit_transform(
    final_real[['MZ_유입_비중', '상권_유입_강도', '상권지표_점수']]
)

final_real['넥스트_성수_지수'] = (
    final_real['MZ_유입_비중'] * 0.4 + 
    final_real['상권_유입_강도'] * 0.4 + 
    final_real['상권지표_점수'] * 0.2
) * 100

print(final_real.sort_values(by='넥스트_성수_지수', ascending=False).head(10))

# %%
# 1. 현실적인 체급 필터 (자취촌 & 재건축 방지 - 이전과 동일)
valid_df = analysis_2025[
    (analysis_2025['MZ_유동_수'] > analysis_2025['MZ_유동_수'].quantile(0.2)) & 
    (analysis_2025['총_상주인구_수'] > analysis_2025['총_상주인구_수'].quantile(0.1))
].copy()

# 2. 강력한 매출 필터: 상위 50% 동네를 통째로 제거
# 서울에서 매출 규모가 중간 이하인 '성장기' 동네만 남깁니다.
mid_low_sales_limit = valid_df['당월_매출_금액'].quantile(0.5)
emerging_df = valid_df[valid_df['당월_매출_금액'] < mid_low_sales_limit].copy()

# 3. 동네별 평균값 집계
final_agg_next = emerging_df.groupby('행정동_코드_명').agg({
    'MZ_유입_비중': 'mean',
    '상권_유입_강도': 'mean',
    '상권지표_점수': 'mean'
}).reset_index()

# 4. 정규화 (남은 동네들 사이에서의 상대 점수)
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
final_agg_next[['MZ_유입_비중', '상권_유입_강도', '상권지표_점수']] = scaler.fit_transform(
    final_agg_next[['MZ_유입_비중', '상권_유입_강도', '상권지표_점수']]
)

# 5. 넥스트 성수 지수 산출 (MZ 40% : 유입강도 40% : 지표 20%)
final_agg_next['넥스트_성수_지수'] = (
    final_agg_next['MZ_유입_비중'] * 0.4 + 
    final_agg_next['상권_유입_강도'] * 0.4 + 
    final_agg_next['상권지표_점수'] * 0.2
) * 100

print(final_agg_next.sort_values(by='넥스트_성수_지수', ascending=False).head(15))

# %%
# 1. '상주인구 대비 외부 유입'이 서울 평균 이상인 곳만 남기기 (자취촌 필터)
# 유입 강도가 낮다는 건 '그 동네 사는 사람' 위주라는 뜻이므로 과감히 제거
inflow_mean = valid_df['상권_유입_강도'].mean()
hip_only_df = valid_df[valid_df['상권_유입_강도'] > inflow_mean].copy()

# 2. 이미 너무 뜬 메이저 상권 제외 (아까보다 더 강력하게 50% 컷)
sales_median = hip_only_df['당월_매출_금액'].median()
emerging_hip_df = hip_only_df[hip_only_df['당월_매출_금액'] < sales_median].copy()

# 3. 동네별 평균 집계
final_agg_final = emerging_hip_df.groupby('행정동_코드_명').agg({
    'MZ_유입_비중': 'mean',
    '상권_유입_강도': 'mean',
    '상권지표_점수': 'mean'
}).reset_index()

# 4. 정규화
scaler = MinMaxScaler()
final_agg_final[['MZ_유입_비중', '상권_유입_강도', '상권지표_점수']] = scaler.fit_transform(
    final_agg_final[['MZ_유입_비중', '상권_유입_강도', '상권지표_점수']]
)

# 5. [중요] 가중치 변경: 유입 강도(외부에서 오는 힘)를 50%로 상향
final_agg_final['넥스트_성수_지수'] = (
    final_agg_final['상권_유입_강도'] * 0.5 +  # 외부 집객력이 가장 중요!
    final_agg_final['MZ_유입_비중'] * 0.3 + 
    final_agg_final['상권지표_점수'] * 0.2
) * 100

print(final_agg_final.sort_values(by='넥스트_성수_지수', ascending=False).head(10))

# %%
# 1. '이미 완성된' 상권지표 4점(만점) 지역 제외
# '성장기' 혹은 '확장기'인 2~3점대 지역만 타겟팅합니다.
emerging_stage_df = valid_df[valid_df['상권지표_점수'].isin([2, 3])].copy()

# 2. 매출 필터 (중간 이하)
sales_limit = emerging_stage_df['당월_매출_금액'].median()
target_df = emerging_stage_df[emerging_stage_df['당월_매출_금액'] < sales_limit].copy()

# 3. 동네별 집계
final_agg_next = target_df.groupby('행정동_코드_명').agg({
    'MZ_유입_비중': 'mean',
    '상권_유입_강도': 'mean',
    '상권지표_점수': 'mean'
}).reset_index()

# 4. 정규화
scaler = MinMaxScaler()
final_agg_next[['MZ_유입_비중', '상권_유입_강도', '상권지표_점수']] = scaler.fit_transform(
    final_agg_next[['MZ_유입_비중', '상권_유입_강도', '상권지표_점수']]
)

# 5. 가중치: 외부 유입(0.5) + MZ 비중(0.3) + 지표 성장성(0.2)
final_agg_next['넥스트_성수_지수'] = (
    final_agg_next['상권_유입_강도'] * 0.5 + 
    final_agg_next['MZ_유입_비중'] * 0.3 + 
    final_agg_next['상권지표_점수'] * 0.2
) * 100

print(final_agg_next.sort_values(by='넥스트_성수_지수', ascending=False).head(10))

# %%
# 1. 전 기간(df_total)에 대해 행정동별 평균 지표 산출
# (연도별 변화를 보기 위해 groupby에 '연도'를 포함하거나, 전체 평균을 냅니다)
all_time_agg = final_df.groupby('행정동_코드_명').agg({
    'MZ_유입_비중': 'mean',
    '상권_유입_강도': 'mean',
    '상권지표_점수': 'mean',
    '당월_매출_금액': 'mean'
}).reset_index()

# 2. 전체 기간 기준 정규화
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
all_time_agg[['MZ_유입_비중', '상권_유입_강도', '상권지표_점수']] = scaler.fit_transform(
    all_time_agg[['MZ_유입_비중', '상권_유입_강도', '상권지표_점수']]
)

# 3. 넥스트 성수 지수 산출 (4:4:2)
all_time_agg['넥스트_성수_지수'] = (
    all_time_agg['MZ_유입_비중'] * 0.4 + 
    all_time_agg['상권_유입_강도'] * 0.4 + 
    all_time_agg['상권지표_점수'] * 0.2
) * 100

# 4. 전체 기간 통합 랭킹 TOP 20
total_ranking = all_time_agg.sort_values(by='넥스트_성수_지수', ascending=False)
print(total_ranking[['행정동_코드_명', '넥스트_성수_지수', 'MZ_유입_비중', '상권_유입_강도']].head(20))

# %%
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정 (환경에 따라 'NanumBarunGothic' 또는 'Malgun Gothic' 사용)
plt.rc('font', family='NanumBarunGothic') 

plt.figure(figsize=(14, 9))

# 1. 회귀선이 포함된 산점도 (weight 대신 linewidth 사용)
sns.regplot(x='상권_유입_강도', y='넥스트_성수_지수', data=all_time_agg, 
            scatter_kws={'alpha':0.4, 'color':'gray', 's':50}, 
            line_kws={'color':'#e74c3c', 'linewidth':3}) # 여기서 수정됨

# 2. 주요 지역(TOP 15)에 라벨링 (수유, 번동, 서교 등)
# 점들이 겹치지 않게 하기 위해 약간의 오프셋을 줍니다.
top_15 = all_time_agg.sort_values(by='넥스트_성수_지수', ascending=False).head(15)

for i, row in top_15.iterrows():
    plt.text(row['상권_유입_강도'] + 0.005, row['넥스트_성수_지수'], row['행정동_코드_명'], 
             fontsize=11, fontweight='bold', va='center', alpha=0.9)

# 3. 그래프 스타일링
plt.title('상권 유입 강도(독립변수)와 넥스트 성수 지수(종속변수)의 상관관계', fontsize=18, pad=20)
plt.xlabel('상권 유입 강도 (외부 집객력)', fontsize=13)
plt.ylabel('넥스트 성수 지수 (성장 잠재력)', fontsize=13)
plt.axvline(all_time_agg['상권_유입_강도'].mean(), color='blue', linestyle='--', alpha=0.3) # 평균선 추가
plt.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.show()

# %%
# 1. 독립변수 정규화 (Min-Max Scaling)
# 이제 '집객시설_총_수'가 수유동의 일시적 노이즈를 누르는 '안전장치' 역할을 합니다.
cols_to_scale = ['MZ_유입_비중', '상권_유입_강도', '집객시설_총_수', '상권지표_점수']
final_df[cols_to_scale] = scaler.fit_transform(final_df[cols_to_scale])

# 2. 넥스트 성수 지수 4.0 (가중치 조정)
# 시설이 부족한데 유입만 많은 지역을 걸러내기 위해 '집객시설'에 힘을 줍니다.
final_df['최종_넥스트_성수_지수'] = (
    final_df['집객시설_총_수'] * 0.3 +   # 상권의 물리적 기초 (Hard)
    final_df['상권_유입_강도'] * 0.3 +   # 외부 집객 동력 (Dynamic)
    final_df['MZ_유입_비중'] * 0.3 +      # 수요의 성격 (Soft)
    final_df['상권지표_점수'] * 0.1      # 변화의 속도
) * 100

# 3. 랭킹 재산출
final_ranking = final_df.sort_values(by='최종_넥스트_성수_지수', ascending=False)
print(final_ranking[['행정동_코드_명', '최종_넥스트_성수_지수', '집객시설_총_수', '상권_유입_강도']].head(15))

# %% [markdown]
# # 지수를 다시 만들어서 회귀를 시켜봄.

# %%
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import re

# 1. 분석용 복사본 생성 (원본 보존)
df_analysis = final_df.copy()

# 2. 행정동 명칭 통합 (종로1234가동 등 유령문자 제거)
df_analysis['행정동_코드_명'] = df_analysis['행정동_코드_명'].str.replace(r'[^가-힣0-9]', '', regex=True)

# 3. [핵심] 이름이 통합된 동네들의 원천 데이터 합산 (중요!)
# 비중(%)을 평균 내는 게 아니라, 전체 합계를 구한 뒤 나중에 다시 계산해야 정확합니다.
df_grouped = df_analysis.groupby(['기준_년분기_코드', '행정동_코드_명']).agg({
    '당월_매출_금액': 'sum',
    'MZ_유동인구': 'sum',
    '총_유동인구_수': 'sum',
    '연령대_20_매출_금액': 'sum',
    '연령대_30_매출_금액': 'sum',
    '집객시설_수': 'max',          # 시설은 합치는 게 아니라 해당 지역의 규모임
    '지하철_역_수': 'max',          # 역 수도 마찬가지
    '상권지표_점수': 'mean',
    '운영_영업_개월_평균': 'mean',
    '총_유동인구_수': 'sum'         # 유입 강도 대용 지표
}).reset_index()

# 4. [핵심] 회귀식에 들어갈 독립변수(X) 재산출
# 합쳐진 총합을 기준으로 비중을 구해야 '종로'의 진짜 파괴력이 나옵니다.
df_grouped['MZ_유동_비중'] = df_grouped['MZ_유동인구'] / df_grouped['총_유동인구_수']
df_grouped['MZ_매출_비중'] = (df_grouped['연령대_20_매출_금액'] + df_grouped['연령대_30_매출_금액']) / df_grouped['당월_매출_금액']

# 5. 정규화 (Min-Max Scaling)
scaler = MinMaxScaler()
# 회귀식에 쓰일 6개 독립변수 선정
cols = ['집객시설_수', '지하철_역_수', 'MZ_유동_비중', 'MZ_매출_비중', '운영_영업_개월_평균', '상권지표_점수']
df_grouped[cols] = scaler.fit_transform(df_grouped[cols])

# 6. [회귀 수식 반영] 가중치에 따른 최종 점수 산출
# 인프라(35%) + MZ영향력(40%) + 지속성(25%)
df_grouped['최종_지수'] = (
    (df_grouped['집객시설_수'] * 0.25 + df_grouped['지하철_역_수'] * 0.10) +  # Infra
    (df_grouped['MZ_유동_비중'] * 0.15 + df_grouped['MZ_매출_비중'] * 0.25) +  # MZ Power
    (df_grouped['상권지표_점수'] * 0.15 + df_grouped['운영_영업_개월_평균'] * 0.10) # Dynamics
) * 100

# 7. 행정동별 전 기간 평균 랭킹 출력
final_ranking = df_grouped.groupby('행정동_코드_명')['최종_지수'].mean().sort_values(ascending=False)
print("--- [넥스트 성수 지수] 데이터 클리닝 및 수식 반영 최종 결과 ---")
print(final_ranking.head(15))

# %%
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import re

# 1. 분석용 복사본 생성
df_analysis = final_df.copy()

# 2. 행정동 명칭 통합 (성수동 전체 + 종로 전체)
# '성수'가 들어가면 무조건 '성수동_통합', '종로'가 들어가면 '종로_통합'
def unify_name(name):
    name = re.sub(r'[^가-힣0-9]', '', name)
    if '성수' in name: return '성수동_통합'
    if '종로' in name: return '종로_통합'
    return name

df_analysis['행정동_코드_명'] = df_analysis['행정동_코드_명'].apply(unify_name)

# 3. 데이터 집계 (비중 재산출을 위해 원천 데이터 sum)
df_grouped = df_analysis.groupby(['기준_년분기_코드', '행정동_코드_명']).agg({
    '당월_매출_금액': 'sum',
    'MZ_유동인구': 'sum',
    '총_유동인구_수': 'sum',
    '연령대_20_매출_금액': 'sum',
    '연령대_30_매출_금액': 'sum',
    '집객시설_수': 'max', 
    '지하철_역_수': 'max',
    '상권지표_점수': 'mean',
    '운영_영업_개월_평균': 'mean'
}).reset_index()

# 4. 가중치 변수 재계산
df_grouped['MZ_유동_비중'] = df_grouped['MZ_유동인구'] / df_grouped['총_유동인구_수']
df_grouped['MZ_매출_비중'] = (df_grouped['연령대_20_매출_금액'] + df_grouped['연령대_30_매출_금액']) / df_grouped['당월_매출_금액']

# 5. 정규화 및 최종 지수 산출
scaler = MinMaxScaler()
cols = ['집객시설_수', '지하철_역_수', 'MZ_유동_비중', 'MZ_매출_비중', '운영_영업_개월_평균', '상권지표_점수']
df_grouped[cols] = scaler.fit_transform(df_grouped[cols])

# 회귀 수식 가중치 적용
df_grouped['최종_지수'] = (
    (df_grouped['집객시설_수'] * 0.25 + df_grouped['지하철_역_수'] * 0.10) +
    (df_grouped['MZ_유동_비중'] * 0.15 + df_grouped['MZ_매출_비중'] * 0.25) +
    (df_grouped['상권지표_점수'] * 0.15 + df_grouped['운영_영업_개월_평균'] * 0.10)
) * 100

# 6. 최종 랭킹 확인
final_ranking = df_grouped.groupby('행정동_코드_명')['최종_지수'].mean().sort_values(ascending=False)
print(final_ranking.head(20))

# %%
# 성수동_통합의 개별 지표 점수 확인
seongsu_score = df_grouped[df_grouped['행정동_코드_명'] == '성수동_통합']
print("--- [성수동_통합] 상세 성적표 ---")
print(seongsu_score[['MZ_유동_비중', 'MZ_매출_비중', '집객시설_수', '상권지표_점수', '최종_지수']])

# 전체 순위에서 몇 위인지 확인
all_ranks = df_grouped.groupby('행정동_코드_명')['최종_지수'].mean().sort_values(ascending=False).reset_index()
print(f"\n성수동의 현재 순위: {all_ranks[all_ranks['행정동_코드_명'] == '성수동_통합'].index[0] + 1}위")

# %%
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import re

# 1. 분석용 복사본 생성
df_analysis = final_df.copy()

# 2. 행정동 명칭 전처리 (성수만 통합)
# 종로는 이미 '종로1234가동'으로 묶여 있으니 특수문자만 정리하면 됩니다.
def unify_names(name):
    # 특수문자 및 공백 제거
    clean_name = re.sub(r'[^가-힣0-9]', '', name)
    # 성수동 시리즈는 하나로 통합
    if '성수' in clean_name:
        return '성수동_통합'
    return clean_name

df_analysis['행정동_코드_명'] = df_analysis['행정동_코드_명'].apply(unify_names)

# 3. 데이터 그룹화 (실측 데이터 기반 합산)
df_grouped = df_analysis.groupby(['기준_년분기_코드', '행정동_코드_명']).agg({
    '당월_매출_금액': 'sum',
    'MZ_유동인구': 'sum',
    '총_유동인구_수': 'sum',
    '연령대_20_매출_금액': 'sum',
    '연령대_30_매출_금액': 'sum',
    '집객시설_수': 'max', 
    '지하철_역_수': 'max',
    '운영_영업_개월_평균': 'mean'
}).reset_index()

# 4. 가중치 변수 재계산 (비중 및 상권 에너지)
# '상권_에너지_지수'는 (매출액 * 시설수)로 계산하여 논밭(시설수 0에 가까움)을 원천 차단합니다.
df_grouped['MZ_유동_비중'] = df_grouped['MZ_유동인구'] / df_grouped['총_유동인구_수']
df_grouped['MZ_매출_비중'] = (df_grouped['연령대_20_매출_금액'] + df_grouped['연령대_30_매출_금액']) / df_grouped['당월_매출_금액']
df_grouped['상권_에너지_지수'] = df_grouped['당월_매출_금액'] * df_grouped['집객시설_수']

# 5. 정규화
scaler = MinMaxScaler()
cols = ['집객시설_수', '지하철_역_수', 'MZ_유동_비중', 'MZ_매출_비중', '운영_영업_개월_평균', '상권_에너지_지수']
df_grouped[cols] = scaler.fit_transform(df_grouped[cols])

# 6. 최종 넥스트 성수 수식 (NSI) 적용
df_grouped['최종_지수'] = (
    (df_grouped['집객시설_수'] * 0.25 + df_grouped['지하철_역_수'] * 0.10) + # 인프라(35%)
    (df_grouped['MZ_매출_비중'] * 0.35 + df_grouped['MZ_유동_비중'] * 0.10) + # MZ파워(45%)
    (df_grouped['상권_에너지_지수'] * 0.10 + df_grouped['운영_영업_개월_평균'] * 0.10) # 지속/에너지(20%)
) * 100

# 7. 최종 랭킹
final_ranking = df_grouped.groupby('행정동_코드_명')['최종_지수'].mean().sort_values(ascending=False)
print(final_ranking.head(20))

# %%
# 1. 행정동별로 전 기간 평균 점수를 계산하여 순위 매기기
final_ranking_df = df_grouped.groupby('행정동_코드_명')['최종_지수'].mean().sort_values(ascending=False).reset_index()
final_ranking_df.index = final_ranking_df.index + 1  # 순위를 1부터 시작하게 변경
final_ranking_df.columns = ['행정동_코드_명', 'NSI_지수']

# 2. 상위 30위 출력
print("--- [NSI 8.0] NEXT 성수 지수 상위 30위 ---")
print(final_ranking_df.head(30))

print("\n" + "="*50)

# 3. '성수동_통합'이 몇 위에 있는지 찾아내기
try:
    seongsu_rank = final_ranking_df[final_ranking_df['행정동_코드_명'] == '성수동_통합'].index[0]
    seongsu_score = final_ranking_df.loc[seongsu_rank, 'NSI_지수']
    print(f"★ 성수동_통합의 현재 위치: {seongsu_rank}위 (점수: {seongsu_score:.2f}점)")
    
    # 성수동 앞뒤 순위 확인 (성수가 왜 밀렸는지 비교용)
    print(f"\n--- 성수동 인근 순위 (Rank {max(1, seongsu_rank-2)} ~ {seongsu_rank+2}) ---")
    print(final_ranking_df.iloc[max(0, seongsu_rank-3):seongsu_rank+2])
    
except IndexError:
    print("성수동_통합 데이터가 리스트에 없습니다. 통합 로직을 다시 확인해주세요.")

# %%
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import re

# 1. 분석용 복사본 생성 (이번에는 성수 통합 안 함!)
df_analysis = final_df.copy()

# 2. 명칭 전처리 (특수문자만 제거)
df_analysis['행정동_코드_명'] = df_analysis['행정동_코드_명'].str.replace(r'[^가-힣0-9]', '', regex=True)

# 3. 데이터 그룹화 (행정동별 개별 집계)
df_grouped = df_analysis.groupby(['기준_년분기_코드', '행정동_코드_명']).agg({
    '당월_매출_금액': 'sum',
    'MZ_유동인구': 'sum',
    '총_유동인구_수': 'sum',
    '연령대_20_매출_금액': 'sum',
    '연령대_30_매출_금액': 'sum',
    '집객시설_수': 'max', 
    '지하철_역_수': 'max',
    '운영_영업_개월_평균': 'mean'
}).reset_index()

# 4. 가중치 변수 재계산
df_grouped['MZ_유동_비중'] = df_grouped['MZ_유동인구'] / df_grouped['총_유동인구_수']
df_grouped['MZ_매출_비중'] = (df_grouped['연령대_20_매출_금액'] + df_grouped['연령대_30_매출_금액']) / df_grouped['당월_매출_금액']
df_grouped['상권_에너지_지수'] = df_grouped['당월_매출_금액'] * df_grouped['집객시설_수']

# 5. 정규화 및 NSI 8.0 수식 적용 (이전과 동일 가중치)
scaler = MinMaxScaler()
cols = ['집객시설_수', '지하철_역_수', 'MZ_유동_비중', 'MZ_매출_비중', '운영_영업_개월_평균', '상권_에너지_지수']
df_grouped[cols] = scaler.fit_transform(df_grouped[cols])

df_grouped['최종_지수'] = (
    (df_grouped['집객시설_수'] * 0.25 + df_grouped['지하철_역_수'] * 0.10) +
    (df_grouped['MZ_매출_비중'] * 0.35 + df_grouped['MZ_유동_비중'] * 0.10) +
    (df_grouped['상권_에너지_지수'] * 0.10 + df_grouped['운영_영업_개월_평균'] * 0.10)
) * 100

# 6. 최종 랭킹 확인
final_ranking = df_grouped.groupby('행정동_코드_명')['최종_지수'].mean().sort_values(ascending=False).reset_index()
final_ranking.index = final_ranking.index + 1
print(final_ranking.head(101)) # 101위 리스트 확인

# %%
import statsmodels.api as sm

# 1. 검증에 사용할 변수들 선택 (우리가 수식에 쓴 독립변수들)
features = ['집객시설_수', '지하철_역_수', 'MZ_유동_비중', 'MZ_매출_비중', '상권_에너지_지수', '운영_영업_개월_평균']
X = df_grouped[features]
y = df_grouped['최종_지수']

# 2. 상수항(Intercept) 추가
X = sm.add_constant(X)

# 3. OLS(Ordinary Least Squares) 모델 피팅
model = sm.OLS(y, X).fit()

# 4. 결과 요약 보고서 출력
print("--- [NSI 8.0] 회귀 모델 통계적 검증 결과 ---")
print(model.summary())

# %%
# 1. 전체 행정동 평균 점수 계산 및 순위 생성
# 분기별 데이터를 행정동별 평균으로 요약
df_final_avg = df_grouped.groupby('행정동_코드_명').mean().reset_index()

# 2. 전체 순위 매기기 (최종_지수 기준 내림차순)
df_final_avg = df_final_avg.sort_values(ascending=False, by='최종_지수').reset_index(drop=True)
df_final_avg['순위'] = df_final_avg.index + 1  # 1위부터 시작하는 순위 컬럼 추가

# 3. 성수가 포함된 행정동만 필터링
seongsu_results = df_final_avg[df_final_avg['행정동_코드_명'].str.contains('성수')].copy()

# 4. 결과 출력 (주요 지표 포함)
print("--- [성수동 4개 행정동 정밀 분석 결과] ---")
output_cols = ['순위', '행정동_코드_명', '최종_지수', 'MZ_매출_비중', '운영_영업_개월_평균', '집객시설_수']
print(seongsu_results[output_cols])


# %%
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import re

# 1. 분석용 복사본 생성 (이번에는 성수 통합 안 함!)
df_analysis = final_df.copy()

# 2. 명칭 전처리 (특수문자만 제거)
df_analysis['행정동_코드_명'] = df_analysis['행정동_코드_명'].str.replace(r'[^가-힣0-9]', '', regex=True)

# 3. 데이터 그룹화 (행정동별 개별 집계)
df_grouped = df_analysis.groupby(['기준_년분기_코드', '행정동_코드_명']).agg({
    '당월_매출_금액': 'sum',
    'MZ_유동인구': 'sum',
    '총_유동인구_수': 'sum',
    '연령대_20_매출_금액': 'sum',
    '연령대_30_매출_금액': 'sum',
    '집객시설_수': 'max', 
    '지하철_역_수': 'max',
    '운영_영업_개월_평균': 'mean'
}).reset_index()

# 4. 가중치 변수 재계산
df_grouped['MZ_유동_비중'] = df_grouped['MZ_유동인구'] / df_grouped['총_유동인구_수']
df_grouped['MZ_매출_비중'] = (df_grouped['연령대_20_매출_금액'] + df_grouped['연령대_30_매출_금액']) / df_grouped['당월_매출_금액']
df_grouped['상권_에너지_지수'] = df_grouped['당월_매출_금액'] * df_grouped['집객시설_수']

# 5. 정규화 및 NSI 8.0 수식 적용 (이전과 동일 가중치)
scaler = MinMaxScaler()
cols = ['집객시설_수', '지하철_역_수', 'MZ_유동_비중', 'MZ_매출_비중', '운영_영업_개월_평균', '상권_에너지_지수']
df_grouped[cols] = scaler.fit_transform(df_grouped[cols])

df_grouped['최종_지수'] = (
    (df_grouped['집객시설_수'] * 0.25 + df_grouped['지하철_역_수'] * 0.10) +
    (df_grouped['MZ_매출_비중'] * 0.35 + df_grouped['MZ_유동_비중'] * 0.10) +
    (df_grouped['상권_에너지_지수'] * 0.10 + df_grouped['운영_영업_개월_평균'] * 0.10)
) * 100

# 6. 최종 랭킹 생성 (기존 코드 연장)
final_ranking = df_grouped.groupby('행정동_코드_명')['최종_지수'].mean().sort_values(ascending=False).reset_index()
final_ranking.columns = ['행정동', '최종_지수'] # 컬럼명 정리
final_ranking.insert(0, 'Rank', range(1, len(final_ranking) + 1)) # 순위 삽입

# 7. 상위 101위만 추출
top_101 = final_ranking.head(101).copy()

# 4. CSV로 저장 (한글 깨짐 방지를 위해 utf-8-sig 사용)
top_101.to_csv('final_ranking_101.csv', index=False, encoding='utf-8-sig')

print("✅ csv 파일이 생성되었습니다. 엑셀에서 'final_ranking_101.csv'를 여세요!")


# %%
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import MinMaxScaler

# 1. 데이터 준비 및 전처리
df_analysis = final_df.copy()
df_analysis['행정동_코드_명'] = df_analysis['행정동_코드_명'].str.replace(r'[^가-힣0-9]', '', regex=True)

# 2. 행정동별/분기별 그룹화
df_grouped = df_analysis.groupby(['기준_년분기_코드', '행정동_코드_명']).agg({
    '당월_매출_금액': 'sum',
    'MZ_유동인구': 'sum',
    '총_유동인구_수': 'sum',
    '연령대_20_매출_금액': 'sum',
    '연령대_30_매출_금액': 'sum',
    '집객시설_수': 'max', 
    '지하철_역_수': 'max',
    '운영_영업_개월_평균': 'mean'
}).reset_index().sort_values(['행정동_코드_명', '기준_년분기_코드'])

# 3. 타겟 변수: MZ 유동인구 증가율
df_grouped['MZ_유동_증가율'] = df_grouped.groupby('행정동_코드_명')['MZ_유동인구'].pct_change()
df_grouped = df_grouped.replace([np.inf, -np.inf], np.nan).dropna(subset=['MZ_유동_증가율'])

# 4. 독립변수 재구성 (MZ 관련 모든 변수 제외)
# 상권_에너지_지수 계산 시 '당월_매출_금액'은 전체 매출이므로 유지
df_grouped['상권_에너지_지수'] = df_grouped['당월_매출_금액'] * df_grouped['집객시설_수']

# 5. 정규화 및 최종 변수 선정
scaler = MinMaxScaler()
# 순수 상권 환경 변수들로만 구성
cols = ['집객시설_수', '지하철_역_수', '운영_영업_개월_평균', '상권_에너지_지수']
df_grouped[cols] = scaler.fit_transform(df_grouped[cols])

# 6. OLS 회귀분석 실행
X = df_grouped[cols]
X = sm.add_constant(X)
Y = df_grouped['MZ_유동_증가율']

model = sm.OLS(Y, X).fit()
weights = model.params

# 7. 최종 지수 산출 (통계 가중치 반영)
df_grouped['최종_지수'] = sum(df_grouped[col] * weights[col] for col in cols)

# 8. 최종 랭킹 및 101위 리스트업
# 전체 기간에 대한 행정동별 평균 점수로 랭킹 산정
final_ranking = df_grouped.groupby('행정동_코드_명')['최종_지수'].mean().sort_values(ascending=False).reset_index()
final_ranking.insert(0, 'Rank', range(1, len(final_ranking) + 1))

# CSV 저장 (이제 이 리스트를 들고 네이버 트렌드로 가서 검증하시면 됩니다!)
final_ranking.head(50).to_csv('NSI_9.0_Candidate_List.csv', index=False, encoding='utf-8-sig')

# 조원들에게 보여줄 통계 근거 출력
print(model.summary())


