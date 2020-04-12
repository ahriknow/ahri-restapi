from django.urls import path
from . import views

urlpatterns = [
    path('<p1>', views.RestapiView.as_view()),
    path('<p1>/', views.RestapiView.as_view()),
    path('<p1>/<p2>', views.RestapiView.as_view()),
    path('<p1>/<p2>/', views.RestapiView.as_view()),
    path('<p1>/<p2>/<p3>', views.RestapiView.as_view()),
    path('<p1>/<p2>/<p3>/', views.RestapiView.as_view()),
    path('<p1>/<p2>/<p3>/<p4>', views.RestapiView.as_view()),
    path('<p1>/<p2>/<p3>/<p4>/', views.RestapiView.as_view()),
    path('<p1>/<p2>/<p3>/<p4>/<p5>', views.RestapiView.as_view()),
    path('<p1>/<p2>/<p3>/<p4>/<p5>/', views.RestapiView.as_view()),
]
