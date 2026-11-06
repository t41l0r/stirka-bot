import logging
import time

import requests

log = logging.getLogger(__name__)

API_URL = "https://api.vk.com/method/messages.send"
API_VERSION = "5.199"
# Временные ошибки VK: слишком много запросов, флуд, внутренняя ошибка сервера
TEMPORARY_CODES = {6, 9, 10}


class VkError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(f"VK error {code}: {message}")
        self.code = code


def send_message(token: str, peer_id: int, text: str, random_id: int,
                 retries: int = 3, delay: float = 5.0) -> int:
    """Отправляет сообщение. random_id одинаков во всех повторах,
    поэтому VK не создаст дубликат. Токен передаётся в заголовке и в логи не попадает."""
    data = {
        "peer_id": peer_id,
        "message": text,
        "random_id": random_id,
        "v": API_VERSION,
    }
    headers = {"Authorization": f"Bearer {token}"}

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(API_URL, data=data, headers=headers, timeout=20)
            if resp.status_code >= 500:
                raise VkError(10, f"HTTP {resp.status_code}")
            payload = resp.json()
            if "error" in payload:
                err = payload["error"]
                raise VkError(err.get("error_code", 0), err.get("error_msg", "unknown"))
            return payload["response"]
        except (requests.RequestException, ValueError) as exc:
            temporary, reason = True, type(exc).__name__
        except VkError as exc:
            temporary, reason = exc.code in TEMPORARY_CODES, str(exc)
            if not temporary:
                raise

        if attempt == retries:
            raise VkError(0, f"не удалось отправить после {retries} попыток ({reason})")
        log.warning("Временная ошибка (%s), попытка %d из %d", reason, attempt, retries)
        time.sleep(delay * attempt)
