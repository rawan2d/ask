import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import ContextTypes

# Global variables
participants = set()  # Set of participants who joined the competition
remaining_participants = []  # List of participants still in the game
questions = [
    {"question": "What is 2 + 2?", "answer": "4"},
    {"question": "What is the capital of France?", "answer": "Paris"},
    {"question": "What is the largest planet in our Solar System?", "answer": "Jupiter"},
    {"question": "How many colors are in the rainbow?", "answer": "7"},
]
current_question = None  # Current question being asked
answers = {}  # Store user answers

# Function: Participants join the competition
async def join_competition(update: Update, context: ContextTypes.DEFAULT):
    user = update.effective_user
    if user.id not in participants:
        participants.add(user.id)
        await update.message.reply_text(f"{user.first_name} has joined the competition!")
    else:
        await update.message.reply_text("You have already joined the competition.")

# Function: Handle answers from participants
async def handle_answer(update: Update, context: ContextTypes.DEFAULT):
    global current_question

    user = update.effective_user
    if user.id not in remaining_participants:
        await update.message.reply_text("You are not in the game or have been eliminated.")
        return

    if not current_question:
        await update.message.reply_text("There is no active question right now.")
        return

    user_answer = " ".join(context.args).strip()
    if not user_answer:
        await update.message.reply_text("Please provide an answer.")
        return

    answers[user.id] = user_answer
    await update.message.reply_text("Answer received!")

# Function: Start the competition
async def start_competition(context: ContextTypes.DEFAULT):
    global remaining_participants, current_question

    if len(participants) < 5:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text="Not enough participants to start the competition. At least 5 players are required."
        )
        return

    remaining_participants = list(participants)
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="The competition has started! 🎉"
    )

    for question_set in questions:
        current_question = question_set
        answers.clear()  # Clear answers for each round

        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f"Question: {question_set['question']}"
        )

        await asyncio.sleep(15)  # Wait 15 seconds for answers

        # Eliminate participants who didn't answer or answered incorrectly
        remaining_participants = [
            user_id for user_id in remaining_participants
            if answers.get(user_id, "").lower() == question_set["answer"].lower()
        ]

        if len(remaining_participants) <= 5:
            break

        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f"Remaining participants: {len(remaining_participants)}"
        )

    # Announce winners
    winners = [f"<b>{context.bot.get_chat(user_id).first_name}</b>" for user_id in remaining_participants]
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f"The competition is over! 🎉\nWinners: {', '.join(winners)}",
        parse_mode="HTML"
    )

# Schedule the competition
def schedule_competition(application, chat_id, hour, minute):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        start_competition,
        trigger="cron",
        hour=hour,
        minute=minute,
        args=[application],
        kwargs={'context': {'job': {'chat_id': chat_id}}},
    )
    scheduler.start()
