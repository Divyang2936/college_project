import json
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .utils import decrypt_file,generate_aes_key,encrypt_file
from .forms import *
from .models import *
from django.contrib.auth.hashers import make_password
@csrf_exempt
def staff_home(request,user_id):
    staff = CustomUser.objects.filter(role__role='teacher')
    print(staff)
    
# Assuming 'staff' is a queryset of teachers
    courses_of_teachers = staff.values_list('course', flat=True)
    print(courses_of_teachers)
# Count total students enrolled in the courses of teachers
    total_students = CustomUser.objects.filter(
    Q(course__in=courses_of_teachers) & Q(role__role='student')).count()
    print(total_students)
    subjects=Subject.objects.all()
    total_subject = subjects.count()
    print(total_subject)
    subject_list = [subject.name for subject in subjects]
    print(subject_list,'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

    context = {
        'user_id':user_id,
        'page_title': 'Staff Panel',
        'total_students': total_students,
        'total_subject': total_subject,
        'subject_list': subject_list,
       
       
    }
    return render(request, 'staff_template/home_content.html', context)

@csrf_exempt
def get_students(request):
    try:
        subject_id = request.POST.get('subject')
        session_id = request.POST.get('session')
        
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        
        students = CustomUser.objects.filter(
            course_id=subject.course.id, session_id=session.id)  # Adjust this filtering based on your models
        print(students,'333333#####################################3')
        student_data = {}
        
        for student in students:
            data = {
                "id": student.id,
                "name": f"{student.last_name} {student.first_name}"
            }
            student_data.update({student.id: data})
        print(student_data)
        return JsonResponse(student_data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def staff_view_profile(request,user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    form = StaffForm(request.POST or None, request.FILES or None,instance=user)
    context = {'user_id':user_id,'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        print('helooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = user
                if password:  # If password is provided, hash it
                    hashed_password = make_password(password)
                    admin.password = hashed_password
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile',kwargs={'user_id': user_id}), context)
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)
@csrf_exempt
def document_upload_teacher(request, user_id):
    try:
        teacher = CustomUser.objects.get(pk=user_id)
        documents_received = Document.objects.filter(teacher=teacher)
        
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES['encrypted_file']
                file_data = uploaded_file.read()
                
                encryption_key = generate_aes_key()
                encrypted_data = encrypt_file(file_data, encryption_key)
                
                document = form.save(commit=False)
                document.owner = teacher  # Assign the teacher as the owner
                document.encrypted_data = encrypted_data
                document.encryption_key = encryption_key.decode()
                document.save()
                
                return redirect('document_upload_teacher', user_id=user_id)
        else:
            form = DocumentForm()

        context = {
            'form': form,
            'user_id': user_id,
            'documents_received': documents_received,
            'username': teacher.username,
            'page_title': 'Upload/Review Documents'
        }

        return render(request, 'staff_template/upload_review_documents.html', context)

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

def download_decrypted_document(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
        encrypted_data = document.encrypted_data
        decrypted_data = decrypt_file(encrypted_data, document.encryption_key)

        response = HttpResponse(decrypted_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{document.encrypted_file}"'
        
        return response
    except Document.DoesNotExist:
        return HttpResponse("Document not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request,user_id):
    staff = get_object_or_404(CustomUser,id=user_id)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'user_id':user_id,
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)
@csrf_exempt

def staff_add_result(request, user_id):
    # Retrieve the current user
    current_user = request.user
    
    # Ensure that the current user is a teacher
    teacher = get_object_or_404(CustomUser, id=current_user.id, role__role='teacher')

    # Retrieve subjects assigned to the teacher
    subjects = Subject.objects.filter(user=teacher)
    sessions = Session.objects.all()
    
    # Prepare the context data
    context = {
        'user_id': user_id,
        'page_title': 'Result Upload',
        'subjects': subjects,
        'sessions': sessions
    }

    # Handle POST request for adding student results
    if request.method == 'POST':
        try:
            # Get the list of student IDs
            student_id = request.POST.get('student_list')
            subject_id = request.POST.get('subject')
            test = request.POST.get('test')
            exam = request.POST.get('exam')

            # Retrieve student and subject objects
            student = get_object_or_404(CustomUser, id=student_id, role__role='student')
            subject = get_object_or_404(Subject, id=subject_id)

            # Update or create student result
            data, created = StudentResult.objects.get_or_create(
                student=student, subject=subject,
                defaults={'test': test, 'exam': exam}
            )

            if not created:
                # Update existing result
                data.exam = exam
                data.test = test
                data.save()
                messages.success(request, "Scores Updated")
            else:
                # Save new result
                messages.success(request, "Scores Saved")

        except Exception as e:
            messages.warning(request, f"Error Occurred While Processing Form: {e}")

    # Render the template with the context
    return render(request, "staff_template/staff_add_result.html", context)

@csrf_exempt
def fetch_student_result(request,user_id):
    students = CustomUser.objects.filter(role__role='student').values('id', 'username')
    print(students,'ttttttttttttt')
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    try:
        print('11111111111111111111111111111111111')
        subject_id = request.POST.get('subject')
        print(subject_id,'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        student_id = request.POST.get('student')
        print(student_id,'444$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        student = get_object_or_404(CustomUser, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        result = StudentResult.objects.get(student=student, subject=subject)
        print(result)
        result_data = {
            'user_id':user_id,
            'students':students,
            'exam': result.exam,
            'test': result.test
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        print('e ayo pan exception')
        return HttpResponse('False')
