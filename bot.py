import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# ჩაშალე ეს ტექსტი ბრჭყალებს შიგნით და ჩასვი შენი BOT_TOKEN (რომელიც BotFather-ისგან დააკოპირე)
BOT_TOKEN = "8802375334:AAHmfLBhEUKygID68wVZRtn5R4zgF5nN07k"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    keyboard = [[InlineKeyboardButton(f"📍 {city}", callback_data=f"city_{city}")] for city in config['cities']]
    await update.message.reply_text("გამარჯობა! აირჩიეთ ქალაქი:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    config = load_config()
    data = query.data

    if data.startswith("city_"):
        selected_city = data.replace("city_", "")
        keyboard = [
            [InlineKeyboardButton(f"🛍️ {p['name']} - {p['price']} {config['currency']}", callback_data=f"prod_{p['id']}")]
            for p in config['products'] if p['city'] == selected_city
        ]
        keyboard.append([InlineKeyboardButton("⬅️ უკან", callback_data="back_home")])
        await query.edit_message_text(f"📍 ქალაქი: {selected_city}\nაირჩიეთ პროდუქტი:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("prod_"):
        prod_id = data.replace("prod_", "")
        prod = next((p for p in config['products'] if p['id'] == prod_id), None)
        if prod:
            pay = config['payment_info']
            msg = (
                f"📦 *{prod['name']}*\n"
                f"📝 {prod['description']}\n"
                f"💰 ფასი: {prod['price']} {config['currency']}\n\n"
                f"💳 *გადახდის რეკვიზიტები:*\n"
                f"ბარათი: `{pay['card_number']}` ({pay['card_recipient']})\n"
                f"კრიპტო: `{pay['crypto_wallet']}`\n\n"
                f"გადახდის შემდეგ გამოაგზავნეთ ქვითრის ფოტო."
            )
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ მთავარი მენიუ", callback_data="back_home")]]))

    elif data == "back_home":
        keyboard = [[InlineKeyboardButton(f"📍 {city}", callback_data=f"city_{city}")] for city in config['cities']]
        await query.edit_message_text("გამარჯობა! აირჩიეთ ქალაქი:", reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
