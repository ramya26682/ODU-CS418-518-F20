from django.shortcuts import render, redirect 
from django.contrib import messages 
from django.contrib.auth import authenticate, login 
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.forms import AuthenticationForm 
from .forms import UserRegisterForm 
from django.core.mail import send_mail 
from django.core.mail import EmailMultiAlternatives 
from django.template.loader import get_template 
from django.template import Context 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
  

# @login_required(login_url='login')
# def index(request): 
#     return render(request, 'dl_app/index.html', {'title':'index'}) 
   

def register(request): 
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            email_subject = 'Activate Your Account'
            message = render_to_string('activate_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            return HttpResponse('We have sent you an email, please confirm your email address to complete registration')


    else:
        form = UserRegisterForm()
    return render(request, 'dl_app/register.html', {'form': form,'title':'reqister here'})



def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Your account has been activate successfully')
    else:
        return HttpResponse('Activation link is invalid!')


def Login(request): 
    if request.method == 'POST': 
        username = request.POST['username']
        password = request.POST['password'] 
        user = authenticate(request, username = username, password = password) 
        # print(user.id)
        if user is not None: 
            form = login(request, user) 
            messages.success(request, f' wecome {username} !!')
            user=User.objects.get(username=username)
            print(user)
            return render(request,'dl_app/index.html',{'username':username}) 
        else: 
            return render(request,'dl_app/error.html') 
    form = AuthenticationForm() 
    return render(request, 'dl_app/login.html', {'form':form, 'title':'log in'})

def index(request,user_id):
    user=User.objects.get(pk=user_id)
    print(user)
    return render(request, 'dl_app/index.html', {'title':'index'}) 
   
def forget_password(request): 
    if request.method == 'POST': 
        form = UserRegisterForm(request.POST) 
        if form.is_valid(): 
            form.save() 
            username = form.cleaned_data.get('username') 
            email = form.cleaned_data.get('email') 
            htmly = get_template('dl_app/Email.html') 
            d = { 'username': username } 
            subject, from_email, to = 'welcome', 'your_email@gmail.com', email 
            html_content = htmly.render(d) 
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to]) 
            msg.attach_alternative(html_content, "text / html") 
            msg.send()   
            messages.success(request, f'Your account has been created ! You are now able to log in') 
            return redirect('login') 
    else: 
        form = UserRegisterForm() 
    return render(request, 'dl_app/forget_password.html', {'form': form, 'title':'reqister here'})


def profile(request):
    if request.method == 'POST':
        print(request)
    else:
        print('--> username : ', request.user)
        print('--> id : ', request.user.id)
        form = UserRegisterForm()
    return render(request, 'dl_app/profile.html', {'form': form,'title':'reqister here', 'name':request.user,'id':request.user.id,'email':request.user.email})