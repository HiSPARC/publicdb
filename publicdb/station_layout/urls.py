from django.urls import path

from . import views

app_name = 'layout'
urlpatterns = [
    path('submit/', views.layout_submit, name="submit"),
    path('submit/validate/', views.validate_layout_submit, name="validate_submit"),
    path('confirm/<slug:hash>/', views.confirmed_layout, name="confirm"),
    path('review/<slug:hash>/', views.review_layout, name="review"),
    path('review/<slug:hash>/validate/', views.validate_review_layout, name="validate_review"),
]
