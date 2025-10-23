import os
import logging
import datetime
import random
from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler
)

# Токен из переменных окружения Railway
BOT_TOKEN = os.environ['BOT_TOKEN']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

MONTH, YEAR, ZODIAC = range(3)
user_data = {}

ZODIAC_SIGNS = ['овен', 'телец', 'близнецы', 'рак', 'лев', 'дева', 'весы', 'скорпион', 'стрелец', 'козерог', 'водолей', 'рыбы']
MONTHS = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [['✨ Узнать свою судьбу'], ['🔄 Перезапустить']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🔮 *Предсказание*\n*Узнай свою судьбу*\n\nНажми на кнопку ниже чтобы начать! ✨",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает диалог"""
    keyboard = [
        ['Январь', 'Февраль', 'Март'],
        ['Апрель', 'Май', 'Июнь'],
        ['Июль', 'Август', 'Сентябрь'],
        ['Октябрь', 'Ноябрь', 'Декабрь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f'🔮 Привет! Выбери месяц рождения:',
        reply_markup=reply_markup
    )
    return MONTH

async def month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    month = update.message.text
    if month not in MONTHS:
        keyboard = [
            ['Январь', 'Февраль', 'Март'],
            ['Апрель', 'Май', 'Июнь'],
            ['Июль', 'Август', 'Сентябрь'],
            ['Октябрь', 'Ноябрь', 'Декабрь']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text('❌ Выбери месяц из списка:', reply_markup=reply_markup)
        return MONTH
    
    context.user_data['month'] = month
    await update.message.reply_text(
        f'✅ Месяц "{month}" сохранен.\n\nВведи год рождения (4 цифры):',
        reply_markup=ReplyKeyboardRemove()
    )
    return YEAR

async def year_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    year = update.message.text
    if not year.isdigit() or len(year) != 4:
        await update.message.reply_text('❌ Введите корректный год (4 цифры):')
        return YEAR
    
    year_int = int(year)
    current_year = datetime.datetime.now().year
    if year_int < 1900 or year_int > current_year:
        await update.message.reply_text(f'❌ Введите реальный год (1900-{current_year}):')
        return YEAR
    
    context.user_data['year'] = year
    keyboard = [
        ['Овен', 'Телец', 'Близнецы'],
        ['Рак', 'Лев', 'Дева'],
        ['Весы', 'Скорпион', 'Стрелец'],
        ['Козерог', 'Водолей', 'Рыбы']
    ]
    await update.message.reply_text(
        '✅ Год сохранен. Выбери знак зодиака:',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ZODIAC

async def zodiac_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    zodiac = update.message.text.lower()
    if zodiac not in [z.lower() for z in ZODIAC_SIGNS]:
        keyboard = [
            ['Овен', 'Телец', 'Близнецы'],
            ['Рак', 'Лев', 'Дева'],
            ['Весы', 'Скорпион', 'Стрелец'],
            ['Козерог', 'Водолей', 'Рыбы']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text('❌ Выбери знак из списка:', reply_markup=reply_markup)
        return ZODIAC
    
    context.user_data['zodiac'] = zodiac
    user_data[update.message.from_user.id] = context.user_data.copy()
    
    keyboard = [['🔮 Получить гороскоп на сегодня'], ['🔄 Перезапустить']]
    await update.message.reply_text(
        f'✅ Профиль сохранен! Знак: {zodiac.title()}',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ConversationHandler.END

async def show_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data:
        zodiac = user_data[user_id]['zodiac']
        horoscope = get_daily_horoscope(zodiac)
        
        await update.message.reply_text(
            f'✨ *Гороскоп для {zodiac.title()}*\n'
            f'📅 На сегодня: {datetime.datetime.now().strftime("%d.%m.%Y")}\n\n'
            f'{horoscope}',
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text('❌ Сначала настрой профиль: /start')

async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    context.user_data.clear()
    
    keyboard = [['✨ Узнать свою судьбу'], ['🔄 Перезапустить']]
    await update.message.reply_text(
        '🔄 Бот перезапущен! Нажми кнопку ниже чтобы начать заново!',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '✨ Узнать свою судьбу':
        await start_conversation(update, context)
    elif text == '🔮 Получить гороскоп на сегодня':
        await show_horoscope(update, context)
    elif text == '🔄 Перезапустить':
        await restart_bot(update, context)

def get_daily_horoscope(zodiac_sign):
    today = datetime.datetime.now()
    random.seed(f"{zodiac_sign}_{today.strftime('%Y%m%d')}")
    
    horoscopes = {
        'овен': "♈ Сегодня звезды благоприятствуют новым начинаниям! Смело беритесь за интересные проекты.",
        'телец': "♉ Хороший день для финансовых операций. Возможны неожиданные поступления.",
        'близнецы': "♊ Вас ждет интересное знакомство. Будьте открыты для общения.",
        'рак': "♋ Позаботьтесь о своем эмоциональном состоянии. Вечер проведите в спокойной обстановке.",
        'лев': "♌ Ваша харизма на высоте - используйте это!",
        'дева': "♍ День подходит для планирования и анализа.",
        'весы': "♎ Важны гармония в отношениях и компромиссы.",
        'скорпион': "♏ Глубокие мысли приведут к важным открытиям.",
        'стрелец': "♐ Путешествия или обучение принесут пользу.",
        'козерог': "♑ Упорство поможет достичь поставленных целей.",
        'водолей': "♒ День благоприятствует творчеству.",
        'рыбы': "♓ Прислушайтесь к своей интуиции."
    }
    return horoscopes.get(zodiac_sign.lower(), "🔮 Гороскоп временно недоступен.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.Regex('^✨ Узнать свою судьбу$'), start_conversation),
            CommandHandler("start", start_conversation)
        ],
        states={
            MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, month_handler)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, year_handler)],
            ZODIAC: [MessageHandler(filters.TEXT & ~filters.COMMAND, zodiac_handler)],
        },
        fallbacks=[CommandHandler("restart", restart_bot)]
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("restart", restart_bot))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("✅ Бот запущен на Railway!")
    application.run_polling()

if __name__ == '__main__':
    main()
