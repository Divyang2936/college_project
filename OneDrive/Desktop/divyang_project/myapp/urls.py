from django.urls import path

from myapp.EditResultView import EditResultView
from . import hod_views,staff_views,student_views
from .views import home, login, logout,forgot_password,PasswordResetDoneView,CustomPasswordResetConfirmView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
   
   
#      path('document_dashboard/<int:user_id>/',document_dashboard, name='document_dashboard'),
      path('student/document/<int:document_id>/delete/', student_views.delete_document, name='delete_document'),
   path(' download/<int:document_id>/', student_views.download_decrypted_document, name='download_decrypted_document'),
#    path('upload_document/<int:user_id>/', upload_document, name='upload_document'),
   path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    path('password-reset-done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
   

#hod urls
   
    path("admin/home/<int:user_id>/", hod_views.admin_home, name='admin_home'),  
    path("staff/add/<int:user_id>/", hod_views.add_staff, name='add_staff'),
    path("course/add/<int:user_id>/", hod_views.add_course, name='add_course'),
    path("send_student_notification/<int:user_id>/", hod_views.send_student_notification,
         name='send_student_notification'),
    path('send_staff_notification/<int:user_id>/', hod_views.send_staff_notification, name='send_staff_notification'),

    path("add_session/<int:user_id>/", hod_views.add_session, name='add_session'),
    path("admin_notify_student/<int:user_id>/", hod_views.admin_notify_student,
         name='admin_notify_student'),
    path("admin_notify_staff/<int:user_id>/", hod_views.admin_notify_staff,
         name='admin_notify_staff'),
     path('admin/view/profile/<int:user_id>/', hod_views.admin_view_profile, name='admin_view_profile'),
    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("session/manage/", hod_views.manage_session, name='manage_session'),
    path("session/edit/<int:session_id>",
         hod_views.edit_session, name='edit_session'),
    
    path("student/add/<int:user_id>/", hod_views.add_student, name='add_student'),
    path("subject/add/<int:user_id>/", hod_views.add_subject, name='add_subject'),
    path("staff/manage/<int:user_id>/", hod_views.manage_staff, name='manage_staff'),
    path("student/manage/<int:user_id>/", hod_views.manage_student, name='manage_student'),
    path("course/manage/", hod_views.manage_course, name='manage_course'),
    path("subject/manage/", hod_views.manage_subject, name='manage_subject'),
    path("staff/edit/<int:user_id>/", hod_views.edit_staff, name='edit_staff'),
    path("staff/delete/<int:user_id>/",
         hod_views.delete_staff, name='delete_staff'),

    path("course/delete/<int:course_id>/",
         hod_views.delete_course, name='delete_course'),

    path("subject/delete/<int:subject_id>/",
         hod_views.delete_subject, name='delete_subject'),

    path("session/delete/<int:session_id>/",
         hod_views.delete_session, name='delete_session'),

    path("student/delete/<int:user_id>/",
         hod_views.delete_student, name='delete_student'),
    path("student/edit/<int:user_id>/",
         hod_views.edit_student, name='edit_student'),
    path("course/edit/<int:course_id>/",
         hod_views.edit_course, name='edit_course'),
    path("subject/edit/<int:subject_id>/",
         hod_views.edit_subject, name='edit_subject'),

     #student
      
    path("student/home/<int:user_id>/", student_views.student_home, name='student_home'),
 
    path("student/view/profile/<int:user_id>/", student_views.student_view_profile,
         name='student_view_profile'),
    path("student/fcmtoken/", student_views.student_fcmtoken,
         name='student_fcmtoken'),
    path("student/view/notification/<int:user_id>/", student_views.student_view_notification,
         name="student_view_notification"),
    path('student/view/result/<int:user_id>/', student_views.student_view_result,
         name='student_view_result'),
     path('student/document/<int:user_id>/', student_views.document_upload_student, name='document_upload_student'),
     
     #staff
      path('document-upload-teacher/<int:user_id>/', staff_views.document_upload_teacher, name='document_upload_teacher'),
     path("staff/home/<int:user_id>/", staff_views.staff_home, name='staff_home'),
    path("staff/view/profile/<int:user_id>/", staff_views.staff_view_profile,
         name='staff_view_profile'),
    path("staff/get_students/", staff_views.get_students, name='get_students'),
    path("staff/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path("staff/view/notification/<int:user_id>/", staff_views.staff_view_notification,
         name="staff_view_notification"),
   path('staff/result/add/<int:user_id>/', staff_views.staff_add_result, name='staff_add_result'),
    path("staff/result/edit/<int:user_id>/", EditResultView.as_view(),
         name='edit_student_result'),
    path('staff/result/fetch/<int:user_id>/', staff_views.fetch_student_result,
         name='fetch_student_result'),

]



