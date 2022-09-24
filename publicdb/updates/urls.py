from django.urls import path

from . import views

app_name = 'updates'
urlpatterns = [
    path('installer/latest/', views.get_latest_installer, name="latest"),
    path('<slug:queue>/check', views.update_check_querystring, name="check"),
    path('<slug:queue>/check/<int:admin_version>/<int:user_version>', views.update_check, name="check"),
    path('<slug:queue>/check/<int:admin_version>/<int:user_version>/', views.update_check, name="check"),
]
