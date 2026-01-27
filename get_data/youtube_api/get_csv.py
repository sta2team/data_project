import requests
from dotenv import load_dotenv
import os
import csv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API")

# @@@@@@@ 검색 설정 @@@@@@@
district = "삼성1동"
keyword = "코엑스 맛집"
publishedAfter = "2022-12-31T15:00:00Z"
publishedBefore = "2025-12-31T14:59:59Z"
total_count = 100


def search_youtube(query, publishedAfter, publishedBefore, total_count=100, max_results=50, region_code="KR"):
    """
    YouTube 검색 결과를 조회수 순으로 가져오기
    """
    base_url = "https://www.googleapis.com/youtube/v3/search"

    video_ids = []
    next_page_token = None
    total_fetched = 0

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
            "order": "viewCount",
            "regionCode": region_code
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            for item in items:
                if "id" in item and "videoId" in item["id"]:
                    video_ids.append(item["id"]["videoId"])

            total_fetched += len(items)
            print(f"[검색] 가져온 데이터: {len(items)}개 (총: {total_fetched}개)")

            next_page_token = data.get("nextPageToken")

            if not next_page_token or total_fetched >= total_count:
                break

        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            break

    return video_ids


def get_video_details(video_ids, district):
    """
    YouTube 동영상 세부 정보를 가져와서 필요한 필드만 반환
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
                    "district": district,
                    "id": item.get("id"),
                    "title": item.get("snippet", {}).get("title"),
                    "publishedAt": item.get("snippet", {}).get("publishedAt"),
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


def save_csv(items, district, folder_path):
    """
    데이터를 CSV 파일로 저장
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    district_clean = district.replace(" ", "").replace("|", "_")
    filename = os.path.join(folder_path, f"{district_clean}_{timestamp}.csv")

    fieldnames = ["district", "id", "title", "publishedAt", "viewCount", "likeCount", "commentCount"]

    # viewCount 기준 내림차순 정렬
    sorted_items = sorted(items, key=lambda x: int(x.get('viewCount') or 0), reverse=True)

    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)

    print(f"[저장 완료] {filename}")
    return filename


# 메인 실행
if __name__ == "__main__":
    # youtubedata 폴더 생성
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_name = os.path.join(script_dir, "youtubedata")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"폴더 생성: {folder_name}/")

    # 1. YouTube 검색 (조회수 순) - keyword로 검색
    video_ids = search_youtube(
        query=keyword,
        publishedAfter=publishedAfter,
        publishedBefore=publishedBefore,
        total_count=total_count,
        region_code="KR"
    )

    if not video_ids:
        print("검색 결과가 없습니다.")
    else:
        # 2. 비디오 상세 정보 가져오기 - district 저장
        items = get_video_details(video_ids, district)

        # 3. CSV 저장
        save_csv(items, district, folder_name)

        print(f"\n{'='*50}")
        print(f"완료: 총 {len(items)}개의 비디오 데이터를 저장했습니다.")
        print(f"저장 위치: {folder_name}/")
        print(f"{'='*50}")