#!/usr/bin/env python
import os
import sys
import logging

dirname = os.path.dirname(__file__)
publicdb_path = os.path.join(dirname, '..')
sys.path.append(publicdb_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'publicdb.settings'

import django
django.setup()

from publicdb.histograms.jobs import check_for_updates, update_all_histograms


def run():
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


if __name__ == '__main__':
    fmt = "%(asctime)s - %(levelname)s - [%(process)d] - %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt)
    logger = logging.getLogger('cron')

    import django
    django.setup()

    try:
        run()
    except:
        logger.exception('Exception occured.')
        sys.exit(1)
    else:
        sys.exit(0)
