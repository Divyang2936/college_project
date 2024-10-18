from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser, Session , Subject,Document
from django import forms
from django.contrib.auth.forms import UserChangeForm, PasswordResetForm
from .models import CustomUser,Document
from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .models import CustomUser
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import *
from django.forms.widgets import DateInput
class UserDetailsForm(UserChangeForm):
    password = None
    class Meta:
        model = CustomUser
        fields = ['username','first_name','last_name','surname','email','gender','date_joined','last_login','profile_pic',]  


# class SessionForm(UserChangeForm):
#     password = None
#     class Meta:
#         model = Session
#         fields = ['start_year', 'end_year']


# class SubjectForm(UserChangeForm):
#     password = None
#     class Meta:
#         model = Subject
#         fields = ['name', 'course']

class DocumentForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(queryset=CustomUser.objects.filter(role__role='teacher'))

    class Meta:
        model = Document
        fields = ['title', 'encrypted_file', 'teacher']
    
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Email')
 
 
class CustomPasswordResetForm(PasswordResetForm):
    """
    A custom password reset form that sends an email with a password reset link.
    """
 
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a Django email using Django's SMTP mail sending function.
        """
        subject = self.format_email_subject(subject_template_name)
        # Email body
        email_body = render_to_string(email_template_name, context)
        # Send email using Django's send_mail function
        send_mail(subject, email_body, from_email, [to_email], html_message=html_email_template_name)
 
    def save(self, domain_override=None, email_template_name='myapp/reset_password_email.html',
             subject_template_name='myapp/password_reset_subject.txt',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None, extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the user.
        """
        email = self.cleaned_data["email"]
        active_users = CustomUser._default_manager.filter(email__iexact=email, is_active=True)
        for user in active_users:
            # Generate uidb64 and token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
 
            # Construct reset URL
            if domain_override is not None:
                site_domain = domain_override
            else:
                site_domain = request.get_host()
            reset_url = f"http://{site_domain}/reset-password/{uid}/{token}/"
 
            # Email context
            context = {
                'email': email,
                'domain': site_domain,
                'site_name': 'Your Site',
                'uid': uid,
                'user': user,
                'token': token,
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                context.update(extra_email_context)
 
            # Send email
            self.send_mail(
                subject_template_name, email_template_name, context, from_email, email,
                html_email_template_name=html_email_template_name,
            )
        return email
 
class YourPasswordResetForm(SetPasswordForm):
    """
    A custom password reset form for setting a new user password.
    """
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the form if needed
        # For example, you can add CSS classes to form fields
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

class CustomUserForm(FormSettings): 
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
   
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance')
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = getattr(instance, field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

            # Prepopulate role field if user is already assigned a role
            if instance.role.exists():
                self.fields['role'].initial = instance.role.first().role

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender', 'password', 'profile_pic', 'role']

class StudentForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].required = False
    class Meta(CustomUserForm.Meta):
        model = CustomUser
        fields = CustomUserForm.Meta.fields + ['course', 'session']
 

class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)
   
    class Meta(CustomUserForm.Meta):
        model = CustomUser
        fields = CustomUserForm.Meta.fields

class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].required = False
    class Meta(CustomUserForm.Meta):
        model = CustomUser
        fields = CustomUserForm.Meta.fields + \
            ['course' ]


class CourseForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Course


# class SubjectForm(FormSettings):

#     def __init__(self, *args, **kwargs):
#         super(SubjectForm, self).__init__(*args, **kwargs)

#     class Meta:
#         model = Subject
#         fields = ['name', 'user','course']
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'course', 'user']
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter queryset for user field to only include teachers
        self.fields['user'].queryset = CustomUser.objects.filter(role__role='teacher')


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }



class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = CustomUser
        fields = CustomUserForm.Meta.fields 


class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Session Year", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'test', 'exam']
