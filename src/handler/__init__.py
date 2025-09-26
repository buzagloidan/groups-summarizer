import asyncio
import logging

import httpx
from cachetools import TTLCache
from sqlmodel.ext.asyncio.session import AsyncSession

from handler.whatsapp_group_link_spam import WhatsappGroupLinkSpamHandler
from models import (
    WhatsAppWebhookPayload,
)
from whatsapp import WhatsAppClient
from summarize_and_send_to_groups import send_immediate_summaries_to_monitor
from config import Settings
from .base_handler import BaseHandler

logger = logging.getLogger(__name__)

# In-memory processing guard: 4 minutes TTL to prevent duplicate handling
_processing_cache = TTLCache(maxsize=1000, ttl=4 * 60)
_processing_lock = asyncio.Lock()


class MessageHandler(BaseHandler):
    def __init__(
            self,
            session: AsyncSession,
            whatsapp: WhatsAppClient,
            settings: Settings,
    ):
        self.whatsapp_group_link_spam = WhatsappGroupLinkSpamHandler(
            session, whatsapp
        )
        self.settings = settings
        super().__init__(session, whatsapp)

    async def __call__(self, payload: WhatsAppWebhookPayload):
        message = await self.store_message(payload)

        if (
                message
                and message.group
                and message.group.managed
                and message.group.forward_url
        ):
            await self.forward_message(payload, message.group.forward_url)

        # ignore messages that don't exist or don't have text
        if not message or not message.text:
            return

        # Ignore messages sent by the bot itself
        my_jid = await self.whatsapp.get_my_jid()
        if message.sender_jid == my_jid.normalize_str():
            return

        if message.sender_jid.endswith("@lid"):
            logging.info(
                f"Received message from {message.sender_jid}: {payload.model_dump_json()}"
            )

        # ignore messages from unmanaged groups
        if message and message.group and not message.group.managed:
            return

        # In-memory dedupe: if this message is already being processed/recently processed, skip
        if message and message.message_id:
            async with _processing_lock:
                if message.message_id in _processing_cache:
                    logging.info(
                        f"Message {message.message_id} already in processing cache; skipping."
                    )
                    return
                _processing_cache[message.message_id] = True

        # Check for secret word to trigger immediate summaries
        if (
            message
            and message.text
            and self.settings.secret_word
            and self.settings.monitor_phone
            and message.text.strip().lower() == self.settings.secret_word.lower()
        ):
            logging.info(f"Secret word detected from {message.sender_jid}, triggering immediate summaries")
            try:
                await send_immediate_summaries_to_monitor(
                    self.session,
                    self.whatsapp,
                    self.settings.monitor_phone,
                    message.sender_jid
                )
            except Exception as e:
                logging.error(f"Error sending immediate summaries: {e}")

        # Handle whatsapp links in group
        if (
                message.group
                and message.group.managed
                and message.group.notify_on_spam
                and "https://chat.whatsapp.com/" in message.text
        ):
            await self.whatsapp_group_link_spam(message)

    async def forward_message(
            self, payload: WhatsAppWebhookPayload, forward_url: str
    ) -> None:
        """
        Forward a message to the group's configured forward URL using HTTP POST.

        :param payload: The WhatsApp webhook payload to forward
        :param forward_url: The URL to forward the message to
        """
        # Ensure we have a forward URL
        if not forward_url:
            return

        try:
            # Create an async HTTP client and forward the message
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    forward_url,
                    json=payload.model_dump(
                        mode="json"
                    ),  # Convert Pydantic model to dict for JSON serialization
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()

        except httpx.HTTPError as exc:
            # Log the error but don't raise it to avoid breaking message processing
            logger.error(f"Failed to forward message to {forward_url}: {exc}")
        except Exception as exc:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error forwarding message to {forward_url}: {exc}")
