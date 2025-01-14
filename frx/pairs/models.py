from django.db import models
from datetime import datetime


class Pair(models.Model):
    name = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Rate(models.Model):
    pair = models.ForeignKey(
        Pair, to_field='name', on_delete=models.DO_NOTHING, related_name='rates', null=False, blank=False)
    date = models.DateField(default=datetime.now, null=False, blank=False)
    high = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False)
    low = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False)
    close = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False)
    open = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pair} - {self.close} - {self.date}'


class Price(models.Model):
    pair = models.ForeignKey(
        Pair, to_field='name', on_delete=models.DO_NOTHING, related_name='prices', null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False)
    checked_at = models.DateTimeField(default=datetime.now, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pair} - {self.price}'


class LastNotification(models.Model):
    class NotificationTypeEnum(models.TextChoices):
        Z2 = 'Z2', 'Z2'
        Z2_LOW = 'Z2_LOW', 'Z2_LOW'

    pair = models.ForeignKey(
        Pair, to_field='name', on_delete=models.DO_NOTHING, related_name='notifications', null=False, blank=False)
    notification_type = models.CharField(choices=NotificationTypeEnum.choices, max_length=255, null=False, blank=False)
    date = models.DateField(default=datetime.now, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pair} - {self.notification_type} - {self.date}'
