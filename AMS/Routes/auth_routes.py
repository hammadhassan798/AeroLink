from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from BL.auth_service import signup_passenger_service, login_passenger_service, login_manager_service

# Define Blueprint
auth_bp = Blueprint("auth", __name__)

# Signup route
@auth_bp.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form['name']
        cnic = request.form['cnic']
        password = request.form['password']
        phone = request.form.get('phone', None)
        success, msg = signup_passenger_service(name, password, cnic, phone)
        flash(msg, "success" if success else "error")
        if success:
            return redirect(url_for("auth.login"))
    return render_template("signup.html")

# Login route
@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        cnic = request.form['cnic']
        password = request.form['password']
        success, result = login_passenger_service(cnic, password)
        if success:
            session['user_type'] = "Passenger"
            session['user_id'] = result['passenger_id']
            flash("Logged in successfully as Passenger", "success")
            return redirect(url_for("passenger.dashboard"))
        success, result = login_manager_service(cnic, password)
        if success:
            session['user_type'] = "Manager"
            session['user_id'] = result['employee_id']
            flash("Logged in successfully as Manager", "success")
            return redirect(url_for("manager.dashboard"))
        flash("Invalid CNIC or password", "error")
    return render_template("login.html")

# Logout route
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("auth.login"))
