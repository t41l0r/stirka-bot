import argparse
import logging
import random
from logging.handlers import RotatingFileHandler

from config import load_config
from scheduler import run
from vk_client import send_message


def setup_logging(log_dir):
    log_dir.mkdir(exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = RotatingFileHandler(log_dir / "bot.log", maxBytes=1_000_000,
                                       backupCount=3, encoding="utf-8")
    console = logging.StreamHandler()
    for h in (file_handler, console):
        h.setFormatter(fmt)
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console])
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def main():
    parser = argparse.ArgumentParser(description="VK бот: одно сообщение в день")
    parser.add_argument("--test", metavar="ТЕКСТ",
                        help="отправить тестовое сообщение прямо сейчас и выйти")
    args = parser.parse_args()

    cfg = load_config()
    setup_logging(cfg.log_dir)

    if args.test:
        msg_id = send_message(cfg.token, cfg.peer_id, args.test,
                              random_id=random.randint(1, 2**31 - 1))
        logging.getLogger("main").info("Тестовое сообщение отправлено (id %s)", msg_id)
        return

    run(cfg)


if __name__ == "__main__":
    main()
