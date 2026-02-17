from .views import ProtectedView
from django.urls import path

urlpatterns = [
    path("protected/", ProtectedView.as_view())
]
