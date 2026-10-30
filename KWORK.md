# KWORK

## Карточка 3. Telegram-бот для заявок → Google Sheets

**Цена:** от 2 500 ₽  
**Срок:** 1–2 дня  
**Репозиторий:** `kwork-tg-bot`

### Что входит

- бот принимает заявку по шагам: имя, телефон, комментарий;
- проверка телефона и команда отмены;
- сохранение в SQLite;
- выгрузка заявок в CSV;
- опциональная отправка в Google Sheets через Apps Script webhook;
- инструкция запуска и ограничения.

### Что нужно от покупателя

- токен Telegram-бота от @BotFather;
- текст приветствия и вопросы, если отличаются от стандартных;
- нужен ли Google Sheets и доступ к тестовой таблице;
- куда уведомлять о новых заявках.

### Что не входит

- админ-панель и роли операторов;
- оплата, рассылки и CRM;
- вложения, фото и голосовые;
- сложная антиспам-защита;
- хостинг и сопровождение после сдачи;
- автоматическая повторная отправка при недоступности Sheets.

### Дополнительно

- меню и FAQ — карточка 8;
- CRM/Sheets-сценарий — карточка 10;
- оплата в боте — карточка 16 и отдельная оценка.

### FAQ

**Где хранятся заявки?** В SQLite на вашем сервере; можно экспортировать в CSV.

**Обязателен ли Google Sheets?** Нет, это опциональный webhook.

**Что будет, если webhook недоступен?** Заявка останется в SQLite; ошибка не теряет данные, но автоматического повтора нет.

## Обложка (не копировать в карточку)

> Это промпт для генератора изображений, а не текст объявления. В Kwork его публиковать не нужно.

**Промпт для ChatGPT / Gemini:**

> 4:3 cover illustration for a Telegram lead-capture bot service. A smartphone with a minimal chat form on the left, a clean lead card and a small database cylinder in the middle, and a tidy spreadsheet row on the right; a subtle paper-plane trail connects them. Deep midnight-blue background, electric blue and mint accents, soft neon rim light, minimal geometric style, professional editorial tech look, high contrast, generous negative space, centered composition that survives a square crop, no text, no letters, no logos, no watermarks, no real person, crisp vector details.

**Коротко по-русски:** телефон с формой заявки → карточка лида и база → строка в таблице; тёмно-синий, голубой и мята; без текста, логотипов и брендов.

**Параметры:** 1200×900, 4:3; телефон и таблица не обрезаны по краям.

**Негатив:** text, typography, letters, Telegram logo, brand mark, watermark, real person, cluttered chat, low contrast, distorted phone.
