import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Config:
    token: str
    peer_id: int
    timezone: str
    hour: int
    minute: int
    days: str
    db_path: Path
    messages_path: Path
    log_dir: Path


def load_config() -> Config:
    token = os.getenv("VK_TOKEN", "").strip()
    peer_id = os.getenv("VK_PEER_ID", "").strip()
    if not token or token.startswith("сюда"):
        raise SystemExit("Ошибка: в файле .env не указан VK_TOKEN")
    if not peer_id.lstrip("-").isdigit():
        raise SystemExit("Ошибка: в файле .env не указан VK_PEER_ID (число)")

    send_time = os.getenv("SEND_TIME", "06:45")
    try:
        hour, minute = (int(x) for x in send_time.split(":"))
    except ValueError:
        raise SystemExit("Ошибка: SEND_TIME должен быть в формате ЧЧ:ММ, например 06:45")

    return Config(
        token=token,
        peer_id=int(peer_id),
        timezone=os.getenv("TIMEZONE", "Europe/Moscow"),
        hour=hour,
        minute=minute,
        days=os.getenv("SEND_DAYS", "tue,wed,thu,fri,sat,sun").lower().replace(" ", ""),
        db_path=BASE_DIR / "bot.db",
        messages_path=BASE_DIR / "messages.json",
        log_dir=BASE_DIR / "logs",
    )
