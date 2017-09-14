import time
from django.db import models


class Pools(models.Model):
    pool = models.CharField(max_length=255)

    def __str__(self):
        return "<" + self.pool + ">"

    class Meta:
        verbose_name = "Пул"
        verbose_name_plural = "Пулы"


class UserPools(models.Model):
    pool = models.ForeignKey(Pools)
    address = models.CharField(max_length=255, blank=False)
    name = models.CharField(max_length=255, blank=False)
    comment = models.CharField(max_length=255, blank=True)
    claymore_port = models.IntegerField(default=3333)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Кошелёк на пуле"
        verbose_name_plural = "Кошельки на пуле"


class Worker(models.Model):
    address_pool = models.ForeignKey(UserPools, null=True, default=None)
    name = models.CharField(max_length=255)
    last_submit_time = models.DateTimeField(null=True)
    reported_hash_rate = models.DecimalField(decimal_places=1, max_digits=5, default = 0)
    valid_shares = models.IntegerField(null=True)
    invalid_shares = models.IntegerField(null=True)
    stale_shares = models.IntegerField(null=True)
    invalid_share_ratio = models.IntegerField(null=True)
    last_update = models.DateTimeField(auto_now=True)
    uptime = models.BigIntegerField(null=True, default=0)
    ip_address = models.CharField(max_length=255, null=True)
    sum_hr_base = models.DecimalField(decimal_places=1, max_digits=5, default=0)
    sum_hr_sec = models.DecimalField(decimal_places=1, max_digits=5, default=0)
    hr_details_base = models.CharField(max_length=255, null=True)
    hr_details_sec = models.CharField(max_length=255, null=True)
    temperature = models.CharField(max_length=255, null=True)
    fun_speed = models.CharField(max_length=255, null=True)
    pools = models.CharField(max_length=255, null=True)
    claymore_version = models.CharField(max_length=255, null=True)
    claymore_uptime =  models.BigIntegerField(null=True, default=0)

    def __str__(self):
        if self.address_pool is None:
            return self.name + ": " + str(self.last_update)
        else:
            return self.address_pool.name + " - " + self.name + ": " + str(self.last_update)


    class Meta:
        unique_together = ['address_pool', 'name']


class WorkersHistory(models.Model):
    worker = models.ForeignKey(Worker)
    reported_hash_rate = models.DecimalField(decimal_places=1, max_digits=5)
    date_time = models.DateTimeField(blank=False)
    sum_hr_base = models.DecimalField(decimal_places=1, max_digits=5, default=0)
    sum_hr_sec = models.DecimalField(decimal_places=1, max_digits=5, default=0)

    def as_list(self):
        return [
            int(time.mktime(self.date_time.timetuple()) * 1000),
            float(self.reported_hash_rate)
        ]

