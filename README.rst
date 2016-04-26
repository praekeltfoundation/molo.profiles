Molo Profiles
=============

.. image:: https://travis-ci.org/praekelt/molo.profiles.svg?branch=develop
    :target: https://travis-ci.org/praekelt/molo.profiles
    :alt: Continuous Integration

.. image:: https://coveralls.io/repos/praekelt/molo.profiles/badge.png?branch=develop
    :target: https://coveralls.io/r/praekelt/molo.profiles?branch=develop
    :alt: Code Coverage

Provides code to help with User profiles in a project using the Molo code base.

.. note::   This library does not provide a Django user model, it provides a
            profile model that can be attached to a user. Our experience is
            that custom User models in Django add all sorts of unpleasantries
            when using migrations.

Installation::

   pip install molo.profiles


Django setup::

   INSTALLED_APPS = (
      'molo.profiles',
   )

If you want to enable user data being sent to a Slack Channel, insert the following::

  SLACK_INCOMING_WEBHOOK_URL = '' # URL of slack webhook
  
  CELERYBEAT_SCHEDULE = {
      # Executes every morning at 8:00 A.M GMT+2
      'add-every-morning': {
          'task': 'molo.profiles.task.send_user_data_to_slack',
          'schedule': crontab(hour=8)
      },
  }
