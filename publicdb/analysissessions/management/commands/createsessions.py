from django.core.management.base import BaseCommand, CommandError

from ...models import SessionRequest


class Command(BaseCommand):
    help = 'Creates sessions for confirmed session requests'

    def handle(*args, **options):
        sessionlist = SessionRequest.objects.filter(session_confirmed=True, session_pending=True)

        # Set confirmed to False to prevent being included in next run of createsessions
        sessionlist.update(session_confirmed=False)

        # Start creating sessions
        for sessionrequest in sessionlist:
            sessionrequest.create_session()
