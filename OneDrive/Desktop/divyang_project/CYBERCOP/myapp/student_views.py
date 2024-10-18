import json
import math
from datetime import datetime
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *
from .utils import decrypt_file,generate_aes_key,encrypt_file
def student_home(request, user_id):
    student = CustomUser.objects.get(id=user_id)  # Assuming user_id is the ID of the student
    courses = Course.objects.filter(customuser=student)
    total_subject = Subject.objects.filter(course__in=courses).count()
    subjects = Subject.objects.filter(course__in=courses)
    print(total_subject)
    context = {
        'user_id': user_id,
        'total_subject': total_subject,
        'subjects': subjects,
        'page_title': 'Student Homepage'
    }
    return render(request, 'student_template/home_content.html', context)

# @csrf_exempt
# def document_handler(request, user_id):
#     try:
#         user = CustomUser.objects.get(pk=user_id)
#         documents = Document.objects.filter(owner_id=user_id)

#         if request.method == 'POST':
#             form = DocumentForm(request.POST, request.FILES)
#             if form.is_valid():
#                 uploaded_file = request.FILES['encrypted_file']
#                 file_data = uploaded_file.read()
#                 course = user.course
                
#                 # Check if the course is None
#                 if course is None:
#                     return HttpResponse("Error: User is not associated with any course", status=400)
#                 encryption_key = generate_aes_key()  # Generate the encryption key
                
#                 encrypted_data = encrypt_file(file_data, encryption_key)
#                 document = form.save(commit=False)
#                 document.owner_id = user_id
#                 document.course = course
#                 document.encrypted_data = encrypted_data
#                 document.encryption_key = encryption_key.decode()  # Save the key
#                 # document.name=name
#                 document.save()
                
#                 return redirect('document_handler', user_id=user_id)
#         else:
#             form = DocumentForm()

#         context = {
#             'form': form,
#             'user_id': user_id,
#             'documents': documents,
#             'username': user.username,
#             'page_title': ' Upload/Download Documents'
#         }

#         return render(request, 'student_template/document_handler.html', context)

#     except Exception as e:
#         return HttpResponse(f"Error: {str(e)}", status=500)

# @csrf_exempt
# def download_decrypted_document(request, document_id):
#     try:
#         document = Document.objects.get(id=document_id)
#         encrypted_data = document.encrypted_data
#         decrypted_data = decrypt_file(encrypted_data, document.encryption_key)

#         response = HttpResponse(decrypted_data, content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{document.encrypted_file}"'
        
#         return response
#     except Document.DoesNotExist:
#         return HttpResponse("Document not found", status=404)
#     except Exception as e:
#         return HttpResponse(f"Error: {str(e)}", status=500)
@csrf_exempt
def document_upload_student(request, user_id):
    try:
        user = CustomUser.objects.get(pk=user_id)
        teachers = CustomUser.objects.filter(role__role__in=['teacher'])
        documents = Document.objects.filter(owner_id=user_id)
        print(user_id)
        print(documents)
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES['encrypted_file']
                file_data = uploaded_file.read()
                course = user.course
                print(form.errors)
                if not course:
                    return HttpResponse("Error: User is not associated with any course", status=400)
                
                encryption_key = generate_aes_key()
                encrypted_data = encrypt_file(file_data, encryption_key)
                
                document = form.save(commit=False)
                # document = Document()
                document.owner_id = user_id
                document.course = course
                document.encrypted_data = encrypted_data
                document.encryption_key = encryption_key.decode()
                print(document, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                # print(document.encrypted_data)
                # Check if a teacher is selected
                if 'teacher' in request.POST: 
                    print("if ma ayu chhe bhai ha") # Corrected to 'teacher' instead of 'teachers'
                    teacher_id = request.POST['teacher'] 
                    print(teacher_id) # Corrected to 'teacher' instead of 'teachers'
                    teacher = CustomUser.objects.get(pk=teacher_id)
                    print(teacher)
                    print(document, 'lllllllllllllllllllllllllllllll')
                    document.teacher = teacher
                
                document.save()
                
            return redirect('document_upload_student', user_id=user_id)
            
        else:
            print('')
            form = DocumentForm()

        context = {
            'form': form,
            'user_id': user_id,
            'documents': documents,
            'teachers': teachers,
            'username': user.username,
            'page_title': 'Upload/Download Documents'
        }

        return render(request, 'student_template/document_handler.html', context)

    except CustomUser.DoesNotExist:
        return HttpResponse("Error: User not found", status=404)
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
def delete_document(request, document_id):
    try:
        print("try ma ayu")
        # Check if the document exists
        document = get_object_or_404(Document, id=document_id)
        
        # Delete the document
        document.delete()
        
        # Redirect to a success page
        return redirect('document_upload_student')  # Replace 'success_url' with the appropriate URL name
        
    except Document.DoesNotExist:
        # Handle the case where the document does not exist
        return HttpResponse("Document not found", status=404)
    
    except Exception as e:
        # Handle other exceptions
        return HttpResponse(f"Error: {str(e)}", status=500)

def student_view_profile(request,user_id):
    student = get_object_or_404(CustomUser, id=user_id)
    form = StudentEditForm(request.POST or None, request.FILES or None,
                           instance=student)
    context = {'user_id': user_id,'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = student
                if password != None:
                    admin.set_password(password)
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
                student.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('student_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "student_template/student_view_profile.html", context)


@csrf_exempt
def student_fcmtoken(request):
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def student_view_notification(request,user_id):
    student = get_object_or_404(CustomUser, id=user_id)
    notifications = NotificationStudent.objects.filter(student=student)
    context = {
        'user_id': user_id,
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_view_result(request,user_id):
    student = get_object_or_404(CustomUser, id=user_id)
    results = StudentResult.objects.filter(student=student)
    context = {
        'user_id': user_id,
        'results': results,
        'page_title': "View Results"
    }
    return render(request, "student_template/student_view_result.html", context)
