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
    num_histograms = hg.jobs.update_all_histograms()
    if num_histograms is False:
        logger.info("Histograms did not complete a previous run yet")
    else:
        logger.info("Finished building %d histograms" % num_histograms)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger('cron')

    try:
        run()
    except:
        logger.exception('Exception occured.')
        sys.exit(1)
    else:
        sys.exit(0)
