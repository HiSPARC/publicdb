import re

from django.db import IntegrityError, models


def upload_queue(instance, filename):
    """Return an upload_to value based on the upload queue"""

    return 'uploads/%s/%s' % (instance.queue, filename)


class UpdateQueue(models.Model):
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.slug


class AdminUpdate(models.Model):
    version = models.PositiveSmallIntegerField()
    update = models.FileField(upload_to=upload_queue)
    queue = models.ForeignKey(UpdateQueue, models.CASCADE, related_name='admin_updates')

    def __unicode__(self):
        return 'Queue: %s - Admin Update v%d' % (self.queue, self.version)

    def save(self, *args, **kwargs):
        match = re.search('_v(\d+)', self.update.name)
        self.version = int(match.group(1))
        super(AdminUpdate, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Admin update'
        verbose_name_plural = 'Admin updates'
        unique_together = ('queue', 'version')
        ordering = ['version']


class UserUpdate(models.Model):
    version = models.PositiveSmallIntegerField()
    update = models.FileField(upload_to=upload_queue)
    queue = models.ForeignKey(UpdateQueue, models.CASCADE, related_name='user_updates')

    def __unicode__(self):
        return 'Queue: %s - User Update v%d' % (self.queue, self.version)

    def save(self, *args, **kwargs):
        match = re.search('_v(\d+)', self.update.name)
        self.version = int(match.group(1))
        try:
            super(UserUpdate, self).save(*args, **kwargs)
        except IntegrityError:
            return

    class Meta:
        verbose_name = 'User update'
        verbose_name_plural = 'User updates'
        unique_together = ('queue', 'version')
        ordering = ['version']


class InstallerUpdate(models.Model):
    version = models.CharField(max_length=5)
    installer = models.FileField(upload_to=upload_queue)
    queue = models.ForeignKey(UpdateQueue, models.CASCADE, related_name='installer_updates')

    def __unicode__(self):
        return 'Installer v%s' % self.version

    def save(self, *args, **kwargs):
        match = re.search('_v(\d+\.\d+)', self.installer.name)
        self.version = match.group(1)
        super(InstallerUpdate, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Installer update'
        verbose_name_plural = 'Installer updates'
        unique_together = ('queue', 'version')
        ordering = ['version']
