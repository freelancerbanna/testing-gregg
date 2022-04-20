from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import models
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import ShortUUIDField
from django_extensions.db.fields.json import JSONField
from django_extensions.db.models import TimeStampedModel
from localflavor.us.models import PhoneNumberField
from timezone_field import TimeZoneField

from companies.models import Company
from core.models import ActiveManager


class IcmoUserManager(BaseUserManager):
    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves an IcmoUser with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=is_staff, is_superuser=is_superuser,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class IcmoUser(AbstractBaseUser, PermissionsMixin):
    """
        The basic user model for this application. he main difference between
        this user model and and the stock django one is that there is no
        username and identity is established by email which is, of course,
        a required field. 
    """
    first_name = models.CharField(_('First Name'), max_length=30)
    last_name = models.CharField(_('Last Name'), max_length=30)
    email = models.EmailField(_('Email'), unique=True)
    phone_number = PhoneNumberField(blank=True)
    title = models.CharField(help_text='Title Override', max_length=255, blank=True)
    is_staff = models.BooleanField(_('Staff status'), default=False,
                                   help_text=_(
                                       'Designates whether the user can log into this admin '
                                       'site.'))
    is_admin = models.BooleanField(_('Admin status'), default=False,
                                   help_text=_('Designates whether the user is an admin'))
    is_beta = models.BooleanField(_('Sees Beta Features'), default=False,
                                  help_text="Designates whether this user can see beta features")
    is_active = models.BooleanField(_('Active'), default=True,
                                    help_text=_(
                                        'Designates whether this user should be treated as '
                                        'active. Unselect this instead of deleting billing.'))
    date_joined = models.DateTimeField(_('Date joined'), auto_now_add=True)
    last_revenue_plan = models.ForeignKey('revenues.RevenuePlan', editable=False, blank=True,
                                          null=True, on_delete=models.SET_NULL)
    activation_token = ShortUUIDField(unique=True)

    company = models.CharField(help_text='Company Name Override', max_length=255, blank=True)
    timezone = TimeZoneField(default='America/Los_Angeles')

    companies = models.ManyToManyField('companies.Company', through='companies.CompanyUser',
                                       through_fields=('user', 'company'))

    objects = IcmoUserManager()
    active = ActiveManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def deactivate(self):
        self.is_active = False
        return self.save()

    @cached_property
    def companies_slugs(self):
        return [x.slug for x in self.companies.all()]

    @property
    def is_account_owner(self):
        return hasattr(self, 'billingaccount')

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def initials(self):
        return "%s%s" % (self.first_name[0].upper(), self.last_name[0].upper())

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    @cached_property
    def owned_companies(self):
        return Company.objects.filter(
            id__in=self.permissions.filter(owner=True).values('company_id'))

    @cached_property
    def shared_companies(self):
        return Company.objects.filter(
            id__in=self.permissions.filter(owner=False).values('company_id'))

    @cached_property
    def can_create_company(self):
        if not hasattr(self, 'billingaccount') or not self.billingaccount:
            return False
        if self.owned_companies >= self.billingaccount.limit_max_companies:
            return False
        return True

    @cached_property
    def employer_name(self):
        if self.company:
            return self.company
        return self.owned_companies.first().name

    @classmethod
    def get_or_create_user(cls, email, first_name, last_name, password):
        try:
            user = cls.objects.get(email=email)
        except cls.DoesNotExist:
            user = cls.objects.create(
                first_name=first_name, last_name=last_name,
                email=email, password=password
            )
            user.set_password(password)
            user.save()
        return user


class Referral(models.Model):
    """ Keeps track of when someone refers us to their friends. Automatically
        sends an email at creation"""
    referrer = models.ForeignKey(IcmoUser, related_name='referrals')
    email = models.EmailField(_('email address'), unique=False)
    message = models.TextField(blank=True, null=True)
    date_sent = models.DateTimeField(_('date sent'), default=None,
                                     null=True)

    def send_referral(self):
        # todo revise this
        subject = get_template('icmo_users/email/referral_subject.txt')
        subject_content = subject.render(Context({'user': self.referrer}))
        subject_content = subject_content.replace('\n', '')

        plaintext = get_template('icmo_users/email/referral_email.txt')
        plaintext_content = plaintext.render(
            Context({'message': self.message,
                     'user': self.referrer,
                     'dest': settings.REFERRAL_LANDING_PAGE})
        )

        htmlish = get_template('icmo_users/email/referral_email.html')
        htmlish_content = plaintext.render(
            Context({'message': self.message,
                     'user': self.referrer,
                     'dest': settings.REFERRAL_LANDING_PAGE})
        )

        msg = EmailMultiAlternatives(subject_content, plaintext_content,
                                     self.referrer.email,
                                     [self.email])
        msg.attach_alternative(htmlish_content, "text/html")
        try:
            m = msg.send()
            if int(m) > 0:
                self.date_sent = timezone.now()
                if self.pk:
                    self.save()
        except:
            pass

    def save(self, *args, **kwargs):
        if not self.pk:
            self.send()
        super(self, Referral).save(*args, **kwargs)


class Suggestion(models.Model):
    """ Keeps track of when someone sends us a suggestion. Automatically
        sends an email at creation"""
    user = models.ForeignKey(IcmoUser, related_name='suggestions')
    message = models.TextField(blank=True, null=True)
    date_sent = models.DateTimeField(_('date sent'), default=None,
                                     null=True)

    def send(self):
        subject = 'iCMO suggestion from ' + self.user.email
        message = self.message
        msg = EmailMultiAlternatives(subject, message,
                                     self.user.email,
                                     [settings.SUPPORT_EMAIL])
        msg.send()
        self.date_sent = timezone.now()
        if self.pk:
            self.save()
        return True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.send()
        super(Suggestion, self).save(*args, **kwargs)


class SignupLead(TimeStampedModel):
    first_name = models.CharField(max_length=30, blank=True, editable=False)
    last_name = models.CharField(max_length=30, blank=True, editable=False)
    email = models.EmailField(unique=True, editable=False)
    phone_number = PhoneNumberField(blank=True, editable=False)
    title = models.CharField(max_length=255, blank=True, editable=False)
    company_name = models.CharField(max_length=255, blank=True, editable=False)
    fields = JSONField(editable=False)
