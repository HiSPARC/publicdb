import logging

from django.core.management.base import BaseCommand

from ...checks import check_for_updates
from ...jobs import update_all_histograms

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Perform tasks to check for new data and process that data'

    def handle(*args, **options):
        logger.info('Checking for new events...')
        has_run = check_for_updates()
        if not has_run:
            logger.warning('Check has not completed a previous run yet')
        else:
            logger.info('Update check finished.')

        logger.info('Building new histograms...')
        completed = update_all_histograms()
        if not completed:
            logger.warning('Histograms did not complete a previous run yet')
        else:
            logger.info('Finished building histograms')

        logger.info('Done.')
