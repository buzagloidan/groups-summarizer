from typing import Annotated

from fastapi import Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from handler import MessageHandler
from whatsapp import WhatsAppClient
from config import Settings


async def get_db_async_session(request: Request) -> AsyncSession:
    assert request.app.state.async_session, "AsyncSession generator not initialized"
    async with request.app.state.async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_whatsapp(request: Request) -> WhatsAppClient:
    assert request.app.state.whatsapp, "WhatsApp client not initialized"
    return request.app.state.whatsapp


def get_settings(request: Request) -> Settings:
    assert request.app.state.settings, "Settings not initialized"
    return request.app.state.settings


async def get_handler(
    session: Annotated[AsyncSession, Depends(get_db_async_session)],
    whatsapp: Annotated[WhatsAppClient, Depends(get_whatsapp)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> MessageHandler:
    return MessageHandler(session, whatsapp, settings)
