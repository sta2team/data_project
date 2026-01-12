import requests
import pandas as pd
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API")

# @@@@@@@ 찾을 키워드 입력하기 @@@@@@@
keyword = "성수 맛집"
publishedAfter = "2024-09-30T15:00:00Z"
publishedBefore = "2025-09-30T14:59:59Z"
order = "relevance"
# order = "viewCount"

def get_youtube_data(query, publishedAfter, publishedBefore, total_count=100, max_results=50, order="relevance", region_code="KR"):
    """
    YouTube 검색 결과를 가져와서 JSON 파일로 저장
    
    Args:
        query (str): 검색 키워드
        total_count (int): 총 가져올 결과 수 (페이지네이션으로 최대 100개)
        max_results (int): 한 번에 가져올 결과 수 (0-50)
        order (str): 정렬 방식
                    (date, rating, relevance(=default, 관련성), title, videoCount, viewCount)
        region_code (str): 지역 코드 ex) KR
    
    Returns:
        dict: 전체 응답 데이터
    """
    
    base_url = "https://www.googleapis.com/youtube/v3/search"
    
    all_items = []
    next_page_token = None
    total_fetched = 0
    total_results_from_api = 0  # API에서 제공하는 totalResults
    results_per_page_from_api = 0  # API에서 제공하는 resultsPerPage
    
    while total_fetched < total_count:
        params = {
            "key": API_KEY,
            "part": "snippet",
            "q": query,
            "publishedAfter": publishedAfter,
            "publishedBefore": publishedBefore,
            "type": "video",
            "maxResults": min(max_results, total_count - total_fetched),
            "order": order,
            "regionCode": region_code
        }
        
        if next_page_token:
            params["pageToken"] = next_page_token
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # 첫 번째 요청에서 pageInfo 저장
            if total_fetched == 0:
                page_info = data.get("pageInfo", {})
                total_results_from_api = page_info.get("totalResults", 0)
                results_per_page_from_api = page_info.get("resultsPerPage", 0)
            
            # items에서 필요한 필드만 추출
            items = data.get("items", [])
            for item in items:
                filtered_item = {
                    "etag": item.get("etag"),
                    "id": item.get("id"),
                    "snippet": {
                        "publishedAt": item["snippet"].get("publishedAt"),
                        "channelId": item["snippet"].get("channelId"),
                        "title": item["snippet"].get("title"),
                        "description": item["snippet"].get("description"),
                        "channelTitle": item["snippet"].get("channelTitle"),
                        "publishTime": item["snippet"].get("publishTime")
                    }
                }
                all_items.append(filtered_item)
            
            total_fetched += len(items)
            
            print(f"가져온 데이터: {len(items)}개 (총: {total_fetched}개)")
            
            # 다음 페이지 토큰
            next_page_token = data.get("nextPageToken")
            
            if not next_page_token or total_fetched >= total_count:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            break
    
    # 최종 결과 구성 (API 응답의 pageInfo 값 사용)
    result = {
        "kind": "youtube#searchListResponse",
        "regionCode": region_code,
        "pageInfo": {
            "totalResults": total_results_from_api,
            "resultsPerPage": results_per_page_from_api
        },
        "items": all_items
    }
    
    # 파일 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"youtube_{query.replace(' ', '_').replace('|', '_')}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n파일 저장 완료: {filename}")
    print(f"총 {len(all_items)}개의 비디오 정보를 저장했습니다.")
    
    return result


# 사용 예시
if __name__ == "__main__":
    result = get_youtube_data(
        query=keyword,
        publishedAfter = publishedAfter,
        publishedBefore = publishedBefore,
        total_count=100,  # 총 100개 가져오기
        max_results=50,   # 한 번에 50개씩 (0-50 범위)
        order= order,
        region_code="KR"
    )