import requests
import json
import time
from tqdm import tqdm
from settings import yd_token


BREED = input("Введите породу собаки на английском языке: ").lower()


class YDiskUploader:
    def __init__(self, token):
        self.token = token

    def create_folder_on_disk(self, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Authorization': f'OAuth {self.token}'}
        params = {'path': folder_name}
        response = requests.put(url, headers=headers, params=params)
        if response.status_code in (200, 201):
            print(f"Папка '{folder_name}' создана на Яндекс.Диске")
        else:
            print(f"Папка '{folder_name}' уже существует на Яндекс.Диске")

    def upload_dog_images(self, upload_folder):
        sub_breed_url = f"https://dog.ceo/api/breed/{BREED}/list"
        response = requests.get(sub_breed_url)
        response.raise_for_status()
        sub_breeds = response.json()["message"]

        image_urls = []
        if sub_breeds:
            print(f"Подпороды найдены: {sub_breeds}")
            for sub in sub_breeds:
                url = f"https://dog.ceo/api/breed/{BREED}/{sub}/images/random"
                resp = requests.get(url)
                resp.raise_for_status()
                img_url = resp.json()["message"]
                if img_url:
                    image_urls.append((sub, img_url))
        else:
            print("Подпород нет. Загружаем изображение основной породы.")
            url = f"https://dog.ceo/api/breed/{BREED}/images/random"
            resp = requests.get(url)
            resp.raise_for_status()
            img_url = resp.json()["message"]
            if img_url:
                image_urls.append((BREED, img_url))

        results = []
        for sub, img_url in tqdm(image_urls, desc="Загрузка изображений"):
            url_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            file_name = f"{sub}_{img_url.split('/')[-1]}"
            disk_path = f"{upload_folder}/{file_name}"
            params = {'path': disk_path, 'url': img_url}
            headers = {'Authorization': yd_token}
            response = requests.post(url_upload, params=params, headers=headers)
            response.raise_for_status()
            results.append({
                "file_name": file_name,
                "url": img_url,
            })

            time.sleep(1)

        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        print("результат сохранён в results.json")

loader = YDiskUploader(yd_token)
loader.create_folder_on_disk(BREED)
loader.upload_dog_images(BREED)



  
