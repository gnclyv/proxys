import telebot
import requests
import io
import os
from telebot import types, apihelper

# --- AYARLAR ---
# Sənin Bot Tokenin
API_TOKEN = '8525524409:AAEQeFv29Sx7D70-bX0imqWnCi5b43feRbE'

# Sənin Telegram ID-n (Admin)
ADMIN_ID = 7754388468 

# !!! DİQQƏT: PythonAnywhere pulsuz istifadəçiləri üçün bu sətir mütləqdir !!!
apihelper.proxy = {'https': 'http://proxy.server:3128'}

bot = telebot.TeleBot(API_TOKEN)

# Proxy siyahısı üçün link
PROXY_URL = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=all&timeout=10000&country=all&ssl=all&anonymity=all"

# İstifadəçi bazası faylı
USER_FILE = "users.txt"

# --- FUNKSİYALAR ---

def save_user(user_id):
    """İstifadəçini bazaya qeyd edir"""
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f: f.write("")
    
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")

# --- KOMANDALAR ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.from_user.id)
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"👋 Merhaba, {user_name}!\n\n"
        "🤖 Bozz Proxy Bot'a hoş geldin. En güncel proxy listeleri için aşağıdakı butonu kullanabilirsin.\n\n"
        "📜 **Komutlar:**\n"
        "/proxy - Proxy listesini indir\n"
        "/stat - Bot istatistikleri (Sadece Admin)"
    )
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn = types.KeyboardButton('/proxy')
    markup.add(itembtn)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['stat'])
def show_stats(message):
    """Yalnız Admin (Sən) baxa bilərsən"""
    if message.from_user.id == ADMIN_ID:
        try:
            with open(USER_FILE, "r") as f:
                users = f.read().splitlines()
            bot.reply_to(message, f"📊 **Bot İstatistikleri:**\n\n👤 Toplam kullanıcı sayısı: {len(users)}")
        except:
            bot.reply_to(message, "⚠️ Henüz veri tabanı oluşmamış.")
    else:
        bot.reply_to(message, "❌ Bu komutu kullanma yetkiniz yok.")

@bot.message_handler(commands=['proxy'])
def get_proxy_list(message):
    sent_msg = bot.send_message(message.chat.id, "🔄 Liste hazırlanıyor, lütfen bekleyin...")
    
    try:
        # ProxyScrape-dən məlumat çəkirik
        response = requests.get(PROXY_URL)
        if response.status_code == 200:
            proxy_data = response.text
            proxy_count = len(proxy_data.splitlines())
            
            proxy_file = io.BytesIO(proxy_data.encode('utf-8'))
            proxy_file.name = "Bozz_Proxies.txt"
            
            bot.send_document(
                message.chat.id, 
                proxy_file, 
                caption=f"✅ Toplam {proxy_count} adet proxy bulundu.\n\n@nvseu tarafından sağlandı."
            )
            bot.delete_message(message.chat.id, sent_msg.message_id)
        else:
            bot.edit_message_text("❌ Proxy API hatası oluştu.", message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"⚠️ Bağlantı hatası: PythonAnywhere bu siteye erişimi engelliyor olabilir.\n\nHata: {str(e)}", message.chat.id, sent_msg.message_id)

# --- BOTU BAŞLAT ---
print("Bot Admin ID tənzimləməsi ilə aktiv edildi...")
bot.polling(none_stop=True)
