from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('codes/<int:code_id>/', code_details, name="code_details"),
    path('codes/<int:code_id>/add_to_tax/', add_code_to_draft_tax, name="add_code_to_draft_tax"),
    path('taxs/<int:tax_id>/delete/', delete_tax, name="delete_tax"),
    path('taxs/<int:tax_id>/', tax)
]
