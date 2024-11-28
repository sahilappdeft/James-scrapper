# tasks.py
from celery import shared_task
from django.core.mail import EmailMessage
from io import BytesIO
import xlsxwriter
import pytz
from datetime import datetime
from django.utils.timezone import make_aware
from .utilis.cruiseline_scrapper import main

@shared_task
def send_email_with_excel(filename, script):
    # Create an Excel file in memory
    file_path = "cruise_lines.xlsx"
    file = main(file_path, script, filename)
    excel_file_content = file.read()

    # Send email with Excel file attachment
    subject = "Weekly Cruise line report"
    message = "Here is your cruise line report."
    from_email = "sahil9023927813@gmail.com"
    to_email = ["recipient@example.com"]  # Add recipient's email

    email = EmailMessage(subject, message, from_email, to_email)
    email.attach("reminder.xlsx", excel_file_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Send the email
    email.send()

    print("Reminder email sent with attachment.")
