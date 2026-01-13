import requests
from dotenv import load_dotenv
import os
import json
import csv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API")

# @@@@@@@ 검색 설정 @@@@@@@
keyword = "부암동 맛집"
publishedAfter = "2020-09-30T15:00:00Z"
publishedBefore = "2025-09-30T14:59:59Z"

order = "relevance"  # date, rating, relevance, title, videoCount, viewCount
total_count = 100


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
        "publishedAfter": publishedAfter,
        "publishedBefore": publishedBefore,
        "order": order,
        "regionCode": region_code,
        "requestedCount": total_count,
        "maxResultsPerPage": max_results
    }

    print(f"검색 키워드: {query}")
    print(f"기간: {publishedAfter} ~ {publishedBefore}")
    print("-" * 50)

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
            "part": "snippet,statistics",
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
    fieldnames = ["id", "publishedAt", "title", "description", "channelTitle", "categoryId", "viewCount", "likeCount", "commentCount"]

    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_items)

    print(f"[정리 데이터 저장] {filename}")

    return filename


# 메인 실행
if __name__ == "__main__":
    from dateutil.relativedelta import relativedelta

    total_videos = 0

    # data/키워드명 폴더 생성 (스크립트 파일 위치 기준)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_name = os.path.join(script_dir, "data", keyword.replace(" ", ""))
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"폴더 생성: {folder_name}/")

    # 날짜+시간 파싱
    start_dt = datetime.strptime(publishedAfter, "%Y-%m-%dT%H:%M:%SZ")
    end_dt = datetime.strptime(publishedBefore, "%Y-%m-%dT%H:%M:%SZ")

    # 시간 부분 추출 (원본 유지용)
    start_time = start_dt.strftime("T%H:%M:%SZ")
    end_time = end_dt.strftime("T%H:%M:%SZ")

    # 1년 단위 구간 생성 (최신 → 과거 순)
    periods = []
    current_end = end_dt
    while current_end > start_dt:
        current_start = current_end - relativedelta(years=1)
        if current_start < start_dt:
            current_start = start_dt
        periods.append((current_start, current_end))
        current_end = current_start

    print(f"총 {len(periods)}개 구간으로 나누어 수집합니다.")

    # 각 구간별로 데이터 수집
    for i, (period_start, period_end) in enumerate(periods, 1):
        period_after = period_start.strftime(f"%Y-%m-%d{start_time}")
        period_before = period_end.strftime(f"%Y-%m-%d{end_time}")

        print(f"\n{'='*50}")
        print(f"[{i}/{len(periods)}] {period_start.strftime('%Y-%m-%d')} ~ {period_end.strftime('%Y-%m-%d')}")
        print(f"{'='*50}")

        # 1. YouTube 검색
        video_ids, search_items, search_params, page_info = search_youtube(
            query=keyword,
            publishedAfter=period_after,
            publishedBefore=period_before,
            total_count=total_count,
            max_results=50,
            order=order,
            region_code="KR"
        )

        if not video_ids:
            print(f"검색 결과가 없습니다.")
            continue

        # 2. 검색 결과 저장 (JSON)
        search_filename = save_search_result(search_items, search_params, page_info, folder_name)

        # 3. 비디오 상세 정보 가져오기
        cleaned_items = get_video_details(video_ids)

        # 4. 정리된 데이터 저장 (CSV)
        cleaned_filename = save_cleaned_csv(cleaned_items, search_filename, folder_name)

        total_videos += len(cleaned_items)
        print(f"{len(cleaned_items)}개의 비디오 데이터 저장 완료")

    print(f"\n{'='*50}")
    print(f"전체 완료: 총 {total_videos}개의 비디오 데이터를 저장했습니다.")
    print(f"저장 위치: {folder_name}/")
    print(f"{'='*50}")
