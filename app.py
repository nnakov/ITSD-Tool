from cs50 import SQL
from flask import Flask, render_template, session, request, redirect, flash, jsonify
from flask_session import Session
from functions import login_required
import re
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "flash_message"

# Configures the cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Importing SQL Database
db = SQL("sqlite:///itsd.db")

# No cache decorator for security reasons


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # Clear previous session
        session.clear()

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Error: Username or password is missing.")
            return redirect("/login")

        if len(username) < 3 or len(username) > 30:
            flash("Invalid username or password.")
            return redirect("/login")

        if len(password) < 8 or len(password) > 64:
            flash("Invalid username or password.")
            return redirect("/login")

        get_userdata = db.execute("SELECT id, user, password FROM users WHERE user=?", username)

        if len(get_userdata) != 1 or not check_password_hash(get_userdata[0]['password'], password):
            flash("Invalid username or password.")
            return redirect("/login")

        session["user_id"] = get_userdata[0]["id"]
        session["username"] = get_userdata[0]["user"]

        return redirect("/")
    else:
        return render_template("login.html")

# Shows if user logged in, so navibar can appear fully


@app.context_processor
def inject_user_logged():

    return {"user_logged": "user_id" in session,
            "username": session.get("username")}


@app.route("/logout")
def logout():

    # Clears session
    session.clear()

    # Redirect user
    return redirect("/")

# Register route


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        session.clear()

        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        repeat = request.form.get("repeat", "")

        # Invaid input checks

        if not username:
            flash("No username")
            return redirect("/register")
        elif not password or not repeat:
            flash("Password field empty")
            return redirect("/register")

        if password != repeat:
            flash("Passwords does not match")
            return redirect("/register")

        if len(username) < 3 or len(username) > 30:
            flash("Username must be between 3 and 30 length")
            return redirect("/register")
        if len(password) < 8 or len(password) > 64:
            flash("Password must be between 8 and 64 length")
            return redirect("/register")
        if not username.isalnum():
            flash("Username may contain only letters and numbers.")
            return redirect("/register")
        actual_user = db.execute("SELECT user FROM users WHERE user=?", username)

        if len(actual_user) > 0:
            flash("Username already exists")
            return redirect("/register")

        # Entering the user in database
        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users(user, password) VALUES(?,?)", username, password_hash)

        user_id = db.execute("SELECT id FROM users WHERE user=?", username)
        session["username"] = username
        session["user_id"] = user_id[0]["id"]

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html")

# AJAX for updating the updated row


@app.route("/ajax_row", methods=["POST"])
def ajax_row():
    update_service = request.get_json("selectedValue")

    updated_row = db.execute(
        "SELECT src_id, service_name, hours, min_fte, shrinkage, max_load, work_days, volume_month, flat_fte FROM services WHERE service_name = ?", update_service["selectedValue"])
    return jsonify(updated_row)

# FTE page


@app.route("/fte", methods=["GET", "POST"])
@login_required
def fte():
    current_service = db.execute("SELECT * FROM services")
    service_rows = ["Working Hours", "Min FTE", "Shrinkage %",
                    "Max Load", "Work days", "Volume per Month", "Flat FTE"]

    if request.method == "POST":
        selectedValue = request.get_json()
        selected_service = db.execute(
            "SELECT hours, min_fte, shrinkage, max_load, work_days, volume_month, flat_fte FROM services WHERE service_name = ?", selectedValue['selectedValue'])
        flat_fte = db.execute(
            "SELECT flat_fte FROM services WHERE service_name = ?", selectedValue['selectedValue'])
        selected_data = list(selected_service[0].values())

        flat_fte = flat_fte[0]['flat_fte']

        if selected_data[0] == 0:
            result = selected_data[5] / (selected_data[4] * selected_data[3])

        elif selected_data[0] != 0:
            if flat_fte < selected_data[1]:
                result = selected_data[1]
            else:
                result = (flat_fte)*(1 + selected_data[2])
        selected_data[2] = selected_data[2] * 100
        return jsonify(selected_data=selected_data, result=round(result, 1))
    else:

        return render_template("fte.html", services=current_service, service_rows=service_rows)

# Budged operational block + AJAX requests


@app.route("/ajax_service", methods=["POST"])
def ajax_service():
    selected_service = request.json.get("selectedService")
    service_year = db.execute(
        "SELECT DISTINCT year FROM monthly_costs WHERE service_id = (SELECT id FROM services WHERE service_name = ?)", selected_service)

    return jsonify(service_year)


@app.route("/ajax_fill", methods=["POST"])
def ajax_fill():
    selectedService = request.json.get("selectedService")
    selectedYear = request.json.get("selectedYear")
    service_values = db.execute(
        "SELECT fte_cost, fte_value, year FROM monthly_costs WHERE year = ? AND service_id = (SELECT id FROM services WHERE service_name = ?)", selectedYear, selectedService)
    return jsonify(service_values)


@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    services = db.execute("SELECT service_name FROM services")

    if request.method == "POST":
        fte_values = {}
        fte_costs = {}

        service = request.form.get("service")
        # Check service
        if not service:
            flash("No service selected", "error")
            return redirect("/budget")

        name = service.strip()
        if not re.match("^[A-Za-z ]+$", name):
            flash("Service name must contain only letters.", "error")
            return redirect("/budget")

        service_id = db.execute("SELECT id FROM services WHERE service_name = ?",
                                service)
        # Check for service_id

        if len(service_id) == 0:
            flash("No service found.", "error")
            return redirect("/budget")
        # Check year
        year = request.form.get("year")

        try:
            year = int(year)
            if year < 0:
                flash("Year can't be negative", "error")
                return redirect("/budget")
        except:
            flash("Invalid year", "error")
            return redirect("/budget")

        month_number = 0
        for month in months:
            month_number += 1
            fte_values[month] = request.form.get(f"fte_{month}")
            fte_costs[month] = request.form.get(f"fte_cost{month}")

            # Checks for correct FTE values
            if fte_values[month]:
                try:
                    fte_input = float(fte_values[month])

                    if fte_input < 0:
                        flash("Invalid input", "error")
                        return redirect("/budget")
                except:
                    flash("Invalid input. Must be numeric", "error")
                    return redirect("/budget")

            # Checks for correct FTE costs
            if fte_costs[month]:
                try:
                    fte_cost = float(fte_costs[month])
                    if fte_cost < 0:
                        flash("Invalid input", "error")
                        return redirect("/budget")
                except:
                    flash("Invalid input. Must be numeric", "error")
                    return redirect("/budget")

            db.execute("UPDATE monthly_costs SET fte_cost = ?, fte_value = ? WHERE service_id = ? AND year = ? AND month = ?",
                       fte_costs[month], fte_values[month], service_id[0]["id"], year, month_number)
        flash("Budget updated", "confirm")
        return redirect("/budget")
    else:
        return render_template("budget.html", months=months, services=services)


@app.route("/services", methods=["GET", "POST"])
@login_required
def services():
    services = db.execute("SELECT * FROM services")
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            fields = ["service_name", "src_id", "hours", "min_fte", "shrinkage",
                      "max_load", "work_days", "volume_month", "flat_fte"]
            data = {}
            for f in fields:
                data[f] = request.form.get(f)

            # Check empty fields
            if any(not v.strip() for v in data.values()):
                flash("All fields are required.", "add")
                return render_template("services.html", data=request.form)

            error = validate_service_inputs(data)
            if error:
                flash(error, "add")
                return render_template("services.html", data=request.form)

            # Check duplicates
            current_service = db.execute(
                "SELECT * FROM services WHERE src_id = ? OR service_name = ?", data["src_id"], data["service_name"])
            if len(current_service) != 0:
                flash("Already exists.", "add")
                return render_template("services.html", data=request.form)
            # Insert row
            db.execute("INSERT INTO services(src_id, service_name, hours, min_fte, shrinkage, max_load, work_days, volume_month, flat_fte) VALUES(?,?,?,?,?,?,?,?,?)",
                       data["src_id"], data["service_name"], data["hours"], data["min_fte"], data["shrinkage"], data["max_load"], data["work_days"], data["volume_month"], data["flat_fte"])

            flash("Row added", "add_success")
            return redirect("/services")

        elif action == "update":
            selected_service = request.form.get("selected")
            selected_id = db.execute(
                "SELECT id FROM services WHERE service_name = ?", selected_service)

            # Check if service exists
            if not selected_id:
                flash("No selected service", "update")
                return redirect("/services")

            fields = ["src_id", "service_name", "hours", "min_fte", "shrinkage",
                      "max_load", "work_days", "volume_month", "flat_fte"]
            data = {}
            for f in fields:
                value = request.form.get(f)
                if value and value.strip():
                    data[f] = value

            # Checks for empty fields
            if not data:
                flash("No fields to update", "update")
                return redirect("/services")
            # Validate updated fields
            error = validate_service_inputs(data, is_update=True)
            if error:
                flash(error, "update")
                return redirect("/services")

            # Updating the service
            for field, value in data.items():
                db.execute(
                    f"UPDATE services SET {field} = ? WHERE id = ?", value, selected_id[0]["id"])
            flash("Rows updated", "update_success")
            return redirect("/services")

        elif action == "delete":
            service = request.form.get("srv_remove")
            print(service)
            selected_id = db.execute("SELECT id FROM services WHERE id = ?", service)
            print(selected_id)
            # Checks if service exists
            if not selected_id:
                flash("No selected service", "delete")
                return redirect("/services")
            db.execute("DELETE FROM monthly_costs WHERE service_id = ?", selected_id[0]['id'])
            db.execute("DELETE FROM services WHERE id = ?", selected_id[0]['id'])
            flash("Row deleted", "delete_success")
            return redirect("/services")
    else:

        return render_template("services.html", services=services, data=request.form or {})


@app.route("/add_budget", methods=["GET", "POST"])
@login_required
def add_budget():
    selected_service = request.form.get("budget_select")
    selected_year = request.form.get("year_select")

    # Check for provided input
    if not selected_service or not selected_year:
        flash("No data provided", "budget_error")
        return redirect("/services")

    # Check value of selected_service
    if selected_service:
        name = selected_service.strip()
        if not re.match("^[A-Za-z ]+$", name):
            flash("Service name must contain only characters.", "budget_error")
            return redirect("/services")

    # Check value of selected_year:
    try:
        selected_year = int(selected_year)
    except:
        flash("Invalid year", "budget_error")

    # Check ID of service
    service_id = db.execute("SELECT id FROM services WHERE service_name = ?", selected_service)
    if not service_id:
        flash("Invalid service", "budget_error")
        return redirect("/services")

    # Check if service there are already records
    budget_check = db.execute(
        "SELECT * FROM monthly_costs WHERE year=? AND service_id=?", selected_year, service_id[0]["id"])

    if len(budget_check) != 0:
        flash("Already exists", "budget_error")
        return redirect("/services")

    # Create budget row for selected year
    for month in range(1, 13):
        db.execute("INSERT INTO monthly_costs(service_id, year, month, fte_cost, fte_value) VALUES(?, ?, ?, 0, 0)",
                   service_id[0]["id"], selected_year, month)
    flash("Budget Added", "budget_success")
    return redirect("/services")


def validate_service_inputs(data, is_update=False):
    # Validate fields for adding or updating a service.

    # Validate src_id
    if "src_id" in data:
        try:
            data["src_id"] = int(data["src_id"])
            if data["src_id"] <= 0:
                return "Service ID must be positive."
        except:
            return "Service ID must be a valid number"

    # Validate service_name
    if "service_name" in data:
        name = data["service_name"].strip()
        if not re.match("^[A-Za-z ]+$", name):
            return "Service name must contain only letters."

    # Validate numeric fileds
    numeric_fields = ["hours", "min_fte", "max_load", "work_days", "volume_month", "flat_fte"]
    for f in numeric_fields:
        if f in data:
            try:
                if float(data[f]) < 0:
                    return f"{f} cannot be negative."
            except:
                return f"{f} must be a number."

    # Validate shrinkage
    if "shrinkage" in data:
        try:
            shrink = float(data["shrinkage"])
            if shrink > 1:
                shrink /= 100
            if shrink < 0 or shrink > 1:
                return "Shrinkage must be between 0% and 100%."
            data["shrinkage"] = shrink
        except:
            return "Shrinkage must be a valid number."

    return None  # When no errors occur
