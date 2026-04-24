from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from core.config import settings
from db.database import engine, Base
from modules.vendors.routers import vendor_router
from modules.users.routers import user_router
from modules.api_keys.routers import api_router
from modules.chatbots.routers import chatbot_router
from modules.conversations.routers import conversation_router
from modules.documents.routers import document_router
from modules.llms.routers import llm_router
from modules.embeddings.routers import embedding_router
from modules.auth.routers import auth_router
from modules.admins.routers import admin_router
from modules.vector_dbs.routers import vector_db_router
from modules.agent_logs.routers import agent_log_router
from modules.agents.routers.agent_router import router as agent_config_router
from modules.agents.routers.agent_activation_router import router as agent_activation_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="chatbot-inventory-FastAPI",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.include_router(user_router.router,          prefix="/users",         tags=["Users"])
app.include_router(vendor_router.router,        prefix="/vendors",       tags=["Vendors"])
app.include_router(api_router.router,           prefix="/api-keys",      tags=["API Keys"])
app.include_router(chatbot_router.router,       prefix="/chatbots",      tags=["Chatbots"])
app.include_router(conversation_router.router,  prefix="/conversations",  tags=["Conversations"])
app.include_router(document_router.router,      prefix="/documents",     tags=["Documents"])
app.include_router(llm_router.router,           prefix="/llms",          tags=["LLMs"])
app.include_router(embedding_router.router,     prefix="/embeddings",    tags=["Embeddings"])
app.include_router(auth_router.router,          prefix="/auth",          tags=["Auth"])
app.include_router(admin_router.router,         prefix="/admins",        tags=["Admins"])
app.include_router(vector_db_router.router,     prefix="/vector_dbs",    tags=["VectorDBs"])
app.include_router(agent_log_router.router,     prefix="/agents",        tags=["Agent Logs"])
app.include_router(agent_config_router,         prefix="/agents-config", tags=["Agents"])
app.include_router(agent_activation_router,     prefix="/agents-config", tags=["Agent Activation"])

# Serve static folder
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def index():
    return FileResponse(FRONTEND_DIR / "index.html", media_type="text/html")

@app.get("/signup")
async def signup():
    return FileResponse(FRONTEND_DIR / "signup.html", media_type="text/html")

@app.get("/admin/dashboard.html")
async def admin_dashboard():
    return FileResponse(FRONTEND_DIR / "admin/dashboard.html", media_type="text/html")

@app.get("/vendor/dashboard.html")
async def vendor_dashboard():
    return FileResponse(FRONTEND_DIR / "vendor/dashboard.html", media_type="text/html")

@app.get("/user/dashboard.html")
async def user_dashboard():
    return FileResponse(FRONTEND_DIR / "user/dashboard.html", media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=9000, reload=True)