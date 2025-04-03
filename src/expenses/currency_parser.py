from typing import Dict
from curl_cffi import requests
from lxml import html


def get_usd_to_uah() -> Dict:
    url = "https://minfin.com.ua/currency/converter/usd-uah/"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "Failed to fetch currency data.", "result": None}

    tree = html.fromstring(response.content)

    try:
        rate = tree.xpath(
            "/html/body/main/div/div/section/div/div/div/section[2]/div/table/tbody/tr[1]/td[2]/text()"
        )[0]
        return {"error": None, "result": float(rate.strip())}
    except IndexError:
        return {"error": "Could not find USD to UAH exchange rate.", "result": None}
    except Exception:
        return {
            "error": "Unkown mistake while getting USD to UAH exchange rate.",
            "result": None,
        }
