"""Проверка: к какому сообществу относится токен и в каких беседах оно видно."""
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


def main():
    cfg = load_config()
    print(f"VK_PEER_ID из .env: {cfg.peer_id}\n")

    # 1. Чьё это сообщество
    data = call(cfg.token, "groups.getById")
    if "error" in data:
        print("1) Токен не подходит:", data["error"].get("error_msg"))
        print("   Создайте новый ключ доступа в нужном сообществе.")
        return
    resp = data["response"]
    groups = resp.get("groups", resp) if isinstance(resp, dict) else resp
    g = groups[0]
    print(f"1) Токен от сообщества: «{g.get('name')}» (id {g.get('id')})\n")

    # 2. В каких беседах оно видно
    data = call(cfg.token, "messages.getConversations", count=200)
    if "error" in data:
        print("2) Не удалось получить список бесед:", data["error"].get("error_msg"))
        print("   Проверьте, что в ключе включено право «Сообщения сообщества»,")
        print("   а в сообществе включены сообщения.")
        return

    items = data["response"].get("items", [])
    print(f"2) Бесед, которые видит бот: {len(items)}")
    found = False
    for it in items:
        conv = it["conversation"]
        peer = conv["peer"]
        title = conv.get("chat_settings", {}).get("title", "")
        cw = conv.get("can_write", {})
        mark = ""
        if peer["id"] == cfg.peer_id:
            found = True
            mark = "   <-- это ваша беседа из .env"
        print(f"   peer_id={peer['id']} тип={peer['type']} "
              f"название='{title}' писать можно={cw.get('allowed')}{mark}")

    print()
    if found:
        print("Вывод: беседа из .env есть в списке. Если там «писать можно=False»,")
        print("сделайте сообщество администратором беседы.")
    else:
        print("Вывод: вашей беседы из .env в списке НЕТ.")
        print("Значит, сообщество с этим токеном не добавлено в беседу.")
        print("Добавьте именно это сообщество в беседу и назначьте администратором.")
        print("Если нужная беседа есть в списке выше под другим peer_id,")
        print("впишите этот peer_id в .env.")


if __name__ == "__main__":
    main()
