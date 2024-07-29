from django.urls import path
from .views import *

urlpatterns = [
    path('create_user',create_user,name='home'),
    path('user_details/<int:user_id>',user_details,name="user_details"),
    path('add/', add_expenses,name="add"),
    path('user/<int:user_id>/', user_expenses,name="user_expenses"),
    path('overall/',overall_expenses,name="all_expenses"),
    path('download/<int:user_id>/', download_balance_sheet, name='download_balance_sheet'),
]
