from django import http
from urllib import urlencode

from django_publicdb.updates.models import *

USER_UPDATE = 1
ADMIN_UPDATE = 2

def update_check_querystring(request, queue):
    """Check for software updates"""

    try:
        admin_version = request.GET['admin_version']
        user_version = request.GET['user_version']
    except KeyError:
        return http.HttpResponseBadRequest("Incomplete request.")

    return update_check(request, queue, admin_version, user_version)

def update_check(request, queue, admin_version, user_version):
    try:
        queue = UpdateQueue.objects.get(slug=queue)
    except UpdateQueue.DoesNotExist:
        return http.HttpResponseBadRequest("Queue does not exist.")

    answer = {'mustUpdate': 0}

    admin_updates = AdminUpdate.objects.filter(queue=queue,
                                               version__gt=admin_version)
    if admin_updates:
        answer['mustUpdate'] |= ADMIN_UPDATE
        latest = admin_updates.reverse()[0]
        answer['newVersionAdmin'] = latest.version
        answer['urlAdmin'] = latest.update.url
    
    user_updates = UserUpdate.objects.filter(queue=queue,
                                             version__gt=user_version)
    if user_updates:
        answer['mustUpdate'] |= USER_UPDATE
        latest = user_updates.reverse()[0]
        answer['newVersionUser'] = latest.version
        answer['urlUser'] = latest.update.url

    return http.HttpResponse(urlencode(answer), content_type='text/plain')
