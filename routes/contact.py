import os
from flask import Blueprint, request, jsonify
import smtplib
from email.mime.text import MIMEText

contact_bp = Blueprint("contact", __name__)

@contact_bp.route("", methods=["POST"])  # ✅ notice: no extra /contact
def contact():
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")
        number = data.get("number")
        message = data.get("message")

        sender = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASS")
        receiver = sender  # send to yourself

        if not sender or not password:
            return jsonify({"success": False, "message": "Email not configured"}), 500

        subject = f"New Contact Message from {name}"
        body = f"""
        You got a new message from your website:

        Name: {name}
        Email: {email}
        Number: {number}

        Message:
        {message}
        """

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())

        return jsonify({"success": True, "message": "Message sent successfully!"})

    except Exception as e:
        print("❌ Error sending email:", e)
        return jsonify({"success": False, "message": str(e)}), 500
