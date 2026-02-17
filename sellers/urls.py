from django.urls import path
from . import views

app_name = 'sellers'

urlpatterns = [
    path('submit/', views.submit_product, name='submit_product'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('submission/<int:pk>/', views.submission_detail, name='submission_detail'),
]
