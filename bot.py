import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from sql import *


db_name = 'data.db'
table_name = 'cards'
column_name = 'name'

# Replace 'YOUR_TOKEN' with the token you got from BotFather
TOKEN = '7240163852:AAHvWtYO6e6tTIB1lsvQo7aMtGgakAdxBtM'

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
        
async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
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
    file = update.message.document

    if file.mime_type == 'text/plain':  # Ensure it's a text file
        file_id = file.file_id
        new_file = await context.bot.get_file(file_id)
        file_url = new_file.file_path

        # Open the file in memory without saving it locally
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status == 200:
                    content = await response.text()
                    await update.message.reply_text(f'Content of the file:\n{content}')
                else:
                    await update.message.reply_text('Failed to read the file content. Please try again.')

    else:
        await update.message.reply_text('Please upload a valid text file.')

def main() -> None:
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("compare", compare))
    
    # Register a message handler to handle file uploads
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file_upload))
    

    

    # Start the Bot
    application.run_polling()
    print("Polling...")
    

if __name__ == '__main__':
    main()
