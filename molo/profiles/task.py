import csv
import requests
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.conf import settings
from celery import task
import StringIO
from django.core.mail import EmailMultiAlternatives
from molo.profiles.models import UserProfile


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
    return ("DAILY UPDATE ON USER DATA\n"
            "New User - joined in the last 24 hours\n"
            "Returning User - joined longer than 24 hours ago"
            "and visited the site in the last 24 hours\n"
            "```"
            "Total Users: {0}\n"
            "New Users: {1}\n"
            "Returning Users: {2}"
            "```"
            .format(get_count_of_all_users(),
                    get_count_of_new_users(),
                    get_count_of_returning_users()))


@task(serializer='json')
def send_user_data_to_slack():
    try:
        url = settings.SLACK_INCOMING_WEBHOOK_URL
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        data = {
            "text": get_message_text()
        }
        requests.post(url, json=data, headers=headers)
    except AttributeError:
        pass


def get_front_end_user_csv_file(field_names, arguments):
    dataset = User.objects.filter(is_staff=False, **arguments)
    csvfile = StringIO.StringIO()
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(field_names[0] + field_names[1])
    for obj in dataset:
        if not hasattr(obj, 'profile'):
            obj.profile = UserProfile.objects.create(user=obj)
        if obj.profile.alias:
            obj.profile.alias = obj.profile.alias.encode('utf-8')
        obj.username = obj.username.encode('utf-8')
        obj.date_joined = obj.date_joined.strftime("%Y-%m-%d %H:%M")
        csvwriter.writerow(
            [getattr(obj, field) for field in field_names[0]] +
            [getattr(obj.profile, field) for field in field_names[1]])
    return csvfile


@task(ignore_result=True)
def send_export_email(recipient, field_names, arguments):
    csvfile = get_front_end_user_csv_file(field_names, arguments)
    subject = 'Molo export: %s' % settings.SITE_NAME
    from_email = settings.DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(subject, '', from_email, (recipient,))
    msg.attach(
        'Molo_export_%s.csv' % settings.SITE_NAME,
        csvfile.getvalue(), 'text/csv')
    msg.send()
