from datetime import datetime,timedelta
from dateutil.tz import tz
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render
from django.template.defaulttags import register
from django.urls import reverse
# from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt

from . import forms
from .models import *


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def index(request):
    return render(request, "index.html")


@csrf_exempt
def loginform(request):

    if request.method == "POST":
        print('In Login if =====>')
        fm = AuthenticationForm(request=request, data=request.POST)
        if fm.is_valid():
            print('Form is valid  =====>')
            un = fm.cleaned_data['username']
            pwd = fm.cleaned_data['password']
            user = authenticate(username=un, password=pwd)
            get_user = SiteUser.objects.get(username = un)
            last_login_date = get_user.last_login
            if user is not None:
                print("User id is =====> ", user.id)
                login(request, user)
                today = datetime.datetime.now().date()
                print("today =====>",today)
                print("last_login =====>",last_login_date.date())
                if last_login_date.date() == today:
                    request.session['count'] = 1
                    request.session.modified = True
                else:
                    request.session['count'] = 0
                    request.session.modified = True

                print("After login User role is =====> ", user.role)
                print(request.user.role,' =====>')
                messages.success(request, "login Successful!")
                if request.user.role == "Admin":
                    return HttpResponseRedirect('/admin/')
                elif request.user.role == "HR":
                    return HttpResponseRedirect('/att_sys/hrprofile/')
                else:
                    emp = Employee.objects.get (user = request.user.id)
                    return HttpResponseRedirect(f"/att_sys/userpersonal/{emp.id}")
    else:
        fm = AuthenticationForm()
        print('In Login else =====>')
    return render(request, 'login.html', {'form': fm})


@csrf_exempt
def logout_profile(request):
    print("In logout  =====>")
    logout(request)

    return render(request, "index.html")



@csrf_exempt
@login_required(login_url="/att_sys/login/")
def hr_profile(request):
    session = request.session['count']
    user = Employee.objects.exclude(id=1)
    emp = Employee.objects.get(user = request.user.id)
    today = datetime.datetime.now ().date ()
    att = Attendance.objects.filter (Q (employee = emp) & Q (date = today))
    designation = set()
    for i in user:
        designation.add(i.designation)
    designation = list(designation)
    print (designation)
    print('session :--------',request.session.get('count'))
    if request.method == "POST":
        role = request.POST['role']
        print(role)
        if role:
            user = Employee.objects.filter(designation = role)
            context = {
                'user': user,
                'designation':designation,
                'emp': emp,
                'session': session,
                'att': att,
             }
            return render (request,'hrprofile.html',context)
        else:
            return render(request,'hrprofile.html',{'user': user,'designation':designation,'emp':emp,'session':session,'att':att})

    elif request.method == 'GET':
        return render (request,'hrprofile.html',{'user': user,'designation':designation,'emp':emp,'session':session,'att':att})
    else:
        return HttpResponse('An Exception Occurred')


@login_required(login_url="/att_sys/login/")
def user_profile(request,id):
    print("In User profile ")
    user = Attendance.objects.filter(employee_id = id).order_by('date')
    emp = Employee.objects.get(id=id)
    dwh = {}
    for i in user:
        t1 = i.chin
        t2 = i.chout
        if i.chout and i.chin:
            t1_datetime = datetime.datetime.combine (datetime.datetime.today (),t1)
            t2_datetime = datetime.datetime.combine (datetime.datetime.today (),t2)
            diff = t2_datetime - t1_datetime
            wh = int (diff.total_seconds () / 3600)
            dwh[i.id] = wh

        else:
            diff = 0
            wh = 0
            dwh[i.id] = wh

    twh = sum (dwh.values ())
    context = {
        'user': user,
        'name': request.user,
        'emp': emp,
        'dwh': dwh,
        'twh': twh,
    }
    if request.method =="POST":
        fromdate = request.POST['fromdate']
        todate = request.POST['todate']
        print(fromdate,todate)
        user = Attendance.objects.filter(Q(employee_id = id) & Q(date__gte=fromdate) & Q(date__lte=todate)).order_by('date')
        print(user,'--------------------------------------')
        context['user'] = user
        print(context)
        return render(request, "userprofile.html", context)
    else:
        context['user'] = user
        return render(request, "userprofile.html", context)


@login_required(login_url="/att_sys/login/")
def update(request,id):
    print ("In Update")
    att = Attendance.objects.get(id = id)
    emp = Employee.objects.get(id=att.employee.id)
    id_user = att.employee.id
    print(emp,'------>')
    if request.method == "POST":
        fm = forms.Update(request.POST)
        print (fm,'------>')
        if fm.is_valid():
            date = request.POST['date']
            chin = request.POST['chin']
            chout = request.POST['chout']
            user = Attendance(id=id, employee = emp,date = date,chin = chin,chout =chout)
            user.save()
            messages.success(request,"Successfully Updated!")
            return HttpResponseRedirect(f"/att_sys/hrprofile/userprofile/{id_user}")
    else:
        fm = forms.Update(instance = att)
        print(fm)
    return render(request,"update.html",{'name': request.user,'form': fm , 'id_user':id_user})


@login_required(login_url="/att_sys/login/")
def success(request, id):
    user = Employee.objects.get(id=id)
    print("In success")
    return render(request, "success.html",{'user':user})


@login_required(login_url="/att_sys/login/")
def delete(request, id):
    user = Employee.objects.get(id=id)
    user.delete()
    return HttpResponseRedirect(reverse('hrprofile'))


@login_required(login_url="/att_sys/login/")
def delete_att(request,id):
    att = Attendance.objects.get(id=id)
    id_user = att.employee.id
    print(id_user)
    att.delete()
    return HttpResponseRedirect(f'/att_sys/hrprofile/userprofile/{id_user}/')


@login_required(login_url="/att_sys/login/")
def add(request):

        today = datetime.datetime.now ().date ()
        emp = Employee.objects.get(user = request.user)
        print(emp,'------>')
        print(emp.user.role,'------>')
        att = Attendance.objects.filter(Q(employee = emp.id) & Q(date = today))
        if request.method == "POST":
            fm = forms.Add(request.POST)
            if fm.is_valid ():
                date = request.POST.get ('date')
                chin = request.POST.get ('chin')
                chout = request.POST.get ('chout')
                if att:
                    for i in att:
                        print("checkout")
                        Attendance.objects.filter(id=i.id).update(chout=chout)
                else:
                    print ("checkin")
                    user = Attendance (employee = emp,date = date,chin = chin)
                    user.save ()
                messages.success (request,"Successfully Add!")
                return HttpResponseRedirect (f'/att_sys/userpersonal/{emp.id}',{'form': fm,'att':att})

        else:
            fm = forms.Add ()
            print (fm)
        return render (request,"add.html",{'name': request.user,'form': fm,'emp': emp,'att':att})


@login_required(login_url="/att_sys/login/")
def user_personal(request,id):
    today = datetime.datetime.now ().date ()
    session = request.session['count']
    emp = Employee.objects.get(user = request.user)
    att = Attendance.objects.filter (Q (employee = emp) & Q (date = today))
    print('session :--------',request.session.get('count'))

    if emp.id == id:
        print("In User profile")
        user = Attendance.objects.filter(employee_id = id).order_by('date')
        dwh = {}
        for i in user:
            t1 = i.chin
            t2 = i.chout
            if i.chout and i.chin:
                t1_datetime = datetime.datetime.combine(datetime.datetime.today (),t1)
                t2_datetime = datetime.datetime.combine(datetime.datetime.today (),t2)
                diff = t2_datetime - t1_datetime
                wh = int (diff.total_seconds () / 3600)
                dwh[i.id] = wh

            else:
                diff = 0
                wh = 0
                dwh[i.id] = wh

        twh = sum (dwh.values ())
        context = {
            'user': user,
            'name': request.user,
            'emp': emp,
            'dwh': dwh,
            'twh': twh,
            'session': session,
            'att': att,
        }
        return render(request, "userpersonal.html", context)
    else:
        return HttpResponseRedirect('/att_sys/login/')

    # add view using session

        # session = request.session['count']
        # emp = Employee.objects.get(user = request.user)
        # print(emp.user.role)
        # if request.method == "POST":
        #     fm = forms.Add(request.POST)
        #     print(fm)
        #
        #     if fm.is_valid():
        #         date = request.POST.get('date')
        #         chin = request.POST.get('chin')
        #         chout = request.POST.get('chout')
        #         if session == 0:
        #             user = Attendance(employee = emp,date = date,chin = chin)
        #             id = user.id
        #             print(id)
        #             message = "Checked in successfully!"
        #         else:
        #             att = Attendance.objects.last()
        #             id = att.id
        #             user = Attendance (id=id,employee = emp,date = date,chin= att.chin,chout = chout)
        #             message = "Checked out successfully!"
        #         user.save ()
        #         messages.success (request,message)
        #         return HttpResponseRedirect(f'/att_sys/userpersonal/{emp.id}',{'form': fm,'session':session})
        #
        # else:
        #     fm = forms.Add()
        #     print(fm)
        # return render (request,"add.html",{'name': request.user,'form': fm ,'emp':emp,'session':session})


# hr_profile without checkin implementation
        # @csrf_exempt
        # @login_required(login_url="/att_sys/login/")
        # def hr_profile(request):
        #     user = Employee.objects.exclude(id=1)
        #     designation = set()
        #     for i in user:
        #         designation.add(i.designation)
        #     designation = list(designation)
        #     emp = Employee.objects.get(user = request.user.id)
        #     print(user)
        #     print("In HR profile")
        #     context = {
        #         'user': user,
        #         'emp': emp,
        #         "designation":designation,
        #     }
        #     return render(request, "hrprofile.html", context)








