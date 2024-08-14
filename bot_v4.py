import random
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load the Excel file
df = pd.read_excel('words_translations.xlsx', header=None)

# Global variables to store the quiz state
current_word = None
correct_answer = None
correct_count = 0
total_questions = 2  # Number of words to check

# Start the quiz
def start(update: Update, context: CallbackContext) -> None:
    global correct_count
    correct_count = 0
    ask_question(update, context)

def ask_question(update: Update, context: CallbackContext) -> None:
    global current_word, correct_answer

    # Randomly select a word and its translation
    word_col = random.choice(df.columns)
    current_word = df.iloc[0, word_col]
    correct_answer = df.iloc[1, word_col]

    # Prepare options (1 correct + 3 random incorrect)
    all_translations = df.iloc[1, :].tolist()
    options = random.sample([t for t in all_translations if t != correct_answer], 3)
    options.append(correct_answer)
    random.shuffle(options)

    # Send the question with reply keyboard
    question = f"What is the translation for '{current_word}'?"
    reply_markup = ReplyKeyboardMarkup([[opt] for opt in options], one_time_keyboard=True)
    update.message.reply_text(question, reply_markup=reply_markup)

# Handle the user's answer
def handle_answer(update: Update, context: CallbackContext) -> None:
    global correct_count

    answer = update.message.text.strip()

    # Check if the answer is correct
    if answer == correct_answer:
        correct_count += 1
        update.message.reply_text("Correct!")
    else:
        update.message.reply_text(f"Incorrect. The correct answer was '{correct_answer}'.")

    # Move to the next question or finish
    if correct_count + context.user_data.get('asked_questions', 1) < total_questions:
        ask_question(update, context)
    else:
        update.message.reply_text(f"Quiz finished! You got {correct_count} out of {total_questions} correct.")
        context.user_data['asked_questions'] = 0  # Reset quiz state

def main():
    # Replace 'YOUR_TOKEN' with your actual bot token
    updater = Updater("YOUR_TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Start command handler
    dp.add_handler(CommandHandler("start", start))

    # Message handler for checking the answer
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_answer))

    # Start the bot
    updater.start_polling()

    # Run the bot until you stop it manually
    updater.idle()

if __name__ == '__main__':
    main()
