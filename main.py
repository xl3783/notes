import re
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import hashlib

MAX_FILENAME_LENGTH = 50  # 设置文件名的最大长度

def download_image(url, save_folder):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # 从URL中计算哈希值，并作为部分文件名
        img_hash = hashlib.md5(url.encode()).hexdigest()[:10]
        file_extension = '.jpg'
        # 截取文件名的一部分以限制长度
        truncated_filename = f"{img_hash[:MAX_FILENAME_LENGTH-15]}{file_extension}"
        print(f"Downloading {url} as {truncated_filename}")
        filename = os.path.join(save_folder, truncated_filename)
        print(f"Saving to {filename}")
        total_size = int(response.headers.get('content-length', 0))
        with open(filename, 'wb') as file, tqdm(
            desc=filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                bar.update(len(data))
                file.write(data)
        return filename
    else:
        return None

def process_markdown_file(input_markdown_file, output_markdown_file, output_image_folder):
    with open(input_markdown_file, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # 使用正则表达式找到所有图片链接
    img_tags = re.findall(r'!\[.*?\]\((.*?)\)', markdown_content)

    for img_url in img_tags:
        # 下载图片并获取本地文件路径
        local_img_path = download_image(img_url, output_image_folder)
        if local_img_path:
            # 替换Markdown中的图片链接
            markdown_content = markdown_content.replace(img_url, local_img_path)

    # 将更新后的Markdown内容写入新文件
    with open(output_markdown_file, 'w', encoding='utf-8') as file:
        file.write(markdown_content)

if __name__ == "__main__":
    input_markdown_file = "Istio.md"  # 替换为您的输入Markdown文件路径
    output_markdown_file = "output.md"  # 替换为生成的输出Markdown文件路径
    output_image_folder = "images"  # 替换为您想要保存图片的本地文件夹路径

    # 创建本地图片保存文件夹
    os.makedirs(output_image_folder, exist_ok=True)

    # 处理Markdown文件并生成新的Markdown文件
    process_markdown_file(input_markdown_file, output_markdown_file, output_image_folder)
