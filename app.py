from flask import Flask, flash, render_template, request, session, redirect, jsonify
from flask_session import Session
from helper import *
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from ast import literal_eval

app = Flask(__name__)

db = SQL("sqlite:///amagambo.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Register user"""
    
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        if not email: #if email is empty
            flash("Email not provided")
            return redirect("/login")
        
        if not password:
            flash("Password not provided")
            return redirect("/login")

        # get password and the password confirmation

        rows = db.execute("SELECT * FROM user where email = ?", email)

        if not rows:
            flash("You are not registered. Sign Up")
            return redirect("/register")
        
        if not check_password_hash(rows[0]['hash'], password):
            flash("Username or password not correct")
            return redirect("/login")
            
        id = rows[0]["id"]
        session["user_id"] = id
        admin_id = [1]
        if id in admin_id:
            session["admin"] = True
        else:
            session["admin"] = False
            
        return redirect("/")
           
    else:

        return render_template("signin.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        if not email: #if email is empty
            flash("Email not provided")
            return redirect("/register")
        
        if not password:
            flash("Password not provided")
            return redirect("/register")
        
        # check if email already exists
        exists = search(email)
        
        if not exists:
            flash("Email already exists")
            return redirect("/register")
        
        # get password and the password confirmation
        
        password_confirm = request.form.get("password_confirm")

        # meets security standards
        response = validate(password)
        if  response == True:
            if password != password_confirm:
                flash("Passwords do not match")
                return redirect("/register")
            
            hash = generate_password_hash(password)
            time = day()
            db.execute("INSERT INTO user(email,hash,created_at) VALUES(?,?,?)", email,hash, time)
            rows = db.execute("SELECT id FROM user where email = ?", email)
            id = rows[0]["id"]
            session["user_id"] = id
            
            # redirect to home page
            flash("Registered")
            return redirect("/onboard")
        
        else:
            # flash response from validate password
            flash(response)
            return redirect("/register")

    else:

        return render_template("signup.html")


@app.route("/", methods=["GET"])
@login_required
def home():
    if request.method == "GET":
        
        board = boardDefault()
        keyboard = keyBoard()
        color_board = boardDefault()

        return render_template("board.html", board=board, letter = letter, keyboard = keyboard, color_board = color_board)
    

@app.route("/admin")
@login_required
@admin_required
def admin():
    
    details = admin_details()
    return render_template("admin.html", details = details)

@app.route("/onboard", methods=["GET","POST"])
@login_required
def onboard():

    if request.method == "GET":
        return render_template("onboard.html")
    
    if request.method == "POST":
        return redirect("/")

@app.route('/gameover')
@login_required
def gameover():

    return render_template('display.html')

@app.route("/game", methods=["POST"])
@login_required
def game():

    data = request.get_json()
    key = data['key']
    board = data['board']
    board = literal_eval(board)
    color_board = data['color_board']
    color_board = literal_eval(color_board)
    i, j = position(board)


    if key == 'DELETE':
        if i > 0 and j == 0:
            if color_board[i-1][5] ==  "":
                board[i-1][5] = ""
                k, m = i-1, 5
            else:

                return jsonify({"success": False})
            
        else:
            board[i][j-1] = ""
            k, m = i, j-1
            
        return jsonify({"success":True, "board": board, "color": color_board, "position":f"{k}_{m}", "value":key, "category":"special"})
    
    elif key == 'ENTER':

        num_days = num_day()
        today = day()
        word = word_for_the_day()

        if i > 0 and j == 0:

            guess = "".join(board[i-1])
            message, response = checkFunction(guess)
            
            if response == True:
                color_board[i-1] = ["GREEN"] * 6 
                if detail_recorded(session['user_id']):
                    db.execute("INSERT INTO play(userId, isPlay, date) values(?,'True',?)", session['user_id'], today)  
                generate_image(color_board, num_days, i)

                return jsonify({"success": True, "isDone": True, "category":"special", "value":key, "message": message})
            
            elif len(message) == 6:
                            
                color_board[i-1] = [x for x in message]

                if i == 7 and j == 0:
                    if detail_recorded(session['user_id']):
                        db.execute("INSERT INTO play(userId, isPlay, date) values(?,'False',?)", session['user_id'], today)
                    new_message = f"You ran out of guesses, today's word is {word.upper()}"
                    generate_image(color_board, num_days, "X")
                    return jsonify({"success": True, "isDone": True, "category":"special", "value":key, "message": new_message})
                        
                else:
                        
                    return jsonify({"success": True, "isDone": False, "category":"special", "value":key, "color": color_board, "position": i-1, "board": board, "inlist": True})
            
            else:

                return jsonify({"success": True, "isDone": False, "category": "special", "value":key, "color": color_board, "board": board, "message": "Word not in list", "inlist": False})
        
        else:

            return jsonify({"success": True, "isDone": False, "category": "special", "value":key, "color": color_board, "board": board, "message": "Not enough letters", "notEnough": True})
            
    else:
        if i > 0 and j == 0:

            if color_board[i-1][5] == '' :
                return jsonify({"success": False})

        board[i][j] = key
        return jsonify({"success":True, "board": board, "color": color_board, "position":f"{i}_{j}", "value":key, "category":"notspecial"})