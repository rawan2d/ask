import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

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
def join_competition(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id not in participants:
        participants.add(user.id)
        update.message.reply_text(f"{user.first_name} has joined the competition!")
    else:
        update.message.reply_text("You have already joined the competition.")

# Function: Handle answers from participants
def handle_answer(update: Update, context: CallbackContext):
    global current_question

    user = update.effective_user
    if user.id not in remaining_participants:
        update.message.reply_text("You are not in the game or have been eliminated.")
        return

    if not current_question:
        update.message.reply_text("There is no active question right now.")
        return

    user_answer = " ".join(context.args).strip()
    if not user_answer:
        update.message.reply_text("Please provide an answer.")
        return

    answers[user.id] = user_answer
    update.message.reply_text("Answer received!")

# Function: Start the competition
def start_competition(context: CallbackContext):
    global remaining_participants, current_question

    if len(participants) < 5:
        context.bot.send_message(
            chat_id=context.job.context,
            text="Not enough participants to start the competition. At least 5 players are required."
        )
        return

    remaining_participants = list(participants)
    context.bot.send_message(
        chat_id=context.job.context,
        text="The competition has started! 🎉"
    )

    for question_set in questions:
        current_question = question_set
        answers.clear()  # Clear answers for each round

        context.bot.send_message(
            chat_id=context.job.context,
            text=f"Question: {question_set['question']}"
        )

        # Wait 15 seconds for answers
        asyncio.run(asyncio.sleep(15))

        # Eliminate participants who didn't answer or answered incorrectly
        remaining_participants = [
            user_id for user_id in remaining_participants
            if answers.get(user_id, "").lower() == question_set["answer"].lower()
        ]

        if len(remaining_participants) <= 5:
            break

        context.bot.send_message(
            chat_id=context.job.context,
            text=f"Remaining participants: {len(remaining_participants)}"
        )

    # Announce winners
    winners = [f"<b>{context.bot.get_chat(user_id).first_name}</b>" for user_id in remaining_participants]
    context.bot.send_message(
        chat_id=context.job.context,
        text=f"The competition is over! 🎉\nWinners: {', '.join(winners)}",
        parse_mode="HTML"
    )

# Schedule the competition
def schedule_competition(dispatcher, chat_id, hour, minute):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        start_competition,
        'cron',
        hour=hour,
        minute=minute,
        args=[dispatcher.bot],
        kwargs={'context': chat_id},
    )
    scheduler.start()
