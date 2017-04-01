import sys
import os
from optparse import OptionParser

sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'publicdb.settings'

from publicdb.inforecords.models import Pc, MonitorService, EnabledService

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-n', '--name', help='Name of the PC')
    (options, args) = parser.parse_args()

    try:
        pc = Pc.objects.get(name=options.name)
    except Pc.DoesNotExist:
        print 'This pc does not exist.  Doing nothing.'
    else:
        for service in EnabledService.objects.filter(pc=pc):
            print 'Deleting service: %s', service
            service.delete()

        for service in MonitorService.objects.filter(is_default_service=True):
            new_service = EnabledService(pc=pc, monitor_service=service)
            print 'Creating service: %s', new_service
            new_service.save()
