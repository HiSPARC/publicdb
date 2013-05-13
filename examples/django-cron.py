#!/usr/bin/env python
import os
import sys
import logging
import traceback
import time

sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

import django_publicdb.histograms as hg

def run():
    logger.info("Checking for new events...")
    status = hg.jobs.check_for_updates()
    if status is False:
        logger.info("Check has not completed a previous run yet")
    else:
        logger.info("Update check finished.")

    logger.info("Building new histograms...")
    completed = hg.jobs.update_all_histograms()
    if not completed:
        logger.info("Histograms did not complete a previous run yet")
    else:
        logger.info("Finished building histograms")

    logger.info("Updating GPS coordinates...")
    hg.jobs.update_gps_coordinates()
    logger.info("Done.")


if __name__ == '__main__':
    fmt = "%(asctime)s - %(levelname)s - [%(process)d] - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=fmt)
    logger = logging.getLogger('cron')

    try:
        run()
    except:
        logger.exception('Exception occured.')
        sys.exit(1)
    else:
        sys.exit(0)
