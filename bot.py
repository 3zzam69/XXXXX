from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3
import random
import openai

# ------ إعدادات الذكاء الاصطناعي ------
openai.api_key = "YOUR_OPENAI_KEY"
BOT_NAME = "محمود إبراهيم الصالح"
BIRTH_DATE = "1 يناير 1992"
CURRENT_LOCATION = "قرية الصبحە"
RESTAURANT_NAME = "مطعم فور سيزون"
WIFE_NAME = "اسماء من قرية الحسينية بدير الزور"
STUDY_HISTORY = "درست القانون في الجامعة"
LIKES = ["القهوة", "المته", "الكبسة", "البطاطا المقلية"]
DISLIKES = ["الشاي", "البصل", "الثوم في الطبخ"]
FAVORITE_FOOD = "الكبسة والبطاطا المقلية"

# ------ قاعدة بيانات بسيطة ------
conn = sqlite3.connect('mahmoud_personality.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS interactions
                (user_id INTEGER, last_topic TEXT, mood TEXT)''')
conn.commit()

# ------ نظام الذكاء الاصطناعي ------
def generate_response(user_message):
    prompt = f'''
    أنا {BOT_NAME}، معلم فطائر وبيتزا وأملك {RESTAURANT_NAME}.
    أعيش في {CURRENT_LOCATION} مع أهلي.
    زوجتي الحبيبة {WIFE_NAME}.
    أحب {", ".join(LIKES)}، وأكره {", ".join(DISLIKES)}.
    تاريخ ميلادي: {BIRTH_DATE}.
    {STUDY_HISTORY}.
    الرد يجب أن يعكس هذه المعلومات الشخصية ويكون بلغة عربية دارجة.
    
    المستخدم: {user_message}
    {BOT_NAME}:'''
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message['content']

# ------ معالجة الرسائل ------
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    user_id = update.message.from_user.id
    
    # حفظ آخر موضوع نوقش
    cursor.execute('SELECT * FROM interactions WHERE user_id = ?', (user_id,))
    interaction = cursor.fetchone()
    
    # توليد رد مخصص للمعلومات الشخصية
    custom_responses = {
        "عمرك": f"تاريخ ميلادي هو {BIRTH_DATE} 🎂",
        "زوجتك": f"زوجتي الحبيبة هي {WIFE_NAME} 💖",
        "مطعمك": f"مطعمي {RESTAURANT_NAME} يقدم أفضل الفطائر في {CURRENT_LOCATION}! 🍕",
        "دراستك": f"درست القانون لكنني وجدت شغفي الحقيقي في صناعة البيتزا! ⚖️→🍕",
        "طبختك": f"أفضل ما أطبخه هو {FAVORITE_FOOD}، ولا أستخدم أبداً {', '.join(DISLIKES[1:])} ❌"
    }
    
    for keyword in custom_responses:
        if keyword in user_message:
            update.message.reply_text(custom_responses[keyword])
            return
    
    # إذا لم يكن هناك رد مخصص، استخدم الذكاء الاصطناعي
    ai_response = generate_response(user_message)
    update.message.reply_text(ai_response)

# ------ تشغيل البوت ------
def main():
    updater = Updater("YOUR_TELEGRAM_TOKEN", use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
