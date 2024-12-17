# tasks.py
from celery import shared_task
from django.core.mail import EmailMessage
from io import BytesIO
import xlsxwriter
import pytz
from datetime import datetime
from django.utils.timezone import make_aware
from .utilis.cruiseline_scrapper import main
from .models import CruiseLineFile, RegionMapping

@shared_task
def send_email_with_excel(filename, script):
    print(">>>>>>>>>>>>>",filename)
    if filename == 'cruisline':   
        file = CruiseLineFile.objects.filter(type='cruise_line').first()
        if file:
            file_path = file.file.url
        else:
            file_path = "scrapper/cruise_line_files/cruise_lines.xlsx"
      
    elif filename == 'interline':
        file = CruiseLineFile.objects.filter(type='interline').first()
        if file:
            file_path = file.file.url
        else:
            file_path = "scrapper/cruise_line_files/interline.xlsx"
    elif filename == 'custom search':
        file = CruiseLineFile.objects.filter(type='custom_search').first()
        if file:
            file_path = file.file.url
        else:
            file_path = "scrapper/cruise_line_files/custom_search.xlsx"
    else:
        file_path = None
    if file_path:
        file = main(file_path, script, filename)    
        excel_file_content = file.read()

        # Send email with Excel file attachment
        subject = "Weekly Cruise line report"
        message = f"Here is your {filename} report."
        from_email = "ankitdhimanvis@gmail.com"
        to_email = ["fab@kvi.travel", "james@kvi.travel"]  # Add recipient's email

        email = EmailMessage(subject, message, from_email, to_email)
        email.attach(f"{filename}.xlsx", excel_file_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Send the email
        email.send()

        print("Reminder email sent with attachment.")


