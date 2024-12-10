from datetime import timedelta
from celery.schedules import crontab

beat_schedule = {
    'send_email_with_excel_instance_1': {
        'task': 'scrapper.tasks.send_email_with_excel',
        # 'schedule': crontab(minute=0, hour=2, day_of_week=6),  # Every Saturday at 2 AM
        'schedule': crontab(minute=0, hour=2, day_of_week=6),  # Every 10 seconds
        'args': ('cruisline', 'script1'),  # First set of arguments for instance 1
    },
    'send_email_with_excel_instance_2': {
        'task': 'scrapper.tasks.send_email_with_excel',
        'schedule': crontab(minute=0, hour=2, day_of_week=6),  # Every Saturday at 2 AM
        'args': ('interline', 'script2'),  # Second set of arguments for instance 2
    },
    'send_email_with_excel_instance_3': {
        'task': 'scrapper.tasks.send_email_with_excel',
        'schedule': crontab(minute=0, hour=2, day_of_week=6),  # Every Saturday at 2 AM
        'args': ('custom search', 'script3'),  # Third set of arguments for instance 3
    },
}
