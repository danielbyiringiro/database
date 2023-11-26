from PIL import Image
from copy import deepcopy
from PIL import Image, ImageDraw, ImageFont
from flask import redirect, session
from functools import wraps
from cs50 import SQL
from datetime import datetime, timedelta
from random import choice

db = SQL("sqlite:///amagambo.db")

color_dic = {"GREEN": "#528d4e", "RED":"#ea433b","YELLOW": "#b49f39",'':None}

def generate_image(board, day, score, gap_size=5, tile_gap=2):
    colorboard = deepcopy(board)
    for i in range(len(board)):
        for j in range(len(board[i])):
            colorboard[i][j] = color_dic[board[i][j]]

    new_colorboard = []
    for row in colorboard:
        if all([x is not None for x in row]):
            new_colorboard.append(row)

    colorboard = new_colorboard

    # Define the size of each color square in the image
    square_size = 30 # Adjust the size according to your requirements

    # Calculate the dimensions of the colorboard image including gaps and the title bar
    num_rows = len(colorboard)
    num_cols = len(colorboard[0])

    #gap_offset = gap_size * (num_rows - 1)  # Total gap size for each row/column
    title_bar_height = 40

    # Calculate the required image width and height to accommodate all tiles
    image_width = max(num_cols * (square_size + gap_size) - gap_size + tile_gap, square_size) + 2
    image_height = num_rows * square_size + gap_size * (num_rows - 1) + title_bar_height + 2

    # Create a new image with the calculated dimensions
    image = Image.new('RGB', (image_width, image_height), color=(0, 0, 0))  # Set background color to black

    draw = ImageDraw.Draw(image)
    font_path = "/home/amagambo/.virtualenvs/flaskamagambo/Arial.ttf"
    title_font = ImageFont.truetype(font_path, 18)  # Use an available system font and adjust the size if needed

    title_text = f"Amagambo {day} - {score}/7"
    title_size = get_text_dimensions(title_text, font=title_font)

    title_x = (image_width - title_size[0]) // 2
    draw.text((title_x, 10), title_text, font=title_font, fill=(255, 255, 255))

    # Iterate through the colorboard and fill in each color square in the image with gaps
    for row in range(num_rows):
        for col in range(num_cols):
            color = colorboard[row][col]
            x1 = col * (square_size + gap_size) + tile_gap
            y1 = row * (square_size + gap_size) + title_bar_height
            x2 = x1 + square_size
            y2 = y1 + square_size
            image.paste(color, (x1, y1, x2, y2))

    # Save the image to a file

    image.save("static/colorboard.png", format='PNG')


def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    _, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def boardDefault():
    board = [
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['']
    ]
    return board

def letter(attempt_val, letter_position, board, color_board):

    letter = board[attempt_val][letter_position]
    color = color_board[attempt_val][letter_position]

    if color == "GREEN":
        return f"<div class='letter' id='correct'>{letter}</div>"
    elif color == "YELLOW":
        return f"<div class='letter' id='almost'>{letter}</div>"
    elif color == "RED":
        return f"<div class='letter' id='error'>{letter}</div>"
    else:
        return f"<div class='letter' id='{attempt_val}_{letter_position}'>{letter}</div>"


def letterDone(attempt_val, letter_position, color_board):

    board = boardDefault()
    letter = board[attempt_val][letter_position]
    color = color_board[attempt_val][letter_position]

    if color == "GREEN":
        return f"<div class='letter' attempt = {attempt_val} pos = {letter_position} id='correct'>{letter}</div>"
    elif color == "YELLOW":
        return f"<div class='letter' id='almost'>{letter}</div>"
    elif color == "RED":
        return f"<div class='letter' id='error'>{letter}</div>"
    else:
        return f"<div class='letter'>{letter}</div>"



def keyBoard():

    keyboard = {

        "key1" : ["Q","W","E","R", "T", "Y", "U", "I", "O", "P"],
        "key2" : ["A","S","D","F", "G", "H", "J", "K", "L"],
        "key3" : ["ENTER","Z","X","C","V", "B", "N", "M","DELETE"]

    }

    return keyboard

def position(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == "":
                return i, j

    return None, None

def checkFunction(guess):
    word = word_for_the_day()
    guess = guess.lower()
    all_words = words()

    if guess not in all_words:

        message = "Word not in list"
        isWin = False

        return message, isWin

    colors = []
    greens = []
    yellow = []

    for i in range(len(guess)):
        if guess[i] == word[i]:
            colors.append("GREEN")
            greens.append(word[i])
        elif guess[i] != word[i] and guess[i] in word and guess[i] not in greens and guess[i] not in yellow:
            colors.append("YELLOW")
            yellow.append(guess[i])
        else:
            colors.append("RED")

    if all([x == "GREEN" for x in colors]):

        isWin = True
        message = "Congratulation you guessed the word !!! Feel free to share your gameboard with friends"

        return message, isWin

    else:

        isWin = False

        return colors,isWin


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorate admin route to require user to be an admin.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin")  == False:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def search(email):
    """Searches if current email is in database"""
    rows = db.execute("SELECT * FROM user WHERE email = ?", email)

    return len(rows) == 0

def validate(password):
    """Validates if password meets security policy"""

    #check length
    if len(password) < 6:
        return "Password has to be at least 8 characters"

    #check if password contains a digit
    if not any([x for x in password if x.isdigit()]):
        return "Password has to contain at least a single digit"

    #check for letters:
    if not any([x for x in password if x.islower() or x.isupper()]):
        return "Password has to contain at least a single letter"

    #passed all checks
    return True


def days_between():
    """return days between the starting date and the current date"""

    today = datetime.today()

    target_date = datetime(2023, 7, 23)

    days_passed = (today - target_date).days

    dates_in_between = []

    for i in range(1, days_passed):
        date = target_date + timedelta(days=i)
        date = date.strftime("%Y-%m-%d")
        dates_in_between.append(date)

    return dates_in_between


def admin_details():

    dates = available_dates()
    details = []
    for date in dates:

        total_users = db.execute("select count(*) as num from user where created_at <= ?", date)[0]['num']
        unguessed = db.execute("select count(*) as num from play where isPlay = 'False' and date = ?", date)[0]['num']
        guessed = db.execute("select count(*) as num from play where isPlay = 'True' and date = ?", date)[0]['num']
        word = db.execute("select word from wordforday where date = ?", date)[0]['word']
        day_detail = {'date': date, 'total_users': total_users, 'guessed': guessed if not None else 0, 'unguessed': unguessed if not None else 0, 'word':word}

        details.append(day_detail)

    rev_details = []
    for i in reversed(details):
        rev_details.append(i)

    return rev_details

def day():

    today = datetime.today()
    date = today.strftime("%Y-%m-%d")
    return date

def num_day():

    numList = available_dates()
    return len(numList) + 1

def detail_recorded(id):

    today = day()
    rows = db.execute("select * from play where userId = ? and date = ?", id, today)
    return len(rows) == 0

def word_for_the_day():

    today = day()
    word_s = db.execute("select word from wordforday")
    rows = db.execute("select date from wordforday")
    dates = [row["date"] for row in rows]
    word_s = [row["word"] for row in word_s]
    if today in dates:
        word = db.execute("select word from wordforday where date = ?", today)[0]['word']
        return str(word)

    else:
        allwords = words()
        unused_words = [x for x in allwords if x not in word_s]
        word_for_day = choice(unused_words)
        bankid = db.execute("select ID from wordbank where word = ?", word_for_day)[0]['ID']
        db.execute("insert into wordforday(word,bankid,date) values(?,?,?)", word_for_day, int(bankid), today)
        return str(word_for_day)

def words():

    kinyaWords = []
    rows = db.execute("select word from wordbank")
    for row in rows:

        word = row['WORD']
        kinyaWords.append(word)

    kinyaWords[219] = 'kuyaga'
    kinyaWords[323] = 'ijambo'
    return kinyaWords

def available_dates():
    today = day()
    rows = db.execute("select date from wordforday where date != ? ", today)

    dates = [row["date"] for row in rows]
    return dates