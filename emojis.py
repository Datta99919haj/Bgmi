"""emojis.py — Catalog and helper methods for Telegram Custom / Premium Emojis.

Reference catalog: https://github.com/Zulut30/premium-telegram-emoji
In Telegram Bot API:
- In HTML: <tg-emoji emoji-id="1234567890">fallback</tg-emoji>
- In MarkdownV2: ![fallback](tg://emoji?id=1234567890)
"""

# Map of semantic / key name -> (emoji_id, fallback)
EMOJI_CATALOG = {
    # ── Section 1 — Animated News Emoji (Pack: https://t.me/addemoji/NewsEmoji) ──
    "breaking": ("5456140674028019486", "🚨"),
    "urgent": ("5224607267797606837", "⚡"),
    "percent": ("5229064374403998351", "%"),
    "ban": ("5260293700088511294", "🚫"),
    "cancel": ("5240241223632954241", "❌"),
    "exclamation": ("5274099962655816924", "❗"),
    "double_excl": ("5440660757194744323", "‼️"),
    "question": ("5436113877181941026", "❓"),
    "warning_yellow": ("5447644880824181073", "⚠️"),
    "warning_red": ("5420323339723881652", "🔴"),
    "internet": ("5447410659077661506", "🌐"),
    "cloud_text": ("5467538555158943525", "💬"),
    "chat": ("5443038326535759644", "💬"),
    "stats": ("5231200819986047254", "📊"),
    "chart_up": ("5449683594425410231", "📈"),
    "chart_down": ("5447183459602669338", "📉"),
    "stock_chart": ("5451882707875276247", "📈"),
    "rising": ("5244837092042750681", "📈"),
    "falling": ("5246762912428603768", "📉"),
    "checkmark": ("5206607081334906820", "✅"),
    "cross": ("5210952531676504517", "❌"),
    "bell": ("5458603043203327669", "🔔"),
    "pin": ("5397782960512444700", "📌"),
    "dollar": ("5409048419211682843", "💵"),
    "euro": ("5233326571099534068", "💶"),
    "ruble": ("5231449120635370684", "₽"),
    "yuan": ("5278751923338490157", "💴"),
    "pound": ("5290017777174722330", "💷"),
    "record": ("5411225014148014586", "⏺"),
    "fire": ("5424972470023104089", "🔥"),
    "explosion": ("5276032951342088188", "💥"),
    "mic": ("5224736245665511429", "🎙"),
    "announcement": ("5424818078833715060", "📢"),
    "fake_news": ("5449875686837726134", "🤥"),
    "secret": ("5431609822288033666", "🤫"),
    "quote": ("5460795800101594035", "💬"),
    "link": ("5271604874419647061", "🔗"),
    "info": ("5323442290708985472", "ℹ️"),
    "info2": ("5334544901428229844", "ℹ️"),
    "like": ("5337080053119336309", "👍"),
    "play": ("5348125953090403204", "▶️"),
    "pause": ("5359543311897998264", "⏸"),
    "refresh": ("5375338737028841420", "🔄"),
    "new_badge": ("5382357040008021292", "🆕"),
    "top": ("5415655814079723871", "🔝"),
    "soon": ("5440621591387980068", "⏳"),
    "location": ("5391032818111363540", "📍"),
    "plus": ("5397916757333654639", "➕"),
    "star": ("5438496463044752972", "⭐"),
    "bookmark": ("5222444124698853913", "🔖"),
    "letter": ("5253742260054409879", "✉️"),
    "lock": ("5296369303661067030", "🔒"),
    "paperclip": ("5305265301917549162", "📎"),
    "settings": ("5341715473882955310", "⚙️"),
    "speaker": ("5388632425314140043", "🔊"),
    "download": ("5386367538735104399", "⬇️"),
    "calendar": ("5413879192267805083", "📅"),
    "idea": ("5422439311196834318", "💡"),
    "free": ("5406756500108501710", "🆓"),
    "pencil": ("5395444784611480792", "✏️"),
    "discount": ("5406683434124859552", "🏷"),
    "red_flag": ("5460755126761312667", "🚩"),

    # ── Section 2 — Static App Icons (Pack: https://t.me/addemoji/logo_by_TgEmojiBot) ──
    "telegram": ("5206208353751024833", "✈️"),
    "tiktok": ("5206421491503088521", "🎵"),
    "instagram": ("5206383450977750405", "📸"),
    "youtube": ("5206230030450975877", "▶️"),
    "discord_static": ("5204222562736819197", "🎮"),
    "twitter_x": ("5204061664671976334", "🐦"),
    "vk": ("5206488346964018944", "💙"),
    "twitch_static": ("5206637287839910058", "🎮"),
    "linkedin": ("5206238027680071780", "💼"),
    "sbp": ("5206636501860893075", "💳"),
    "yoomoney": ("5206577300031684638", "💰"),
    "visa": ("5204357742537492089", "💳"),
    "mir": ("5206430772927416278", "💳"),
    "mastercard": ("5206505943445034137", "💳"),
    "unionpay": ("5204146997082212715", "💳"),
    "reddit": ("5204297737549401749", "🤖"),
    "boosty": ("5206603503627158548", "💛"),
    "firefox": ("5206467129825576500", "🦊"),
    "chrome": ("5206714141984703098", "🌐"),
    "safari": ("5204393970586634794", "🧭"),
    "edge": ("5206246871017733775", "🌊"),
    "opera": ("5204049982360930089", "🔴"),
    "yandex": ("5206329063806879532", "🔴"),
    "google": ("5206308821626012868", "🔍"),
    "photoshop": ("5206286797033719693", "🖼"),
    "after_effects": ("5203999112768279777", "🎬"),
    "premiere": ("5206200751658911590", "🎬"),
    "figma": ("5206378662089214861", "🎨"),
    "blender": ("5206629470999429293", "🌀"),
    "word": ("5204024191082318452", "📝"),
    "excel": ("5204205747939856389", "📊"),
    "powerpoint": ("5206624102290311682", "📊"),

    # ── Section 3 — Animated App Icons ──
    "tg_stars": ("5172484558305625218", "⭐"),
    "github": ("4999005636604723783", "🐙"),
    "twitch_anim": ("4999434394599948988", "🎮"),
    "discord_anim": ("5019579577924584242", "🎮"),
    "toggle": ("4970142833605345805", "🔁"),
    "heart_anim": ("4996980495100150380", "❤️"),
    "live": ("4927197721900614739", "🔴"),

    # ── Section 4 — Minimalist B&W Icons (Pack: https://t.me/addemoji/TgAndroidIcons) ──
    "tg_bw": ("5875465628285931233", "✈️"),
    "stars_bw": ("5958376256788502078", "⭐"),
    "settings_bw": ("5877260593903177342", "⚙️"),
    "install": ("5899757765743615694", "⬇️"),
    "back": ("5875082500023258804", "↩️"),
    "data": ("5877485980901971030", "📊"),
    "dog": ("5771887475421090729", "🐕"),
    "link_bw": ("5877465816030515018", "🔗"),
    "tag": ("5985433648810171091", "🏷"),
    "fav": ("5843843420468024653", "⭐"),
    "keyboard": ("5877396173135811032", "⌨️"),
    "dots": ("5875019892284985369", "…"),
    "check_bw": ("5825794181183836432", "✅"),
    "dots_up": ("5877219383691972108", "⋮"),
    "search": ("5874960879434338403", "🔍"),
    "forward": ("5877468380125990242", "↗️"),
    "trash": ("5879896690210639947", "🗑"),
    "copy": ("5877301185639091664", "📋"),
    "profile": ("5879770735999717115", "👤"),
    "archive": ("5967456680940671207", "🗃"),
    "pencil_bw": ("5879841310902324730", "✏️"),
    "updates": ("5877410604225924969", "🔄"),
    "rec_bw": ("5846024087033353251", "⏺"),
    "info_bw": ("5879785854284599288", "ℹ️"),
    "ban_bw": ("5872829476143894491", "🚫"),
    "excl_bw": ("5879813604068298387", "❗"),
    "internet_bw": ("5879585266426973039", "🌐"),

    # ── Section 5 — Custom Pack: DelvornCheat (https://t.me/addstickers/DelvornCheat) ──
    "delvorn_cheat": ("6161151927804502806", "😀"),
    "delvorn": ("6161151927804502806", "😀"),

    # ── Section 6 — Premium Emojis (DSPSIR, Random_emfx, Patriot_Pack, NewsEmoji, etc.) ──
    "dspsir_check": ("6116362711761687276", "✅"),
    "dspsir_alert": ("6257780484281997093", "🚨"),
    "heart_eyes": ("5233702221824173748", "🥰"),
    "heart_red": ("5244753103957277760", "❤️"),
    "strawberry": ("5238239167577628255", "🍓"),
    "nsfw_18": ("5275974823254725631", "🔞"),
    "strawberry_2": ("5260361384478157819", "🍓"),
    "strawberry_3": ("5346164763648870440", "🍓"),
    "smirk": ("5411420250476406699", "😏"),
    "black_heart": ("5913448455035949334", "🖤"),
    "black_heart_2": ("5913345616339014439", "🖤"),
    "checkbox_patriot": ("5913344229064577598", "☑️"),
    "eyes": ("5210956306952758910", "👀"),
    "lip_bite": ("5395444514028529554", "🫦"),
    "cool_sunglasses": ("6289761575272191135", "😎"),

    # ── Section 7 — New Batch (139 Emojis: sticks_f1795, Tgshaitaan, Kashyap, Kripansh, Memespremium, MatrixFont) ──
    "rocket_anim": ("6289276883917870488", "🚀"),
    "right_arrow_anim": ("6208698328167750089", "➡️"),
    "megaphone_anim": ("6208500192736450951", "📣"),
    "stop_sign_anim": ("6206384371587356863", "🛑"),
    "detective_anim": ("6141024787637471668", "🧐"),
    "smile_anim": ("6140999116617943287", "🙂"),
    "masks_anim": ("6141060654909360432", "🎭"),
    "pin_anim": ("6215512701804748627", "📌"),
    "cross_anim": ("6215407840178216561", "❌"),
    "desktop_anim": ("6113759377464760865", "🖥"),
    "tv_anim": ("6113666159494569105", "📺"),
    "stop_round_anim": ("6115919428187068527", "⛔"),
    "fire_shaitaan": ("6203736073277807578", "🔥"),
    "shield_anim": ("6282759103542468958", "🛡"),
    "kiss_cat_anim": ("6204033525532858608", "😽"),
    "fire_stick": ("6289627134205891883", "🔥"),
    "refresh_stick": ("6289508876576363345", "🔄"),
    "black_cat_anim": ("5958605483488055761", "🐈‍⬛"),
    "black_cat_anim2": ("5929300264497453950", "🐈‍⬛"),
    "japan_flag": ("5929487954568289296", "🇯🇵"),
    "leopard_anim": ("5929404477583922214", "🐆"),
    "lion_anim": ("5929146474603483609", "🦁"),
    "finger_up_1": ("5465144931230190889", "☝️"),
    "finger_up_2": ("5462931610028510371", "☝️"),
    "finger_up_3": ("5463123191339715467", "☝️"),
    "finger_up_4": ("5462900531645154669", "☝️"),
    "pink_heart": ("5294516622273318680", "🩷"),
    "tongue_anim": ("5199646700284687065", "👅"),
    "yum_anim": ("5294261750324042913", "😋"),
    "yum_anim2": ("5293990986995768044", "😋"),
    "swear_anim": ("5276419816226328169", "🤬"),
    "love_eyes": ("5343549493637827794", "😍"),
    "angry_anim": ("5242192272656708627", "😡"),
    "sleepy_anim": ("6129574787078429498", "😪"),
    "money_wings": ("6129680679497111287", "💸"),
    "star_gold": ("6129672630728400259", "🌟"),
    "lightning_anim": ("6129817830687775854", "⚡"),
    "skull_crossbones": ("6129889801454754893", "☠️"),
    "siren_anim": ("6129532640564354033", "🚨"),
    "gift_box": ("6129520790749584124", "🎁"),
    "bell_gold": ("6129652186684070216", "🔔"),
    "lightning_cloud": ("6129769130053605799", "🌩"),
    "heart_ribbon": ("6129895818703936830", "💝"),
    "two_hearts": ("6129476453802188018", "💕"),
    "ghost_anim": ("6129758830722030858", "👻"),
    "heart_arrow": ("6129602914819250817", "💘"),
    "surprised_anim": ("6129795982189141421", "😮"),
    "red_heart_glow": ("6156715484285770345", "❤️"),
    "star_glow": ("6156541396376361727", "🌟"),
    "skull_anim": ("6204172639523572930", "💀"),
    "thinking_anim": ("6204062606756415887", "🤔"),
    "moai_anim": ("6203999513686837822", "🗿"),
    "laugh_anim": ("6203985421899139846", "😂"),
    "blush_smile": ("6203936377667586967", "😊"),
    "unamused_anim": ("6204052328899679322", "😒"),
    "skull_meme": ("6204124913846979800", "💀"),
    "tongue_squint": ("6204154828294196038", "😝"),
    "coffee_cup": ("6204246817903741953", "☕️"),
    "angry_face": ("6203988273757424313", "😠"),
    "sunglasses_meme": ("6204203400079346542", "😎"),
    "eyebrow_anim": ("6204137858878408770", "🤨"),
    "cat_smile": ("6204211380128581672", "😺"),
    "peeking_anim": ("6206102428459206960", "🫣"),
    "rofl_anim": ("6206186330645334486", "🤣"),
    "crying_anim": ("6206495744384305279", "😭"),
    "disguise_face": ("6204152199774210704", "🥸"),
    "devil_anim": ("6203927663178945555", "😈"),
    "dancing_man": ("6204261266173725393", "🕺"),
    "crazy_face": ("6204083179649764891", "🤪"),
    "hot_face": ("6206367432236338118", "🥵"),
    "screaming_face": ("6206486750722787733", "😱"),
    "star_struck": ("6203715736607656627", "🤩"),
    "party_popper": ("6204071299770225371", "🥳"),
    "neutral_face": ("6204195110792464626", "😐"),
    "grin_anim": ("6204140861060549447", "😀"),
    "mute_speaker": ("6203752982564047567", "🔇"),
    "mind_blown": ("6203865454872627806", "🤯"),
    "steam_nose": ("6204096433918839077", "😤"),
    "dancing_woman": ("6203752282484378089", "💃"),
    "headphones_anim": ("6204100084641041391", "🎧"),
    "hugging_face": ("6203804376142712227", "🤗"),
    "facepalm_anim": ("6203887994860998039", "🤦‍♂️"),
    "weary_face": ("6204178716902296546", "😩"),
    "alien_anim": ("6206005727270537885", "👽"),
    "stop_sign_meme": ("6206087701016349357", "🛑"),
    "pensive_face": ("6203781745960028521", "😔"),
    "no_gesture": ("6204152642155843525", "🙅‍♂️"),
    "matrix_a": ("5193141001652285304", "🅰️"),
    "matrix_font1": ("5203919265031270345", "🔤"),
    "matrix_font2": ("5204202483764701671", "🔤"),
    "matrix_font3": ("5204140275458386538", "🔤"),
    "matrix_font4": ("5231018528689108942", "🔤"),
}



def get_custom_emoji_html(name_or_id: str, fallback: str = "") -> str:
    """Returns HTML tag for custom emoji: <tg-emoji emoji-id="...">fallback</tg-emoji>"""
    if name_or_id in EMOJI_CATALOG:
        eid, fb = EMOJI_CATALOG[name_or_id]
        return f'<tg-emoji emoji-id="{eid}">{fallback or fb}</tg-emoji>'
    # If passed directly as an ID
    return f'<tg-emoji emoji-id="{name_or_id}">{fallback or "✨"}</tg-emoji>'


def get_custom_emoji_md(name_or_id: str, fallback: str = "") -> str:
    """Returns MarkdownV2 format for custom emoji: ![fallback](tg://emoji?id=...)"""
    if name_or_id in EMOJI_CATALOG:
        eid, fb = EMOJI_CATALOG[name_or_id]
        fb_text = fallback or fb
        return f"![{fb_text}](tg://emoji?id={eid})"
    return f"![{fallback or '✨'}](tg://emoji?id={name_or_id})"


class _HtmlEmojiMeta(type):
    def __getattr__(cls, name: str) -> str:
        key = name.lower()
        if key in EMOJI_CATALOG:
            return get_custom_emoji_html(key)
        for cat_key in EMOJI_CATALOG:
            if key == cat_key or key in cat_key:
                return get_custom_emoji_html(cat_key)
        return get_custom_emoji_html("star_gold")


# Convenient quick accessors for common bot emojis in HTML
class HTML_EMOJI(metaclass=_HtmlEmojiMeta):
    FIRE        = get_custom_emoji_html("fire")
    URGENT      = get_custom_emoji_html("urgent")
    CHECKMARK   = get_custom_emoji_html("dspsir_check")  # Uses custom verified check
    CROSS       = get_custom_emoji_html("cancel")
    WARNING     = get_custom_emoji_html("warning_red")
    WARNING_YELLOW = get_custom_emoji_html("warning_yellow")
    INFO        = get_custom_emoji_html("info")
    BELL        = get_custom_emoji_html("bell")
    PIN         = get_custom_emoji_html("pin")
    LOCK        = get_custom_emoji_html("lock")
    SETTINGS    = get_custom_emoji_html("settings")
    STATS       = get_custom_emoji_html("stats")
    PLAY        = get_custom_emoji_html("play")
    PAUSE       = get_custom_emoji_html("pause")
    REFRESH     = get_custom_emoji_html("refresh")
    NEW         = get_custom_emoji_html("new_badge")
    STAR        = get_custom_emoji_html("star")
    TG_STARS    = get_custom_emoji_html("tg_stars")
    TELEGRAM    = get_custom_emoji_html("telegram")
    GITHUB      = get_custom_emoji_html("github")
    DISCORD     = get_custom_emoji_html("discord_anim")
    CALENDAR    = get_custom_emoji_html("calendar")
    DOWNLOAD    = get_custom_emoji_html("download")
    SEARCH      = get_custom_emoji_html("search")
    PROFILE     = get_custom_emoji_html("profile")
    EXPLOSION   = get_custom_emoji_html("explosion")
    LIVE        = get_custom_emoji_html("live")

    # Delvorn & newly added premium animated emojis
    DELVORN_CHEAT    = get_custom_emoji_html("delvorn_cheat")
    DELVORN          = get_custom_emoji_html("delvorn")
    DSPSIR_CHECK     = get_custom_emoji_html("dspsir_check")
    DSPSIR_ALERT     = get_custom_emoji_html("dspsir_alert")
    ALERT            = get_custom_emoji_html("dspsir_alert")
    EYES             = get_custom_emoji_html("eyes")
    COOL             = get_custom_emoji_html("cool_sunglasses")
    SMIRK            = get_custom_emoji_html("smirk")
    BLACK_HEART      = get_custom_emoji_html("black_heart")
    HEART_RED        = get_custom_emoji_html("heart_red")
    HEART_EYES       = get_custom_emoji_html("heart_eyes")
    STRAWBERRY       = get_custom_emoji_html("strawberry")
    NSFW             = get_custom_emoji_html("nsfw_18")
    LIP_BITE         = get_custom_emoji_html("lip_bite")
    CHECKBOX_PATRIOT = get_custom_emoji_html("checkbox_patriot")
    TARGET           = get_custom_emoji_html("pin_anim")
    HOURGLASS        = get_custom_emoji_html("soon")
    BAN              = get_custom_emoji_html("stop_sign_anim")
    QUESTION         = get_custom_emoji_html("question")
    EXCLAMATION      = get_custom_emoji_html("exclamation")
    DOUBLE_EXCL      = get_custom_emoji_html("double_excl")

    # Additional animated batch accessors
    ROCKET           = get_custom_emoji_html("rocket_anim")
    SHIELD           = get_custom_emoji_html("shield_anim")
    ARROW_RIGHT      = get_custom_emoji_html("right_arrow_anim")
    MEGAPHONE        = get_custom_emoji_html("megaphone_anim")
    STOP             = get_custom_emoji_html("stop_sign_anim")
    STOP_ROUND       = get_custom_emoji_html("stop_round_anim")
    DESKTOP          = get_custom_emoji_html("desktop_anim")
    TV               = get_custom_emoji_html("tv_anim")
    CROSS_ANIM       = get_custom_emoji_html("cross_anim")
    LIGHTNING        = get_custom_emoji_html("lightning_anim")
    SKULL            = get_custom_emoji_html("skull_anim")
    SKULL_BONES      = get_custom_emoji_html("skull_crossbones")
    MONEY            = get_custom_emoji_html("money_wings")
    STAR_GOLD        = get_custom_emoji_html("star_gold")
    GIFT             = get_custom_emoji_html("gift_box")
    GHOST            = get_custom_emoji_html("ghost_anim")
    THINKING         = get_custom_emoji_html("thinking_anim")
    ROFL             = get_custom_emoji_html("rofl_anim")
    DEVIL            = get_custom_emoji_html("devil_anim")
    PARTY            = get_custom_emoji_html("party_popper")
    COFFEE           = get_custom_emoji_html("coffee_cup")
    HEADPHONES       = get_custom_emoji_html("headphones_anim")
    LINK             = get_custom_emoji_html("link")
    CAMERA           = get_custom_emoji_html("instagram")
    DOCUMENT         = get_custom_emoji_html("word")
    TRASH            = get_custom_emoji_html("trash")
    USERS            = get_custom_emoji_html("profile")

    # Bot specific UI properties
    BROOM            = get_custom_emoji_html("refresh")
    CROWN            = get_custom_emoji_html("star_gold")
    STORE            = get_custom_emoji_html("money_wings")
    RESELLER         = get_custom_emoji_html("money_wings")
    KEY              = get_custom_emoji_html("lock")
    WAVE             = get_custom_emoji_html("delvorn_cheat")
    RULES            = get_custom_emoji_html("word")
    BOOK             = get_custom_emoji_html("word")
    NUM_1            = get_custom_emoji_html("pin_anim", "1️⃣")
    NUM_2            = get_custom_emoji_html("pin_anim", "2️⃣")
    NUM_3            = get_custom_emoji_html("pin_anim", "3️⃣")
    NUM_4            = get_custom_emoji_html("pin_anim", "4️⃣")
    NUM_5            = get_custom_emoji_html("pin_anim", "5️⃣")
    CANARY           = get_custom_emoji_html("delvorn_cheat")
    TIP              = get_custom_emoji_html("idea")
    CREDIT           = get_custom_emoji_html("dollar")
    COOLDOWN         = get_custom_emoji_html("refresh")
    REPEAT           = get_custom_emoji_html("refresh")
    BACK             = get_custom_emoji_html("back")
    VIP              = get_custom_emoji_html("lightning_anim")
    USER             = get_custom_emoji_html("profile")
    FREE_USER        = get_custom_emoji_html("profile")
    ACTIVE           = get_custom_emoji_html("dspsir_check")
    EXPIRED          = get_custom_emoji_html("cancel")
    BANNED           = get_custom_emoji_html("stop_sign_anim")
    MEDAL            = get_custom_emoji_html("star_gold")
    TIMER            = get_custom_emoji_html("soon")


# Mapping of raw unicode emojis to their corresponding custom animated emoji key
RAW_EMOJI_MAP = {
    "✅": "dspsir_check",
    "🚨": "dspsir_alert",
    "❌": "cancel",
    "⚡": "lightning_anim",
    "🔥": "fire",
    "🎯": "pin_anim",
    "📌": "pin_anim",
    "📍": "location",
    "⏳": "soon",
    "⏱": "soon",
    "⏰": "soon",
    "🚫": "stop_sign_anim",
    "⛔": "stop_sign_anim",
    "⚠️": "warning_yellow",
    "🔴": "warning_red",
    "🛑": "stop_sign_anim",
    "👑": "star_gold",
    "🌟": "star_gold",
    "⭐": "star_gold",
    "🚀": "rocket_anim",
    "🛡": "shield_anim",
    "🔑": "lock",
    "🔒": "lock",
    "💳": "money_wings",
    "💰": "money_wings",
    "💸": "money_wings",
    "👤": "profile",
    "👥": "profile",
    "📊": "stats",
    "📈": "chart_up",
    "📉": "chart_down",
    "🔄": "refresh",
    "🔁": "refresh",
    "🔔": "bell",
    "📢": "announcement",
    "📣": "megaphone_anim",
    "💬": "chat",
    "🎬": "tv_anim",
    "📺": "tv_anim",
    "🖥": "desktop_anim",
    "ℹ️": "info",
    "ℹ": "info",
    "💡": "idea",
    "❓": "question",
    "❗": "exclamation",
    "‼️": "double_excl",
    "💥": "explosion",
    "🆕": "new_badge",
    "🗑️": "trash",
    "🗑": "trash",
    "📋": "copy",
    "📝": "word",
    "🔗": "link",
    "📥": "download",
    "⬇️": "download",
    "📸": "instagram",
    "🎉": "party_popper",
    "🥳": "party_popper",
    "🎁": "gift_box",
    "💀": "skull_anim",
    "☠️": "skull_crossbones",
    "☠": "skull_crossbones",
    "👻": "ghost_anim",
    "🖤": "black_heart",
    "❤️": "heart_red",
    "❤": "heart_red",
    "🥰": "heart_eyes",
    "😍": "love_eyes",
    "😎": "cool_sunglasses",
    "😏": "smirk",
    "☕️": "coffee_cup",
    "☕": "coffee_cup",
    "🏪": "money_wings",
    "📜": "word",
    "📖": "word",
    "🛠️": "settings",
    "🛠": "settings",
    "⚙️": "settings",
    "⚙": "settings",
    "👉": "right_arrow_anim",
    "➡️": "right_arrow_anim",
    "▶️": "play",
    "👋": "delvorn_cheat",
    "😀": "delvorn_cheat",
    "🙂": "smile_anim",
    "✨": "star_gold",
    "📭": "letter",
    "✉️": "letter",
    "✉": "letter",
    "🆔": "profile",
    "📛": "profile",
    "📅": "calendar",
    "📆": "calendar",
    "🏷️": "tag",
    "🏷": "tag",
    "🔞": "nsfw_18",
    "🍓": "strawberry",
    "🫦": "lip_bite",
    "👀": "eyes",
    "🧐": "detective_anim",
    "🎭": "masks_anim",
    "🐱": "cat_smile",
    "😺": "cat_smile",
    "😽": "kiss_cat_anim",
    "🐈‍⬛": "black_cat_anim",
    "🐆": "leopard_anim",
    "🦁": "lion_anim",
    "🎧": "headphones_anim",
    "👽": "alien_anim",
    "🕺": "dancing_man",
    "💃": "dancing_woman",
    "🤯": "mind_blown",
    "🤔": "thinking_anim",
    "😂": "laugh_anim",
    "🤣": "rofl_anim",
    "😭": "crying_anim",
    "😡": "angry_anim",
    "🤬": "swear_anim",
    "😈": "devil_anim",
    "1️⃣": "pin_anim",
    "2️⃣": "pin_anim",
    "3️⃣": "pin_anim",
    "4️⃣": "pin_anim",
    "5️⃣": "pin_anim",
    "🧹": "refresh",
    "💼": "money_wings",
    "🔰": "shield_anim",
    "🎖️": "star_gold",
    "🎖": "star_gold",
    "🔙": "back",
    "🐥": "delvorn_cheat",
    "🐣": "delvorn_cheat",
    "🐤": "delvorn_cheat",
    "🎨": "figma",
    "📎": "paperclip",
    "🎮": "discord_anim",
    "🔊": "speaker",
    "🟢": "checkmark",
    "☝️": "right_arrow_anim",
    "☝": "right_arrow_anim",
    "⚔️": "shield_anim",
    "⚔": "shield_anim",
    "🐙": "github",
    "💶": "euro",
    "💛": "boosty",
    "🦊": "firefox",
    "🌀": "blender",
    "🐕": "dog",
    "💻": "desktop_anim",
    "☑️": "check_bw",
    "☑": "check_bw",
    "🎙️": "mic",
    "🎙": "mic",
    "↗️": "forward",
    "↗": "forward",
    "🔓": "lock",
    "🐦": "twitter_x",
    "💙": "vk",
    "🌊": "edge",
    "🤦": "mind_blown",
    "😠": "angry_anim",
    "🐍": "alien_anim",
    "😜": "mind_blown",
    "😤": "angry_anim",
    "▶": "play",
    "👍": "like",
    "🤥": "fake_news",
    "💷": "pound",
    "⏸️": "pause",
    "⏸": "pause",
    "🤨": "thinking_anim",
    "🤫": "secret",
    "✏️": "pencil",
    "✏": "pencil",
    "😱": "mind_blown",
    "🔇": "speaker",
    "🫣": "lip_bite",
    "📁": "archive",
    "📂": "archive",
    "🔖": "bookmark",
    "🥱": "thinking_anim",
    "💴": "yuan",
    "🤗": "heart_eyes",
    "💎": "star_gold",
    "🧭": "safari",
    "🤖": "reddit",
    "👅": "lip_bite",
    "🥵": "fire",
    "↩️": "back",
    "↩": "back",
    "➕": "plus",
    "✈️": "telegram",
    "✈": "telegram",
    "🙅": "stop_sign_anim",
    "💵": "dollar",
    "🔹": "star_gold",
    "🤪": "mind_blown",
    "➖": "cancel",
    "🔍": "search",
    "🔎": "search",
    "📦": "gift_box",
    "😒": "smirk",
    "🆓": "free",
    "💕": "heart_red",
    "🎵": "tiktok",
    "🧮": "stats",
    "🚩": "red_flag",
    "😐": "smile_anim",
    "⌨️": "keyboard",
    "⌨": "keyboard",
    "🌐": "internet",
    "💾": "archive",
    "🤩": "star_gold",
    "🗃️": "archive",
    "🗃": "archive",
    "😔": "crying_anim",
    "🔧": "settings",
    "💤": "soon",
    "😊": "smile_anim",
    "😮": "mind_blown",
    "🔝": "top",
    "⬇": "download",
    "⛈️": "lightning_anim",
    "⛈": "lightning_anim",
    "🥸": "detective_anim",
    "🌩️": "lightning_anim",
    "🌩": "lightning_anim",
    "🖼️": "photoshop",
    "🖼": "photoshop",
    "💘": "heart_red",
    "🔀": "refresh",
    "🩷": "heart_red",
    "➔": "right_arrow_anim",
    "➜": "right_arrow_anim",
    "➡": "right_arrow_anim",
    "🚧": "stop_sign_anim",
    "🗿": "star_gold",
    "😪": "thinking_anim",
    "😝": "mind_blown",
    "🐈": "cat_smile",
    "😩": "crying_anim",
    "🏓": "discord_anim",
    "😋": "heart_eyes",
    "⚠️": "warning_yellow",
    "⚠": "warning_yellow",
    "⏺️": "record",
    "⏺": "record",
    "🔤": "word",
    "💝": "gift_box",
}


import re

_TAG_SPLIT_REGEX = re.compile(r'(!\[.*?\]\(tg://emoji\?id=\d+\)|<tg-emoji[^>]*>.*?</tg-emoji>)')


def animate_text(text: str, mode: str = "html") -> str:
    """Replaces raw standard unicode emojis with premium animated telegram emojis,
    skipping text segments that are already premium emoji tags."""
    if not text:
        return ""
    # Filter mapping to base keys without \ufe0f for clean single pass replacement
    cleaned_map = {}
    for k, v in RAW_EMOJI_MAP.items():
        base = k.replace("\ufe0f", "")
        if base not in cleaned_map:
            cleaned_map[base] = v

    sorted_emojis = sorted(cleaned_map.keys(), key=len, reverse=True)
    parts = _TAG_SPLIT_REGEX.split(text)
    new_parts = []
    for part in parts:
        if not part:
            continue
        # If part is already an emoji tag, leave untouched
        if part.startswith("![") or part.startswith("<tg-emoji"):
            new_parts.append(part)
            continue
        # Normalize text by removing \ufe0f in non-tag parts
        sub = part.replace("\ufe0f", "")
        for emo in sorted_emojis:
            if emo in sub:
                cat_key = cleaned_map[emo]
                if mode == "html":
                    replacement = get_custom_emoji_html(cat_key, fallback=emo)
                else:
                    replacement = get_custom_emoji_md(cat_key, fallback=emo)
                sub = sub.replace(emo, replacement)
        new_parts.append(sub)
    return "".join(new_parts)




