import datetime
import hashlib
import random
import re

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


SHA1_RE = re.compile('^[a-f0-9]{40}$')
ACTIVATED = u"ALREADY_ACTIVATED"
# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, email, screen_name, password=None):
        now = timezone.now()
        if not email:
            raise ValueError('User must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, screen_name=screen_name,
                          is_staff=False, is_active=False,
                          last_login=now, date_joined=now)

        user.set_password(password)
        user.save(using=self._db)
        activation = self.create_activation(user)
        try:
            print "sending activation email"
            self.send_activation_email(activation)
            print "email sent"
        except Exception, e:
            print e
            user.delete()
            activation.delete()
        return user

    def create_activation(self, user):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        activation_key = hashlib.sha1(salt+user.email).hexdigest()
        activation = Activation.objects.create(user=user, activation_key=activation_key)
        return activation

    def send_activation_email(self, activation):
        current_site = "Rateyourclub"

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

    def create_superuser(self, email, password):
        u = self.create_user(email, password)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u

    def activate_user(self, activation_key):
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
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

class User(AbstractBaseUser):
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

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['screen_name']

    def get_full_name(self):
        return self.screen_name

    def get_short_name(self):
        return self.screen_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])


class Activation(models.Model):
    user = models.ForeignKey(User, unique=True)
    activation_key = models.CharField(_('activation key'), max_length=40)

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == ACTIVATED or \
               (self.user.date_joined.replace(tzinfo=None) + expiration_date <= datetime.datetime.now())



