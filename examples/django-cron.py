#!/usr/bin/env python
import os
import sys
import logging
import traceback
import time

sys.path.append('/user/admhispa/http/pique')
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

import django_publicdb.histograms as hg

def run():
    logger.info("Checking for new events...")
    num_events, num_stations = hg.jobs.check_for_updates()
    if num_events is False:
        logger.info("Check has not completed a previous run yet")
    else:
        logger.info("Got %d new events from %d stations" % (num_events,
                                                            num_stations))

    logger.info("Building new histograms...")
    num_histograms = hg.jobs.update_all_histograms()
    if num_histograms is False:
        logger.info("Histograms did not complete a previous run yet")
    else:
        logger.info("Finished building %d histograms" % num_histograms)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        filename='/user/admhispa/log/cron.log',
                        format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger('cron')

    try:
        run()
    except:
        logger.error(traceback.format_exc())
        sys.exit(1)
    else:
        sys.exit(0)
