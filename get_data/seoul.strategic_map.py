import pandas as pd
import folium
from folium.plugins import Fullscreen

# 1. 데이터 로드 및 분석
df = pd.read_csv('quad_analysis2.csv')
cols_to_norm = ['CAGR', 'avg_naver', 'blog_post']

# 순위(Rank) 변환
df_rank = df[cols_to_norm].rank(pct=True)
w1, w2, w3 = 0.34, 0.33, 0.33 

# X, Y 지수 생성 (0~1 사이 값)
df['X_Index'] = (df_rank['CAGR'] * w1) + (df_rank['avg_naver'] * w2) + (df_rank['blog_post'] * w3)
df['Y_Index'] = df['하이브리드_점수'].rank(pct=True)

# 2. 위경도 딕셔너리 (성수동 키값 반영 버전)
geo_master = {
    '가산동': [37.4766, 126.8872], '여의동': [37.5244, 126.9317], '서교동': [37.5543, 126.9208],
    '압구정동': [37.5303, 127.0305], '상암동': [37.5815, 126.8860], '삼성1동': [37.5144, 127.0626],
    '서초2동': [37.4877, 127.0315], '대치4동': [37.4997, 127.0526], '성수동': [37.5415, 127.0435],
    '청담동': [37.5251, 127.0492], '문정2동': [37.4851, 127.1202], '용강동': [37.5413, 126.9408],
    '서초3동': [37.4836, 127.0116], '신당동': [37.5566, 127.0163], '염리동': [37.5463, 126.9458],
    '양평2동': [37.5381, 126.8920], '송파2동': [37.5019, 127.1121], '방배1동': [37.4831, 126.9934],
    '논현2동': [37.5173, 127.0372], '중림동': [37.5595, 126.9672], '구로3동': [37.4851, 126.8943],
    '효창동': [37.5435, 126.9632], '삼성2동': [37.5111, 127.0459]
}

# 3. 지도 초기화
m = folium.Map(location=[37.55, 126.98], zoom_start=12, tiles='CartoDB positron')

# 4. 분석 결과를 바탕으로 지도에 마커 추가
for i, row in df.iterrows():
    name = row['행정동']
    if name not in geo_master: continue  # 좌표 없는 동네는 패스
    
    x, y = row['X_Index'], row['Y_Index']
    coords = geo_master[name]
    
    # 사분면 판정 및 스타일 설정 (님의 Matplotlib 색상 로직 반영)
    if x >= 0.5 and y >= 0.5:
        color, label = '#e74c3c', '1사분면 (핵심)'
    elif x < 0.5 and y >= 0.5:
        color, label = '#f1c40f', '2사분면 (잠재)'
    elif x < 0.5 and y < 0.5:
        color, label = '#95a5a6', '3사분면 (정체)'
    else:
        color, label = '#3498db', '4사분면 (효율)'
        
    # 유망주(송파2동, 양평2동) 및 추격자(신당동) 강조 로직 추가
    weight = 1
    radius = 12
    if name in ['송파2동', '양평2동', '신당동']:
        weight = 4  # 테두리 강조
        radius = 16 # 크기 키움
        
    # 마커 추가
    folium.CircleMarker(
        location=coords,
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        weight=weight,
        tooltip=f"{name} ({label})",
        popup=folium.Popup(f"""
            <div style='width:150px'>
                <b>{name}</b><br>
                X_Rank: {x:.2f}<br>
                Y_Rank: {y:.2f}<br>
                <hr>
                {label}
            </div>""", max_width=200)
    ).add_to(m)

# 5. 저장 및 확인
Fullscreen().add_to(m)
m.save('seoul_strategic_map.html')
print("지도 파일 생성 완료!")