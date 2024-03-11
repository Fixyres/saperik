import telebot
from telebot import types
import Minesweeper
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('API_BOT_TOKEN')
bot = telebot.TeleBot(token)
bot_users = {}

class BotUser:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.field_size = 0
        self.number_of_mines = 0
        self.field_with_hints = []
        self.mine_field = []
        self.minesweeper_game_mode = False
        self.number_of_opened_fields = 0

    def turn_on_game_mode(self):
        self.minesweeper_game_mode = True

    def turn_off_game_mode(self):
        self.minesweeper_game_mode = False

    def increase_count(self):
        self.number_of_opened_fields += 1


@bot.message_handler(commands=["start"])
def greetings(message):
    keyboard = types.InlineKeyboardMarkup()
    play_button = types.InlineKeyboardButton(text="Play Minesweeper", callback_data="/minesweeper")
    none_button = types.InlineKeyboardButton(text="Nothing", callback_data="/none")
    keyboard.add(play_button, none_button)
    bot.send_message(message.chat.id, "Hello, " + str(message.from_user.first_name) + "! What are we going to do"
                                                                                      " today?", reply_markup=keyboard)


@bot.message_handler(commands=["help"])
def help_message(message):
    bot.send_message(message.chat.id, "<b>/minesweeper - start game</b>", parse_mode="html")


@bot.message_handler(commands=["minesweeper"])
def minesweeper_game(message):
    global bot_users
    chat_id = message.chat.id
    if chat_id not in bot_users:
        bot_users[chat_id] = BotUser(chat_id)
    reply_keyboard = types.ReplyKeyboardMarkup()
    itm1 = types.KeyboardButton("4 on 4")
    itm2 = types.KeyboardButton("6 on 6")
    itm3 = types.KeyboardButton("8 on 8")
    reply_keyboard.add(itm1, itm2, itm3)
    clr_btn = types.KeyboardButton("Return")
    reply_keyboard.add(clr_btn)
    bot.send_message(message.chat.id, "Let's get started! Select field size:", reply_markup=reply_keyboard)
    bot.register_next_step_handler(message, field_size_selection)


def field_size_selection(message):
    global bot_users
    chat_id = message.chat.id
    user = bot_users[chat_id]
    user.number_of_opened_fields = 0
    if message.text in ("4 on 4", "4"):
        user.field_size = 4
        creating_difficulty_selection(message)
    elif message.text in ("6 on 6", "6"):
        user.field_size = 6
        creating_difficulty_selection(message)
    elif message.text in ("8 on 8", "8"):
        user.field_size = 8
        creating_difficulty_selection(message)
    elif message.text == "Return":
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "You have returned to the main menu.\nTo start, type /start",
                         reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.register_next_step_handler(message, field_size_selection)


def creating_difficulty_selection(message):
    global bot_users
    chat_id = message.chat.id
    user = bot_users[chat_id]
    easy = user.field_size ** 2 // 4
    normal = user.field_size ** 2 // 3
    hard = user.field_size ** 2 // 2
    reply_keyboard = types.ReplyKeyboardMarkup()
    itm_e = types.KeyboardButton(str(easy))
    itm_n = types.KeyboardButton(str(normal))
    itm_h = types.KeyboardButton(str(hard))
    reply_keyboard.add(itm_e, itm_n, itm_h)
    bot.send_message(message.chat.id,
                     "Great! Your field size: " + str(user.field_size) + " on " + str(user.field_size) +
                     ".\nNow let's choose the number of mines.", reply_markup=reply_keyboard)
    bot.register_next_step_handler(message, difficulty_selection)


def difficulty_selection(message):
    global bot_users
    chat_id = message.chat.id
    user = bot_users[chat_id]
    try:
        user_pick = int(message.text)
        if user_pick == 0:
            bot.send_message(message.chat.id, "Impossible without mines!!!\nTry again.")
            bot.register_next_step_handler(message, difficulty_selection)

        elif user_pick >= user.field_size ** 2 - 1:
            bot.send_message(message.chat.id, "Too many mines!!!\nTry again.")
            bot.register_next_step_handler(message, difficulty_selection)

        elif user_pick != 0 and int(message.text) < user.field_size ** 2 - 1:
            user.number_of_mines = int(message.text)
            bot.send_message(message.chat.id, "Great! Your number of mines: " + str(user.number_of_mines),
                             reply_markup=types.ReplyKeyboardRemove())

            user.mine_field = Minesweeper.generate_mine_field(user.field_size, user.number_of_mines)
            user.field_with_hints = Minesweeper.fill_field_with_hints(user.field_size, user.mine_field)
            start_game(message)
    except ValueError:
        bot.send_message(message.chat.id, "Insert the number.")
        bot.register_next_step_handler(message, difficulty_selection)


def start_game(message):
    global bot_users
    chat_id = message.chat.id
    user = bot_users[chat_id]
    n = user.field_size
    user.turn_on_game_mode()
    keyboard = types.InlineKeyboardMarkup(row_width=n)
    for i in range(n):
        buttons_list = []
        for j in range(n):
            button = types.InlineKeyboardButton(text="🥚️", callback_data=f"{str(i)+str(j)}")
            buttons_list.append(button)
        keyboard.add(*buttons_list)
    bot.send_message(message.chat.id, "Let's start the game!", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(callback):
    global bot_users
    chat_id = callback.message.chat.id
    if chat_id not in bot_users:
        bot_users[chat_id] = BotUser(chat_id)
    user = bot_users[chat_id]

    bot.answer_callback_query(callback_query_id=callback.id)

    if callback.data == "/minesweeper":
        bot.send_message(callback.message.chat.id, "To start the game, enter\n/minesweeper")

    if not user.minesweeper_game_mode: return

    try:
        user_choice = str(callback.data)
        x = int(user_choice[0])
        y = int(user_choice[1])
        n = user.field_size
        position = n * x + y
        if user.mine_field[position] == 0:
            user.number_of_opened_fields += 1  # COUNT
            if user.number_of_opened_fields >= len(user.mine_field) - user.number_of_mines:
                keyboard = types.InlineKeyboardMarkup(row_width=n)
                for i in range(n):
                    buttons_list = []
                    for j in range(n):
                        if user.mine_field[n * i + j] in ["open_field", 0]:
                            button = types.InlineKeyboardButton(text="🐣",
                                                                callback_data="🐣")
                            buttons_list.append(button)
                        else:
                            button = types.InlineKeyboardButton(text="💣",
                                                                callback_data="💣")  # 💣 🐣
                            buttons_list.append(button)
                    keyboard.add(*buttons_list)
                bot.delete_message(callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, f"You won!!!\n For a new game, enter /minesweeper",
                                 reply_markup=keyboard)
                user.number_of_opened_fields = 0
                user.turn_off_game_mode()
            else:
                user.mine_field[position] = "open_field"
                keyboard = types.InlineKeyboardMarkup(row_width=n)
                for i in range(n):
                    buttons_list = []
                    for j in range(n):
                        if user.mine_field[n * i + j] == "open_field":
                            button = types.InlineKeyboardButton(text=f"{user.field_with_hints[n * i + j]}",
                                                                callback_data=f"{str(i) + str(j)}")
                            buttons_list.append(button)
                        else:
                            button = types.InlineKeyboardButton(text="🥚",
                                                                callback_data=f"{str(i) + str(j)}")
                            buttons_list.append(button)
                    keyboard.add(*buttons_list)
                bot.delete_message(callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, f"{'🐣' * 3 * n}", reply_markup=keyboard)

        if user.mine_field[position] == 1:
            user.number_of_opened_fields = 0
            user.turn_off_game_mode()
            keyboard = types.InlineKeyboardMarkup(row_width=n)
            for i in range(n):
                buttons_list = []
                for j in range(n):
                    if user.mine_field[n * i + j] in ["open_field", 0]:
                        button = types.InlineKeyboardButton(text="🐣",
                                                            callback_data="🐣")
                        buttons_list.append(button)
                    else:
                        button = types.InlineKeyboardButton(text="💣",
                                                            callback_data="💣")
                        buttons_list.append(button)
                keyboard.add(*buttons_list)
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
            bot.send_message(callback.message.chat.id, f"You lost. \nLet's try again?\n/minesweeper",
                             reply_markup=keyboard)

    except ValueError:
        pass


@bot.message_handler(commands=["clear"])
def clear_handler(message):
    bot.delete_message(message.chat.id, message.id)
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "text", reply_markup=types.ReplyKeyboardRemove())


if __name__ == '__main__':
    bot.infinity_polling()
