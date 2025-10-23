import os
import logging
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

# Настройка логирования для Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из переменных окружения Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не найден!")
    exit(1)

logger.info("✅ BOT_TOKEN загружен")

MONTH, YEAR, ZODIAC = range(3)
user_data = {}

ZODIAC_SIGNS = ['овен', 'телец', 'близнецы', 'рак', 'лев', 'дева', 'весы', 'скорпион', 'стрелец', 'козерог', 'водолей', 'рыбы']
MONTHS = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    logger.info(f"Пользователь {update.message.from_user.id} запустил бота")
    
    keyboard = [['✨ Узнать свою судьбу']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🔮 *Предсказание*\n*Узнай свою судьбу*\n\nНажми кнопку ниже чтобы начать! ✨",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает диалог"""
    logger.info("Начало диалога")
    
    keyboard = [
        ['Январь', 'Февраль', 'Март'],
        ['Апрель', 'Май', 'Июнь'],
        ['Июль', 'Август', 'Сентябрь'],
        ['Октябрь', 'Ноябрь', 'Декабрь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        '🔮 Выбери месяц рождения:',
        reply_markup=reply_markup
    )
    return MONTH

async def month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    month = update.message.text
    logger.info(f"Выбран месяц: {month}")
    
    if month not in MONTHS:
        await update.message.reply_text('❌ Выбери месяц из списка:')
        return MONTH
    
    context.user_data['month'] = month
    await update.message.reply_text(
        f'✅ Месяц сохранен. Введи год (4 цифры):',
        reply_markup=ReplyKeyboardRemove()
    )
    return YEAR

async def year_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    year = update.message.text
    logger.info(f"Введен год: {year}")
    
    if not year.isdigit() or len(year) != 4:
        await update.message.reply_text('❌ Введите корректный год (4 цифры):')
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
    zodiac = update.message.text
    logger.info(f"Выбран знак: {zodiac}")
    
    if zodiac.lower() not in [z.lower() for z in ZODIAC_SIGNS]:
        await update.message.reply_text('❌ Выбери знак из списка:')
        return ZODIAC
    
    context.user_data['zodiac'] = zodiac
    user_id = update.message.from_user.id
    user_data[user_id] = context.user_data.copy()
    
    keyboard = [['🔮 Получить гороскоп']]
    await update.message.reply_text(
        f'✅ Профиль сохранен! Знак: {zodiac}',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ConversationHandler.END

async def show_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    logger.info(f"Запрос гороскопа от пользователя {user_id}")
    
    if user_id in user_data:
        zodiac = user_data[user_id]['zodiac']
        horoscope = get_daily_horoscope(zodiac)
        await update.message.reply_text(f'✨ {zodiac}:\n{horoscope}')
    else:
        await update.message.reply_text('❌ Сначала настрой профиль: /start')

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logger.info(f"Текстовое сообщение: {text}")
    
    if text == '✨ Узнать свою судьбу':
        await start_conversation(update, context)
    elif text == '🔮 Получить гороскоп':
        await show_horoscope(update, context)

def get_daily_horoscope(zodiac_sign):
    horoscopes = {
        'овен': "♈ Сегодня звезды благоприятствуют новым начинаниям!",
        'телец': "♉ Хороший день для финансовых операций.",
        'близнецы': "♊ Вас ждет интересное знакомство.",
        'рак': "♋ Позаботьтесь о своем эмоциональном состоянии.",
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
    try:
        logger.info("🚀 Запуск бота...")
        
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
            fallbacks=[]
        )
        
        application.add_handler(conv_handler)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        
        logger.info("✅ Бот успешно запущен на Railway!")
        logger.info("🤖 Ожидание сообщений...")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")
        exit(1)

if __name__ == '__main__':
    main()
