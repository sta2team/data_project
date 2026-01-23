import requests
from dotenv import load_dotenv
import os
import json
import csv
from datetime import datetime
import config as cf

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API")

# @@@@@@@ config.py에서 설정 @@@@@@@

# 단일 키워드 설정 
# keyword = "가산 카페"

print(f"\n{'='*50}")
print(f"📋 생성된 키워드: {len(cf.KEYWORDS)}개") 
for i, kw in enumerate(cf.KEYWORDS, 1): 
    print(f"  {i}. {kw}") 
print(f"{'='*50}\n")

def search_youtube(query, publishedAfter, publishedBefore, total_count=100, max_results=50, order="relevance", region_code="KR"):
    """
    YouTube 검색 결과를 가져오기

    Args:
        query (str): 검색 키워드
        publishedAfter (str): 검색 시작 날짜
        publishedBefore (str): 검색 종료 날짜
        total_count (int): 총 가져올 결과 수
        max_results (int): 한 번에 가져올 결과 수 (0-50)
        order (str): 정렬 방식 (date, rating, relevance, title, videoCount, viewCount)
        region_code (str): 지역 코드

    Returns:
        tuple: (video_ids 리스트, all_items 리스트, 검색 파라미터 dict, page_info dict)
    """

    base_url = "https://www.googleapis.com/youtube/v3/search"

    video_ids = []
    all_items = []
    next_page_token = None
    total_fetched = 0
    total_results_from_api = 0
    results_per_page_from_api = 0

    search_params = {
        "query": query,
        "publishedAfter": cf.publishedAfter,
        "publishedBefore": cf.publishedBefore,
        "order": cf.order,
        "regionCode": region_code,
        "requestedCount": total_count,
        "maxResultsPerPage": max_results
    }

    print(f"검색 키워드: {query}")
    print(f"기간: {cf.publishedAfter} ~ {cf.publishedBefore}")
    print("-" * 50)

    while total_fetched < total_count:
        params = {
            "key": API_KEY,
            "part": "snippet",
            "q": query,
            "publishedAfter": cf.publishedAfter,
            "publishedBefore": cf.publishedBefore,
            "type": "video",
            "maxResults": min(max_results, total_count - total_fetched),
            "order": cf.order,
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

            items = data.get("items", [])
            for item in items:
                # video ID 추출
                if "id" in item and "videoId" in item["id"]:
                    video_ids.append(item["id"]["videoId"])

                # 원본 데이터 저장 (keyword_search.py 형식)
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
            print(f"[검색] 가져온 데이터: {len(items)}개 (총: {total_fetched}개)")

            next_page_token = data.get("nextPageToken")

            if not next_page_token or total_fetched >= total_count:
                break

        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            break

    page_info = {
        "totalResults": total_results_from_api,
        "resultsPerPage": results_per_page_from_api
    }

    return video_ids, all_items, search_params, page_info

def is_valid_content(title, description):
    """제목과 설명에 금지어가 포함되어 있는지 확인"""
    # 공백을 제거하고 소문자로 변환하여 검색 정확도를 높입니다.
    text = (str(title) + " " + str(description)).replace(" ", "").lower()
    for word in cf.STOPWORDS:
        if word in text:
            return False
    return True

def get_duration_seconds(duration_str):
    """ISO 8601 duration을 초로 변환 (예: PT2M30S → 150초)""" # <----- duration 변환 함수 추가
    import re
    if not duration_str:
        return 0
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds
    return 0


'''
def get_video_details(video_ids):
    """
    YouTube 동영상 세부 정보를 가져와서 필요한 필드만 반환

    Args:
        video_ids (list): 비디오 ID 리스트

    Returns:
        list: 정리된 비디오 데이터 리스트
    """

    base_url = "https://www.googleapis.com/youtube/v3/videos"
    all_items = []
    batch_size = 50

    print("-" * 50)

    for i in range(0, len(video_ids), batch_size):
        batch_ids = video_ids[i:i+batch_size]

        params = {
            "key": API_KEY,
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch_ids)
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])

            for item in items:
                statistics = item.get("statistics", {})
                cleaned_item = {
                    "id": item.get("id"),
                    "publishedAt": item.get("snippet", {}).get("publishedAt"),
                    "title": item.get("snippet", {}).get("title"),
                    "description": item.get("snippet", {}).get("description"),
                    "channelTitle": item.get("snippet", {}).get("channelTitle"),
                    "categoryId": item.get("snippet", {}).get("categoryId"),
                    "viewCount": statistics.get("viewCount"),
                    "likeCount": statistics.get("likeCount"),
                    "commentCount": statistics.get("commentCount")
                }
                all_items.append(cleaned_item)

            print(f"[상세] 가져온 데이터: {len(items)}개 (총: {len(all_items)}개)")

        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            break

    return all_items
'''

def get_video_details(video_ids):
    """
    YouTube 동영상 세부 정보를 가져와서 필요한 필드만 반환
    + 개선된 다단계 필터링 적용 # <----- 개선된 필터링
    """

    base_url = "https://www.googleapis.com/youtube/v3/videos"
    all_items = []
    batch_size = 50
    
    # 필터링 통계 # <----- 필터링 통계 추적
    stats = {
        'total': 0,
        'filtered_channel': 0,
        'filtered_stopwords': 0,
        'filtered_title': 0,
        'filtered_duration': 0,
        'filtered_ads': 0,
        'passed': 0
    }

    print("-" * 50)

    for i in range(0, len(video_ids), batch_size):
        batch_ids = video_ids[i:i+batch_size]

        params = {
            "key": API_KEY,
            "part": "snippet,statistics,contentDetails",  
            "id": ",".join(batch_ids)
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            
            stats['total'] += len(items)

            for item in items:
                snippet = item.get("snippet", {})
                title = snippet.get("title", "")
                description = snippet.get("description", "")
                channel_title = snippet.get("channelTitle", "")
                
                # 1️⃣ 채널 블랙리스트 필터 # <----- 채널 필터
                if channel_title in cf.CHANNEL_BLACKLIST:
                    stats['filtered_channel'] += 1
                    continue
                
                # 2️⃣ Stopwords 필터 (기존) # <----- 금지어 필터
                if not is_valid_content(title, description):
                    stats['filtered_stopwords'] += 1
                    continue
                
                # 3️⃣ 제목에 필수 키워드 체크 # <----- 제목 키워드 필터
                # if not any(kw in title for kw in cf.REQUIRED_IN_TITLE):
                #     stats['filtered_title'] += 1
                #     continue
                
                # 4️⃣ 영상 길이 확인 # <----- 길이 필터
                content_details = item.get("contentDetails", {})
                duration = content_details.get("duration", "")
                duration_seconds = get_duration_seconds(duration)
                
                if cf.FILTER_SHORTS and duration_seconds < cf.MIN_DURATION:
                    stats['filtered_duration'] += 1
                    continue
                
                # 5️⃣ 협찬 필터 # <----- 협찬 필터
                if cf.FILTER_ADS:
                    text = (title + " " + description).lower()
                    if any(kw.lower() in text for kw in cf.AD_KEYWORDS):
                        stats['filtered_ads'] += 1
                        continue

                # 통과! # <----- 통과한 영상만 저장
                stats['passed'] += 1
                statistics = item.get("statistics", {})

                cleaned_item = {
                    "id": item.get("id"),

                    # --- snippet ---
                    "publishedAt": snippet.get("publishedAt"),
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "channelTitle": snippet.get("channelTitle"),
                    "categoryId": snippet.get("categoryId"),  
                    "tags": ",".join(snippet.get("tags", [])),  

                    # --- statistics ---
                    "viewCount": statistics.get("viewCount"),
                    "likeCount": statistics.get("likeCount"),
                    "commentCount": statistics.get("commentCount"),

                    # --- contentDetails ---
                    "duration": content_details.get("duration"),  
                    "licensedContent": content_details.get("licensedContent")  
                }

                all_items.append(cleaned_item)

            # 배치별 통계 출력 # <----- 상세 통계 출력
            print(f"[상세] 배치 {i//batch_size + 1}: {len(items)}개 중 {stats['passed']-len(all_items)+len(items)}개 유지")

        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            break
    
    # 최종 필터링 통계 # <----- 최종 통계 출력
    print("\n" + "="*70)
    print("📊 필터링 통계")
    print("="*70)
    print(f"  • 총 영상: {stats['total']}개")
    print(f"  • 채널 제외: {stats['filtered_channel']}개")
    print(f"  • 금지어 제외: {stats['filtered_stopwords']}개")
    print(f"  • 제목 불일치: {stats['filtered_title']}개")
    print(f"  • 길이 부족: {stats['filtered_duration']}개")
    print(f"  • 협찬 제외: {stats['filtered_ads']}개")
    print(f"  ✅ 최종 통과: {stats['passed']}개 ({stats['passed']/stats['total']*100:.1f}%)")
    print("="*70 + "\n")

    return all_items


def save_search_result(search_items, search_params, page_info, folder_path, region_code="KR"):
    """
    검색 결과를 JSON 파일로 저장 (keyword_search.py 형식)

    Args:
        search_items (list): 검색 결과 아이템 리스트
        search_params (dict): 검색 파라미터
        page_info (dict): 페이지 정보
        folder_path (str): 저장할 폴더 경로
        region_code (str): 지역 코드

    Returns:
        str: 저장된 파일명
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    query = search_params["query"].replace(" ", "").replace("|", "_")
    filename = os.path.join(folder_path, f"{query}_{timestamp}.json")

    result = {
        "searchParams": search_params,
        "kind": "youtube#searchListResponse",
        "regionCode": region_code,
        "pageInfo": page_info,
        "items": search_items
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[검색 결과 저장] {filename}")

    return filename


def save_cleaned_csv(cleaned_items, search_filename, folder_path):
    """
    정리된 데이터를 CSV 파일로 저장

    Args:
        cleaned_items (list): 정리된 비디오 데이터 리스트
        search_filename (str): 검색 결과 파일명 (CSV 파일명 생성용)
        folder_path (str): 저장할 폴더 경로

    Returns:
        str: 저장된 파일명
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 파일명에서 폴더 경로 제거 후 처리
    base_name = os.path.basename(search_filename).replace(".json", "")
    filename = os.path.join(folder_path, f"{base_name}_data_{timestamp}.csv")

    # CSV 컬럼 순서
    fieldnames = [
        "id",
        "publishedAt",
        "title",
        "description",
        "channelTitle",
        "categoryId",
        "tags",              
        "duration",          
        "licensedContent",   
        "viewCount",
        "likeCount",
        "commentCount"
    ]
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_items)

    print(f"[정리 데이터 저장] {filename}")

    return filename


# 메인 실행
if __name__ == "__main__":
    # from dateutil.relativedelta import relativedelta  # 구간 분할 제거로 불필요

    total_videos = 0
    
    # 전체 키워드 순회 
    for keyword_idx, keyword in enumerate(cf.KEYWORDS, 1): 
        print(f"\n{'#'*70}")
        print(f"키워드 [{keyword_idx}/{len(cf.KEYWORDS)}]: {keyword}") 
        print(f"{'#'*70}")

        # data/키워드명 폴더 생성 (스크립트 파일 위치 기준)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 폴더명에서 특수문자 제거 
        safe_keyword = keyword.split()[0] if ' ' in keyword else keyword # 첫 번째 단어만 폴더명으로 사용
        folder_name = os.path.join(script_dir, "data", safe_keyword.replace(" ", "").replace("|", ""))
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"폴더 생성: {folder_name}/")

        # 구간 분할 제거: 전체 기간을 한 번에 검색 
        print(f"\n{'='*50}")
        print(f"전체 기간 검색: {cf.publishedAfter} ~ {cf.publishedBefore}") 
        print(f"{'='*50}")

        # 1. YouTube 검색 (구간 분할 없이 한 번에 실행) <-----
        video_ids, search_items, search_params, page_info = search_youtube(
            query=keyword,
            publishedAfter=cf.publishedAfter,  # <----- 전체 기간 시작
            publishedBefore=cf.publishedBefore,  # <----- 전체 기간 종료
            total_count=cf.total_count,
            max_results=50,
            order=cf.order,
            region_code="KR"
        )

        if not video_ids:
            print(f"❌ 검색 결과가 없습니다.") # <-----
            continue  # <----- 다음 키워드로 넘어감

        # 2. 검색 결과 저장 (JSON)
        search_filename = save_search_result(search_items, search_params, page_info, folder_name)

        # 3. 비디오 상세 정보 가져오기
        cleaned_items = get_video_details(video_ids)

        # 4. 정리된 데이터 저장 (CSV)
        cleaned_filename = save_cleaned_csv(cleaned_items, search_filename, folder_name)

        total_videos += len(cleaned_items)
        print(f"{len(cleaned_items)}개의 비디오 데이터 저장 완료")
        
        # 키워드별 구분선 
        print(f"\n{'#'*70}") 
        print(f"✅ 키워드 [{keyword_idx}/{len(cf.KEYWORDS)}] 완료: {keyword}") 
        print(f"{'#'*70}\n") 

    print(f"\n{'='*70}") 
    print(f"🎉 전체 완료: 총 {total_videos}개의 비디오 데이터를 저장했습니다.") 
    print(f"📁 저장 위치: {script_dir}/data/") 
    print(f"🔑 처리한 키워드 수: {len(cf.KEYWORDS)}개") 
    print(f"{'='*70}")