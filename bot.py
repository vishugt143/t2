# ============================================
# TELEGRAM REACTION BOT SYSTEM - PYTHON EDITION
# Deploy on Render.com
# ============================================

import asyncio
import time
import random
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import httpx

# 👇 YAHAN APNI CONFIG DAALO 👇
CONFIG = {
    "FIREBASE_URL": "https://rxn-bot-default-rtdb.asia-southeast1.firebasedatabase.app", # Apna Firebase URL daalo
    "FIREBASE_SECRET": "YOUR_FIREBASE_SECRET",                # Apna Database Secret daalo
    "ADMIN_SECRET": "8787",                                   # Panel aur Webhook ka password
    "TELEGRAM_API_BASE": "https://api.telegram.org/bot"
}
# 👆 BAS ITNA HI CHANGE KARNA HAI 👆

app = FastAPI(title="ReactCore Python Backend")

# Allow Panel to communicate (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. FIREBASE SERVICE ---
class FirebaseService:
    @staticmethod
    async def get_database():
        url = f"{CONFIG['FIREBASE_URL']}/campaigns.json?auth={CONFIG['FIREBASE_SECRET']}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json() or {}

    @staticmethod
    async def save_campaign(campaign_id: str, data: dict):
        url = f"{CONFIG['FIREBASE_URL']}/campaigns/{campaign_id}.json?auth={CONFIG['FIREBASE_SECRET']}"
        async with httpx.AsyncClient() as client:
            await client.put(url, json=data)

    @staticmethod
    async def update_campaign(campaign_id: str, data: dict):
        url = f"{CONFIG['FIREBASE_URL']}/campaigns/{campaign_id}.json?auth={CONFIG['FIREBASE_SECRET']}"
        async with httpx.AsyncClient() as client:
            await client.patch(url, json=data)

    @staticmethod
    async def delete_campaign(campaign_id: str):
        url = f"{CONFIG['FIREBASE_URL']}/campaigns/{campaign_id}.json?auth={CONFIG['FIREBASE_SECRET']}"
        async with httpx.AsyncClient() as client:
            await client.delete(url)

# --- 2. TELEGRAM SERVICE ---
class TelegramBotService:
    @staticmethod
    async def make_request(bot_token: str, method: str, params: dict):
        url = f"{CONFIG['TELEGRAM_API_BASE']}{bot_token}/{method}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=params)
                return response.json()
        except Exception:
            return {"ok": False}

    @staticmethod
    async def set_reaction(bot_token: str, chat_id: str, message_id: int, reaction: str):
        return await TelegramBotService.make_request(bot_token, 'setMessageReaction', {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": [{"type": "emoji", "emoji": reaction}]
        })

    @staticmethod
    async def add_view(bot_token: str, chat_id: str, message_id: int):
        bot_id = bot_token.split(":")[0]
        return await TelegramBotService.make_request(bot_token, 'forwardMessage', {
            "chat_id": bot_id,
            "from_chat_id": chat_id,
            "message_id": message_id
        })

    @staticmethod
    async def set_webhook(bot_token: str, url: str):
        return await TelegramBotService.make_request(bot_token, 'setWebhook', {
            "url": url,
            "secret_token": CONFIG['ADMIN_SECRET']
        })

    @staticmethod
    async def delete_webhook(bot_token: str):
        return await TelegramBotService.make_request(bot_token, 'deleteWebhook', {})

# --- 3. BACKGROUND TASKS (Logic for Webhook & Expiry) ---
async def process_post_reactions(campaign_id: str, post: dict):
    """Background task to handle reactions without blocking Telegram"""
    db = await FirebaseService.get_database()
    campaign = db.get(campaign_id)
    
    if campaign and campaign.get('status') == 'active' and campaign.get('reactions'):
        reactions_pool = campaign['reactions']
        chat_id = campaign['channel_id']
        msg_id = post['message_id']
        
        tasks = []
        
        # 1. Master Bot Action
        master_reaction = random.choice(reactions_pool).strip()
        tasks.append(TelegramBotService.set_reaction(campaign['bot_token'], chat_id, msg_id, master_reaction))
        
        # 2. Swarm Mode Actions (Secondary Bots)
        if campaign.get('type') == 'multi' and campaign.get('session_strings'):
            for token in campaign['session_strings']:
                token = token.strip()
                if ":" in token: # Validating simple bot token format
                    random_reaction = random.choice(reactions_pool).strip()
                    tasks.append(TelegramBotService.set_reaction(token, chat_id, msg_id, random_reaction))
        
        # Execute all bots at the exact same time
        await asyncio.gather(*tasks)

        # 3. View Boost
        if campaign.get('view_mode'):
            await TelegramBotService.add_view(campaign['bot_token'], chat_id, msg_id)

async def check_expired_campaigns():
    """Background loop that runs continuously to auto-expire bots"""
    while True:
        try:
            db = await FirebaseService.get_database()
            now = int(time.time() * 1000)
            
            for cid, campaign in db.items():
                if campaign.get('status') == 'active' and campaign.get('expiry') and now > campaign['expiry']:
                    await FirebaseService.update_campaign(cid, {"status": "expired"})
                    if campaign.get('bot_token'):
                        await TelegramBotService.delete_webhook(campaign['bot_token'])
        except Exception as e:
            print(f"Cron Error: {e}")
            
        await asyncio.sleep(60) # Check every 60 seconds

@app.on_event("startup")
async def startup_event():
    # Start the background expiry checker when server starts
    asyncio.create_task(check_expired_campaigns())

# --- 4. API ENDPOINTS (Connects with PHP Panel) ---

@app.post("/webhook/{campaign_id}")
async def webhook(campaign_id: str, request: Request, background_tasks: BackgroundTasks, x_telegram_bot_api_secret_token: str = Header(None)):
    if x_telegram_bot_api_secret_token != CONFIG["ADMIN_SECRET"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    update = await request.json()
    if "channel_post" in update:
        # Hand off the heavy lifting to the background task instantly
        background_tasks.add_task(process_post_reactions, campaign_id, update["channel_post"])
    
    return {"status": "OK"}

@app.get("/api/campaigns")
async def get_campaigns():
    data = await FirebaseService.get_database()
    return {"campaigns": data}

@app.post("/api/campaigns")
async def create_campaign(request: Request, x_admin_secret: str = Header(None)):
    if x_admin_secret != CONFIG["ADMIN_SECRET"]:
        raise HTTPException(status_code=401)
    
    body = await request.json()
    campaign_id = f"camp_{int(time.time() * 1000)}"
    body["status"] = "active"
    
    await FirebaseService.save_campaign(campaign_id, body)
    
    # Set webhook using Render's URL
    base_url = str(request.base_url).rstrip("/")
    await TelegramBotService.set_webhook(body["bot_token"], f"{base_url}/webhook/{campaign_id}")
    
    return {"success": True, "id": campaign_id}

@app.put("/api/campaigns/{campaign_id}")
async def edit_campaign(campaign_id: str, request: Request, x_admin_secret: str = Header(None)):
    if x_admin_secret != CONFIG["ADMIN_SECRET"]:
        raise HTTPException(status_code=401)
    
    body = await request.json()
    await FirebaseService.update_campaign(campaign_id, body)
    
    if body.get("bot_token"):
        base_url = str(request.base_url).rstrip("/")
        await TelegramBotService.set_webhook(body["bot_token"], f"{base_url}/webhook/{campaign_id}")
        
    return {"success": True}

@app.delete("/api/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, x_admin_secret: str = Header(None)):
    if x_admin_secret != CONFIG["ADMIN_SECRET"]:
        raise HTTPException(status_code=401)
    
    db = await FirebaseService.get_database()
    campaign = db.get(campaign_id)
    if campaign and campaign.get("bot_token"):
        await TelegramBotService.delete_webhook(campaign["bot_token"])
        
    await FirebaseService.delete_campaign(campaign_id)
    return {"success": True}

@app.get("/api/stats")
async def get_stats():
    data = await FirebaseService.get_database()
    active = sum(1 for c in data.values() if c.get("status") == "active")
    return {"stats": {"total": len(data), "active": active}}

@app.get("/")
def home():
    return {"status": "Render Node Active", "framework": "FastAPI"}
