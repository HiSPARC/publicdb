import logging

from django.core.management.base import BaseCommand

from ...jobs import check_for_updates, update_all_histograms

logger = logging.getLogger('histograms.jobs')


class Command(BaseCommand):
    help = "Perform tasks to check for new data and process that data"

    def handle(*args, **options):
        logger.info("Checking for new events...")
        status = check_for_updates()
        if status is False:
            logger.info("Check has not completed a previous run yet")
        else:
            logger.info("Update check finished.")

        logger.info("Building new histograms...")
        completed = update_all_histograms()
        if not completed:
            logger.info("Histograms did not complete a previous run yet")
        else:
            logger.info("Finished building histograms")
        logger.info("Done.")
