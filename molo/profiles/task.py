from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.conf import settings
from celery.task import periodic_task
from celery.schedules import crontab
import urllib2
import json


def get_count_of_new_users():
    now = datetime.now()
    qs = User.objects.filter(date_joined__gte=now - timedelta(hours=24))
    return qs.count()


def get_count_of_returning_users():
    now = datetime.now()
    qs = User.objects.filter(last_login__gte=now - timedelta(hours=24)).filter(
        date_joined__lt=now - timedelta(hours=24))
    return qs.count()


def get_count_of_all_users():
    qs = User.objects.all()
    return qs.count()


def get_message_text():
    return ("Daily Update On User Data\n"
            "Total Users: {0}\n"
            "New Users: {1}\n"
            "Returning Users: {2}"
            .format(get_count_of_all_users(),
                    get_count_of_new_users(),
                    get_count_of_returning_users()))


@periodic_task(run_every=crontab(hour='8'))
def send_announcement():
    try:
        url = settings.SLACK_INCOMING_WEBHOOK_URL
        data = {
            "text": get_message_text()
        }
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data=json.dumps(data))
        request.add_header("Content-Type", "application/json")
        opener.open(request)
    except AttributeError:
        pass
