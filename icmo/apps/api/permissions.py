import logging

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

logger = logging.getLogger('icmo.%s' % __name__)


class IcmoAPIPermissions(BasePermission):
    # API
    # User query filters to restrict company, plans, and segments
    # Restrict endpoints based on app permissions
    # Use app permissions check to restrict change/delete

    def has_permission(self, request, view):
        # NOTE: Restricting to the correct company, revenue_plan,
        # and segment should be done at the queryset level.
        # This protection is put in place to ensure that both blocked
        # and non-existent slugs are rejected rather than returning a
        company_slug = view.kwargs.get('parent_lookup_company__slug')
        plan_slug = view.kwargs.get('parent_lookup_revenue_plan__slug')
        segment_slug = view.kwargs.get('parent_lookup_segment__slug')

        if company_slug and company_slug not in request.user.companies_slugs:
            return False
        if plan_slug and plan_slug not in request.company_user.permitted_revenue_plans_slugs:
            return False
        if segment_slug and segment_slug not in request.company_user.permitted_segments_slugs:
            return False

        # Enforce app VIEW restrictions
        if hasattr(view, 'app_name') and view.app_name:
            permission_granted = request.company_user.can_view(view.app_name)
            if not permission_granted:
                logger.debug(
                    'Permission Denied:  User %s attempted to access a VIEW method of app `%s` '
                    'without permission' %
                    (request.user, view.app_name))
                return False
        return True

    def has_object_permission(self, request, view, obj):
        # Enforce app CHANGE restrictions
        if request.method not in permissions.SAFE_METHODS:
            if hasattr(view, 'app_name') and view.app_name and not request.company_user.can_change(
                    view.app_name):
                logger.debug(
                    'Permission Denied: User %s attempted to access a CHANGE method of app `%s` '
                    'without permission' %
                    (request.user, view.app_name))
                return False

        # NOTE: None of these should be needed given proper querysets filtering each
        # ViewSet.  DRF will not allow you to access an object not in a queryset.
        # However, these are still included in order to err on the side of security in the
        # case that a viewset queryset is NOT set up properly.

        # Enforce Company, Revenue Plan, and Segment restrictions
        if hasattr(obj, 'company') and hasattr(obj.company, 'slug') and obj.company.slug not in \
                request.user.companies_slugs:
            logger.warning('Permission Denied:  User %s attempted to access blocked company %s' % (
                request.user, obj.company))
            raise PermissionDenied

        if hasattr(obj,
                   'revenue_plan') and hasattr(obj.revenue_plan,
                                               'slug') and obj.revenue_plan.slug not in \
                request.company_user.permitted_revenue_plans_slugs:
            logger.warning('Permission Denied:  User %s attempted to access blocked plan %s' % (
                request.user, obj.revenue_plan))
            raise PermissionDenied

        if hasattr(obj, 'segment') and hasattr(obj.segment, 'slug') and obj.segment.slug not in \
                request.company_user.permitted_segments_slugs:
            logger.warning('Permission Denied:  User %s attempted to access blocked segment %s' % (
                request.user, obj.segment))
            raise PermissionDenied
        return True
