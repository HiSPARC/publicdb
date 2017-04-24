from django.conf.urls import url

from . import views

app_name = 'layout'
urlpatterns = [
    url(r'^submit/$', views.layout_submit),
    url(r'^submit/validate/$', views.validate_layout_submit),
    url(r'^confirm/(?P<hash>\w{32})/$', views.confirmed_layout),
    url(r'^review/(?P<hash>\w{32})/$', views.review_layout),
    url(r'^review/(?P<hash>\w{32})/validate/$', views.validate_review_layout),
]
