from django.conf.urls import url

from ..analysissessions import views

app_name = 'oldsessions'
urlpatterns = [
    url(r'^get_coincidence/$', views.get_coincidence, name="get_coincidence"),
    url(r'^result/$', views.result, name="result"),
]
