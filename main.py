from flask import Flask, request
from patchright.sync_api import Response
from urllib.parse import urlencode
from scrapling.fetchers import StealthySession

app = Flask(__name__)


def generate_url(keyword: str):
    params = urlencode({"keyword": keyword})
    # bisa tambah order=asc&page=0&sortBy=price untuk sort by price dari sisi shopee
    return f"https://shopee.co.id/search?{params}"


def generate_product_url(shopid, itemid):
    return f"https://shopee.co.id/product/{shopid}/{itemid}"


def parse_json(json):
    products = []

    for item in json.get("items", []):
        basic = item.get("item_basic", {})
        name = basic.get("name")
        price = basic.get("price", 0) / 100000
        shopid = basic.get("shopid")
        itemid = basic.get("itemid")
        products.append(
            {"name": name, "price": price, "link": generate_product_url(shopid, itemid)}
        )
    return products


def selection_sort(array):
    size = len(array)
    for ind in range(size - 1):
        min_index = ind

        for j in range(ind + 1, size):
            if array[j]["price"] < array[min_index]["price"]:
                min_index = j

        array[ind], array[min_index] = array[min_index], array[ind]
    return array


def get_products(keyword: str):
    products = []
    stop_flag = False

    with StealthySession(
        real_chrome=True,
        headless=True,
        allow_webgl=False,
    ) as s:
        browser = s.context
        page = browser.new_page()

        def on_response(response: Response):
            nonlocal stop_flag
            nonlocal products

            url = response.url
            if "search_items" in url:
                products = parse_json(response.json())
                products = selection_sort(products)
                stop_flag = True

        page.on("response", on_response)
        page.goto(generate_url(keyword))

        while not stop_flag:
            page.wait_for_timeout(100)

        page.close()
        browser.close()
        s.close()

    return products[:3]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form.get("keyword", "")
        products = get_products(keyword)

        html = f"<h2>Hasil untuk '{keyword}':</h2>"
        html += "<ol>"
        for p in products:
            price_formatted = f"{int(p['price']):,}".replace(",", ".")
            html += f"""
            <li>
                <p>Nama: <b>{p['name']}</b></p>
                <p>Harga: Rp {price_formatted}</p>
                <a href="{p['link']}" target="_blank">Link: {p['link']}</a>
            </li>
            <hr>
            """
        html += "</ol>"
        html += """
            <form action="/" method="get">
                <button type="submit">Kembali</button>
            </form>
        """
        return html

    return """
        <form method="POST" style="text-align:center;">
            <input name="keyword" placeholder="Masukkan keyword">
            <br><br>
            <button type="submit">Cari</button>
        </form>
    """
