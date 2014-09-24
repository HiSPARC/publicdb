#!/usr/bin/env python

import datetime
import sys
import os
from textwrap import dedent

dirname = os.path.dirname(__file__)
publicdb_path = os.path.join(dirname, '..')
sys.path.append(publicdb_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

from django_publicdb.histograms.models import *


def prepare_histograms_fixture():
    Summary.objects.exclude(station__number=501).delete()
    Summary.objects.filter(date__lt=datetime.date(2011, 1, 1)).delete()
    Summary.objects.filter(date__gt=datetime.date(2011, 12, 31)).delete()

    DailyDataset.objects.exclude(source__date=datetime.date(2011, 7, 7)).delete()
    DailyHistogram.objects.exclude(source__date=datetime.date(2011, 7, 7)).delete()

    PulseheightFit.objects.filter(source__date__lt=datetime.date(2011, 6, 16)).delete()
    PulseheightFit.objects.filter(source__date__gt=datetime.date(2011, 9, 8)).delete()


def print_warning():
    print dedent("""\
                 This script modifies the histograms tables. Since it
                 directly changes the database, you have to add the
                 --shut-up argument to imply that you know what you are
                 doing.

                 Usage: prepare_histograms_fixture.py --shut-up""")


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "--shut-up":
        prepare_histograms_fixture()
    else:
        print_warning()
