from urllib.parse import quote, urljoin

import requests


class ParaBankApiClient:
    def __init__(self, api_base_url: str, timeout_seconds: float) -> None:
        self.api_base_url = f"{api_base_url.rstrip('/')}/"
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def get(self, path: str) -> requests.Response:
        return self.session.get(
            urljoin(self.api_base_url, path.lstrip("/")),
            timeout=self.timeout_seconds,
        )

    def login(self, username: str, password: str) -> requests.Response:
        return self.get(f"login/{quote(username, safe='')}/{quote(password, safe='')}")

    def customer_accounts(self, customer_id: int) -> requests.Response:
        return self.get(f"customers/{customer_id}/accounts")

    def close(self) -> None:
        self.session.close()
