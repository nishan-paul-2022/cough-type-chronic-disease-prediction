from django.urls import path
from django.contrib.auth import views as auth_views
from .views import home, RegisterView, CustomLoginView, ChangePasswordView
from .forms import LoginForm
from users import views

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('login/', CustomLoginView.as_view(redirect_authenticated_user=True, template_name='login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('password_change/', ChangePasswordView.as_view(), name='password_change'),
    path('appointment', getattr(views, 'disease_diagnosis_view'), name='disease_diagnosis_view'),
    path('doctor', getattr(views, 'appointment_view'), name='appointment_view'),
]
