CHANGE LOG
==========

1.2.4
-----
- Added BEM class rules to Viewprofiles template 

1.2.3
-----
- Added encoding to username when downloading CSV

1.2.2
-----
- Make sure we only encode for users that have alias

1.2.1
-----
- Added encoding to user alias when downloading CSV

1.2.0
-----
- Added End Users view to Wagtail Admin

1.1.0
-----
- Adding BEM rules to the templates

1.0.1
-----
- Removed clean method from EditProfileForm

1.0.0
-----
- Added email address to registration
- Upgraded to Molo 3.0
- Upgraded to Django 1.9

NOTICE:
~~~~~~~
- Not compatible with `molo<3.0`


0.2.7
-----
- Fixed bug in slack stats integration

0.2.6
-----
- Added the option of exporting user data as CSV in django admin

0.2.5
-----
- Added cellphone number to registration
- Added User Profiles Settings in wagtail

0.2.4
-----
- Removed requirement for date of birth when editing profile

0.2.2
-----
- Add missing migrations

0.2.1
-----
- Updated celery task and readme for posting user statistics to a Slack Channel

0.2.0
-----
- Added a task to post user statistics to a Slack Channel
