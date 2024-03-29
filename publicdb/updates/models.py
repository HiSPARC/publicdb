import re

from django.db import IntegrityError, models


def upload_queue(instance, filename):
    """Return an upload_to value based on the upload queue"""

    return f'uploads/{instance.queue}/{filename}'


class UpdateQueue(models.Model):
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class AdminUpdate(models.Model):
    version = models.PositiveSmallIntegerField()
    update = models.FileField(upload_to=upload_queue)
    queue = models.ForeignKey(UpdateQueue, models.CASCADE, related_name='admin_updates')

    class Meta:
        verbose_name = 'Admin update'
        verbose_name_plural = 'Admin updates'
        unique_together = ('queue', 'version')
        ordering = ['-version']

    def __str__(self):
        return f'Queue: {self.queue} - Admin Update v{self.version}'

    def save(self, *args, **kwargs):
        match = re.search(r'_v(\d+)', self.update.name)
        self.version = int(match.group(1))
        super().save(*args, **kwargs)


class UserUpdate(models.Model):
    version = models.PositiveSmallIntegerField()
    update = models.FileField(upload_to=upload_queue)
    queue = models.ForeignKey(UpdateQueue, models.CASCADE, related_name='user_updates')

    class Meta:
        verbose_name = 'User update'
        verbose_name_plural = 'User updates'
        unique_together = ('queue', 'version')
        ordering = ['-version']

    def __str__(self):
        return f'Queue: {self.queue} - User Update v{self.version}'

    def save(self, *args, **kwargs):
        match = re.search(r'_v(\d+)', self.update.name)
        self.version = int(match.group(1))
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            return


class InstallerUpdate(models.Model):
    version = models.CharField(max_length=5)
    installer = models.FileField(upload_to=upload_queue)
    queue = models.ForeignKey(UpdateQueue, models.CASCADE, related_name='installer_updates')

    class Meta:
        verbose_name = 'Installer update'
        verbose_name_plural = 'Installer updates'
        unique_together = ('queue', 'version')
        ordering = ['-version']

    def __str__(self):
        return f'Installer v{self.version}'

    def save(self, *args, **kwargs):
        match = re.search(r'_v(\d+\.\d+)', self.installer.name)
        self.version = match.group(1)
        super().save(*args, **kwargs)
