import logging
from dotenv import load_dotenv
import os
import random
import csv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes



# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# User tracker
user_tracker = {}

question_bank = {
    1: set(),
    2: set(),
    3: set()
}

# Read the CSV file
with open('questions.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        level = int(row['Level'])
        question = row['Question']
        question_bank[level].add(question)

print("-------QUESTION BANK-----------")
for level in question_bank.keys():
    questions = question_bank[level]
    print(f"LEVEL {level}")
    for qn in questions:
        print(qn)
print("-------------------------------")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if user not in user_tracker.keys():
        user_tracker[user] = {
            1: set(),
            2: set(),
            3: set()
        }
    
    print("------------------")
    print(user_tracker.keys())
    print("------------------")

    full_text = rf'''Hi {user.username}! Welcome to the UTR Picnic 2023 Bot, which will be used to facilitate the We Are Not Really Strangers Game.

To avoid repeating the same question, ensure that one group only uses one phone to interact with the bot.

To begin, press /help for instructions on how to play the game!
    '''

    await update.message.reply_html(
        full_text
    )

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE, level: int) -> None:
    user = update.effective_user

    if len(user_tracker[user][level]) == len(question_bank[level]):
        await update.message.reply_html(
            f"You have seen all the questions for level {level}! If you would like to reuse questions from this level, please press /reset!"
        )
        return
    
    question_list = list(question_bank[level])
    sampled_question = random.choice(question_list)
    while sampled_question in user_tracker[user][level]:
        sampled_question = random.choice(question_list)
    
    user_tracker[user][level].add(sampled_question)

    print("------------------")
    print(user)
    print(user_tracker[user])
    print("------------------")

    await update.message.reply_html(
        sampled_question
    )

async def level_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user not in user_tracker.keys():
        await start(update, context)

    level_text = update.message.text
    level = int(level_text[-1])

    assert level >= 1 and level <= 3
    await question(update, context, level=level)

# TODO: "List all questions" function

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user not in user_tracker.keys():
        await start(update, context)
    
    full_text = '''We Are Not Really Strangers is a game that allows people to understand each other better, through a series of questions ranked from Level 1 to 3.

Level 1 questions are simple, while subsequent levels become deeper and deeper, asking more and more about a person's beliefs and personality.

The flow of the game is as follows:

<b>Steps</b>

0. Make sure that your group is only using one phone to communicate with me! This phone is the "chosen phone".

1. Sit in a circle and nominate a person to begin.

2. The first person (Person A) to begin will type /level1 to the bot using the chosen phone.

3. I will reply with a Level 1 question.

4. Person A will ask the level 1 question to another person on their right (Person B).

5. Person B will give their answer and share more about themselves, based on the question.

6. <b>(Optional)</b> After Person B shares, the rest of the group can provide their responses to the question as well.

7. Person A will pass the phone to Person B.

8. Person B will repeat steps 2 to 7, asking the question to another person on their right (Person C).

9. Thus, the game will move in a circular fashion, from Person A to B, B to C, and so on.

10. After level 1 questions are exhausted, you may move on to /level2, and lastly /level3.

Hope you enjoy!
'''

    await update.message.reply_html(
        full_text
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user not in user_tracker.keys():
        await start(update, context)

    user_tracker[user] = {
        1: set(),
        2: set(),
        3: set()
    }

    await update.message.reply_html(
        f"Reset complete! You may now reuse questions that you have gone through previously again!"
    )


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("level1", level_handler))
    application.add_handler(CommandHandler("level2", level_handler))
    application.add_handler(CommandHandler("level3", level_handler))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

