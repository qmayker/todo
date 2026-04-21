import zoneinfo
from django.http import HttpRequest
from django.utils import timezone


class TimeZoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        try:
            tzname = None
            if request.user.is_authenticated:
                tzname = request.user.profile.timezone
            tzname = tzname or request.COOKIES.get("django_timezone")
            if tzname:
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            else:
                timezone.deactivate()
        except Exception:
            timezone.deactivate()
        return self.get_response(request)
