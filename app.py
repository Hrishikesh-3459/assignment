import os
from flask import Flask, flash, request, redirect, url_for, render_template, session
from flask_session import Session
from werkzeug.utils import secure_filename
import jwt
from tempfile import mkdtemp
import random
import string


app = Flask(__name__)
app.secret_key = os.urandom(24)

# Specifing the path and the extentions for the image to be stored
app.config["IMAGE_UPLOADS"] = '/Users/hrishikesh/codeBase/qzzo/static/'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = [
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def index():
    """
    Index page
    """
    return render_template("/signup.html")

# Signup route
@app.route('/signup', methods=["GET", "POST"])
def signup():
    """
    Takes the input data and stores in session
    """

    if request.method == "POST":

        # Saving the image
        image = request.files["image"]
        if not image:
            return render_template("apology.html")

        filename = secure_filename(image.filename)
        image.save(os.path.join(
            app.config["IMAGE_UPLOADS"], filename))
        session["img"] = "static\\" + filename

        session["first"] = request.form.get("first_name")
        session["last"] = request.form.get("last_name")
        session["age"] = request.form.get("age")

        # If the user Doesn’t provide unique_id, we generate it
        session["unique_id"] = request.form.get("unique_id")
        if not request.form.get("unique_id"):
            session["unique_id"] = ''.join(random.choices(
                string.ascii_letters + string.digits, k=6))

        session["email_id"] = request.form.get("email_id")
        session["password"] = request.form.get("password")
        session["confirmation"] = request.form.get("confirmation")

        # Cheking if any of the fields are empty
        for i in session:
            if session[i] == None:
                return render_template("apology.html", inp="Important Fields Empty")

        # Checking if the password is less than 8 characters
        if len(session["password"]) < 8:
            return render_template("apology.html", inp="Password too small")

        # Checking if the unique id is less than 6 characters
        if len(session["unique_id"]) < 6:
            return render_template("apology.html", inp="Unique Id too small")

        # Checking of the password and the confirm password are same
        if session["password"] != session["confirmation"]:
            return render_template("apology.html", inp="Passwords Don’t match")

        # Getting JWT token, using unique_id as key
        session["token"] = jwt.encode(
            {"email_id": session["email_id"], "password": session["password"]}, session["unique_id"])

        return render_template("login.html")
    else:
        return render_template("signup.html")

# Login Route
@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Logs User in
    """
    if request.method == "POST":

        # Retrieving input data
        inp_email = request.form.get("email_id")
        inp_password = request.form.get("password")

        saved = jwt.decode(session["token"], session["unique_id"])

        # Checking if the input data matches to stored data
        if saved["email_id"] != inp_email or saved["password"] != inp_password:
            return render_template("apology.html", inp="Invalid Input")

        return render_template("homepage.html", img=session["img"], first_name=session["first"], last_name=session["last"], age=session["age"], unique_id=session["unique_id"], email_id=session["email_id"])
    else:
        return render_template("login.html")

# Logout route
@app.route("/logout")
def logout():
    """
    Log user out
    """

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect('/')
