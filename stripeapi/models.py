from django.db import models

class CustomUser(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    stripe_customer_id = models.CharField(max_length=255)

    def __str__(self):
        return self.email

class Subscription(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255)
    
    def __str__(self):
        return self.stripe_subscription_id
