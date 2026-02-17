from django.shortcuts import render
from .models import Notification


def handler403(request, exception=None):
    """Custom 403 error handler"""
    return render(request, '403.html', status=403)


def handler404(request, exception=None):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    try:
        Notification.objects.create(
            title="System Error",
            message="A server error occurred and was captured by the error handler.",
            type="system",
            priority="high",
            created_by="system",
        )
    except Exception:
        pass
    return render(request, '500.html', status=500)
