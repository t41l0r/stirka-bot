import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config
from storage import Storage
from vk_client import send_message

log = logging.getLogger(__name__)

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday"]


def load_messages(path) -> dict:
    # Файл читается при каждой отправке, поэтому тексты можно менять без перезапуска
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def daily_job(cfg: Config, storage: Storage):
    now = datetime.now(ZoneInfo(cfg.timezone))
    day = now.date().isoformat()
    weekday = WEEKDAYS[now.weekday()]

    if storage.is_sent(day):
        log.info("%s: сообщение уже отправлено, пропускаю", day)
        return

    text = load_messages(cfg.messages_path).get(weekday, "").strip()
    if not text:
        log.warning("%s: для %s нет текста в messages.json, пропускаю", day, weekday)
        return

    # Один и тот же random_id на весь день: повтор не создаст дубликат в VK
    random_id = int(now.strftime("%Y%m%d"))
    try:
        msg_id = send_message(cfg.token, cfg.peer_id, text, random_id)
    except Exception as exc:
        log.error("%s: не удалось отправить: %s", day, exc)
        storage.record(day, "failed", random_id, error=str(exc))
        return

    storage.record(day, "sent", random_id, vk_message_id=msg_id)
    log.info("%s: сообщение отправлено (id %s)", day, msg_id)


def run(cfg: Config):
    storage = Storage(cfg.db_path)
    scheduler = BlockingScheduler(timezone=cfg.timezone)
    scheduler.add_job(
        daily_job,
        CronTrigger(day_of_week=cfg.days, hour=cfg.hour, minute=cfg.minute,
                    timezone=cfg.timezone),
        args=[cfg, storage],
        id="daily_message",
        coalesce=True,
        max_instances=1,
        # Опоздание больше 5 минут = пропуск, задним числом ничего не шлём
        misfire_grace_time=300,
    )
    log.info("Бот запущен: дни %s, время %02d:%02d (%s)",
             cfg.days, cfg.hour, cfg.minute, cfg.timezone)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Бот остановлен")
