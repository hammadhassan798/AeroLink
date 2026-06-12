from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from BL.airport_Dal import *
from DL.route_service import *
from BL.flight_service import *
from BL.manager_service import *
from BL.employees_service import *
from BL.employee_history_service import *
from mysql.connector import IntegrityError
from DL.graph_loader import build_route_graph

# Define Blueprint
manager_bp = Blueprint("manager", __name__, url_prefix="/manager")

# Dashboard route
@manager_bp.route("/dashboard")
def dashboard():
    stats = get_dashboard_stats()
    return render_template(
        "manager/dashboard.html",
        total_airports=stats[0],
        total_routes=stats[1],
        total_flights=stats[2],
        total_employees=stats[3]
    )

# Flights route
@manager_bp.route("/flights", methods=["GET", "POST"])
def flights():
    if request.method == "POST":
        action = request.form.get("action")
        flight_no = request.form['flight_no']
        airline = request.form.get('airline')
        aircraft_id = request.form.get('aircraft_id')
        departure = request.form.get('departure')
        arrival = request.form.get('arrival')
        price = request.form.get('price')
        status = request.form.get('status')
        try:
            if action == "add":
                leg_nos = request.form.getlist('leg_no[]')
                route_ids = request.form.getlist('route_id[]')
                emp_ids = request.form.getlist('employee_id[]')
                roles = request.form.getlist('role[]')
                legs = [(ln, rid) for ln, rid in zip(leg_nos, route_ids) if ln and rid]
                employees = [(eid, role) for eid, role in zip(emp_ids, roles) if eid and role]
                add_flight_with_details(
                    flight_no, airline, aircraft_id,
                    departure, arrival, price, status,
                    legs, employees
                )
                flash("Flight added successfully", "success")
            elif action == "edit":
                leg_nos = request.form.getlist('leg_no[]')
                route_ids = request.form.getlist('route_id[]')
                emp_ids = request.form.getlist('employee_id[]')
                roles = request.form.getlist('role[]')
                legs = [(ln, rid) for ln, rid in zip(leg_nos, route_ids) if ln and rid]
                employees = [(eid, role) for eid, role in zip(emp_ids, roles) if eid and role]
                update_flight_with_details(
                    flight_no, airline, aircraft_id,
                    departure, arrival, price, status,
                    legs, employees
                )
                flash("Flight updated successfully", "success")
            elif action == "delete":
                delete_flight_transactional(flight_no)
                flash("Flight deleted successfully", "success")
            elif action == "add_leg":
                leg_no = request.form['leg_no']
                route_id = request.form['route_id']
                add_flight_leg(flight_no, leg_no, route_id)
            elif action == "delete_leg":
                leg_no = request.form['leg_no']
                delete_flight_leg(flight_no, leg_no)
        except Exception as e:
            flash(f"MySQL Error: {e}", "error")
            flash(f"Error: {e}", "error")
        return redirect(url_for("manager.flights"))
    flights_list = get_flights()
    aircrafts_list = get_aircrafts()
    routes_list = get_routes()
    employees_list = get_employees()
    flight_legs_dict = {f['flight_no']: get_flight_legs(f['flight_no']) for f in flights_list}
    flight_employees_dict = {f['flight_no']: get_flight_employees(f['flight_no']) for f in flights_list}
    return render_template(
        "manager/flights.html",
        flights=flights_list,
        aircrafts=aircrafts_list,
        routes=routes_list,
        employees=employees_list,
        flight_legs=flight_legs_dict,
        flight_employees=flight_employees_dict
    )

# Employees route
@manager_bp.route('/employees', methods=['GET', 'POST'])
def employees():
    if request.method == 'POST':
        action = request.form.get('action')
        employee_id = request.form.get('employee_id')
        name = request.form.get('name')
        role = request.form.get('role')
        cnic = request.form.get('cnic')
        phone = request.form.get('phone')
        experience = request.form.get('experience_years')
        airport_code = request.form.get('current_airport')
        if action == 'add' or action == 'edit':
            if not airport_code:
                flash("Please select an airport", "error")
                return redirect(url_for('manager.employees'))
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            if action == 'add':
                try:
                    add_employee_with_history(
                        name, role, cnic, phone, experience, airport_code, username, password
                    )
                    flash("Employee added successfully", "success")
                except IntegrityError as e:
                    flash(f"Error adding employee: {e}", "error")
            elif action == 'edit':
                try:
                    edit_employee_with_history(
                        employee_id, name, role, cnic, phone, experience, airport_code, username, password
                    )
                    flash("Employee updated successfully", "success")
                except IntegrityError as e:
                    flash(f"Error updating employee: {e}", "error")
            elif action == 'delete':
                try:
                    delete_employee_with_history(employee_id)
                    flash("Employee deleted successfully", "success")
                except IntegrityError as e:
                    flash(f"Error deleting employee: {e}", "error")
        except IntegrityError as e:
            if e.errno == 1062:
                flash("Error: Employee with this CNIC or username already exists.", "error")
            elif e.errno == 1451:
                flash("Cannot delete employee: assigned to flights.", "error")
            else:
                flash(f"Database error: {str(e)}", "error")
        except Exception as e:
            flash(f"Unexpected error: {str(e)}", "error")
        return redirect(url_for('manager.employees'))
    employees = get_employees()
    airports = get_airports()
    search = request.args.get('search')
    if search:
        search = search.lower()
        emp_hash = build_employee_hash(employees)
        if search in emp_hash:
            employees = [emp_hash[search]]
        else:
            employees = [
            emp for emp in employees
            if search in emp['name'].lower()
        ]
    sort = request.args.get('sort')
    if sort == 'experience':
        employees = merge_sort_employees(employees)
    return render_template(
        'manager/employees.html',
        employees=employees,
        airports=airports
    )

# Undo and Redo routes
@manager_bp.route("/undo", methods=["POST"])
def undo():
    if not UNDO_STACK:
        flash("Nothing to undo", "error")
        return redirect(url_for("manager.employees"))
    action = UNDO_STACK.pop()
    try:
        if action['action_type'] == "ADD":
            delete_employee(action['affected_id'])
        elif action['action_type'] == "EDIT":
            old = action['old_value']
            edit_employee(
                old['employee_id'],
                old['name'],
                old['role'],
                old['cnic'],
                old['phone'],
                old['experience_years'],
                old['current_airport'],
                old['username']
            )
        elif action['action_type'] == "DELETE":
            old = action['old_value']
            add_employee(
                old['name'],
                old['role'],
                old['cnic'],
                old['phone'],
                old['experience_years'],
                old['current_airport'],
                old['username'],
                password=None,
                employee_id=old['employee_id']
            )
    except Exception as e:
        flash(f"Undo failed: {e}", "error")
        return redirect(url_for("manager.employees"))
    REDO_STACK.append(action)
    flash("Undo successful", "success")
    return redirect(url_for("manager.employees"))

@manager_bp.route("/redo", methods=["POST"])
def redo():
    if not REDO_STACK:
        flash("Nothing to redo", "error")
        return redirect(url_for("manager.employees"))
    action = REDO_STACK.pop()
    try:
        if action['action_type'] == "ADD":
            new = action['new_value']
            add_employee(
                new['name'],
                new['role'],
                new['cnic'],
                new['phone'],
                new['experience_years'],
                new['current_airport'],
                new['username'],
                password=None
            )
        elif action['action_type'] == "EDIT":
            new = action['new_value']
            edit_employee(
                new['employee_id'],
                new['name'],
                new['role'],
                new['cnic'],
                new['phone'],
                new['experience_years'],
                new['current_airport'],
                new['username']
            )
        elif action['action_type'] == "DELETE":
            delete_employee(action['affected_id'])
    except Exception as e:
        flash(f"Redo failed: {e}", "error")
        return redirect(url_for("manager.employees"))
    UNDO_STACK.append(action)
    flash("Redo successful", "success")
    return redirect(url_for("manager.employees"))

# Airports route
@manager_bp.route("/airports", methods=["GET", "POST"])
def airports():
    if request.method == "POST":
        action = request.form.get("action")
        airport_code = request.form.get("airport_code")
        name = request.form.get("name")
        city = request.form.get("city")
        country = request.form.get("country")
        try:
            if action == "add":
                add_airport(airport_code, name, city, country)
                flash("Airport added successfully", "success")
            elif action == "edit":
                update_airport(airport_code, name, city, country)
                flash("Airport updated successfully", "success")
            elif action == "delete":
                delete_airport(airport_code)
                flash("Airport deleted successfully", "success")
        except IntegrityError as e:
            if e.errno == 1062:
                flash("Airport code already exists", "error")
            elif e.errno == 1451:
                flash("Cannot delete airport: linked with flights", "error")
            else:
                flash(str(e), "error")
        except Exception as e:
            flash(f"Unexpected error: {e}", "error")
        return redirect(url_for("manager.airports"))
    airports = get_airports()
    search = request.args.get("search")
    if search:
        search = search.lower()
        airport_hash = build_airport_hash(airports)
        if search in airport_hash:
            airports = [airport_hash[search]]
        else:
            airports = linear_search_airports(airports, search)
    edit_code = request.args.get("edit")
    airport_to_edit = None
    if edit_code:
        airport_to_edit = get_airport_by_code(edit_code)
    return render_template(
        "manager/airports.html",
        airports=airports,
        edit_airport=airport_to_edit
    )

# Routes route
@manager_bp.route("/routes", methods=["GET", "POST"])
def routes():
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "add":
                add_route(
                    request.form['from_airport'],
                    request.form['to_airport'],
                    request.form['distance_km'],
                    request.form['time_minutes'],
                    request.form['cost']
                )
                flash("Route added successfully", "success")
            elif action == "edit":
                edit_route(
                    request.form['route_id'],
                    request.form['from_airport'],
                    request.form['to_airport'],
                    request.form['distance_km'],
                    request.form['time_minutes'],
                    request.form['cost']
                )
                flash("Route updated successfully", "success")
            elif action == "delete":
                delete_route(request.form['route_id'])
                flash("Route deleted successfully", "success")
        except Exception as e:
            flash(f"Database Error: {e}", "error")
        return redirect(url_for("manager.routes"))
    return render_template(
        "manager/routes.html",
        routes=get_routes(),
        airports=get_airports()
    )

@manager_bp.route("/routes/from/<airport_code>")
def routes_from_airport(airport_code):
    graph = build_route_graph()
    next_routes = graph.get_next_routes(airport_code)
    return jsonify(next_routes)