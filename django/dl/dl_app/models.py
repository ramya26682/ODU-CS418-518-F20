from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver 
from django.db.models.signals import post_save 



class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class search_history(models.Model):
	username=models.CharField(max_length=500,default="",blank=True)
	search=models.CharField(max_length=500,default="P-0001",null=True)


class history(models.Model):
	username=models.CharField(max_length=500,default="",blank=True)
	search=models.CharField(max_length=500,default="P-0001",null=True)
	created_at = models.DateField(auto_now_add=True)
