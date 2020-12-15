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
from .models import Profile,s_history,history
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
import speech_recognition as sr

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
    search_form = s_history.objects.filter(username=request.user)
    searchresult_form = history.objects.filter(username=request.user)
    delete=request.POST.get('image')
    if delete==None:
        print('none')
    else:
        object1 = s_history.objects.get(username=request.user,search=delete)
        object1.delete()
        print('object',object1)
    print('delete',delete)
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
    x=s_history(username=request.user,search=imagesave)
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
    imagesave=request.POST.get('save')
    print('imagesave',imagesave)
    x=s_history(username=request.user,search=imagesave)
    x.save()
    if request.method == "GET":
        if request.GET.get('q'):
            text=request.GET.get('q')
            page = int(request.GET.get('page', '1'))
    
    start = (page-1) * 10
    end = start + 10
    count=start+end
    print('count',count)
    totalResults,search,posts = Singlesearch(Q_text=text,pageLowerLimit=start,pageUpperLimit=end,page=page)

    context = {
        'users': search,
        'text':text,
        'paginator':posts,
        'query': { 'q' : text}
    }
    return render(request,'dl_app/search.html',context)

# def delete(request):
#     object = YourModel.objects.get(id=part_id)
#     object.delete()
#     return render(request,'ur template where you want to redirect')



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

def imgdetails(request):
    item = request.GET.get('imgitem')
    imgg =item[:-11]
    pid ="p-"+item[22:-4]
    is_multiple=0
    origreftext="FIG. "+item[24:-4]
    figid=item[24:-4]
    is_caption=1
    index="_id: "+item[24:-4]
    context={
    'item':item,
    'imgg':imgg,
    'pid':pid,
    'is_multiple':is_multiple,
    'origreftext':origreftext,
    'index':index,
    'is_caption':is_caption,
    'figid':figid
    }
    print('item',item)
    print('imgg',imgg)
    print('pid',pid)
    print('is_multiple',is_multiple)
    print('origreftext',origreftext)
    print('index',index)
    print('is_caption',is_caption)
    print('figid',figid)
    return render(request, 'dl_app/imgdetails.html',context)

@login_required
def editjson(request):
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



# def speech_to_text(request):
#     data = request.POST.get('record')
#     import speech_recognition as sr

#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         #print("Say something!")
#         audio = r.listen(source)

#     try:
#         # for testing purposes, we're just using the default API key
#         # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
#         # instead of `r.recognize_google(audio)`
#         speech = r.recognize_google(audio)
#     except sr.UnknownValueError:
#         speech = "Google Speech Recognition could not understand audio"
#     except sr.RequestError as e:
#         speech = "Could not request results from Google Speech Recognition service; {0}".format(e)

#     return render(request,'dl_app/speech.html',{'speech': speech})

