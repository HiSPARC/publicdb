from django.urls import path, re_path

from . import views

app_name = 'layout'
urlpatterns = [
    path('submit/', views.layout_submit, name="submit"),
    path('submit/validate/', views.validate_layout_submit, name="validate_submit"),
    re_path(r'^confirm/(?P<hash>[a-zA-Z0-9_]{32})/$', views.confirmed_layout, name="confirm"),
    re_path(r'^review/(?P<hash>[a-zA-Z0-9_]{32})/$', views.review_layout, name="review"),
    re_path(r'^review/(?P<hash>[a-zA-Z0-9_]{32})/validate/$', views.validate_review_layout, name="validate_review"),
]
