from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path("", lambda request: redirect("dashboard_admin"), name="root"),
    path("upload/", views.upload_ijazah, name="home"),
    path("upload-single/", views.upload_single, name="upload_single"),

    path("login/", views.login_admin, name="login"),
    path("logout/", views.logout_admin, name="logout"),

    path("dashboard/", views.dashboard_admin, name="dashboard_admin"),
    path("reports/", views.reports_admin, name="reports_admin"),
    path("reports/download/pdf/", views.download_reports_pdf, name="download_reports_pdf"),
    path("reports/download/excel/", views.download_reports_excel, name="download_reports_excel"),
    path("settings/", views.settings_admin, name="settings_admin"),
    path("settings/users/", views.manage_users, name="manage_users"),
    path("settings/users/add/", views.add_user, name="add_user"),
    path("settings/users/edit/<int:user_id>/", views.edit_user, name="edit_user"),
    path("settings/users/delete/<int:user_id>/", views.delete_user, name="delete_user"),

    path("view-document/<int:document_id>/", views.view_document, name="view_document"),

    path("verifikasi-valid/<int:id>/", views.verifikasi_valid, name="verifikasi_valid"),
    path("verifikasi-tidak-sesuai/<int:id>/", views.verifikasi_tidak_sesuai, name="verifikasi_tidak_sesuai"),
    path("edit-verifikasi/", views.edit_verifikasi, name="edit_verifikasi"),
]