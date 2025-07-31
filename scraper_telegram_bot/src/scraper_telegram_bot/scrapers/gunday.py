from bs4 import BeautifulSoup
import requests
import time
from ..urls import GUNDAY_URL
from ..config import LOG_FILE

def scrape_gunday():
    url = GUNDAY_URL
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        ogloszenia = soup.select("div.row.cols-xl-6.cols-lg-5.cols-md-4.cols-sm-3.cols-2 > div.swiper-slide.mb-3")
        print(f"GunDay: Znaleziono {len(ogloszenia)} ogłoszeń")
        nowe_ogloszenia = []
        for ogl in ogloszenia:
            # Tytuł
            title = None
            for selector in ["h2", "h3", "h4", "div.title", "span.title", "a.title", "div.product-title", "p"]:
                title_elem = ogl.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    title = title_elem.get_text(strip=True)
                    break
            # Link
            link_elem = ogl.select_one("a[href]")
            link = link_elem["href"] if link_elem else "Brak linku"
            if not link.startswith("http"):
                link = "https://gunday.pl" + link
            # Cena
            price_elem = ogl.select_one("div.col-6.pricenumber a")
            price = price_elem.get_text(strip=True) if price_elem else "Brak ceny"
            # Miniaturka
            img_elem = ogl.select_one("img")
            img_url = img_elem["src"] if img_elem and img_elem.get("src") else None
            if img_url and not img_url.startswith("http"):
                img_url = "https://gunday.pl" + img_url
            lokalizacja = "Podlaskie"
            nowe_ogloszenia.append({
                "tytul": title or "Brak tytułu",
                "link": link,
                "lokalizacja": lokalizacja,
                "cena": price,
                "img_url": img_url,
                "source": "GunDay"
            })
        return nowe_ogloszenia
    except Exception as e:
        error_msg = f"[{time.ctime()}] Błąd GunDay: {str(e)}\n"
        print(error_msg)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(error_msg)
        return []