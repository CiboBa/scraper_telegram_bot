from .scrapers.netgun import scrape_netgun
from .scrapers.gunday import scrape_gunday
from .scrapers.optyka import scrape_optykamysliwska
from .utils import send_multiple_telegram_messages
from .config import DATA_FILE

import os
import json
import asyncio
import time

#Funkcja sprawdza nowe ogłoszenia
async def check_new_ogloszenia():
    netgun_ogloszenia = scrape_netgun()[::-1]
    gunday_ogloszenia = scrape_gunday()[::-1]
    optyka_ogloszenia = scrape_optykamysliwska()[::-1]
    wszystkie_ogloszenia = netgun_ogloszenia + gunday_ogloszenia + optyka_ogloszenia

    # Wczytaj istniejące linki
    wyslane_linki = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                wyslane_linki = json.load(f)
            except json.JSONDecodeError:
                print(f"[{time.ctime()}] Plik {DATA_FILE} uszkodzony - resetuję")
                wyslane_linki = []

    # Filtruj nowe ogłoszenia po linku
    nowe = [ogl for ogl in wszystkie_ogloszenia if ogl['link'] not in wyslane_linki]

    if nowe:
        print("Znaleziono nowe ogłoszenia!")
        messages = []
        for ogl in nowe:
            message = (
                f"🔥 NOWE Z {ogl['source']}!\n"
                f"{ogl['tytul']}\n"
                f"💵 {ogl['cena']}\n"
                f"🔗 {ogl['link']}"
            )
            messages.append((message, ogl['img_url']))

        # Wyślij wiadomości
        await send_multiple_telegram_messages(messages)
        
        # Zaktualizuj listę wysłanych linków
        wyslane_linki += [ogl['link'] for ogl in nowe]
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(wyslane_linki, f, ensure_ascii=False, indent=4)
    else:
        print("Brak nowych ogłoszeń.")

# Uruchom
async def main():
    print("Bot uruchomiony. Sprawdzam co 10 minut...")
    while True:
        await check_new_ogloszenia()
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())
