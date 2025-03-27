from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

import os
from dotenv import load_dotenv

load_dotenv()  # завантажує змінні з .env файлу

TOKEN = os.getenv("BOT_TOKEN")

# Словник для зберігання зареєстрованих користувачів
users = {}


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    users[user.id] = user.username  # Зберігаємо користувача в списку
    await update.message.reply_text(
        "Вітаємо! Я бот підтримки для осіб, що перебувають у прифронтовій зоні. Ось деякі команди, які ви можете використовувати:\n"
        "/situation - Поточна ситуація\n"
        "/resources - Доступні ресурси та послуги\n"
        "/communicate - Спілкування\n"
        "/safety - Інформація про безпеку\n"
        "/other - Інші ресурси"
    )


# Команда /communicate з кнопками
async def communicate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Спілкуйтеся з іншими людьми в прифронтовій зоні", callback_data='show_users')
        ],
        [
            InlineKeyboardButton("Спілкуйтеся з тими, хто підтримує", callback_data='support')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Спілкування:", reply_markup=reply_markup)


# Обробник для відображення списку користувачів
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Підтверджуємо запит

    if query.data == 'show_users':
        # Створюємо список інлайн-кнопок з доступними користувачами
        if users:
            keyboard = [[InlineKeyboardButton(username, callback_data=f'chat_{user_id}')] for user_id, username in
                        users.items()]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Оберіть користувача для спілкування:", reply_markup=reply_markup)
        else:
            await query.edit_message_text("Наразі немає доступних користувачів для спілкування.")


    elif query.data == 'support':
        await query.edit_message_text("Зараз ви не можете спілкуватися з підтримкою. Зв'яжіться пізніше.")


# Обробник вибору конкретного користувача для чату
async def chat_with_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Витягуємо ID вибраного користувача з callback_data
    user_id = int(query.data.split('_')[1])

    if user_id in users:
        await query.edit_message_text(
            f'Ви обрали {users[user_id]} для спілкування. Напишіть /send {user_id} <повідомлення>, щоб надіслати повідомлення.')
    else:
        await query.edit_message_text("Цей користувач більше недоступний для спілкування.")


# Команда для відправки повідомлення іншому користувачу
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = int(context.args[0])  # Отримуємо ID отримувача
        message_text = ' '.join(context.args[1:])  # Отримуємо повідомлення

        # Перевіряємо, чи зареєстрований отримувач
        if user_id in users:
            await context.bot.send_message(chat_id=user_id,
                                           text=f"Повідомлення від {update.message.from_user.username}: {message_text}")
            await update.message.reply_text(f"Повідомлення надіслано користувачу {users[user_id]}.")
        else:
            await update.message.reply_text("Користувач з таким ID не знайдений.")
    except (IndexError, ValueError):
        await update.message.reply_text("Невірний формат команди. Використовуйте /send <user_id> <повідомлення>.")


# Інші команди
async def situation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Поточна ситуація в прифронтовій зоні:\n"
        "1. Розташування бомбосховищ: ...\n"
        "2. Маршрути евакуації: ...\n"
        "3. Інші важливі дані: ..."
    )


async def resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Доступні ресурси та послуги:\n"
        "1. Медична допомога: ...\n"
        "2. Психологічне консультування: ...\n"
        "3. Правова допомога: ..."
    )


async def safety(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Інформація про безпеку:\n"
        "1. Як залишатися в безпеці: ...\n"
        "2. Як уникати обстрілів: ...\n"
        "3. Як знайти бомбосховище: ..."
    )


async def other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Інші ресурси:\n"
        "1. Карти: ...\n"
        "2. Новини: ...\n"
        "3. Погода: ..."
    )


def main() -> None:
    # Створюємо екземпляр Application
    application = Application.builder().token(TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("situation", situation))
    application.add_handler(CommandHandler("resources", resources))
    application.add_handler(CommandHandler("communicate", communicate))
    application.add_handler(CommandHandler("safety", safety))
    application.add_handler(CommandHandler("other", other))

    # Додаємо обробник натискань на кнопки
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^show_users$'))
    application.add_handler(CallbackQueryHandler(chat_with_user, pattern='^chat_'))

    # Додаємо обробник для надсилання повідомлень
    application.add_handler(CommandHandler("send", send_message))

    # Запускаємо бота в режимі опитування
    application.run_polling()


if __name__ == '__main__':
    main()
