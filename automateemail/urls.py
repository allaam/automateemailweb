from django.contrib import admin
from django.urls import path
# from shceduleremail.views import dashboard, scheduler, detail_scheduler, form, GenerateReportLog ,delete_schedule, update_schedule, update, send_email_func, status_on, status_off, update_job, login_admin, logout_view, template_report, configure_template, delete_template, update_template_form, update_template
from shceduleremail.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_admin),
    path('logut-admin/', logout_view),
    # -------------------------------------------------------------------
    # url action pada laman dashboard
    # -------------------------------------------------------------------
    path('dashboard/', dashboard),
    path('scheduler/', scheduler),
    path('detail-scheduler/<int:running_id>', detail_scheduler),
    path('delete/<int:running_id>', delete_schedule),
    path('update/<int:running_id>', update_schedule),
    path('update_scheduler/<int:running_id>', update),
    path('status_update_on/<int:running_id>', status_on),
    path('status_update_off/<int:running_id>', status_off),
    path('form', form),
    path('update_job/<int:id_job>', update_job),
    # -------------------------------------------------------------------
    # url konfigurasi template
    # -------------------------------------------------------------------
    path('configure_template/', configure_template),
    path('template-report/', template_report),
    path('update_template_form/<int:id_template>/', update_template_form),
    path('update_template/<int:id_template>', update_template),
    path('delete_template/<int:id_template>', delete_template),
    # -------------------------------------------------------------------
    path('pdf_report/<int:id_log>/', GenerateReportLog.as_view()),
    path('excel_report/<int:id_log>/', export_excel),
    path('send_email/<int:id_job>', send_email_func),
    # ---------------------------------
    # commnet url
    # ---------------------------------
    path('status_update_on_job/<int:running_id>/<int:id_job>', status_on_job),
    path('status_update_off_job/<int:running_id>/<int:id_job>', status_off_job),
    # path('tambah-email/', add_email),
    # path('update_cabang/<str:kode_cabang>', update_cabang),
    # path('update_cabang_form/<str:kode_cabang>', update_cabang_form),
    # path('delete_cabang/<str:kode_cabang>', delete_cabang),
    # path('insert_email/', insert_email),
] 
