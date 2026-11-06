"""Слушает сообщество через Long Poll и печатает, из каких бесед приходят сообщения.
Тексты сообщений НЕ печатаются, только номера. Остановка: Ctrl+C."""
import requests

from config import load_config
from vk_client import API_VERSION


def call(token, method, **params):
    params["v"] = API_VERSION
    resp = requests.post(
        f"https://api.vk.com/method/{method}",
        data=params,
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    return resp.json()


def get_server(token, group_id):
    data = call(token, "groups.getLongPollServer", group_id=group_id)
    if "error" in data:
        print("Не удалось подключиться к Long Poll:", data["error"].get("error_msg"))
        print("Включите его: сообщество → Управление → Работа с API → Long Poll API:")
        print("  «Long Poll API» = включён, версия 5.199,")
        print("  вкладка «Типы событий» → «Входящие сообщения» = включено.")
        raise SystemExit(1)
    return data["response"]


def main():
    cfg = load_config()
    data = call(cfg.token, "groups.getById")
    resp = data["response"]
    groups = resp.get("groups", resp) if isinstance(resp, dict) else resp
    group_id = groups[0]["id"]
    print(f"Слушаю сообщество «{groups[0].get('name')}».")
    print("Теперь напишите что-нибудь в беседе, например: /test")
    print("Остановить: Ctrl+C\n")

    srv = get_server(cfg.token, group_id)
    key, server, ts = srv["key"], srv["server"], srv["ts"]
    seen = set()

    while True:
        try:
            r = requests.get(
                server,
                params={"act": "a_check", "key": key, "ts": ts, "wait": 25},
                timeout=40,
            ).json()
        except KeyboardInterrupt:
            print("Остановлено")
            return
        except Exception as exc:
            print("Сбой сети:", type(exc).__name__)
            continue

        if "failed" in r:
            if r["failed"] == 1:
                ts = r["ts"]
            else:
                srv = get_server(cfg.token, group_id)
                key, ts = srv["key"], srv["ts"]
            continue

        ts = r["ts"]
        for ev in r.get("updates", []):
            if ev.get("type") != "message_new":
                continue
            peer = ev["object"]["message"]["peer_id"]
            kind = "беседа" if peer >= 2000000000 else "личный диалог"
            if peer not in seen:
                seen.add(peer)
                print(f"Пришло сообщение: peer_id={peer} ({kind})")
                if peer >= 2000000000:
                    print(f"  -> впишите в .env: VK_PEER_ID={peer}")


if __name__ == "__main__":
    main()
