import asyncio
import sys
from contextlib import suppress
from itertools import chain, islice
from typing import Iterable, Optional

from bs4 import BeautifulSoup
from httpx import AsyncClient, ConnectError, ConnectTimeout, Response, Timeout

# Configurations
# ===============================================
try:
    BASE_URL = sys.argv[1]
except IndexError:
    print(
        "🔴 Syntax: python run.py <hostname>"
        "\n🟡 Remember hostname should have a slash in the end"
    )
    raise SystemExit
CHUNK_SIZE = 200
WORDLIST_FILENAME = "./wordlist.txt"
RESULTS_FILENAME = "./results.txt"

TEXT_TO_MATCH = [
    "Страница не найдена",
    "Неизвестный URL",
    "Ошибка",
    "Invalid URI",
    "Error 404",
    "Not found",
]
# ===============================================


def group_elements(lst, chunk_size) -> list[Iterable]:
    """Return list of iterables with size == CHUNK_SIZE"""
    lst = iter(lst)
    return list(iter(lambda: tuple(islice(lst, chunk_size)), ()))


def text_in_body(response: Response) -> bool:
    """Check if text exists in body html"""
    try:
        soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
    except UnicodeDecodeError:
        return False

    text = str(soup)
    for pattern in TEXT_TO_MATCH:
        if pattern in text:
            return False

    return True


async def fetch(url: str) -> Optional[Response]:
    """Fetch the URL and check next:
    - Status 100 < code < 400
    - No Invalide text from TEXT_TO_MATCH on site
    """
    async with AsyncClient(timeout=Timeout(5, read=None)) as client:
        with suppress(ConnectError, ConnectTimeout):
            response = await client.get(url)
            if not response.status_code < 400:
                return

            if not text_in_body(response):
                return

            print(f"✅ [{response.status_code}]  ", url)
            return response


async def fetch_urls(urls: tuple):
    return [result for result in [await fetch(url) for url in urls] if result]


def main():
    words = open(WORDLIST_FILENAME).read().split("\n")[:-1]
    urls = ["".join([BASE_URL, word]) for word in words]

    urls_batches = group_elements(urls, CHUNK_SIZE)

    loop = asyncio.get_event_loop()
    tasks = [fetch_urls(urls) for urls in urls_batches]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

    filtered_results: list[str] = [
        str(r.url) for r in chain.from_iterable(results) if r
    ]

    with open(RESULTS_FILENAME, "w") as file:
        text = "\n".join(filtered_results)
        file.write(text)


if __name__ == "__main__":
    main()
