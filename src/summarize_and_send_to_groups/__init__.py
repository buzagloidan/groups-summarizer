import asyncio
import logging
from datetime import datetime

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from tenacity import (
    retry,
    wait_random_exponential,
    stop_after_attempt,
    before_sleep_log,
)

from models import Group, Message
from utils.chat_text import chat2text
from whatsapp import WhatsAppClient, SendMessageRequest

logger = logging.getLogger(__name__)


@retry(
    wait=wait_random_exponential(min=1, max=30),
    stop=stop_after_attempt(6),
    before_sleep=before_sleep_log(logger, logging.DEBUG),
    reraise=True,
)
async def summarize(group_name: str, messages: list[Message]) -> AgentRunResult[str]:
    agent = Agent(
        model="anthropic:claude-4-sonnet-20250514",
        system_prompt=f""""
        Write a quick summary of what happened in the chat group since the last summary.
        
        - Start by stating this is a quick summary of what happened in "{group_name}" group recently.
        - Use a casual conversational writing style.
        - Keep it short and sweet.
        - Write in the same language as the chat group. You MUST use the same language as the chat group!
        - Please do tag users while talking about them (e.g., @972536150150). ONLY answer with the new phrased query, no other text.
        """,
        output_type=str,
    )

    return await agent.run(chat2text(messages))


async def summarize_group(session, whatsapp: WhatsAppClient, group: Group) -> str | None:
    """Generate summary for a single group"""
    resp = await session.exec(
        select(Message)
        .where(Message.group_jid == group.group_jid)
        .where(Message.timestamp >= group.last_summary_sync)
        .where(Message.sender_jid != (await whatsapp.get_my_jid()).normalize_str())
        .order_by(desc(Message.timestamp))
    )
    messages: list[Message] = resp.all()

    if len(messages) < 15:
        logging.info("Not enough messages to summarize in group %s", group.group_name)
        return None

    try:
        response = await summarize(group.group_name or "group", messages)

        # Update the group with the new last_summary_sync
        group.last_summary_sync = datetime.now()
        session.add(group)
        await session.commit()

        return f"📱 *{group.group_name or 'Unknown Group'}*\n{response.data}\n\n"
    except Exception as e:
        logging.error("Error summarizing group %s: %s", group.group_name, e)
        return None


async def send_daily_summaries_to_monitor(session, whatsapp: WhatsAppClient, monitor_phone: str):
    """Send all group summaries to a single monitoring phone number"""
    groups = await session.exec(select(Group).where(Group.managed == True))  # noqa: E712

    summaries = []
    for group in list(groups.all()):
        summary = await summarize_group(session, whatsapp, group)
        if summary:
            summaries.append(summary)

    if not summaries:
        logging.info("No summaries generated for any groups")
        return

    full_message = "🌟 *Daily Group Summaries*\n\n" + "\n".join(summaries)

    try:
        await whatsapp.send_message(
            SendMessageRequest(phone=monitor_phone, message=full_message)
        )
        logging.info(f"Daily summaries sent to {monitor_phone}")
    except Exception as e:
        logging.error(f"Error sending daily summaries to {monitor_phone}: {e}")


async def send_immediate_summaries_to_monitor(session, whatsapp: WhatsAppClient, monitor_phone: str, requesting_jid: str):
    """Send immediate summaries triggered by secret word"""
    groups = await session.exec(select(Group).where(Group.managed == True))  # noqa: E712

    summaries = []
    for group in list(groups.all()):
        # For immediate summaries, don't update last_summary_sync - just generate summary
        resp = await session.exec(
            select(Message)
            .where(Message.group_jid == group.group_jid)
            .where(Message.timestamp >= group.last_summary_sync)
            .where(Message.sender_jid != (await whatsapp.get_my_jid()).normalize_str())
            .order_by(desc(Message.timestamp))
        )
        messages: list[Message] = resp.all()

        if len(messages) < 5:  # Lower threshold for immediate summaries
            logging.info("Not enough messages for immediate summary in group %s", group.group_name)
            continue

        try:
            response = await summarize(group.group_name or "group", messages)
            summaries.append(f"📱 *{group.group_name or 'Unknown Group'}*\n{response.data}\n\n")
        except Exception as e:
            logging.error("Error generating immediate summary for group %s: %s", group.group_name, e)

    if not summaries:
        message = "📋 *Immediate Summary Request*\n\nNo new messages found in any managed groups since last daily summary."
    else:
        message = "📋 *Immediate Summary Request*\n\n" + "\n".join(summaries)

    try:
        await whatsapp.send_message(
            SendMessageRequest(phone=monitor_phone, message=message)
        )
        logging.info(f"Immediate summaries sent to {monitor_phone} (requested by {requesting_jid})")
    except Exception as e:
        logging.error(f"Error sending immediate summaries to {monitor_phone}: {e}")


# Legacy function for API compatibility - now redirects to daily monitoring
async def summarize_and_send_to_groups(session: AsyncSession, whatsapp: WhatsAppClient):
    """Legacy function - now used for manual triggering of daily summaries"""
    # This would need the monitor phone to be configured
    logging.warning("summarize_and_send_to_groups called - consider using send_daily_summaries_to_monitor instead")
