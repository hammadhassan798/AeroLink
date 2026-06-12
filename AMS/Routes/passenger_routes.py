import os
import io
from flask import send_file
from DL.passenger_flights import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from DL.heap_loader import FlightMinHeap
from reportlab.lib.colors import HexColor
from flask import Blueprint, flash, jsonify, render_template, request, send_file, session, redirect, url_for

# Define Blueprint
passenger_bp = Blueprint(
    "passenger",
    __name__,
    url_prefix="/passenger"
)

# Passenger dashboard
@passenger_bp.route("/dashboard")
def dashboard():
    if session.get("user_type") != "Passenger":
        return redirect(url_for("auth_routes.login"))
    return render_template("passenger/dashboard.html")

# Booking flights
@passenger_bp.route("/flights", methods=["GET", "POST"])
def passenger_flights():
    if session.get("user_type") != "Passenger":
        flash("Please login as passenger first", "error")
        return redirect(url_for("passenger_auth.passenger_login"))
    passenger_id = session.get("user_id")
    if request.method == "POST":
        flight_no = request.form.get("flight_no")
        seat_no = request.form.get("seat_no")
        flight_type = request.form.get("flight_type")
        if not all([flight_no, seat_no, flight_type]):
            flash("Missing booking information", "error")
            return redirect(url_for("passenger.passenger_flights"))
        success, msg = book_flight(
            passenger_id,
            flight_no,
            seat_no,
            flight_type
        )
        flash(msg, "success" if success else "error")
        return redirect(url_for("passenger.passenger_flights"))
    flights = get_available_flights()
    return render_template("passenger/flights.html", flights=flights)

# API to get flight legs
@passenger_bp.route("/flight/<flight_no>/legs")
def get_flight_legs_api(flight_no):
    legs = get_flight_legs_for_passenger(flight_no)
    return jsonify(legs)

# Showing passenger bookings
@passenger_bp.route("/bookings")
def passenger_bookings():
    if session.get("user_type") != "Passenger":
        return redirect(url_for("passenger_auth.passenger_login"))
    bookings = get_passenger_bookings(session["user_id"])
    return render_template("passenger/booking.html", bookings=bookings)

# Cancel booking
@passenger_bp.route("/booking/<int:ticket_id>/cancel", methods=["POST"])
def cancel_booking(ticket_id):
    if session.get("user_type") != "Passenger":
        flash("Unauthorized", "error")
        return redirect(url_for("passenger.passenger_bookings"))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM booking
        WHERE ticket_id=%s AND passenger_id=%s
    """, (ticket_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("❌ Booking cancelled successfully", "success")
    return redirect(url_for("passenger.passenger_bookings"))

# Ticket PDF download
@passenger_bp.route("/booking/<int:ticket_id>/pdf")
def download_ticket(ticket_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            b.ticket_id,
            b.flight_no,
            b.seat_no,
            b.flight_type,
            f.departure,
            f.arrival
        FROM booking b
        JOIN flight f ON f.flight_no = b.flight_no
        WHERE b.ticket_id=%s AND b.passenger_id=%s
    """, (ticket_id, session["user_id"]))
    b = cursor.fetchone()
    conn.close()
    if not b:
        flash("Ticket not found", "error")
        return redirect(url_for("passenger.passenger_bookings"))
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    primary = HexColor("#2563eb")
    dark = HexColor("#1e293b")
    gray = HexColor("#64748b")
    light = HexColor("#f1f5f9")
    pdf.setFillColor(primary)
    pdf.rect(0, height - 140, width, 140, fill=1)
    logo_path = os.path.join("static", "Images", "logo.png")
    if os.path.exists(logo_path):
        pdf.drawImage(
            logo_path,
            40,
            height - 110,
            width=70,
            height=70,
            mask='auto'
        )
    pdf.setFillColor("white")
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawString(130, height - 70, "AIROLINK")
    pdf.setFont("Helvetica", 14)
    pdf.drawString(130, height - 95, "✈ Boarding Pass")
    pdf.setFillColor(light)
    pdf.roundRect(30, height - 560, width - 60, 420, 22, fill=1)
    pdf.setStrokeColor(primary)
    pdf.setLineWidth(2)
    pdf.roundRect(30, height - 560, width - 60, 420, 22)
    pdf.setFillColor(dark)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(
        width / 2,
        height - 200,
        f"{b['departure']}  →  {b['arrival']}"
    )
    y = height - 260
    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(gray)
    pdf.drawString(60, y, "Flight No")
    pdf.drawString(200, y, "Seat")
    pdf.drawString(340, y, "Class")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(dark)
    pdf.drawString(60, y - 25, b["flight_no"])
    pdf.drawString(200, y - 25, b["seat_no"])
    pdf.drawString(340, y - 25, b["flight_type"])
    y -= 90
    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(gray)
    pdf.drawString(60, y, "Departure Time")
    pdf.drawString(340, y, "Arrival Time")
    pdf.setFont("Helvetica-Bold", 13)
    pdf.setFillColor(dark)
    pdf.drawString(60, y - 25, str(b["departure"]))
    pdf.drawString(340, y - 25, str(b["arrival"]))
    pdf.setStrokeColor(HexColor("#cbd5e1"))
    pdf.setDash(4, 4)
    pdf.line(60, height - 410, width - 60, height - 410)
    pdf.setDash()
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(gray)
    pdf.drawString(60, height - 450, f"Ticket ID: {b['ticket_id']}")
    pdf.drawRightString(
        width - 60,
        height - 450,
        "Please arrive 45 minutes before departure"
    )
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawCentredString(
        width / 2,
        height - 500,
        "Thank you for choosing SkyHigh Airways ✈"
    )
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"SkyHigh_Ticket_{ticket_id}.pdf",
        mimetype="application/pdf"
    )