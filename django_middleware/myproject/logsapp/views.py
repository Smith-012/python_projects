from django.shortcuts import render
from django.db.models import Count
from .models import RequestLog

def logs_graph(request):
    data = (
        RequestLog.objects
        .values("status_code")
        .annotate(count=Count("status_code"))
    )

    labels = [item["status_code"] for item in data]
    counts = [item["count"] for item in data]

    return render(request, "logs_graph.html", {
        "labels": labels,
        "counts": counts
    })
