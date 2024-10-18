import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.contrib.auth.hashers import make_password
from .forms import *
from .models import *

@csrf_exempt
def admin_home(request,user_id):
    user = get_object_or_404(CustomUser, id=user_id)
   
    total_staff = CustomUser.objects.all().count()
    total_students = CustomUser.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_course = Course.objects.all().count()
    # received_cookies = request.COOKIES
    # print("Received Cookies:", received_cookies)
    # print("Role:", role)
    subject_list = []
    for subject in subjects:
        
        subject_list.append(subject.name[:7])

    context = {
        'user_id':user_id,
        'user': user,
        'page_title': "Administrative Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        
      

    }
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request,user_id):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'user_id':user_id,'form': form, 'page_title': 'Add Staff'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                username = email
                user = CustomUser.objects.create_user(
                username=username ,email=email, password=password,first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.course = course

                user.role.set([5])  # Assuming 'student' is the role you want to assign

                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff', kwargs={'user_id': user_id}))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request,user_id):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'user_id':user_id,'form': student_form, 'page_title': 'Add Student'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            address = student_form.cleaned_data.get('address')
            email = student_form.cleaned_data.get('email')
            gender = student_form.cleaned_data.get('gender')
            password = student_form.cleaned_data.get('password')
            course = student_form.cleaned_data.get('course')
            session = student_form.cleaned_data.get('session')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                # Generate a unique username
                username = email  # You can use email as the username for simplicity

                # Create the user with a unique username
                user = CustomUser.objects.create_user(
                username=username, email=email, password=password, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.session = session
                user.course = course

                # Assign role using set() method
                user.role.set([7])  # Assuming 'student' is the role you want to assign

                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_student', kwargs={'user_id': user_id}))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_student_template.html', context)


def add_course(request,user_id):
    form = CourseForm(request.POST or None)
    context = {
        'user_id':user_id,
        'form': form,
        'page_title': 'Add Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course()
                course.name = name
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_course', kwargs={'user_id': user_id}))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_course_template.html', context)


def add_subject(request,user_id):
    form = SubjectForm(request.POST or None)
    context = {
        'user_id':user_id,
        'form': form,
        'page_title': 'Add Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            user = CustomUser.objects.get(id=user_id)
            try:
                subject = Subject()
                subject.name = name
                subject.user = user
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_subject',kwargs={'user_id': user_id}))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_subject_template.html', context)

@csrf_exempt
def manage_staff(request,user_id):
    allStaff = CustomUser.objects.filter(role__role = 'teacher')
    context = {
        'user_id':user_id,
        'allStaff': allStaff,
        'page_title': 'Manage Staff'
    }
    return render(request, "hod_template/manage_staff.html", context)

@csrf_exempt
def manage_student(request,user_id):
    students = CustomUser.objects.filter(role__role='student').values('id', 'first_name', 'last_name', 'email')
    context = {
        'user_id':user_id,
        'students': students,
        'page_title': 'Manage Students'
    }
    return render(request, "hod_template/manage_student.html", context)
def manage_course(request):
    courses = Course.objects.all()
    context = {
      
        'courses': courses,
        'page_title': 'Manage Courses'
    }
    return render(request, "hod_template/manage_course.html", context)


def manage_subject(request):
    subjects = Subject.objects.all()
    users = CustomUser.objects.all().values('id')
    user_ids = [user['id'] for user in users]
    context = {
        'user_ids': user_ids,
        'subjects': subjects,
        'page_title': 'Manage Subjects'
    }
    return render(request, "hod_template/manage_subject.html", context)


def edit_staff(request,user_id):
    staff = get_object_or_404(CustomUser, id=user_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'staff_id': user_id,
        'form': form,
        'page_title': 'Edit Staff'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
           
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                staff.email = email
                if password != None:
                    staff.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    staff.profile_pic = passport_url
                
                staff.first_name = first_name
                staff.last_name = last_name
                staff.gender = gender
                staff.address = address
                staff.course = course
                staff.save()
                
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[user_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, user_id):
    student = get_object_or_404(CustomUser, id=user_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'student_id': user_id,
        'form': form,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        print('post ma aiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
        if form.is_valid():
            print('pan valid naiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    student.profile_pic = passport_url
                
                student.email = email
                if password != None:
                    student.set_password(password)
                student.first_name = first_name
                student.last_name = last_name
                student.session = session
                student.gender = gender
                student.address = address
                student.course = course
                student.save()
                
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[user_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            print(form.errors)
            messages.error(request, "Please Fill Form Properly!")
    return render(request, "hod_template/edit_student_template.html", context)

def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)

def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    
    # Retrieve users with the role 'teacher'
    teacher_users = CustomUser.objects.filter(role__role='teacher')
    print(teacher_users,'******************************')
    context = {
        'form': form,
        'subject_id': subject_id,
        'teacher_users': teacher_users,
        'page_title': 'Edit Subject'
    }
    
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            user = form.cleaned_data.get('user')
            
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.name = name
                subject.user = user
                subject.course = course
                subject.save()
                
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    
    return render(request, 'hod_template/edit_subject_template.html', context)

def add_session(request,user_id):
    form = SessionForm(request.POST or None)
    context = {'user_id':user_id, 'form': form, 'page_title': 'Add Batch'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Batch Created")
                return redirect(reverse('add_session',kwargs={'user_id': user_id}))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Batch'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Batch'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Batch Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Batch Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt

def admin_view_profile(request,user_id):
    print("=================")
    user = get_object_or_404(CustomUser, id=user_id)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=user)
   
  
    context = {
        'form': form,
        'user_id': user_id,
        'page_title': 'View/Edit Profile',
       
    }
    
    print(user_id, 'KKKKKKKKKKKkk')
    if request.method == 'POST':
        print('postttttttttttttttttttttttttttttttttttttttttt')
        try:
            if form.is_valid():
                print('validddddddddddddddddddddddddddddddddddddddddddddddddddddd')
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = user
                if password:  # If password is provided, hash it
                    hashed_password = make_password(password)
                    custom_user.password = hashed_password
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                
                custom_user.first_name = first_name
            
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile',kwargs={'user_id': user.id}))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    print('getttttttttttttttttttttttttttttttttttttttttt')
    return render(request, "hod_template/admin_view_profile.html", context)

@csrf_exempt
def admin_notify_staff(request, user_id):
    # Assuming you want to filter by the role name 'teacher'
    staff = CustomUser.objects.filter(role__role='teacher')

    context = {
        'user_id':user_id,
        'page_title': "Send Notifications To Staff",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)

def admin_notify_student(request,user_id):
    student = CustomUser.objects.filter(role__role='student')
    context = {
        'user_id':user_id,
        'page_title': "Send Notifications To Students",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request,user_id):
    user_id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(CustomUser,id=user_id)
    fcm_token = student.fcm_token
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('student_view_notification',kwargs={'user_id': user_id}),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")
@csrf_exempt
def send_staff_notification(request,user_id):
    user_id = request.POST.get('id')
    # Get the CustomUser object with the given ID
    user = get_object_or_404(CustomUser, id=user_id)
    # Fetch the fcm_token associated with the user
    fcm_token = user.fcm_token
    message = request.POST.get('message')
    
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('staff_view_notification', kwargs={'user_id': user_id}),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        print(headers)
        data = requests.post(url, data=json.dumps(body), headers=headers)
        print(data)
        # Check if the request was successful (status code 200)
        if data.status_code == 200:
            print('perfect lalal')
            # Save the notification in the database
            notification = NotificationStaff(staff=user, message=message)
            notification.save()
            return HttpResponse("True")
        elif data.status_code == 401:
            print('ej chheeeeeeee')
            # Unauthorized - FCM server key may be incorrect or unauthorized
            return HttpResponse("Unauthorized: Please check FCM server key and project settings.")
        else:
            # Other error occurred
            return HttpResponse("Error: Failed to send notification.")
    
    except Exception as e:
        # Log the exception for debugging purposes
        print('Exception:', e)
        return HttpResponse("False")

def delete_staff(request, user_id):
    staff = get_object_or_404(CustomUser, id=user_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff',kwargs={'user_id':user_id}))


def delete_student(request, user_id):
    student = get_object_or_404(CustomUser, id=user_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse('manage_student',kwargs={'user_id':user_id}))


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_course'))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Batch deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this Batch. Please move them to another Batch.")
    return redirect(reverse('manage_session'))
