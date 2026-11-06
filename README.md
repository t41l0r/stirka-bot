# VK бот: одно сообщение в день

Каждый день в заданное время отправляет в беседу VK текст из `messages.json`
(по умолчанию вт–вс в 06:45 по Москве, в понедельник не отправляет).

## 1. Подготовка VK
1. Сообщество → Управление → Работа с API → создать ключ доступа с правом «Сообщения сообщества».
2. Сообщество → Управление → Сообщения → включить сообщения сообщества.
3. Добавьте сообщество в беседу и **назначьте администратором** (иначе ошибки 917/927).
4. ID беседы: `VK_PEER_ID = 2000000000 + номер беседы` (первая беседа = 2000000001).

## 2. Запуск на Windows (проверка)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # впишите токен и VK_PEER_ID
python main.py --test "Проверка связи"
```
Если сообщение пришло в беседу, всё работает.
Постоянный запуск по расписанию: `python main.py`

## 3. Установка на Ubuntu VPS
```
sudo mkdir -p /opt/stirka-bot && sudo chown $USER /opt/stirka-bot
# скопируйте файлы проекта в /opt/stirka-bot
cd /opt/stirka-bot
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env
venv/bin/python main.py --test "Проверка связи"
sudo cp vk-daily-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vk-daily-bot
journalctl -u vk-daily-bot -f      # смотреть логи
```
В `vk-daily-bot.service` замените `User=botuser` на своего пользователя.

## Как это работает
- Тексты меняются в `messages.json` без перезапуска.
- В `bot.db` хранится история: за дату сообщение не уйдёт дважды.
- Бот включился позже 06:45 (опоздание больше 5 минут): за сегодня не отправляет, ждёт следующий день.
- При временных ошибках VK делает 3 попытки; `random_id` один и тот же, дубликатов нет.
- Токен хранится только в `.env` и не попадает ни в логи, ни в Git.
