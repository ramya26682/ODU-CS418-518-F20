from django.urls import path, include
from . import views
from . import views as user_view 
from django.contrib.auth import views as auth 
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


urlpatterns = [ 
    # path('index/', views.index, name ='index'),
    path('dl_app/profile', views.profiledetails, name= "profile"),
    path('login/', user_view.Login, name ='login'), 
    path('', user_view.Login, name ='login'), 
    path('logout/', auth.LogoutView.as_view(template_name ='user / index.html'), name ='logout'), 
    path('reg/', user_view.reg, name ='reg'), 
    path('search/',views.samplesearch,name="search"),
    path('index/',views.samplesearch,name="search"),
    path('advanced/',views.Advancedsearch,name="Advancedsearch"),
    path('app/login/dl_app/reg.html/', user_view.reg, name ='reg'), 
    path('forget_password/', user_view.forget_password, name ='forget_password'), 
    path('edit/', views.editjson,name='edit'),
    path('moredetails/',views.moredetails,name="moredetails"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate_account, name='activate'),

    path('reset_password/',
     auth_views.PasswordResetView.as_view(template_name="Passwords/password_reset.html"),
     name="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="Passwords/password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name="Passwords/password_reset_form.html"), 
     name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="Passwords/password_reset_done.html"), 
        name="password_reset_complete"),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='Passwords/password_change_done.html'), 
        name='password_change_done'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='Passwords/password_change.html'), 
        name='password_change'),



     ]

# 1 - Submit email form                         //PasswordResetView.as_view()
# 2 - Email sent success message                //PasswordResetDoneView.as_view()
# 3 - Link to password Reset form in email       //PasswordResetConfirmView.as_view()
# 4 - Password successfully changed message     //PasswordResetCompleteView.as_view()
