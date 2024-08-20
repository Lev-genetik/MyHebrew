import random
import json
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import gspread as gc

# Load the Excel file
df = pd.read_csv('https://docs.google.com/spreadsheets/d/1zN9TD34nBWxIjSELOacF5CuTGIH1Pcak/pub?output=csv',
                   header=0,
                  )


#get token
# Opens the file in read-only mode and assigns the contents to the variable cfg to be accessed further down
with open('config.json', 'r') as cfg:
  # Deserialize the JSON data (essentially turning it into a Python dictionary object so we can use it in our code) 
  data = json.load(cfg)

# Global variables to store the quiz state
current_word = None
correct_answer = None
correct_count = 0
question_count = 0
total_questions = 20  # Number of words to check
token = data["token"]

# Start the quiz
def start(update: Update, context: CallbackContext) -> None:
    global correct_count
    global question_count
    correct_count = 0
    question_count = 0
    update.message.reply_text("Started")
    ask_question(update, context)

def ask_question(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Asking question! Ready?")
    global current_word, correct_answer
    # Randomly select a word and its translation
    word_row = random.choice(df.index)
    current_word = df.iloc[word_row, 0]
    correct_answer = df.iloc[word_row, 1]
    # Prepare options (1 correct + 3 random incorrect)
    all_translations = df.iloc[:, 1].tolist()
    options = random.sample([t for t in all_translations if t != correct_answer], 3)
    options.append(correct_answer)
    random.shuffle(options)
    # Send the question with reply keyboard
    question = f"What is the translation for '{current_word}'?"
    reply_markup = ReplyKeyboardMarkup([[opt] for opt in options], one_time_keyboard=True)
    update.message.reply_text(question, reply_markup=reply_markup)

# Handle the user's answer
def handle_answer(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Evaluating question..")
    global correct_count
    global question_count
    answer = update.message.text.strip() 
    # Check if the answer is correct
    if answer == correct_answer.strip():
        correct_count += 1
        update.message.reply_text("Correct!")
    else:
        update.message.reply_text(f"Incorrect. The correct answer was '{correct_answer}'.")
    # Move to the next question or finish
    question_count += 1
    if question_count < total_questions:
        update.message.reply_text("Going to next question")
        ask_question(update, context)
    else:
        update.message.reply_text(f"Quiz finished! You got {correct_count} out of {question_count} correct.")
        context.user_data['asked_questions'] = 0  # Reset quiz state

def main():
    updater = Updater(token, use_context=True)
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

