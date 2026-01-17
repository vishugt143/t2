


from os import path, getenv

class Config:
    API_ID = int(getenv("API_ID", "21419016"))
    API_HASH = getenv("API_HASH", "79198e1eb4cfd0f771a89d83b9144e7e")
    BOT_TOKEN = getenv("BOT_TOKEN", "8455395512:AAGbNe2nv9_ztC685urGaGLIeDH5hQdJIRQ")
    # Your Force Subscribe Channel Id Below=
    CHID = int(getenv("CHID", "-1003431327885")) # Make Bot Admin In This Channel
    # Admin Or Owner Id |
    SUDO = list(map(int, getenv("SUDO", "7554081592 7001232146 7564050858 5656436152").split()))
    MONGO_URI = getenv("MONGO_URI", "mongodb+srv://melodysotto4_db_user:BCUKIKDEAqFEzeCj@cluster0.trrt89o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    POSTS = [
        "https://t.me/forward_hack_lnx/3",
        "https://t.me/forward_hack_lnx/4"
    ]

cfg = Config()
