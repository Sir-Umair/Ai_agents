from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.api import leads, emails, settings, responses, logs, auth
from app.services.follow_up_service import follow_up_service
from app.services.auto_reply_service import auto_reply_service

async def background_monitoring_task():
    """Runs continuously in the background to sync emails and send follow-ups."""
    while True:
        try:
            print("[Background Worker] Executing auto-reply and follow-up checks...")
            # 1. Process incoming replies (detects reply_received=True)
            # await auto_reply_service.check_and_reply_to_emails(user_email="...") 
            # Wait, auto_reply_service needs a specific user email! 
            # For a multi-user scalable system, we should query all connected users with valid tokens and run the check.
            from app.db import users_collection
            if users_collection is not None:
                users = await users_collection.find({"access_token": {"$exists": True}}).to_list(length=None)
                for u in users:
                    try:
                        await auto_reply_service.check_and_reply_to_emails(u["email"])
                    except Exception as e:
                        print(f"Error checking emails for {u['email']}: {e}")
            
            # 2. Send pending AI automated follow-ups
            await follow_up_service.process_pending_follow_ups()
            
        except Exception as e:
            print(f"[Background Worker] Error: {e}")
            
        await asyncio.sleep(30) # Run every 30 seconds for more responsiveness

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: spawn the background task
    task = asyncio.create_task(background_monitoring_task())
    yield
    # Shutdown: wait and cancel
    task.cancel()

app = FastAPI(
    title="Email Marketing Agent Backend",
    description="Backend for AI-powered Email Marketing with Auto Follow-ups and Reply Detection",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(emails.router)
app.include_router(settings.router)
app.include_router(responses.router)
app.include_router(logs.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Email Marketing Agent API. Visit /docs for Swagger UI."}
