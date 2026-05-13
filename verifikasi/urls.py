from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_ijazah, name="home"),
    path("upload-single/", views.upload_single, name="upload_single"),

    path("login/", views.login_admin, name="login"),
    path("logout/", views.logout_admin, name="logout"),

    path("dashboard/", views.dashboard_admin, name="dashboard_admin"),
    path("reports/", views.reports_admin, name="reports_admin"),
    path("reports/download/pdf/", views.download_reports_pdf, name="download_reports_pdf"),
    path("reports/download/excel/", views.download_reports_excel, name="download_reports_excel"),
    path("settings/", views.settings_admin, name="settings_admin"),

    path("view-document/<int:document_id>/", views.view_document, name="view_document"),

    path("verifikasi-valid/<int:id>/", views.verifikasi_valid, name="verifikasi_valid"),
    path("verifikasi-tidak-sesuai/<int:id>/", views.verifikasi_tidak_sesuai, name="verifikasi_tidak_sesuai"),
    path("edit-verifikasi/", views.edit_verifikasi, name="edit_verifikasi"),
]