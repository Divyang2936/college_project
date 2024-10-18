import base64
import os
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from django.contrib.auth.models import BaseUserManager
from .utils import generate_aes_key
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
class Role(models.Model):
    role_choices = [
    ('1', 'Hod'),
    ('2', 'Teacher'),
    ('3', 'Student'),
]
    role=models.CharField(choices=role_choices,max_length=20)
    class Meta:
        managed=True
class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)
    class Meta:
        managed=True 

class Course(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


       
class CustomUser(AbstractUser):
    gender_choices=[
        ('F','Female'),
        ('M','Male'),
        ('O','Other'),
    ]
    email = models.EmailField(unique=True)  # Ensure email is unique for each user
    USERNAME_FIELD = 'email'  # Use email as the unique identifier for authentication
    REQUIRED_FIELDS = []  # Remove 'email' from REQUIRED_FIELDS since it's already the USERNAME_FIELD
    fcm_token = models.TextField(default="") 
    surname=models.CharField(max_length=20)
    role = models.ManyToManyField(Role,related_name='users')
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)
    gender=models.CharField(max_length=10,choices=gender_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions')
    class Meta:
        managed=True
    objects = CustomUserManager()   
    
  

class Subject(models.Model):
    name = models.CharField(max_length=120)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    encrypted_file = models.FileField(upload_to='') 
    encryption_key = models.TextField(blank=True)
    encrypted_data = models.BinaryField(default=b'')
    visible_to_staff = models.BooleanField(default=False)
    visible_to_admin = models.BooleanField(default=False) 
    teacher = models.ForeignKey(CustomUser, related_name='documents_teacher', on_delete=models.CASCADE, null=True, blank=True)
   
    def save(self, *args, **kwargs):
        # Generate encryption key if not provided
        if not self.encryption_key:
            self.encryption_key = base64.b64encode(generate_aes_key()).decode()
       
            super().save(*args, **kwargs)
            
            # Get the role of the owner
            owner_role = self.owner.role.first()
            
            # Check if the owner is a teacher
            if owner_role and owner_role.role == 'teacher':
                self.teacher = self.owner
                self.save(update_fields=['teacher'])  # Save only the 'teacher' field
        else:
            super().save(*args, **kwargs)
        
    class Meta:
        managed=True  


class NotificationStaff(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class NotificationStudent(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StudentResult(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

