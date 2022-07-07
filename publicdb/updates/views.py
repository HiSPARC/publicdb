from urllib.parse import urlencode

from django import http

from .models import InstallerUpdate, UpdateQueue

USER_UPDATE = 0b01
ADMIN_UPDATE = 0b10


def get_latest_installer(request):
    """Get latest full HiSPARC installer"""

    installer = InstallerUpdate.objects.filter(queue__slug='hisparc').first()
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

    admin_updates = queue.admin_updates.filter(version__gt=admin_version)
    if admin_updates:
        answer['mustUpdate'] |= ADMIN_UPDATE
        latest = admin_updates.first()
        answer['newVersionAdmin'] = latest.version
        answer['urlAdmin'] = latest.update.url

    user_updates = queue.user_updates.filter(version__gt=user_version)
    if user_updates:
        answer['mustUpdate'] |= USER_UPDATE
        latest = user_updates.first()
        answer['newVersionUser'] = latest.version
        answer['urlUser'] = latest.update.url

    return http.HttpResponse(urlencode(answer), content_type='text/plain')
