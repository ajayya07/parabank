from dataclasses import dataclass
import os
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    base_url: str
    demo_username: str
    demo_password: str
    timeout_ms: int
    api_timeout_seconds: float

    @property
    def api_base_url(self) -> str:
        return f"{self.base_url}/services/bank"

    @classmethod
    def from_environment(cls) -> "Settings":
        base_url = os.getenv(
            "PARABANK_BASE_URL", "https://parabank.parasoft.com/parabank"
        ).rstrip("/")
        parsed_url = urlparse(base_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("PARABANK_BASE_URL must be an absolute HTTP(S) URL")

        try:
            timeout_ms = int(os.getenv("PARABANK_TIMEOUT_MS", "15000"))
            api_timeout_seconds = float(
                os.getenv("PARABANK_API_TIMEOUT_SECONDS", "15")
            )
        except ValueError as error:
            raise ValueError("ParaBank timeout settings must be numeric") from error
        if timeout_ms <= 0 or api_timeout_seconds <= 0:
            raise ValueError("ParaBank timeout settings must be greater than zero")

        return cls(
            base_url=base_url,
            demo_username=os.getenv("PARABANK_DEMO_USERNAME", "john"),
            demo_password=os.getenv("PARABANK_DEMO_PASSWORD", "demo"),
            timeout_ms=timeout_ms,
            api_timeout_seconds=api_timeout_seconds,
        )
