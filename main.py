import boto3
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
from replit import db as users
import random
import io
import os
from dotenv import load_dotenv

load_dotenv()

access_key = os.getenv("ACCESS")
secret_key = os.getenv("SECRET")

linode_obj_config = {
    "aws_access_key_id": access_key,
    "aws_secret_access_key": secret_key,
    "endpoint_url": "https://us-southeast-1.linodeobjects.com",
}

client = boto3.client("s3", **linode_obj_config)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        f = request.form
        if f.get("email") in users.keys():
            flash("There is already an account associated with this email address!")
            return redirect(url_for("login"))
        user_obj = {
            "First Name": f.get("fname"),
            "Last Name": f.get("lname"),
            "Email": f.get("email"),
            "Phone": f.get("phone"),
            "Password": f.get("password"),
            "Bio": f.get("bio"),
            "Socials": {
                "GitHub": f.get("github"),
                "LinkedIn": f.get("linkedin"),
                "Devpost": f.get("devpost"),
                "Website": f.get("website")
            },
            "Other Links": {
                f.get("name1"): f.get("link1"),
                f.get("name2"): f.get("link2"),
                f.get("name3"): f.get("link3")
            }
        }
        users[f.get("email")] = user_obj
        session["user"] = user_obj
        print(user_obj)
        file = request.files["resume"]
        print(file.filename)

        client.upload_fileobj(file, "resumes", f.get("email"))
        flash("Successfully logged in!")
        return redirect(url_for("find"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        f = request.form
        if users.get(f.get("email")) and users[f.get("email")]["Password"] == f.get("password"):
            print(dict(users[f.get("email")]))
            od = dict(users[f.get("email")])
            session["user"] = {
                "First Name": od["First Name"],
                "Last Name": od["Last Name"],
                "Email": od["Email"],
                "Phone": od["Phone"],
                "Password": od["Password"],
                "Bio": od["Bio"],
                "Socials": dict(od["Socials"]),
                "Other Links": dict(od["Other Links"]),
            }
            flash("Successfully logged in!")
            return redirect(url_for("profile", user=f.get("email")))
        else:
            flash("Invalid username or password!")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/find")
def find():
    usrs = list(users.keys())
    if len(usrs) > 24:
        usrs = list(random.choice(usrs, k=12))
    for x, usr in enumerate(usrs):
        od = users[usr]
        usrs[x] = {
            "First Name": od["First Name"],
            "Last Name": od["Last Name"],
            "Email": od["Email"],
            "Phone": od["Phone"],
            "Password": od["Password"],
            "Bio": od["Bio"],
            "Socials": dict(od["Socials"]),
            "Other Links": dict(od["Other Links"]),
        }
        print(usrs)
    return render_template("find.html", users=usrs)

@app.route("/profile/<string:user>")
def profile(user):
    od = users.get(user)
    if od:
        newuser = {
            "First Name": od["First Name"],
            "Last Name": od["Last Name"],
            "Email": od["Email"],
            "Phone": od["Phone"],
            "Password": od["Password"],
            "Bio": od["Bio"],
            "Socials": dict(od["Socials"]),
            "Other Links": dict(od["Other Links"]),
        }
        print(dict(od["Other Links"]).keys())
        return render_template("profile.html", user=dict(newuser), names=dict(od["Other Links"]).keys())
    return redirect(url_for("find"))

@app.route("/resume/<string:user>")
def resume(user):
    client.download_file("resumes", user, f"resumes/{user}.pdf")
    return send_file(f"resumes/{user}.pdf")

if __name__ == "__main__":
    app.run("0.0.0.0", 8080, True)