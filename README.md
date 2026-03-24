# Telegram feedback bot for Vercel

Простой Telegram-бот на Python, который работает через webhook:

1. Пользователь пишет вашему боту.
2. Telegram отправляет `POST` на ваш endpoint на Vercel.
3. Код пересылает текст сообщения в ваш личный Telegram.

## Что нужно заранее

- аккаунт в Telegram
- аккаунт в [Vercel](https://vercel.com/)
- установленный [Vercel CLI](https://vercel.com/docs/cli), если хотите деплоить из терминала

## Файлы проекта

- `/api/index.py` — Flask entrypoint для Vercel
- `/requirements.txt` — Python зависимости
- `/vercel.json` — конфиг деплоя
- `/.python-version` — версия Python для Vercel
- `/.env.template` — шаблон для локального `.env`

## Переменные окружения

В Vercel добавьте:

- `TELEGRAM_BOT_TOKEN` — токен бота от BotFather
- `OWNER_CHAT_ID` — ваш личный Telegram chat id
- `WEBHOOK_SECRET` — любая длинная случайная строка, например `my-super-secret-token-123`

Для локальной разработки:

1. Скопируйте `.env.template` в `.env`
2. Подставьте свои реальные значения

```bash
cp .env.template .env
```

## Версия Python на Vercel

Vercel берет версию Python из файла `.python-version`.

В этом проекте указано:

```text
3.12
```

Если захотите, сможете поменять это значение позже.

## Где получить токены и id

### 1. Создать бота и получить `TELEGRAM_BOT_TOKEN`

1. Откройте в Telegram [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Задайте имя и username бота
4. BotFather пришлет токен вида:

```text
1234567890:AAExampleTokenHere
```

### 2. Получить ваш `OWNER_CHAT_ID`

Самый простой способ:

1. Откройте [@userinfobot](https://t.me/userinfobot)
2. Нажмите `Start`
3. Бот покажет ваш Telegram ID

Именно это число и нужно положить в `OWNER_CHAT_ID`.

## Как задеплоить на Vercel

### Вариант 1. Через сайт Vercel

1. Загрузите этот проект в GitHub
2. В Vercel нажмите `Add New Project`
3. Импортируйте репозиторий
4. В разделе Environment Variables добавьте:
   - `TELEGRAM_BOT_TOKEN`
   - `OWNER_CHAT_ID`
   - `WEBHOOK_SECRET`
5. Нажмите `Deploy`

### Вариант 2. Через Vercel CLI

Установить CLI:

```bash
npm i -g vercel
```

Логин:

```bash
vercel login
```

Первый деплой:

```bash
vercel
```

Продакшен-деплой:

```bash
vercel --prod
```

После этого Vercel даст URL, например:

```text
https://my-feedback-bot.vercel.app
```

Ваш webhook endpoint будет:

```text
https://my-feedback-bot.vercel.app/api/webhook
```

## Как привязать webhook к Telegram

После деплоя выполните в браузере или через `curl`:

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://my-feedback-bot.vercel.app/api/webhook",
    "secret_token": "my-super-secret-token-123"
  }'
```

Замените:

- `<TELEGRAM_BOT_TOKEN>` на ваш реальный токен
- `https://my-feedback-bot.vercel.app/api/webhook` на ваш реальный URL
- `my-super-secret-token-123` на значение `WEBHOOK_SECRET`

Если все хорошо, Telegram вернет:

```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

## Как проверить

1. Напишите что-нибудь вашему боту в Telegram
2. Telegram отправит webhook на Vercel
3. Ваш код отправит вам сообщение в личный Telegram

## Важно

- Бот пересылает только текст и подписи к медиа
- Голосовые, стикеры, файлы и другие типы сообщений помечаются как `unsupported message type`
- Этот проект не отвечает пользователю, а только пересылает сообщения вам

## Локальный запуск

Если хотите протестировать локально:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app api.index run --port 8000
```

Приложение само подхватит переменные из файла `.env`.

Локальная проверка health endpoint:

```bash
curl http://127.0.0.1:8000/
```

Ожидаемый ответ:

```json
{"message":"Telegram webhook is running","ok":true}
```

### Локальная проверка пересылки без Telegram

Можно руками отправить тестовый webhook:

```bash
curl -X POST http://127.0.0.1:8000/ \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: my-super-secret-token-123" \
  -d '{
    "message": {
      "message_id": 1,
      "from": {
        "id": 111111111,
        "first_name": "Test",
        "username": "test_user"
      },
      "chat": {
        "id": 111111111,
        "type": "private"
      },
      "text": "hello from local test"
    }
  }'
```

Если `TELEGRAM_BOT_TOKEN` и `OWNER_CHAT_ID` правильные, вы получите это сообщение у себя в Telegram.

### Локальная проверка настоящего webhook через ngrok

Telegram не умеет слать webhook на `localhost`, поэтому нужен публичный HTTPS URL.

1. Установите [ngrok](https://ngrok.com/)
2. Запустите локальный сервер:

```bash
flask --app api.index run --port 8000
```

3. В другом окне терминала поднимите туннель:

```bash
ngrok http 8000
```

4. Возьмите HTTPS URL от ngrok, например:

```text
https://abcd-1234.ngrok-free.app
```

5. Установите webhook в Telegram:

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://abcd-1234.ngrok-free.app/",
    "secret_token": "my-super-secret-token-123"
  }'
```

6. Напишите боту сообщение
7. Telegram отправит webhook в ваш локальный сервер через ngrok
8. Бот перешлет сообщение вам в Telegram

### Проверить текущий webhook

```bash
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

### Удалить webhook

Это полезно, если хотите переключиться с Vercel на локальный ngrok или обратно:

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/deleteWebhook"
```

Для продакшена лучше использовать Vercel, а локальный запуск удобен для быстрой проверки и отладки.
