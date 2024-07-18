from django.contrib import admin
from django.urls import path
from stripeapi.views import CreateSubscription, StripeWebhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create-subscription/', CreateSubscription.as_view(), name='create-subscription'),
    path('webhook/', StripeWebhook.as_view(), name='stripe_webhook'),
]
