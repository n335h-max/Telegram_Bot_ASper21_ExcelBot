import logging
import os
import asyncio
import sys
import random
from html import escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
import database

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states for uploading notes
UPLOAD_FILE, UPLOAD_TITLE, UPLOAD_SUBJECT = range(3)

# Fixed list of subjects
ALLOWED_SUBJECTS = [
    "BIOLOGY II",
    "CHEMISTRY II",
    "PHYSICS II",
    "MATHEMATICS II",
    "AGRICULTURE II"
]

# Initialize database
database.init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    # Add user to database
    database.add_user(user.id, user.full_name)
    
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Welcome to ASper21_ExcelBot. 📚"
        "\n\nYou can upload your notes or browse notes shared by others."
        "\n\nCommands:"
        "\n/upload - Share a new note"
        "\n/browse - View available notes"
        "\n/search - Find notes by keyword"
        "\n/my_notes - Manage your uploads"
        "\n/help - Show this help message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "📚 <b>ASper21_ExcelBot Help</b>\n\n"
        "<b>/upload</b> - Share a new note (PDF, Image, etc.)\n"
        "<b>/browse</b> - Browse notes by subject\n"
        "<b>/search [keyword]</b> - Search notes by title or subject\n"
        "<b>/my_notes</b> - See and delete your own shared notes\n"
        "<b>/cancel</b> - Stop the current upload process",
        parse_mode="HTML"
    )

# --- Search Functionality ---

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Search for notes by keyword."""
    if not context.args:
        await update.message.reply_text("Please provide a keyword to search for. Example: <code>/search cell</code>", parse_mode="HTML")
        return

    query = " ".join(context.args)
    results = database.search_notes(query)

    if not results:
        await update.message.reply_text(f"No results found for '{query}'.")
        return

    keyboard = [
        [InlineKeyboardButton(f"📄 {res[1]} ({res[2]})", callback_data=f"note_{res[0]}")]
        for res in results
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Search results for '{query}':", reply_markup=reply_markup)

# --- User Dashboard ---

async def my_notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List notes uploaded by the user."""
    user_id = update.effective_user.id
    notes = database.get_user_notes(user_id)

    if not notes:
        await update.message.reply_text("You haven't uploaded any notes yet. Use /upload to start sharing!")
        return

    text = "📂 <b>Your Uploaded Notes:</b>\n\n"
    keyboard = []
    for note in notes:
        note_id, title, subject, _ = note
        safe_title = escape(title)
        safe_subject = escape(subject)
        text += f"• {safe_title} ({safe_subject})\n"
        keyboard.append([InlineKeyboardButton(f"🗑 Delete '{title}'", callback_data=f"del_{note_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

async def handle_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle note deletion."""
    query = update.callback_query
    await query.answer()
    
    note_id = int(query.data.replace("del_", ""))
    user_id = update.effective_user.id
    
    success = database.delete_note(note_id, user_id)
    if success:
        await query.edit_message_text("✅ Note successfully deleted.")
    else:
        # Check if admin
        if str(user_id) == str(ADMIN_ID):
             if database.force_delete_note(note_id):
                 await query.edit_message_text("✅ Note deleted by Admin.")
                 return
        
        await query.edit_message_text("❌ Could not delete the note. You might not be the owner.")

# --- Admin Controls ---

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin controls."""
    user_id = str(update.effective_user.id)
    logger.info(f"Admin command attempted by user_id: {user_id}. Expected ADMIN_ID: {ADMIN_ID}")
    
    if user_id != ADMIN_ID:
        # Ignore unauthorized users
        return

    user_count, note_count = database.get_stats()
    
    await update.message.reply_text(
        "🕵️‍♂️ <b>Admin Dashboard</b>\n\n"
        f"👥 Total Users: {user_count}\n"
        f"📄 Total Notes: {note_count}\n\n"
        "Commands:\n"
        "/broadcast [message] - Send message to all users\n"
        "/delete_note [id] - Force delete a note by ID",
        parse_mode="HTML"
    )

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message to all users."""
    user_id = str(update.effective_user.id)
    if user_id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Please provide a message to broadcast.")
        return

    message = " ".join(context.args)
    safe_message = escape(message)
    users = database.get_all_users()
    
    success_count = 0
    await update.message.reply_text(f"📢 Starting broadcast to {len(users)} users...")
    
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>Announcement:</b>\n\n{safe_message}", parse_mode="HTML")
            success_count += 1
        except Exception as e:
            logger.warning(f"Failed to send to {uid}: {e}")
    
    await update.message.reply_text(f"✅ Broadcast complete. Sent to {success_count}/{len(users)} users.")

async def admin_delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Force delete a note by ID."""
    user_id = str(update.effective_user.id)
    if user_id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /delete_note <note_id>")
        return

    try:
        note_id = int(context.args[0])
        # We need a force delete function in database
        # For now, let's just assume we'll add `force_delete_note` to database.py
        if database.force_delete_note(note_id):
             await update.message.reply_text(f"✅ Note {note_id} deleted.")
        else:
             await update.message.reply_text(f"❌ Note {note_id} not found.")
    except ValueError:
        await update.message.reply_text("Invalid Note ID.")

# --- Upload Flow ---

async def start_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the upload process by asking for a file."""
    await update.message.reply_text(
        "Please send the note file you want to share (PDF, image, or any document)."
    )
    return UPLOAD_FILE

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the uploaded file and ask for a title."""
    message = update.message
    file = None
    file_name = "note"

    if message.document:
        file = message.document
        file_name = file.file_name
    elif message.photo:
        file = message.photo[-1]
        file_name = f"photo_{file.file_unique_id}.jpg"
    else:
        await update.message.reply_text("Please send a valid document or image.")
        return UPLOAD_FILE

    context.user_data['upload_file_id'] = file.file_id
    context.user_data['upload_file_unique_id'] = file.file_unique_id
    context.user_data['upload_file_name'] = file_name

    await update.message.reply_text(f"File received! Now, enter a title for this note.")
    return UPLOAD_TITLE

async def handle_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the title and ask for a subject."""
    context.user_data['upload_title'] = update.message.text
    
    reply_keyboard = [[sub] for sub in ALLOWED_SUBJECTS]
    await update.message.reply_text(
        "Great! Now, select the subject for this note from the options below:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return UPLOAD_SUBJECT

async def handle_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the subject and save the note."""
    subject = update.message.text
    
    if subject not in ALLOWED_SUBJECTS:
        await update.message.reply_text(
            "Please select a subject from the provided keyboard buttons."
        )
        return UPLOAD_SUBJECT

    user = update.effective_user
    
    database.add_note(
        file_id=context.user_data['upload_file_id'],
        file_unique_id=context.user_data['upload_file_unique_id'],
        file_name=context.user_data['upload_file_name'],
        title=context.user_data['upload_title'],
        subject=subject,
        user_id=user.id,
        user_name=user.full_name
    )

    # Random thank you messages
    messages = [
        f"✅ Successfully shared! I hope you will get an A for {subject}! 🌟",
        "✅ Successfully shared! Guess you are really smart huh? 😎",
        f"✅ Successfully shared! Thanks for helping others with {subject}! 📚",
        "✅ Successfully shared! You're a lifesaver! 🚀",
        f"✅ Successfully shared! {subject} notes received. Keep up the great work! ✨"
    ]
    thank_you_msg = random.choice(messages)

    await update.message.reply_text(
        thank_you_msg,
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text("Upload cancelled.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

# --- Browse Flow ---

async def browse_subjects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of subjects."""
    keyboard = [
        [InlineKeyboardButton(subject, callback_data=f"sub_{subject}")]
        for subject in ALLOWED_SUBJECTS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a subject to browse:", reply_markup=reply_markup)

async def handle_subject_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show notes for the selected subject."""
    query = update.callback_query
    await query.answer()
    
    subject = query.data.replace("sub_", "")
    notes = database.get_notes_by_subject(subject)
    
    if not notes:
        await query.edit_message_text(f"No notes found for {subject}.")
        return

    keyboard = [
        [InlineKeyboardButton(f"📄 {note[1]} ({note[2]})", callback_data=f"note_{note[0]}")]
        for note in notes
    ]
    keyboard.append([InlineKeyboardButton("🔙 Back to Subjects", callback_data="back_to_subjects")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Notes for {subject}:", reply_markup=reply_markup)

async def handle_note_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the selected note to the user."""
    query = update.callback_query
    await query.answer()
    
    note_id = int(query.data.replace("note_", ""))
    note = database.get_note_by_id(note_id)
    
    if not note:
        await query.edit_message_text("Sorry, note not found.")
        return

    file_id, file_name, title, subject = note
    
    await query.message.reply_text(f"Sending '{title}' ({subject})...")
    
    # Telegram handles file sending by file_id
    try:
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=file_id,
            filename=file_name,
            caption=f"Title: {title}\nSubject: {subject}"
        )
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        # Try sending as photo if document fails (might have been uploaded as photo)
        try:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=file_id,
                caption=f"Title: {title}\nSubject: {subject}"
            )
        except Exception as e2:
            logger.error(f"Error sending photo: {e2}")
            await query.message.reply_text("Could not send the file. It might have been deleted from Telegram servers.")

async def handle_back_to_subjects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to subject list."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton(subject, callback_data=f"sub_{subject}")]
        for subject in ALLOWED_SUBJECTS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select a subject to browse:", reply_markup=reply_markup)

def main() -> None:
    """Start the bot."""
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file.")
        return

    application = Application.builder().token(TOKEN).build()

    # Upload conversation handler
    upload_handler = ConversationHandler(
        entry_points=[CommandHandler("upload", start_upload)],
        states={
            UPLOAD_FILE: [MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file)],
            UPLOAD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)],
            UPLOAD_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_subject)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("browse", browse_subjects))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("my_notes", my_notes_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("delete_note", admin_delete_note))
    application.add_handler(upload_handler)
    
    # Callback queries for browsing and management
    application.add_handler(CallbackQueryHandler(handle_subject_selection, pattern="^sub_"))
    application.add_handler(CallbackQueryHandler(handle_note_selection, pattern="^note_"))
    application.add_handler(CallbackQueryHandler(handle_back_to_subjects, pattern="^back_to_subjects$"))
    application.add_handler(CallbackQueryHandler(handle_delete_callback, pattern="^del_"))

    # Run the bot
    print("Bot is starting...")
    
    # Check if we are running on Render (WEBHOOK_URL env var set)
    webhook_url = os.getenv("WEBHOOK_URL")
    
    if webhook_url:
        port = int(os.environ.get("PORT", 8080))
        print(f"Starting Webhook on port {port}...")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TOKEN,
            webhook_url=f"{webhook_url}/{TOKEN}",
            health_check_path="/"
        )
    else:
        print("Starting Polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Fix for asyncio event loop issue in some environments/Python versions
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    main()
