from dotenv import get_key
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler, CallbackQueryHandler

from commands import (
    start, 
    caps, 
    talk, 
    get_all_links, 
    inline_link_provider, 
    get_token_status, 
    search,
    search_result_buttons,
    renew,
    cancel,
    extract_links,
    info,
)
from logging_module import logger
import traceback
import html
import json
from variables import DEVELOPER_CHAT_ID, ENV_PATH
from telegram.constants import ParseMode

    
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


if __name__ == '__main__':
    
    # load_dotenv('.env')
    BOT_TOKEN = get_key(ENV_PATH, 'API_TOKEN')
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps)
    talk_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), talk)
    links_handler = CommandHandler('season', get_all_links)

    application.add_handler(InlineQueryHandler(inline_link_provider)) #inline Handler
    application.add_handler(talk_handler)
    application.add_handler(start_handler)
    application.add_handler(caps_handler)
    application.add_handler(links_handler)
    application.add_handler(CommandHandler('info', info))
    
    # /verify token
    application.add_handler(CommandHandler('verify', get_token_status))
    application.add_handlers((CommandHandler('renew', renew), CommandHandler('cancel', cancel), )) # For token renewal

    application.add_handler(CommandHandler('search', search))
    application.add_handler(CallbackQueryHandler(search_result_buttons, pattern='^(\d+)$'))
    application.add_handler(CallbackQueryHandler(extract_links, pattern='^(\d+)p$'))

    application.add_error_handler(error_handler)

    application.run_polling()