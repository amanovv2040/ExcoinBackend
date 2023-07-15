import json
import requests
from bs4 import BeautifulSoup

def collect_data():

    url = "https://coinmarketcap.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    r = requests.get(url, headers=headers).text
    soup = BeautifulSoup(r, 'lxml')

    tbody = soup.find('tbody')
    coins = tbody.find_all('tr')


    result = []

    for coin in coins[:10]:
        if coin.find(class_='sc-4984dd93-0 kKpPOn') and coin.find(class_='coin-item-symbol'):
            name = coin.find('p', class_='sc-4984dd93-0 kKpPOn').text
            symbol = coin.find('p', class_='coin-item-symbol').text
            p = coin.find(class_='sc-bc83b59-0')
            price = p.find('span').text
            v = coin.find('div', class_='sc-aef7b723-0 sc-f93239f7-0 bpHLqp')
            volume_24 = v.find('p', class_='sc-4984dd93-0').text
            market_cap = coin.find('span', class_='sc-f8982b1f-1').text
            graph = coin.find('img', class_='sc-996d6db8-0')['src']
            # print(f"Name: {name}, Symbol: {symbol}, Price: {price}, Volume(24h): {volume_24}, Market cap: {market_cap}, graph: {graph}")
            result.append(
                {
                    'name': name,
                    'symbol': symbol,
                    'price': price,
                    'volume_24': volume_24,
                    'market_cap': market_cap,
                    'graph': graph
                }
            )
        else:
            break
    # with open('parser/data.json', 'w') as file:
    #     json.dump(result, file, indent=4, ensure_ascii=False)
    return result