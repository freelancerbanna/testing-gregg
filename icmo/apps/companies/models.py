from cloudinary.models import CloudinaryField
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.dates import MONTHS
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from companies.notifications import send_share_notification_email, \
    send_invited_user_activation_email
from core.helpers import get_fiscal_year_quarters, get_fiscal_year_months, \
    get_fiscal_quarter_by_month_name, MONTHS_FULL, MONTHS_3
from core.models import IcmoModel, SORTED_STATE_AND_PROVINCE, COUNTRY_CHOICES, BLANK_CHOICE
from revenues.models import RevenuePlan


class NoLivePlanException(Exception):
    pass


class AppPermissions(object):
    NONE = 'none'
    VIEW = 'view'
    CHANGE = 'change'

    choices = (
        (NONE, 'None'),
        (VIEW, 'View'),
        (CHANGE, 'Change'),
    )


class SharePermissions(object):
    NONE = 'none'
    MODERATED = 'moderated'
    UNMODERATED = 'unmoderated'

    choices = (
        (NONE, 'None'),
        (NONE, 'View'),
        (NONE, 'Change'),
    )


class Company(IcmoModel):
    class Meta:
        verbose_name_plural = "Companies"
        permissions = (
            ('view_company', 'View company'),
        )
        unique_together = (('account', 'name'), ('account', 'slug'))

    account = models.ForeignKey('billing.BillingAccount', related_name='companies')
    name = models.CharField(_('Company Name'), max_length=150)
    slug = AutoSlugField(populate_from='name')
    website = models.URLField(max_length=150, blank=True)
    address1 = models.CharField(_('Address 1'), max_length=255)
    address2 = models.CharField(_('Address 2'), max_length=255, blank=True)
    city = models.CharField(max_length=75)
    state = models.CharField(max_length=2,
                             choices=BLANK_CHOICE + SORTED_STATE_AND_PROVINCE)
    zip = models.CharField(max_length=12)
    country = models.CharField(max_length=3, choices=BLANK_CHOICE + COUNTRY_CHOICES,
                               default='US')
    logo = CloudinaryField(blank=True, null=True)
    fiscal_year_start = models.PositiveSmallIntegerField(choices=MONTHS.items(), default=1)

    @cached_property
    def segments(self):
        return self.segment_set.filter(is_active=True)

    @property
    def revenue_plans(self):
        return self.revenueplan_set.filter(is_active=True)

    @property
    def published_revenue_plan(self):
        try:
            return self.revenue_plans.get(plan_type='published')
        except ObjectDoesNotExist:
            return None

    @cached_property
    def has_active_subscription(self):
        return self.account.has_active_subscription()

    @cached_property
    def active_plans(self):
        return self.revenue_plans.filter(is_active=True)

    @property
    def fiscal_year_start_full_name(self):
        return MONTHS_FULL[self.fiscal_year_start - 1]

    @property
    def fiscal_quarters(self):
        return get_fiscal_year_quarters(self.fiscal_year_start)

    @property
    def fiscal_quarters_by_name(self):
        return get_fiscal_year_quarters(self.fiscal_year_start, month_type='name')

    def get_fiscal_quarter_by_month_name(self, month_name):
        return get_fiscal_quarter_by_month_name(self.fiscal_year_start, month_name)

    def get_current_quarter(self):
        return self.get_fiscal_quarter_by_month_name(MONTHS_3[timezone.now().month - 1])

    @property
    def fiscal_months(self):
        return get_fiscal_year_months(self.fiscal_year_start)

    @property
    def fiscal_months_by_name(self):
        return get_fiscal_year_months(self.fiscal_year_start, month_type='name')

    def assign_owner(self, user, title=None):
        if self.users.filter(owner=True).count() != 0:
            raise ValueError("This company already has an owner.")
        if not title:
            title = ""
        return CompanyUser.objects.create(
            company=self,
            user=user,
            group=CompanyUserGroup.objects.get(company=self, name='Admin', editable=False),
            owner=True,
            title=title
        )

    def assign_user(self, user, group, title=None):
        if not title:
            title = ""
        try:
            group = CompanyUserGroup.objects.get(company=self, name=group)
        except CompanyUserGroup.DoesNotExist:
            raise ValueError("Group `%s` not found" % group)
        company_user, created = CompanyUser.objects.get_or_create(defaults=dict(group=group),
                                                                  company=self, user=user,
                                                                  title=title)
        return company_user

    def create_default_plan(self):
        from demos.tasks import task_create_sample_revenue_plan
        task_create_sample_revenue_plan.delay(self.id)

    @cached_property
    def logo_thumbnail(self):
        if self.logo:
            return self.logo.build_url(height=60, crop='fit')
        return None

    @cached_property
    def logo_large(self):
        if self.logo:
            return self.logo.build_url(height=100, crop='fit')
        return None

    @cached_property
    def url(self):
        return self.get_absolute_url()

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('companies_list', kwargs=dict(company_slug=self.slug))

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        created = not self.pk
        super(Company, self).save(*args, **kwargs)
        if created:
            # Every new company instance gets a default revenue plan
            # Note that this is queued, and may take a couple minutes
            self.create_default_plan()
            # and a set of default user groups
            CompanyUserGroup.create_default_groups(self)


class CompanyUserGroup(IcmoModel):
    icmo_parent_levels = ('company',)

    class Meta:
        unique_together = ('company', 'name')

    slug = AutoSlugField(populate_from='name')
    name = models.CharField(max_length=255)
    company = models.ForeignKey('Company')
    editable = models.BooleanField(default=True,
                                   help_text="Some default plans should never be deleted or "
                                             "edited by the user")
    revenue_plans = models.CharField(max_length=50, default=AppPermissions.NONE,
                                     choices=AppPermissions.choices)
    program_mix = models.CharField(max_length=50, default=AppPermissions.NONE,
                                   choices=AppPermissions.choices)
    budgets = models.CharField(max_length=50, default=AppPermissions.NONE,
                               choices=AppPermissions.choices)
    performance = models.CharField(max_length=50, default=AppPermissions.NONE,
                                   choices=AppPermissions.choices)
    resources = models.CharField(max_length=50, default=AppPermissions.NONE,
                                 choices=AppPermissions.choices)
    timeline = models.CharField(max_length=50, default=AppPermissions.NONE,
                                choices=AppPermissions.choices)
    task_boards = models.CharField(max_length=50, default=AppPermissions.NONE,
                                   choices=AppPermissions.choices)
    dashboards = models.CharField(max_length=50, default=AppPermissions.NONE,
                                  choices=AppPermissions.choices)
    reports = models.CharField(max_length=50, default=AppPermissions.NONE,
                               choices=AppPermissions.choices)
    permissions = models.CharField(max_length=50, default=AppPermissions.NONE,
                                   choices=AppPermissions.choices)

    live_plan_only = models.BooleanField(default=True)
    permitted_segments_list = models.TextField(
        blank=True,
        help_text="Restrict this group to certain segments.  Each exact segment name should be "
                  "entered on a separate line.  Note, in the case that all of the segments a user "
                  "has access to are not found or are inactive, users from  this group will not "
                  "be able to access anything."
    )
    publish_plans = models.BooleanField(default=False)
    archive_plans = models.BooleanField(default=False)
    share = models.CharField(max_length=50, default=SharePermissions.NONE,
                             choices=SharePermissions.choices)
    moderate_shares = models.BooleanField(default=False)

    @staticmethod
    def create_default_groups(company):
        # Admin users can do everything, including manage revenue plans and moderate shares.
        CompanyUserGroup.objects.create(
            name='Admin',
            company=company,
            editable=False,
            revenue_plans=AppPermissions.CHANGE,
            program_mix=AppPermissions.CHANGE,
            budgets=AppPermissions.CHANGE,
            performance=AppPermissions.CHANGE,
            resources=AppPermissions.CHANGE,
            timeline=AppPermissions.CHANGE,
            task_boards=AppPermissions.CHANGE,
            dashboards=AppPermissions.CHANGE,
            reports=AppPermissions.CHANGE,
            permissions=AppPermissions.CHANGE,
            share=SharePermissions.UNMODERATED,
            live_plan_only=False,
            publish_plans=True,
            archive_plans=True,
            moderate_shares=True
        )
        # Planners can do everything with the live plan, but cannot create their own plans
        CompanyUserGroup.objects.create(
            name='Planner',
            company=company,
            revenue_plans=AppPermissions.VIEW,
            program_mix=AppPermissions.CHANGE,
            budgets=AppPermissions.CHANGE,
            performance=AppPermissions.CHANGE,
            resources=AppPermissions.CHANGE,
            timeline=AppPermissions.CHANGE,
            task_boards=AppPermissions.CHANGE,
            dashboards=AppPermissions.CHANGE,
            reports=AppPermissions.CHANGE,
            share=SharePermissions.MODERATED,
        )
        # Updaters are data entry accounts, mainly used for staff who will not be doing anything
        #  else
        CompanyUserGroup.objects.create(
            name='Updater',
            company=company,
            budgets=AppPermissions.CHANGE,
            performance=AppPermissions.CHANGE,
            timeline=AppPermissions.VIEW,
        )
        # Dashboards Only accounts are for CEO's, VC's or anyone else who just needs the high level
        # overview
        CompanyUserGroup.objects.create(
            name='Dashboards Only',
            company=company,
            dashboards=AppPermissions.VIEW,
            reports=AppPermissions.VIEW,
            live_plan_only=True,
            share=SharePermissions.MODERATED,
        )
        # Dashboards Only accounts are for CEO's, VC's or anyone else who just needs the high level
        # overview
        CompanyUserGroup.objects.create(
            name='Taskboards Only',
            company=company,
            task_boards=AppPermissions.CHANGE,
            live_plan_only=True,
            share=SharePermissions.MODERATED,
        )

    def __unicode__(self):
        return self.name


class CompanyUser(IcmoModel):
    icmo_parent_levels = ('company',)

    class Meta:
        unique_together = ('company', 'user')

    slug = AutoSlugField(populate_from=('company', 'user'))
    company = models.ForeignKey('Company', related_name='users')
    user = models.ForeignKey('icmo_users.IcmoUser', related_name='permissions')
    group = models.ForeignKey('CompanyUserGroup')
    title = models.CharField(max_length=75, blank=True)
    owner = models.BooleanField(default=False)
    permitted_segments_list = models.TextField(blank=True)

    @property
    def permitted_revenue_plans(self):
        if self.owner:
            return self.company.revenue_plans
        if self.group.live_plan_only:
            if not self.company.published_revenue_plan:
                raise NoLivePlanException(
                    "This company does not have a published revenue plan and this user is "
                    "restricted to published revenue plans.")
            return RevenuePlan.objects.filter(id=self.company.published_revenue_plan.id)
        return self.company.revenue_plans

    @cached_property
    def permitted_revenue_plans_slugs(self):
        return [x.slug for x in self.permitted_revenue_plans]

    @property
    def permitted_segments(self):
        qs = self.company.segments
        if self.owner:
            return qs
        if self.permitted_segments_list:
            name_list = self.permitted_segments_list
        else:
            name_list = self.group.permitted_segments_list
        if name_list:
            name_filter = Q()
            for name in [x.strip() for x in name_list.splitlines()]:
                name_filter |= Q(name__iexact=name)
            qs = qs.filter(name_filter)
        return qs

    @cached_property
    def permitted_segments_slugs(self):
        return [x.slug for x in self.permitted_segments.all()]

    def can_view(self, app):
        if self.owner:
            return True
        if app in self._unrestricted_apps:
            return True
        if app not in self._restricted_apps:
            raise ValueError(
                "Invalid app name `%s`, valid names are: %s" % (app, ", ".join(self._restricted_apps)))
        if getattr(self.group, app) in [AppPermissions.CHANGE, AppPermissions.VIEW]:
            return True
        return False

    def can_change(self, app):
        if self.owner:
            return True
        if app not in self._restricted_apps:
            raise ValueError("Invalid app name, valid names are: %s" % ", ".join(self._restricted_apps))
        if getattr(self.group, app) == AppPermissions.CHANGE:
            return True
        return False

    def get_permitted_plan_segments(self, revenue_plan):
        qs = revenue_plan.segments.all()
        if self.owner:
            return qs
        return qs.filter(id__in=self.permitted_segments)

    @cached_property
    def is_segment_restricted(self):
        if self.owner:
            return False
        if self.permitted_segments_list or self.group.permitted_segments_list:
            return True
        return False

    def __getattr__(self, item):
        if 'can_view_' in item:
            app = item.split('can_view_')[1]
            if app in self._restricted_apps:
                return self.can_view(app)
        elif 'can_change_' in item:
            app = item.split('can_change_')[1]
            if app in self._restricted_apps:
                return self.can_change(app)
        raise AttributeError

    @property
    def _restricted_apps(self):
        return ['revenue_plans', 'segments', 'program_mix', 'budgets', 'performance',
                'resources', 'timeline', 'dashboards', 'permissions', 'task_boards',
                'reports']

    @property
    def _unrestricted_apps(self):
        return ['notifications']

    def __unicode__(self):
        return "%s - %s" % (self.user, self.company)


class CompanyUserInvitation(IcmoModel):
    company = models.ForeignKey('Company')
    inviting_user = models.ForeignKey('icmo_users.IcmoUser', related_name='+')
    target_email = models.EmailField(max_length=255)
    user = models.ForeignKey('icmo_users.IcmoUser', related_name='+')
    is_new_user = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            request = kwargs.pop('request', None)
            if not request:
                raise ValueError("You must pass a request kwarg to this"
                                 " save method when saving a new invitation")

            from icmo_users.models import IcmoUser
            try:
                self.user = IcmoUser.objects.get(email=self.target_email)
                self.accepted = True
            except IcmoUser.DoesNotExist:
                self.user = IcmoUser.objects.create(email=self.target_email, first_name="New User",
                                                    last_name="(Unactivated)")
                self.is_new_user = True
            if self.is_new_user:
                send_invited_user_activation_email(request, self.user, self.inviting_user,
                                                   self.company)
            else:
                # new users will receive the invitation in their welcome email, existing users
                # need a different email notification
                send_share_notification_email(request, self.user, self.inviting_user, self.company)

        super(CompanyUserInvitation, self).save(*args, **kwargs)


class ShareManager(models.Manager):
    def create_share(self, application_name, instance, user, author):
        """ Creates a new share """
        share = self.model(application_name=application_name,
                           object_name=type(instance).__name__,
                           object_id=instance.id, user=user,
                           created_by=author)
        share.save()
        return share


class Share(models.Model):
    """
        Generic way of sharing specific objects with users. Please note that
        the share is independent of permissions pertaining to the app that
        the underlying object belongs to. In other words, you can share a
        revenue plan with a user, but the user would have to have either
        read access or write access to revenue plans for a specific company
        in order to actually use the share effectively.
    """
    application_name = models.CharField(_('Application Name'), max_length=25, blank=False,
                                        null=False)
    object_name = models.CharField(_('Object Name'), max_length=25, blank=False, null=False)
    object_id = models.IntegerField(_('Object ID'), blank=False, null=False)
    user = models.ForeignKey('icmo_users.IcmoUser', related_name='shares', blank=False, null=True)
    created_by = models.ForeignKey('icmo_users.IcmoUser', related_name='shares_granted',
                                   blank=False, null=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True)

    objects = ShareManager()

    @cached_property
    def shared_object(self):
        model = apps.get_model(self.application_name, self.object_name)
        return model.objects.get(pk=self.object_id)

    def notify_shared_user(self, link, subject=None, body=""):
        recipient = self.user.email
        if self.created_by.first_name and self.created_by.last_name:
            sender = "%s %s" % \
                     (self.created_by.first_name, self.created_by.last_name)
        else:
            sender = self.created_by.email

        if not subject:
            subject = sender + ' has Shared an intelligentRevenue Item With You'

        footer = '. You can view this shared item at '
        footer += link
        body += footer

        return self.user.email_user(subject, body, from_email=self.created_by.email)
