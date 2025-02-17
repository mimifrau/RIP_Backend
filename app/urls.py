from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('codes/<int:code_id>/', code),
    path('taxs/<int:tax_id>/', tax),
]