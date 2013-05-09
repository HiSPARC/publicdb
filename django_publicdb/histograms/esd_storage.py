""" Functions to get the locations of files in the ESD

"""
import os
import logging

import tables

from django.conf import settings


logger = logging.getLogger('histograms.esd_storage')


def get_esd_data_path(date):
    """Return path to ESD file

    Return path to the ESD file of a particular date

    :param date: the date as a datetime.date object

    :return: path to the ESD file

    """
    rootdir = settings.ESD_PATH
    filepath = date.strftime('%Y/%-m/%Y_%-m_%-d.h5')
    return os.path.join(rootdir, filepath)


def get_or_create_esd_data_path(date):
    """Return path to ESD file, creating directories if necessary

    :param date: datetime.date object

    :returns: path to ESD file

    """
    filepath = get_esd_data_path(date)
    dirpath, filename = os.path.split(filepath)

    if not os.path.exists(dirpath):
        # create dir and parent dirs with mode rwxr-xr-x
        os.makedirs(dirpath, 0755)

    return filepath
