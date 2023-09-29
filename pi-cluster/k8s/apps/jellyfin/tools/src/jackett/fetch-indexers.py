# from bs4 import BeautifulSoup
# using time module
import time
import requests
import gzip
import brotli
import json
from functools import cached_property
from typing import List, Dict
from utils.utils import get_cookies_for_domain


class Jackett:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.7,pl;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "DNT": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    DOMAIN = "192.168.18.192"

    COOKIES = get_cookies_for_domain(DOMAIN)

    BASE_URL = f"http://{DOMAIN}:30002"

    def get_all_indexers(self) -> List[Dict]:
        res = requests.get(
            f"{self.BASE_URL}/api/v2.0/indexers?_={time.time()!s}",
            headers=self.HEADERS,
            cookies=self.COOKIES,
            stream=True,
        )

        if res.status_code != 200:
            raise Exception(res.status_code)

        res_parts = []
        for chunk in res.iter_content(1000):
            res_parts.append(chunk)
        res_full = b"".join(res_parts)

        return list(json.loads(str(res_full, "utf-8")))

    def get_configured_indexers(self) -> List[Dict]:
        return list(
            filter(lambda indexer: indexer["configured"], self.get_all_indexers())
        )

    def _filter_indexers(self, filters: List[str]) -> List[Dict]:
        return list(
            filter(
                lambda indexer: any(
                    any(_filter.lower() in cap["Name"].lower() for _filter in filters)
                    for cap in indexer["caps"]
                ),
                self.get_configured_indexers(),
            )
        )

    def get_movie_indexers(self) -> List[Dict]:
        return self._filter_indexers(["movie"])

    def get_tvseries_indexers(self) -> List[Dict]:
        return self._filter_indexers(["tv"])

    def _indexer_url(self, id: str) -> str:
        return f"{self.BASE_URL}/api/v2.0/indexers/{id}/results/torznab/"


if __name__ == "__main__":
    main = Jackett()

    # with open("out.configured.json", "w") as fptr:
    #     json.dump(main.get_configured_indexers(), fptr)

    # print(json.dumps(main.get_configured_indexers(), indent=2))
