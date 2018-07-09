from urllib import urlencode

from django import http

from .models import AdminUpdate, InstallerUpdate, UpdateQueue, UserUpdate

USER_UPDATE = 0b01
ADMIN_UPDATE = 0b10


def get_latest_installer(request):
    """Get latest full HiSPARC installer"""

    installer = InstallerUpdate.objects.filter(queue__slug='hisparc').order_by('-version')[0]
    return http.HttpResponseRedirect(installer.installer.url)


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

    answer = {'mustUpdate': 0b00}

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
