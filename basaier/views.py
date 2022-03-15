from django.http import Http404, HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import image , demo, Project
from django.conf import settings
from basaier.Forms import ProjectForm
import os

# Create your views here.


def index(request):
    img =image.objects.all()
    return render(request, 'index.html',{'data':img})


def demo_view(request):
    # if request.method == 'GET':
    data = Project.objects.get(pk=8)
    return render(request, 'demo.html',{'data':data})



def news(request):
    return render(request, 'news.html')


def volunteer(request):
    return render(request, 'volunteer.html')


def happystories(request):
    return render(request, 'happystories.html')


def iqalculator(request):
    return render(request, 'iqalculator.html')


def donatedonation(request):
    return render(request, 'donatedonation.html')


def seasonalprojects(request):
    project_data = Project.objects.all()
    form = ProjectForm()
    return render(request, 'seasonalprojects.html',{'project_data':project_data,'form':form},)

def search_project(request):
    # Search bar on seasonal projects page i.e seasonalprojects.html
    project_data = Project.objects.all()
    if request.method == 'POST':
        
        searched = request.POST['searched']
        project = Project.objects.filter(name__contains=searched)
        
        return render(request,"seasonalprojects.html",{'searched':searched,'searched_project':project})
    


def joinchat(request):
    return render(request, 'joinchat.html')


def createownproject(request):
    return render(request, 'createownproject.html')


def refundproject(request,id):
    proj_data = Project.objects.get(pk=id)
    the_id = id
    return render(request, 'refundproject.html',{'project_id':proj_data,'the_id':id})

def upload_pdf(request,the_id):
    if request.method == 'POST':
        pdf_files = request.FILES.getlist("pdf_files")
        # proj = Project.objects.filter(pk=the_id)
        for f in pdf_files:
             Project.objects.filter(pk=the_id).update(files=pdf_files)
        messages.success(request,"Files Uploaded Successfully")
            # proj(files=f).save()
    proj_data = Project.objects.get(pk=the_id)
    tid = the_id
    return render(request,'refundproject.html',{'project':proj_data,'the_id':tid})

def download_file(request):
    file_path= os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(file_path):
        with open(file_path,'rb') as fh:
            response = HttpResponse(fh.read(),content_type='application/files')
            response['Content-Disposition'] = 'inline;filename='+os.path.basename(file_path)
            return response
    return Http404
    

def bepartner(request):
    return render(request, 'bepartner.html')


def bepartnersave(request):
    return render(request, 'bepartnersave.html')


def joinfieldvolunteer(request):
    return render(request, 'joinfieldvolunteer.html')


def volunteerandspread(request):
    return render(request, 'volunteerandspread.html')


def contactus(request):
    return render(request, 'contactus.html')


def ourpartners(request):
    return render(request, 'ourpartners.html')


def aboutus(request):
    return render(request, 'aboutus.html')


def donationbasket(request):
    return render(request, 'donationbasket.html')


def paynow(request):
    return render(request, 'paynow.html')


# def signup(request):
#     if request.method == 'POST':
#         form = signupform(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, "Registration successful." )
#             return redirect("aboutus.html") 
            		
#     else:
#         messages.error(request, "Unsuccessful registration. Invalid information.")
#         form = signupform()
#     content = {'form':form}
#     return render(request, 'signup.html',content)

def signin(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
		       
            if user is not None:
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}.")
                    return render(request,'aboutus.html')
            else:
                messages.error(request,"Invalid username or password.")
				
    else:
        messages.error(request,"Invalid username or password.")
        form = AuthenticationForm()
        
    return render(request=request, template_name="signin.html", context={"login_form":form})
    


def controlboard(request):
    return render(request, 'controlboard.html')


def donatedonation2(request):
    return render(request, 'donatedonation2.html')


def detailpage(request):
    return render(request, 'detailpage.html')
