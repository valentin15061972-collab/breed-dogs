import requests
import json
import time
from tqdm import tqdm
from settings import yd_token


BREED = input("Введите породу собаки на английском языке: ").lower()
DISK_BASE_PATH = f"/{BREED.capitalize()}_Images"

def get_dog_images(breed):
    sub_breed_url = f"https://dog.ceo/api/breed/{breed}/list"
    response = requests.get(sub_breed_url)
    response.raise_for_status()
    data = response.json()
    sub_breeds = data.get("message", [])
    image_urls = []
    for sub in sub_breeds:
        url = f"https://dog.ceo/api/breed/{breed}/{sub}/images/random"
        resp = requests.get(url)
        resp.raise_for_status()
        img_data = resp.json()
        img_url = img_data["message"]
        if img_url:
            image_urls.append({"sub_breed": sub, "url": img_url})
    return image_urls

def create_folder_on_disk(token, path):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": path}
    response = requests.put(url, headers=headers, params=params)
    response.raise_for_status()

def upload_image_to_disk(token, url, file_name, folder_path):
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {"Authorization": f"OAuth {token}"}
    file_path = f"{folder_path}/{file_name}"
    params = {
        "path": file_path,
        "url": url,
        "overwrite": "true"
    }
    response = requests.post(upload_url, headers=headers, params=params)
    response.raise_for_status()

def main():
    images = get_dog_images(BREED)
    create_folder_on_disk(yd_token, DISK_BASE_PATH)
    results = []
    for item in tqdm(images, desc="Загрузка изображений", unit="file"):
        url = item["url"]
        sub_breed = item["sub_breed"] or BREED
        file_name = f"{sub_breed}_{url.split('/')[-1]}"
        success = upload_image_to_disk(yd_token, url, file_name, DISK_BASE_PATH)
        result_entry = {
            "file_name": file_name,
            "url": url,
            "disk_path": f"{DISK_BASE_PATH}/{file_name}",
            "uploaded": success,
            "timestamp": time.time()
        }
        results.append(result_entry)
        time.sleep(0.5)
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()



  
