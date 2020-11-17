from django.shortcuts import render, redirect 
from django.contrib import messages 
from django.contrib.auth import authenticate, login 
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.forms import AuthenticationForm 
from django.core.mail import send_mail 
from django.core.mail import EmailMultiAlternatives 
from django.template.loader import get_template 
from django.template import Context 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from .forms import UserRegisterForm,DSEPaginator
from .models import Profile,search_history,history
from .forms import EditProfileForm,UserProfileForm,SearchHistoryForm
# from .es_test import AdvancedSearch, Singlesearch, updateIndex
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import requests
import json
import urllib
from functools import wraps
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchRank, SearchQuery,SearchVector
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404
from django.shortcuts import render,get_object_or_404
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MultiMatch
from multiprocessing import Value
from .es_test import Singlesearch,AdvancedSearch,updateIndex


counter = Value('i',0)
def reg(request): 
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req =  urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''

            if result['success']:
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
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
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
        captcha_token=request.POST.get("g-recaptcha-response")
        cap_url="https://www.google.com/recaptcha/api/siteverify"
        cap_secret="6LfWoOMZAAAAAKk4Alyw4QkASIkx4zGcmO-uewjf";
        cap_data={"secret":cap_secret,"response":captcha_token}
        cap_server_response=requests.post(url=cap_url,data=cap_data)
        print(cap_server_response.text)
        cap_json=json.loads(cap_server_response.text)
        if cap_json['success']==False:
            messages.error(request,("Invalid Captcha"))
            return render(request,'dl_app/recaptcha_error.html')
        user = authenticate(request, username = username, password = password)
        if user is not None: 
            form = login(request, user)
            messages.success(request, 'New comment added with success!')
            messages.success(request, f' welcome {username} !!')
            user=User.objects.get(username=username)
            print(user)
            return redirect('/index/')
            #return render(request,'dl_app/index.html',{'username':username}) 
        else: 
            return render(request,'dl_app/error.html') 
    form = AuthenticationForm() 
    return render(request, 'dl_app/login.html', {'form':form, 'title':'log in'})


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


@login_required(login_url='/login/')
def profiledetails(request):
    search_form = search_history.objects.filter(username=request.user)
    searchresult_form = history.objects.filter(username=request.user)  
    # print('request.user',search_form)
    if request.method == "POST":
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = EditProfileForm(request.POST, instance=request.user.profile)
        search_form=SearchHistoryForm(request.POST,instance=request.user)
        if user_form.is_valid():
            user_form.save()
        elif profile_form.is_valid():
            profile_form.save()
        else:
            messages.error(request,('Unable to complete request'))
        return redirect ("/dl_app/profile")
    user_form = UserProfileForm(instance=request.user)
    profile_form = EditProfileForm(instance=request.user.profile)
    return render(request=request, template_name="dl_app/profile.html", context={"search":search_form,"result":searchresult_form, "user":request.user, "form":user_form, "profile_form":profile_form})

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("dl_app/index")

@login_required
def advanced_search(request):
    return render(request,'dl_app/advanced.html')

#advanced search
@login_required
def search(request):
    return render(request,'dl_app/search.html')



@login_required
def Advancedsearch(request):
    results=[]
    testpatentID=""
    testaspect=""
    page=1
    if request.method=="POST":
        if request.POST.get('patentID') and request.POST.get('aspect'):
            testpatentID=request.POST.get('patentID')
            testaspect=request.POST.get('aspect')
        elif request.POST.get('patentID'):
            testpatentID=name=request.POST.get('patentID')
        elif request.POST.get('aspect'):
            testaspect=request.POST.get('aspect')
        page=1
    imagesave=request.POST.get('save')
    x=search_history(username=request.user,search=imagesave)
    x.save()
    if request.method == "GET":
        if request.GET.get('q'):
            testpatentID=request.GET.get('q1')
            testaspect=request.GET.get('q2')
            page = int(request.GET.get('page', '1')) 
    start = (page-1) * 10
    end = start + 10
    totalResults,results,posts = AdvancedSearch(patentID=testpatentID, aspect=testaspect,pageLowerLimit=start,pageUpperLimit=end,page=page)
    context={
    'users': results,
    'request.user':'request.user',
    'paginator':posts,
    'patentID':testpatentID,
    'aspect':testaspect,
    'query': { 'q1' : testpatentID,'q2':testaspect}
    }
    return render(request,'dl_app/Advanced.html',context)


@login_required
def samplesearch(request):
    results=[]
    text=""
    page = 1
    print(request.POST)
    if request.method == "POST":
        if request.POST.get('pid'):
            text=request.POST.get('pid')
            y=history(username=request.user,search=text)
            y.save()
        page=1
    imagesave=request.POST.get('save')
    print('imagesave',imagesave)
    x=search_history(username=request.user,search=imagesave)
    x.save()
    if request.method == "GET":
        if request.GET.get('q'):
            text=request.GET.get('q')
            page = int(request.GET.get('page', '1'))
    
    start = (page-1) * 10
    end = start + 10
    totalResults,search,posts = Singlesearch(Q_text=text,pageLowerLimit=start,pageUpperLimit=end,page=page)

    context = {
        'users': search,
        'text':text,
        'paginator':posts,
        'query': { 'q' : text}
    }




    # results=Singlesearch(Q_text=text)
    # page = request.GET.get('page', 1)
    # paginator = Paginator(results, 10)
    # try:
    #     users = paginator.page(page)
    # except PageNotAnInteger:
    #     users = paginator.page(1)
    # except EmptyPage:
    #     users = paginator.page(paginator.num_pages)
    # context={
    # 'results':results,
    # 'request.user':'request.user',
    # 'users':users,
    # 'count':paginator.count,
    # 'text':text
    # }
    return render(request,'dl_app/search.html',context)




def moredetails(request):
    item = request.GET.get('getitem')
    ret = item.split(",")
    imgg =ret[0][2:-8]+"-D0"+ret[0][24:-1]+".png"
    context={
    'ret':ret,
    'img':imgg
    }
    print('ret',ret[2])
    print('img',imgg)
    return render(request, 'dl_app/moredetails.html',context)


# @login_required
# def samplesearch(request):
#     results=[]
#     text=""
#     print(request.POST)
#     if request.POST.get('pid'):
#         text=request.POST.get('pid')
#         messages.success(request,'item':+text+' saved to profile')
#         return redirect()
#     results=Singlesearch(Q_text=text)
#     print(results)
#     context={
#     'results':results,
#     'request.user':'request.user'
#     }
#     return render(request,'dl_app/search.html',context)
@login_required
def editjson(request):
    #if request.POST.get(patentID) and request.POST.get(pid) and request.POST.get(is_multiple) and request.POST.get(origreftext) and request.POST.get(figid) and request.POST.get(subfig) and request.POST.get(is_caption) and request.POST.get(description) and request.POST.get(aspect) and request.POST.get(objects):
    if request.method == "POST":
        # save file
        print(request.POST)
        myfile = request.FILES['myfile']
        print(myfile.name)
        fs = FileSystemStorage()
        print(request.POST['patentID'])
        print(request.POST['pid'])
        filename = request.POST['patentID'] + '-D0' + str(request.POST['pid'])[2:]+'.png'
        print(filename)
        fs.save(filename, myfile)
        if updateIndex(request.POST):
            return render(request,'dl_app/messgae.html',context = {'message': 'Index Updated and File Uploaded !!!'})
        else:
            return render(request,'dl_app/messgae.html',context = {'message': 'update index failed !!!'}) 

    return render(request, 'dl_app/editform.html')





