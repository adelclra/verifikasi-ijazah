import os
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from io import BytesIO
import csv

from .ocr import extract_year
from .models import VerifikasiIjazah


# ======================
# UPLOAD USER
# ======================
def upload_ijazah(request):
    tahun = None
    hasil_ocr = ""
    uploaded_file_url = None
    uploaded_file_name = None
    uploaded_file_is_image = False
    uploaded_file_is_pdf = False

    last_data = VerifikasiIjazah.objects.order_by("-created_at").first()

    if request.method == "GET" and request.GET.get("reset") == "1":
        request.session.flush()

    if request.method == "POST" and request.FILES.get("ijazah"):
        file = request.FILES["ijazah"]
        nama = os.path.splitext(file.name)[0]

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)

        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        uploaded_file_name = file.name
        uploaded_file_url = f"{settings.MEDIA_URL}{file.name}"

        file_lower = file.name.lower()
        uploaded_file_is_image = file_lower.endswith((".png", ".jpg", ".jpeg"))
        uploaded_file_is_pdf = file_lower.endswith(".pdf")

        tahun, hasil_ocr = extract_year(file_path)

        if tahun:
            status = "MENUNGGU VERIFIKASI"
        else:
            status = "TIDAK TERDETEKSI"

        VerifikasiIjazah.objects.create(
            nama=nama,
            file=file,
            extracted_year=str(tahun) if tahun else "",
            status=status,
        )

        last_data = VerifikasiIjazah.objects.order_by("-created_at").first()

    return render(request, "index.html", {
        "data": last_data,
        "ocr_text": hasil_ocr,
        "uploaded_file_url": uploaded_file_url,
        "uploaded_file_name": uploaded_file_name,
        "uploaded_file_is_image": uploaded_file_is_image,
        "uploaded_file_is_pdf": uploaded_file_is_pdf,
    })


# ======================
# DASHBOARD ADMIN
# ======================
@login_required(login_url="login")
def dashboard_admin(request):
    data_list = VerifikasiIjazah.objects.order_by("-created_at")

    search = request.GET.get("search")
    status = request.GET.get("status")

    if search:
        data_list = data_list.filter(nama__icontains=search)

    if status:
        if status == "VALID":
            data_list = data_list.filter(status__iexact="VALID")
        elif status == "MENUNGGU":
            data_list = data_list.filter(status__icontains="MENUNGGU")
        elif status == "TIDAK MEMENUHI SYARAT":
            data_list = data_list.filter(status__iexact="TIDAK MEMENUHI SYARAT")
        elif status == "TIDAK TERDETEKSI":
            data_list = data_list.filter(status__iexact="TIDAK TERDETEKSI")

    paginator = Paginator(data_list, 10)
    page_number = request.GET.get("page")
    data = paginator.get_page(page_number)

    all_data = VerifikasiIjazah.objects.all()

    return render(request, "dashboard_admin.html", {
        "data": data,
        "total": all_data.count(),
        "valid": all_data.filter(status__iexact="VALID").count(),
        "not_valid": all_data.filter(status__iexact="TIDAK MEMENUHI SYARAT").count(),
        "pending": all_data.filter(status__icontains="MENUNGGU").count(),
        "unknown_year": all_data.filter(status__iexact="TIDAK TERDETEKSI").count(),
        "today": all_data.filter(created_at__date=timezone.localdate()).count(),

        "search": search or "",
        "status": status or "",
    })


# ======================
# VERIFIKASI ADMIN
# ======================
@login_required(login_url="login")
def verifikasi_valid(request, id):
    data = get_object_or_404(VerifikasiIjazah, id=id)
    data.status = "VALID"
    data.save()
    return redirect("dashboard_admin")


@login_required(login_url="login")
def verifikasi_tidak_sesuai(request, id):
    data = get_object_or_404(VerifikasiIjazah, id=id)
    data.status = "TIDAK MEMENUHI SYARAT"
    data.save()
    return redirect("dashboard_admin")


# ======================
# REPORTS
# ======================
def reports_admin(request):
    context = _build_report_data(request)
    return render(request, "reports_admin.html", context)


def _build_report_data(request):
    today = timezone.localdate()
    data = VerifikasiIjazah.objects.order_by("-created_at")

    search = request.GET.get("search")
    status = request.GET.get("status")

    # FILTER
    if search:
        data = data.filter(nama__icontains=search)

    if status:
        if status == "VALID":
            data = data.filter(status__iexact="VALID")
        elif status == "MENUNGGU":
            data = data.filter(status__icontains="MENUNGGU")
        elif status == "TIDAK MEMENUHI SYARAT":
            data = data.filter(status__iexact="TIDAK MEMENUHI SYARAT")
        elif status == "TIDAK TERDETEKSI":
            data = data.filter(status__iexact="TIDAK TERDETEKSI")

    # PAGINATION
    paginator = Paginator(data, 10)
    page_number = request.GET.get("page")
    report_rows = paginator.get_page(page_number)

    # STATS
    month_data = VerifikasiIjazah.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month,
    )

    total_month = month_data.count()
    valid = month_data.filter(status__iexact="VALID").count()
    not_valid = month_data.filter(status__iexact="TIDAK MEMENUHI SYARAT").count()
    pending = month_data.filter(status__icontains="MENUNGGU").count()
    unknown_year = month_data.filter(status__iexact="TIDAK TERDETEKSI").count()

    accuracy = round((valid / total_month) * 100, 2) if total_month else 0

    total_all = data.count()
    akurasi_total = round(
        (data.filter(status__iexact="VALID").count() / total_all) * 100, 2
    ) if total_all else 0

    return {
        "total_month": total_month,
        "valid": valid,
        "not_valid": not_valid,
        "pending": pending,
        "unknown_year": unknown_year,
        "accuracy": accuracy,
        "report_rows": report_rows,
        "akurasi_total": akurasi_total,

        # 🔥 penting
        "search": search or "",
        "status": status or "",
    }


# ======================
# EXPORT EXCEL
# ======================
def download_reports_excel(request):
    report_data = _build_report_data(request)
    rows = report_data["report_rows"]

    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename="laporan.xls"'

    writer = csv.writer(response, delimiter="\t")
    writer.writerow(["No", "Nama", "Tahun", "Status"])

    for i, item in enumerate(rows, 1):
        writer.writerow([i, item.nama, item.extracted_year or "-", item.status])

    writer.writerow([])
    writer.writerow(["Akurasi", f"{report_data['akurasi_total']}%"])

    return response


# ======================
# EXPORT PDF
# ======================
def download_reports_pdf(request):
    report_data = _build_report_data(request)
    rows = report_data["report_rows"]

    lines = [
        "Laporan Verifikasi",
        f"Akurasi: {report_data['akurasi_total']}%",
        "",
    ]

    for i, item in enumerate(rows, 1):
        lines.append(f"{i}. {item.nama} | {item.status}")

    pdf = _build_simple_pdf(lines)

    return HttpResponse(pdf, content_type="application/pdf")


def _build_simple_pdf(lines):
    buffer = BytesIO()
    buffer.write("\n".join(lines).encode("utf-8"))
    return buffer.getvalue()


# ======================
# VIEW DOCUMENT
# ======================
def view_document(request, document_id):
    item = get_object_or_404(VerifikasiIjazah, id=document_id)

    file_url = item.file.url if item.file else None

    return render(request, "view_document.html", {
        "item": item,
        "file_url": file_url,
    })


# ======================
# LOGIN LOGOUT
# ======================
def login_admin(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user:
            login(request, user)
            return redirect("dashboard_admin")

    return render(request, "login.html")


def logout_admin(request):
    logout(request)
    return redirect("login")


# ======================
# SETTINGS
# ======================
def settings_admin(request):

    admin_data = {
        "name": request.user.get_full_name() or request.user.username,
        "email": request.user.email,
        "role": "Super Admin" if request.user.is_superuser else "Admin",
    }

    return render(request, "settings_admin.html", {"admin": admin_data})