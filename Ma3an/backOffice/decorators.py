# from django.http import HttpResponseForbidden
# from accounts.models import Profile

# def admin_only(view_func):
#     def wrapper(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return HttpResponseForbidden("Login required.")
#         try:
#             if request.user.profile.role != 'admin':
#                 return HttpResponseForbidden("You do not have access to this page.")
#         except Profile.DoesNotExist:
#             return HttpResponseForbidden("Profile missing for this user.")
#         return view_func(request, *args, **kwargs)
#     return wrapper



from django.http import HttpResponseForbidden
from accounts.models import User

def admin_only(view_func):
    """
    يسمح فقط للمستخدمين الذين لديهم الدور 'admin' بالوصول للـ view.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Login required.")
        if request.user.role != 'admin':
            return HttpResponseForbidden("You do not have access to this page.")
        return view_func(request, *args, **kwargs)
    return wrapper
