import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    base_url: str = "http://localhost:3000"
    username: str = "qa@test.com"
    password: str = "test1234"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            base_url=os.getenv("BASE_URL", cls.base_url).rstrip("/"),
            username=os.getenv("E2E_USERNAME", cls.username),
            password=os.getenv("E2E_PASSWORD", cls.password),
        )

    def url(self, path: str) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{normalized_path}"
