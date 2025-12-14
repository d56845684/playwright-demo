from flask import request, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

DEMO_USER = {"username": "demo", "password": "demo123"}

login_manager = LoginManager()
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, user_id: str):
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    if user_id == DEMO_USER["username"]:
        return User(user_id)
    return None


def init_auth(app):
    login_manager.init_app(app)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            u = request.form.get("username", "")
            p = request.form.get("password", "")
            if u == DEMO_USER["username"] and p == DEMO_USER["password"]:
                login_user(User(u))
                return redirect(url_for("reserve"))
            error = "Invalid credentials"
        return render_template("login.html", error=error)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))