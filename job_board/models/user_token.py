from django.db import models
from django.contrib.auth.models import User


class UserToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tokens = models.PositiveSmallIntegerField()

    def deduct(self):
        self.tokens -= 1
        self.save()

    def __str__(self):
        return "%s - %s" % (self.user.username, self.tokens)
