import asyncio
import sys
from contextlib import suppress
from itertools import chain, islice

from bs4 import BeautifulSoup
from httpx import AsyncClient, ConnectError, ConnectTimeout, Timeout


# Configurations
# ===============================================
BASE_URL = sys.argv[1]
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


words = open(WORDLIST_FILENAME).read().split("\n")[:-1]
urls = ["".join([BASE_URL, word]) for word in words]


def group_elements(lst, chunk_size):
    lst = iter(lst)
    return list(iter(lambda: tuple(islice(lst, chunk_size)), ()))


urls_batches = group_elements(urls, CHUNK_SIZE)


async def fetch(url: str):
    async with AsyncClient(timeout=Timeout(5, read=None)) as client:
        with suppress(ConnectError, ConnectTimeout):
            response = await client.get(url)
            if response.status_code == 200:
                try:
                    soup = BeautifulSoup(
                        response.content.decode("utf-8"), "html.parser"
                    )
                except UnicodeDecodeError:
                    return

                text = str(soup)
                for pattern in TEXT_TO_MATCH:
                    if pattern in text:
                        return

                print("[200]  ", url)
                return response


async def fetch_urls(urls: tuple):
    return [result for result in [await fetch(url) for url in urls] if result]


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tasks = [fetch_urls(urls) for urls in urls_batches]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

    filtered_results: list[str] = [
        str(r.url) for r in chain.from_iterable(results) if r
    ]

    with open(RESULTS_FILENAME, "w") as file:
        text = "\n".join(filtered_results)
        for result in filtered_results:
            file.write(text)
