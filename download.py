import requests
from bs4 import BeautifulSoup
import csv
import re

# Генерация списка URL для всех эпизодов
episode_urls = [
    f"https://fangj.github.io/friends/season/{s:02}{e:02}.html"
    for s in range(1, 11) for e in range(1, 25)
]

def get_phoebe_lines(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка при загрузке {url}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    
    # Ищем реплики Фиби
    pattern = re.compile(r"Phoebe: (.+)", re.IGNORECASE)
    lines = pattern.findall(text)
    
    return lines

# Извлекаем реплики из всех эпизодов
all_phoebe_lines = []
for url in episode_urls:
    all_phoebe_lines.extend(get_phoebe_lines(url))

# Очищаем реплики от лишних символов
cleaned_lines = [re.sub(r'[^a-zA-Z0-9 .,!?\'\"]+', '', line).strip() for line in all_phoebe_lines]

# Сохраняем в CSV
with open("phoebe_quotes.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["quote"])
    for line in cleaned_lines:
        writer.writerow([line])

print(f"Сохранено {len(cleaned_lines)} реплик Фиби в 'phoebe_quotes.csv'")
