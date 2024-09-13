import aiohttp
import os
import logging # to be implemented
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from sql import *


db_name = 'data.db'
table_name = 'cards'
column_name = 'name'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! Use /search <query> to search.')
    
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Join all the arguments to form the search query
    query = ' '.join(context.args)
    if query:
        response = search_card(db_name,table_name,column_name,query)
        if response =="No results...":
            await update.message.reply_text(response)
        else:
            for row in response:
                await update.message.reply_text(row)
    else:
        await update.message.reply_text('Please provide a query.')
        
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Join all the arguments to form the search query
    query :str = ' '.join(context.args)
    if query:
        
        response = add_or_update_quantity(db_name,table_name,query)
        
        await update.message.reply_text(response)
    else:
        await update.message.reply_text('Please provide a query.')


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
    query = ' '.join(context.args)
    if query:
        response = subtract_quantity(db_name,table_name, query)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text('Please provide a query.')
        
async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:##TODO implement ez list compare
    query = ' '.join(context.args)
    if query:
        response = search_card_exact_and_compare(db_name,table_name,column_name, file_path=query)
        if isinstance(response,list):
            for row in response:
             await update.message.reply_text(row)
        else:
            await update.message.reply_text(response)
    else:
        await update.message.reply_text('Please provide a query.')


async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    # logging.info(update.message.chat.first_name + "" + " uploaded a file")
    command = update.message.caption.split()[0]
    file = update.message.document
    if command == "/compare":  
        if file.mime_type == 'text/plain':  # Ensure it's a text file
            file_id = file.file_id
            new_file = await context.bot.get_file(file_id)
            file_url = new_file.file_path

            # Open the file in memory without saving it locally
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        content = search_card_exact_and_compare(db_name,table_name,column_name, await response.text())
                        response = ""
                        for row in content:
                            response += row + "\n"
                        await update.message.reply_text(response)
                    else:
                        await update.message.reply_text('Failed to read the file content. Please try again.')
        else:
            await update.message.reply_text('Please upload a valid text file.')
    if command == "/add":
        if file.mime_type == 'text/plain':  # Ensure it's a text file
            file_id = file.file_id
            new_file = await context.bot.get_file(file_id)
            file_url = new_file.file_path

            # Open the file in memory without saving it locally
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        content = add_cards_from_file(db_name,table_name, await response.text())
                        response = ""
                        for row in content:
                            response += row + "\n"
                        await update.message.reply_text(response)
                    else:
                        await update.message.reply_text('Failed to read the file content. Please try again.')
        else:
            await update.message.reply_text('Please upload a valid text file.')

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.args = update.message.text.split()[1:]
    if context.args[0] == "search":
        await update.message.reply_text("Searching...")
    elif context.args[0] == "add":
        await update.message.reply_text("Adding...")

def get_env_variable(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError:
        message = f"Expected environment variable '{name}' not set."
        raise Exception(message)

def main() -> None:
    # Create the Application and pass it your bot's token
    application = Application.builder().token(get_env_variable("TG_API")).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("compare", compare))
    
    # Register a message handler to handle file uploads
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file_upload))
    #application.add_handler(MessageHandler(filters=[filters.Document.ALL,filters.Command], ))
    

    

    # Start the Bot
    application.run_polling()
    print("Polling...")
    

if __name__ == '__main__':
    main()
