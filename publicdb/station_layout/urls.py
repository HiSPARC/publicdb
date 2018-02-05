from django.conf.urls import url

from . import views

app_name = 'layout'
urlpatterns = [
    url(r'^submit/$', views.layout_submit, name="submit"),
    url(r'^submit/validate/$', views.validate_layout_submit, name="validate_submit"),
    url(r'^confirm/(?P<hash>[a-zA-Z0-9_]{32})/$', views.confirmed_layout, name="confirm"),
    url(r'^review/(?P<hash>[a-zA-Z0-9_]{32})/$', views.review_layout, name="review"),
    url(r'^review/(?P<hash>[a-zA-Z0-9_]{32})/validate/$', views.validate_review_layout, name="validate_review"),
]
