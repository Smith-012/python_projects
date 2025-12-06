from django.contrib import admin
from django.urls import path, include
from logsapp.views import logs_graph  # add this

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", logs_graph, name="home"),        # <-- root shows the graph
    path("", include("logsapp.urls")),        # keep your app urls too
]
