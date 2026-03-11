from django.urls import path
from . import views
from timetabling import views as timetabling_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('force-password-change/', views.force_password_change, name='force_password_change'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/generate/', timetabling_views.generate_timetable_view, name='generate_timetable'),
    path('dashboard/admin/publish/', timetabling_views.publish_timetable_view, name='publish_timetable'),
    path('dashboard/admin/master-timetable/', timetabling_views.master_timetable_view, name='master_timetable_view'),
    path('dashboard/lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('dashboard/lecturer/report-missed/', views.report_missed_class, name='report_missed_class'),
    path('dashboard/lecturer/set-availability/', views.set_availability, name='set_availability'),
    path('dashboard/lecturer/request-makeup/<int:report_id>/', views.request_makeup_session, name='request_makeup_session'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/student/profile/', views.student_profile_update, name='student_profile_update'),
    path('dashboard/student/export/', views.export_timetable, name='export_timetable'),
    path('notification/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
]
