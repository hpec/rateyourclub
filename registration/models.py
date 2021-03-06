import datetime
import hashlib
import random
import re

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _


SHA1_RE = re.compile('^[a-f0-9]{40}$')
ACTIVATED = u"ALREADY_ACTIVATED"

def generate_random_key(info):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    return hashlib.sha1(salt+info).hexdigest()

def valid_hash(string):
    return string and SHA1_RE.search(string)


class UserManager(BaseUserManager):

    def create_user(self, email, screen_name, password=None):
        now = timezone.now()
        if not email:
            raise ValueError('User must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, screen_name=screen_name,
                          is_staff=False, is_active=True,
                          last_login=now, date_joined=now)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_inactive_user(self, email, screen_name, password=None):
        user = self.create_user(email, screen_name, password)
        activation = self.create_activation(user)
        try:
            self.send_activation_email(activation)
            user.is_active = False
            user.save()
        except Exception, e:
            print '[ERROR]: Fail to create inactive user'
            print '[ERROR]:', e
            user.delete()
            activation.delete()
        return user

    def create_superuser(self, email, screen_name, password):
        u = self.create_user(email, screen_name, password)
        u.is_staff = True
        u.is_active = True
        u.is_admin = True
        u.save(using=self._db)
        return u

    def create_activation(self, user):
        return Activation.objects.create(user=user, activation_key=generate_random_key(user.email))

    def create_invitation(self, email):
        if Invitation.objects.filter(email=email).count() > 0:
            return Invitation.objects.get(email=email)
        else:
            return Invitation.objects.create(email=email, invitation_key=generate_random_key(email))

    def send_activation_email(self, activation):
        current_site = "CalBEAT"

        subject = render_to_string('activation_email_subject.txt',
                                   { 'site': current_site,
                                     'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                    })
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('activation_email.txt',
                                   { 'activation_key': activation.activation_key,
                                     'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                     'site': current_site,
                                    })

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [activation.user.email])

    def send_invitation_email(self, invitation, user):
        current_site = "CalBEAT"

        subject = render_to_string('invitation_email_subject.txt',
                                   { 'site': current_site,
                                     'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                    })
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('invitation_email.txt',
                                   { 'invitation_key': invitation.invitation_key,
                                     'site': current_site,
                                     'who': user,
                                    })

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [invitation.email])



    def activate_user(self, activation_key):
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if valid_hash(activation_key):
            try:
                activation = Activation.objects.get(activation_key=activation_key)
            except Activation.DoesNotExist:
                return False
            if not activation.activation_key_expired():
                user = activation.user
                user.is_active = True
                user.save()
                activation.activation_key = ACTIVATED
                activation.save()
                return user
        return False


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True,
    )
    screen_name = models.CharField(_('screen name'), max_length=30)
    is_active = models.BooleanField(_('active'), default=False,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    subscribed_clubs = models.ManyToManyField('clubreview.Club', through='Subscription')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['screen_name']

    def get_full_name(self):
        return self.screen_name

    def get_short_name(self):
        return self.screen_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_group_permissions(self, obj=None):
        return None
    def get_all_permissions(self, obj=None):
        return None
    def has_perm(self, perm, obj=None):
        return obj.is_staff if obj else self.is_staff
    def has_perms(self, perm, obj=None):
        return obj.is_staff if obj else self.is_staff
    def has_module_perms(self, package_name):
        return self.is_staff



class Activation(models.Model):
    user = models.ForeignKey(User, unique=True)
    activation_key = models.CharField(_('activation key'), max_length=40)
    created_at = models.DateTimeField(_('created_at'), default=timezone.now)

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == ACTIVATED or \
               (self.user.date_joined.replace(tzinfo=None) + expiration_date <= datetime.datetime.now())

class Invitation(models.Model):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
        db_index=True,
    )
    invitation_key = models.CharField(_('invitation key'), max_length=40)
    created_at = models.DateTimeField(_('created_at'), default=timezone.now)

class SubscriptionManager(models.Manager):
    def send_events_update(self, email=None):
        def send_update_email(user, events):
            subject = render_to_string('emails/events_update_email_subject.txt')
            subject = ''.join(subject.splitlines()) # Email subject *must not* contain newlines
            html_content = render_to_string('emails/events_update_email.txt', { 'user':user, 'events':events })
            text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        subscriptions = self.get_query_set().all()
        users = User.objects.filter(email=email) if email else User.objects.all()
        for user in users:
            events = []
            clubs = user.subscribed_clubs.all()
            for club in clubs:
                events.extend(list(club.event_set.future()
                    .filter(start_time__lte=timezone.now() + datetime.timedelta(days=7))
                    .order_by('start_time')))
            events = list(set(events)) # Eliminate duplicate events
            if events:
                send_update_email(user, events[:6])

class Subscription(models.Model):
    club = models.ForeignKey('clubreview.Club')
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = SubscriptionManager()

    class Meta:
        unique_together = ('club', 'user')

    def __unicode__(self):
        return "%s - %s" % (self.user, self.club)
