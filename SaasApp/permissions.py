from rest_framework.permissions import BasePermission
from .models import Membership


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        membership = Membership.objects.filter(
            user=request.user
        ).first()

        return membership and membership.role == 'ADMIN'


class IsAdminOrManager(BasePermission):

    def has_permission(self, request, view):
        membership = Membership.objects.filter(
            user=request.user
        ).first()

        if not membership:
            return False

        return membership.role in ['ADMIN', 'MANAGER']