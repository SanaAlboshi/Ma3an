from functools import wraps
from django.http import HttpResponseForbidden


def admin_only(view_func):
    """
    Allows only admins to access the view.
    Works with:
    - user.is_superuser
    - user.role == 'admin' (if you added role to User)
    - user.traveler.role == 'admin' (if role lives on Traveler)
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return HttpResponseForbidden("Login required.")

        if getattr(user, "is_superuser", False):
            return view_func(request, *args, **kwargs)

        role = getattr(user, "role", None)

        if role is None:
            traveler = getattr(user, "traveler", None) or getattr(user, "traveler_profile", None)
            role = getattr(traveler, "role", None)

        if role != "admin":
            return HttpResponseForbidden("You do not have access to this page.")

        return view_func(request, *args, **kwargs)

    return wrapper
