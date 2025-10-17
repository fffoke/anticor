from django.urls import path
from .views import *

app_name = 'web'

urlpatterns = [
    path('', main, name='home'),
    path('all_reports/', all_reports, name='all_reports'),
    path('all_reports/<str:category>/', all_reports, name='reports_by_category'),
    path("sos_page/", sos_page, name="sos_page"),
    path("report_stats/<str:period>/", report_stats, name="reports_period"),
    path('is_decided/<int:report_id>', is_decided ,name='is_decided'),
    path('sos_decided/<int:sos_id>', sos_decided, name='sos_decided'),
    path('sos_stats/<str:period>/', sos_stats, name='sos_stats'),
    path('decided_reports/',decided_reports, name='decided_reports'),
    path('decided_sos/', decided_sos, name='decided_sos')
]
