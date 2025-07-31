from bs4 import BeautifulSoup
import requests
from ..urls import NETGUN_URL
from ..config import LOG_FILE
import datetime
import time

def scrape_netgun():
    url = NETGUN_URL
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{time.ctime()}] Pobrano NetGun, HTML: {len(response.text)} znaków\n")
        
        ogloszenia = soup.select('div.listing-inner .item')
        
        print(f"NetGun: Znaleziono {len(ogloszenia)} ogłoszeń")
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{time.ctime()}] NetGun: Znaleziono {len(ogloszenia)} ogłoszeń\n")
        
        nowe_ogloszenia = []
        for ogl in ogloszenia:
            tytul_elem = ogl.select_one('.title h3')
            tytul = tytul_elem.text.strip() if tytul_elem else "Brak tytułu"
            
            link_elem = ogl.select_one('a[href]')
            link = link_elem['href'] if link_elem else "Brak linku"
            if not link.startswith('http'):
                link = 'https://www.netgun.pl' + link
            
            cena_elem = ogl.select_one('.price span')
            cena = cena_elem.text.strip() if cena_elem else "Brak ceny"
            if ogl.select_one('.price .old'):
                cena_elem = ogl.select('.price span')[-1]
                cena = cena_elem.text.strip() if cena_elem else "Brak ceny"
            
            img_elem = ogl.select_one('img')
            img_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else None
            if img_url and not img_url.startswith('http'):
                img_url = 'https://www.netgun.pl' + img_url
            
            lokalizacja = "Podlaskie"
            
            nowe_ogloszenia.append({
                "tytul": tytul,
                "link": link,
                "lokalizacja": lokalizacja,
                "cena": cena,
                "img_url": img_url,
                "source": "NetGun",
                "timestamp": datetime.datetime.now().timestamp(),  # Dodaj timestamp
                "id": link.split('/')[-1]  # Unikalny ID z linku
            })
        
        return nowe_ogloszenia
    
    except Exception as e:
        error_msg = f"[{time.ctime()}] Błąd NetGun: {str(e)}\n"
        print(error_msg)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(error_msg)
        return []
