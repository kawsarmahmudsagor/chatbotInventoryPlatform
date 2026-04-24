from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and ALL models
from backend.app.db.database import Base

from backend.app.modules.vendors.models.vendor_model import Vendor
from backend.app.modules.users.models.user_model import User
from backend.app.modules.chatbots.models.chatbot_model import Chatbot
from backend.app.modules.agents.models.agent_model import Agent
from backend.app.modules.documents.models.document_model import Document
from backend.app.modules.vector_dbs.models.vector_db_model import VectorDB
from backend.app.modules.conversations.models.conversation_model import Conversation
from backend.app.modules.messages.models.messages_model import Message
from backend.app.modules.llms.models.llm_model import LLM
from backend.app.modules.embeddings.models.embedding_model import Embedding
from backend.app.modules.api_keys.models.api_model import APIKey
from backend.app.modules.admins.models.admin_model import Admin
from backend.app.modules.agent_logs.models.agent_log_model import AgentLog

target_metadata = Base.metadata  # ← only set ONCE, here at the bottom of imports


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()