import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command
from django.conf import settings

def run_management_command():
    call_command('check_github_repos')

def start():
    if os.environ.get('RUN_MAIN',None) == 'true':
        scheduler = BackgroundScheduler()

        trigger=CronTrigger(hour="15",minute="0")

        scheduler.add_job(run_management_command,trigger)
        scheduler.start()
        print('Scheduler started')
