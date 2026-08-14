"""应用配置：从环境变量 / .env 文件读取。

- 使用 pydantic-settings，字段名与 .env 中的 KEY 自动映射（不区分大小写）。
- BASE_DIR 定位到项目根目录，使 .env 的读取不依赖"当前工作目录"。
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "MiniMall"
    app_env: str = "dev"
    debug: bool = True
    log_level: str = "INFO"


settings = Settings()
