from bs4 import BeautifulSoup
import requests
from ..urls import OPTYKA_URL
from ..config import LOG_FILE
import datetime
import time
import re

# Funkcja scrapująca stronę OptykaMyśliwska
def scrape_optykamysliwska():
    url = OPTYKA_URL
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        announcements = soup.find_all('table', class_='Announcement')
        nowe_ogloszenia = []

        for ann in announcements:
            # Miniatura
            img_url = None
            img_elem = ann.find('td', class_='Image')
            if img_elem:
                img_tag = img_elem.find('img')
                if img_tag and img_tag.get('src'):
                    img_url = img_tag['src']
                    if not img_url.startswith('http'):
                        img_url = f'https://www.optykamysliwska.pl/{img_url.lstrip("/")}'

            # Tytuł i link
            tytul_elem = ann.find('a', href=True)
            if not tytul_elem:
                continue
            tytul = tytul_elem.get_text(strip=True)
            link = tytul_elem['href']
            if not link.startswith('http'):
                link = f'https://www.optykamysliwska.pl/{link.lstrip("/")}'

            # Cena z linku (np. "cena-4200" w URL)
            cena_match = re.search(r'cena-(\d+)', link)
            cena = f"{cena_match.group(1)} zł" if cena_match else "Brak ceny"

            nowe_ogloszenia.append({
                "tytul": tytul,
                "link": link,
                "lokalizacja": "Podlaskie",
                "cena": cena,
                "img_url": img_url,
                "source": "OptykaMyśliwska",
                "timestamp": datetime.datetime.now().timestamp()
            })

        print(f"OptykaMyśliwska: Znaleziono {len(nowe_ogloszenia)} ogłoszeń")
        return nowe_ogloszenia

    except Exception as e:
        error_msg = f"[{time.ctime()}] Błąd OptykaMyśliwska: {str(e)}\n"
        print(error_msg)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(error_msg)
        return []
