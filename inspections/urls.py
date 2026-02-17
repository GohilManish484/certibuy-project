from django.urls import path
from . import views

app_name = 'inspections'

urlpatterns = [
    path('', views.inspection_list, name='list'),
    path('<int:pk>/', views.inspection_detail, name='detail'),
    path('<int:pk>/update/', views.update_inspection, name='update'),
    path('create/<int:submission_id>/', views.create_inspection, name='create'),
]
