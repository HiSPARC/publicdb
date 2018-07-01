from django.core.management.base import BaseCommand

from ...models import SessionRequest


class Command(BaseCommand):
    help = 'Creates sessions for confirmed session requests'

    def handle(*args, **options):
        sessionrequests = SessionRequest.objects.filter(session_confirmed=True, session_pending=True)

        # Set confirmed to False to prevent being included in next run of createsessions
        for sessionrequest in sessionrequests:
            sessionrequest.session_confirmed = False
            sessionrequest.save()

        # Start creating sessions
        for sessionrequest in sessionrequests:
            sessionrequest.create_session()
