import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API")

# @@@@@@ 파일명 입력 @@@@@@
filename = "./youtube_성수_맛집_20260112_202050.json"


def get_video_details_cleaned(video_ids):
    """
    YouTube 동영상 세부 정보를 가져와서 필요한 필드만 저장

    Args:
        video_ids (list): 비디오 ID 리스트

    Returns:
        list: 정리된 비디오 데이터 리스트
    """

    base_url = "https://www.googleapis.com/youtube/v3/videos"

    all_cleaned_items = []

    # API는 한 번에 최대 50개의 ID만 처리 가능
    batch_size = 50

    for i in range(0, len(video_ids), batch_size):
        batch_ids = video_ids[i:i+batch_size]

        params = {
            "key": API_KEY,
            "part": "snippet",
            "id": ",".join(batch_ids)
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])

            # 각 item에서 필요한 필드만 추출
            for item in items:
                cleaned_item = {
                    "id": item.get("id"),
                    "publishedAt": item.get("snippet", {}).get("publishedAt"),
                    "title": item.get("snippet", {}).get("title"),
                    "description": item.get("snippet", {}).get("description"),
                    "channelTitle": item.get("snippet", {}).get("channelTitle"),
                    "categoryId": item.get("snippet", {}).get("categoryId")
                }
                all_cleaned_items.append(cleaned_item)

            print(f"가져온 데이터: {len(items)}개 (총: {len(all_cleaned_items)}개)")

        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            break

    return all_cleaned_items


def extract_video_ids_from_search_result(search_json_file):
    """
    검색 결과 JSON 파일에서 video ID 추출

    Args:
        search_json_file (str): 검색 결과 JSON 파일 경로

    Returns:
        list: video ID 리스트
    """
    with open(search_json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    video_ids = []
    for item in data.get("items", []):
        if "id" in item and "videoId" in item["id"]:
            video_ids.append(item["id"]["videoId"])

    print(f"추출된 video ID 개수: {len(video_ids)}")
    return video_ids


def save_cleaned_data(cleaned_items, original_filename):
    """
    정리된 데이터를 JSON 파일로 저장

    Args:
        cleaned_items (list): 정리된 비디오 데이터 리스트
        original_filename (str): 원본 파일명 (출력 파일명 생성용)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 원본 파일명에서 youtube_ 제거하고 _cleaned 추가
    base_name = original_filename.replace("./", "").replace("youtube_", "").replace(".json", "")
    output_filename = f"{base_name}_data_{timestamp}.json"

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(cleaned_items, f, ensure_ascii=False, indent=2)

    print(f"\n파일 저장 완료: {output_filename}")
    print(f"총 {len(cleaned_items)}개의 비디오 데이터를 저장했습니다.")

    return output_filename


# 사용 예시
if __name__ == "__main__":
    # 검색 결과 파일에서 video ID 추출
    search_file = filename
    video_ids = extract_video_ids_from_search_result(search_file)

    # 세부 정보 가져오기 (필요한 필드만)
    cleaned_items = get_video_details_cleaned(video_ids=video_ids)

    # 정리된 데이터 저장
    output_file = save_cleaned_data(cleaned_items, search_file)

    # 첫 번째 항목 출력 (확인용)
    if cleaned_items:
        print("\n첫 번째 항목 예시:")
        print(json.dumps(cleaned_items[0], ensure_ascii=False, indent=2))
