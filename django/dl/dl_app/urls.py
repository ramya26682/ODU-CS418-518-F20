from django.urls import path, include
from . import views
from . import views as user_view 
from django.contrib.auth import views as auth 
from django.conf.urls import url
from django.contrib.auth import views as auth_views


urlpatterns = [ 
    path('index/', views.index, name ='index'),
    path('profile/', views.profile, name ='profile'),


    path('login/', user_view.Login, name ='login'), 
    path('', user_view.Login, name ='login'), 
    path('logout/', auth.LogoutView.as_view(template_name ='user / index.html'), name ='logout'), 
    path('register/', user_view.register, name ='register'), 
    path('app/login/dl_app/register.html/', user_view.register, name ='register'), 
    path('forget_password/', user_view.forget_password, name ='forget_password'), 
     url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate_account, name='activate'),

    path('reset_password/',
     auth_views.PasswordResetView.as_view(template_name="dl_app/password_reset.html"),
     name="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="dl_app/password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name="dl_app/password_reset_form.html"), 
     name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="dl_app/password_reset_done.html"), 
        name="password_reset_complete"),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='dl_app/password_change_done.html'), 
        name='password_change_done'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='dl_app/password_change.html'), 
        name='password_change'),



     ]

# 1 - Submit email form                         //PasswordResetView.as_view()
# 2 - Email sent success message                //PasswordResetDoneView.as_view()
# 3 - Link to password Reset form in email       //PasswordResetConfirmView.as_view()
# 4 - Password successfully changed message     //PasswordResetCompleteView.as_view()
