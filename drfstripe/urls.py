from django.contrib import admin
from django.urls import path
from stripeapi.views import CreateSubscription

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create-subscription/', CreateSubscription.as_view(), name='create-subscription'),
]
