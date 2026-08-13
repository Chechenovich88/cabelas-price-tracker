import os
import json
import re
import requests
from datetime import datetime

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

CONFIG_FILE = "config.json"

PRODUCT_URLS = {
    "Cabela's Trans Alaska":
        "https://www.cabelas.com/shop/en/cabelas-trans-alaska-insulated-waterproof-pac-boots-for-men-black-9m-3352546",
    "Cabela's Saskatchewan":
        "https://www.cabelas.com/shop/en/cabelas-saskatchewan-gore-tex-insulated-hunting-boots-for-men-dark-brown-truetimber-kanati-9m-2676556"
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1"
    )
}


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )

    response.raise_for_status()


def get_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_product_data(name, url, sizes):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()
    html = response.text

    # Try to find product price
    prices = re.findall(r'\$(\d{1,4}(?:\.\d{2})?)', html)

    if not prices:
        return None, []

    price = float(prices[0])

    # Look for requested sizes in the product page
    available_sizes = []

    for size in sizes:
        patterns = [
            rf'Shoe Size[^<]{{0,500}}>{re.escape(size)}<',
            rf'Shoe Size[^"]{{0,500}}{re.escape(size)}',
            rf'"{re.escape(size)}"',
            rf'>{re.escape(size)}<'
        ]

        if any(re.search(pattern, html, re.IGNORECASE) for pattern in patterns):
            available_sizes.append(size)

    return price, available_sizes


def main():
    config = get_config()

    price_limit = float(config["price_limit"])
    sizes = config["sizes"]
    products = config["products"]

    lines = [
        "🔎 Cabela's Tracker проверка",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ""
    ]

    alert = False

    for product in products:
        url = PRODUCT_URLS.get(product)

        if not url:
            lines.append(f"⚠️ {product}: URL не настроен")
            continue

        try:
            price, found_sizes = get_product_data(
                product,
                url,
                sizes
            )

            if price is None:
                lines.append(f"❌ {product}: цена не найдена")
                continue

            lines.append(f"🥾 {product}")
            lines.append(f"💰 Цена: ${price:.2f}")

            if found_sizes:
                lines.append(
                    "📏 Размеры на странице: " +
                    ", ".join(found_sizes)
                )
            else:
                lines.append("📏 Нужные размеры: не найдены")

            if price <= price_limit:
                lines.append(
                    f"🚨 ЦЕНА НИЖЕ ЛИМИТА ${price_limit:.2f}!"
                )
                alert = True

            lines.append("")

        except Exception as e:
            lines.append(
                f"❌ {product}: ошибка проверки — {str(e)[:150]}"
            )

    message = "\n".join(lines)

    # During the first real test we send every check,
    # so we can verify that the tracker actually works.
    send_message(message)

    print(message)
    print("Real Cabela's check completed")


if __name__ == "__main__":
    main()
