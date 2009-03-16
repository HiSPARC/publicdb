from pyamf.remoting.gateway.django import DjangoGateway
from models import *

def get_services(request):
    return services.keys()

services = {'hisparc.get_services': get_services}

publicgateway = DjangoGateway(services)
