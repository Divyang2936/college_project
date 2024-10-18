from datetime import datetime,timedelta, timezone
import jwt
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm, YourPasswordResetForm,ForgotPasswordForm
from django.contrib.auth.hashers import make_password
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser,Role
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
import logging
from django.contrib.auth.views import PasswordResetConfirmView,PasswordResetDoneView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .utils import decrypt_file,generate_aes_key,encrypt_file
import base64
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .signals import *
# from django.views.decorators.cache import cache_page


logger=logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# file to handle the log
file_handler=logging.FileHandler('myform.log')
file_handler.setLevel(logging.DEBUG)

#formatter
# handler=handlers.TimedRotatingFileHandler(log_file,when='midnight',interval=1,backupCount=6)
# handler.suffix="%Y-%m-%d.log"
log_formatter='{asctime} ** {name} ** {levelname} ** {lineno} ** {message}'
formatter=logging.Formatter(log_formatter,style='{')
file_handler.setFormatter(formatter)

# add file handler to logger 
logger.addHandler(file_handler)


@csrf_exempt
def home(request):
    if request.method == 'POST':
        # Retrieve form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role_request = request.POST.get('role').lower()
        logger.debug(f"Name:{username}, Email:{email}, Password:{password}, Role:{role_request}")
        
        # Validate form data
        if not (username and email and password and role_request):
            # If any required field is missing, return an error message
            return render(request, 'myapp/signup.html', {'error_message': 'Please fill out all the fields.'})
        if CustomUser.objects.filter(email=email).exists():
            logger.warning('User with this email already exists')
            return render(request, 'myapp/signup.html', {'error_message': 'User with this email already exists.'})
        role = Role.objects.filter(role=role_request).first()
        print(role, 'llllllllllllllllllllllllll')

        # If the Role doesn't exist, create it
        if not bool(role):
            role = Role.objects.create(role=role_request)
           
            print('aaaayyuuuuuuuuu')
        
        # Hash the password before saving
        hashed_password = make_password(password)
        
        # Save the new user
        user = CustomUser.objects.create(
            username=username,
            email=email,
            password=hashed_password)
        role_value=role.role
        print(role_value,'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^>')
        # Assign role to the user
        user.role.add(role)
        logger.info('User data saved successfully')
        
        # Set a signed cookie with email (example)
        response = redirect('login')
         # Example of setting a cookie
        return response

    else:
        # Render the form for user input
        return render(request, 'myapp/signup.html')

@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not (email and password):
            messages.error(request, 'Please fill out all the fields.')
            return render(request, 'myapp/loginform.html', {'error_message': 'Please fill out all the fields.'})
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            logger.info("User authenticated successfully: %s", user)
            auth_login(request, user)
            
            # Fetch user's roles
            try:
                user_obj = CustomUser.objects.get(email=email)
                roles = user_obj.role.all()  
                print(roles, ')')
                # Assuming user has only one role, you can choose the first role
                role = roles.first() if roles.exists() else None
            except CustomUser.DoesNotExist:
                logger.warning("User with email %s does not exist.", email)
                return JsonResponse({'error_message': 'User does not exist.'}, status=404)
            
            # Generate JWT token and determine redirection URL based on user role
            jwt_token_str = generate_jwt_token(user)
            redirect_url = determine_redirect_url(user)
            
            # Set cookies for email and role
            response = JsonResponse({'token': jwt_token_str, 'redirect_url': redirect_url})
            response.set_signed_cookie('email', email, salt="email")
            if role:
                response.set_signed_cookie('role', role.role, salt="role")
            
            return response
        else:
            logger.warning("Authentication failed for email: %s", email)
            return JsonResponse({'error_message': 'Invalid credentials.'}, status=401)
 
    return render(request, 'myapp/loginform.html')

def generate_jwt_token(user):
    # Retrieve user's roles
    roles = user.role.all()
    # Assume the user has only one role, otherwise handle multiple roles accordingly
    if roles:
        role = roles[0].role  # Get the role name
    else:
        role = "Default"  # Set a default role if the user has no roles
    
    # Define payload for JWT token
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=1)  # Set expiration time
    }
    logger.info(payload)

    # Generate JWT token with custom payload and secret key
    jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    logger.info(jwt_token)

    return jwt_token
def determine_redirect_url(user):
    for role in user.role.all():
        if role.role == 'hod':  # Check if role is 'Hod'
            logger.info("user is redirect to hod dashboard")
            return reverse('admin_home', kwargs={'user_id': user.id})
        elif role.role == 'teacher':  # Check if role is 'Teacher'
            logger.info("user is redirect to teacher dashboard")
            return reverse('staff_home', kwargs={'user_id': user.id})
        elif role.role == 'student':  # Check if role is 'Student'
            logger.info("user is redirect to student dashboard")
            return reverse('student_home', kwargs={'user_id': user.id})

# def default_dashboard(request):
#     # Your logic for the default dashboard view goes here
#     return render(request, 'myapp/default_dashboard.html')


@csrf_exempt
def logout(request):
    user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
    auth_logout(request)
    
    # Create a response for the logout action
    response = render(request, 'myapp/logout.html')
    
    # Expire the cookies
    response.delete_cookie('email')
    response.delete_cookie('role')
 
    return response


# @csrf_exempt
# def document_dashboard(request, user_id):
#     user = CustomUser.objects.get(pk=user_id)
#     documents = Document.objects.filter(owner_id=user_id)

#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = request.FILES['encrypted_file']
#             file_data = uploaded_file.read()
            
#             encryption_key = generate_aes_key()  # Generate the encryption key
#             encrypted_data = encrypt_file(file_data, encryption_key)
            
#             document = form.save(commit=False)
#             document.owner_id = user_id
#             document.encrypted_data = encrypted_data
#             document.encryption_key = encryption_key  # Save the key
#             document.save()
            
#             return redirect('document_dashboard', user_id=user_id)
#     else:
#         form = DocumentForm()

#     context = {
#         'form': form,
#         'user_id': user_id,
#         'documents': documents,
#         'username': user.username
#     }

#     return render(request, 'myapp/document_dashboard.html', context)

# @csrf_exempt
# def download_decrypted_document(request, document_id):
#     try:
#         document = Document.objects.get(id=document_id)
#         encrypted_data = document.encrypted_data
        
#         # Decoding the encryption key when retrieving it
#         # encryption_key = base64.urlsafe_b64decode(document.encryption_key)
#         # print(encryption_key,'::::')
        
#         print(document.encryption_key,'::::::')
#         decrypted_data = decrypt_file(encrypted_data, document.encryption_key)

#         response = HttpResponse(decrypted_data, content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{document.encrypted_file}"'
        
#         return response
#     except:
#         import traceback
#         print(traceback.format_exc())
#     # except Document.DoesNotExist:
#         # return HttpResponse("Document not found", status=404)
#     # except ValueError as ve:
#         return HttpResponse(f"Error: {traceback.format_exc()}", status=500)
#     # except Exception as e:
#     #     return HttpResponse(f"Error: {str(e)}", status=500)
# # Your existing view function for uploading documents
# @csrf_exempt
# def upload_document(request, user_id):
#     user = CustomUser.objects.get(pk=user_id)
#     documents = Document.objects.filter(owner_id=user_id)

#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = request.FILES['encrypted_file']
#             file_data = uploaded_file.read()
            
#             encryption_key = generate_aes_key()  # Generate the encryption key
            
#             encrypted_data = encrypt_file(file_data, encryption_key)
#             # print(encrypted_data,'enc dta',base64.b64encode(encrypted_data),'key',encryption_key,'after encode',base64.b64encode(encryption_key))
#             document = form.save(commit=False)
#             document.owner_id = user_id
#             document.encrypted_data = encrypted_data
#             document.encryption_key = encryption_key.decode()  # Save the key
#             document.save()
            
#             return redirect('document_dashboard', user_id=user_id)
#     else:
#         form = DocumentForm()

#     context = {
#         'form': form,
#         'user_id': user_id,
#         'documents': documents,
#         'username': user.username
#     }

#     return render(request, 'myapp/upload_document.html', context)

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                # Generate uidb64 and token
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
 
                # Construct reset URL
                reset_url = request.build_absolute_uri(
                    f"/reset-password/{uid}/{token}/"
                )
 
                # Render email template
                email_subject = 'Reset Your Password'
                email_body = render_to_string('myapp/reset_password_email.html', {'reset_url': reset_url})
 
                # Send email
                send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [email])
 
                # Redirect to password reset done page
                return redirect('password_reset_done')
            else:
                # Handle case where email is not found
                pass
    else:
        form = ForgotPasswordForm()
    return render(request, 'myapp/forgot_password.html', {'form': form})
 
 
 
 
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    A custom password reset confirm view that uses the custom password reset form.
    """
 
    form_class = SetPasswordForm
    template_name = 'myapp/reset_password_confirm.html'  # Customize as needed
    success_url = '/password-reset-complete/'  # Customize as needed
 
    def form_valid(self, form):
        form.save()
        # You can add any additional logic here after the form is successfully submitted
        return super().form_valid(form)
 
class CustomPasswordResetView(auth_views.PasswordResetView):
    """
    A custom password reset view that uses the custom password reset form.
    """
 
    form_class = CustomPasswordResetForm
    template_name = 'myapp/forgot_password.html'  # Customize as needed
    email_template_name = 'myapp/reset_password_email.html'  # Customize as needed
    success_url = reverse_lazy('password_reset_done')  # Customize as needed
 

# If you need any additional context data for the template, you can override the get_context_data method
class CustomPasswordResetDoneView(PasswordResetDoneView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here if needed
        return context
 
# views.py
 

def reset_password(request, uidb64, token):


    if request.method == 'POST':
        # Assuming you have a form for password reset
        form = YourPasswordResetForm(request.POST)
        if form.is_valid():
            # Form is valid, reset password and log the user in
            form.save()  # Handle password reset logic in your form
            # Redirect the user to the dashboard or wherever appropriate
            return redirect('dashboard')
    else:
        # Decode the uidb64 and get the user
        try:
            uid = force_bytes(base64.urlsafe_b64decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
 
        # Check if the user and token are valid
        if user is not None and default_token_generator.check_token(user, token):
            # User and token are valid, render the password reset form
            form = YourPasswordResetForm()
            return render(request, 'myapp/reset_password.html', {'form': form})
        else:
            # Invalid user or token, handle accordingly (e.g., display an error message)
            return render(request, 'myapp/invalid_reset_link.html')
        

