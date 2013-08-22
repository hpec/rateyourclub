import yaml, argparse, sys, os
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from rateyourclub import settings
from constance import config
class Command(BaseCommand):
    help = 'Sets facebook email and password'
    option_list = BaseCommand.option_list + (
            make_option('-e','--email',
                                    action='store',
                                    dest='email',
                                    type='string',
                                    help='facebook email'),
            make_option('-p','--password',
                                    action='store',
                                    type='string',
                                    dest='password',
                                    help='facebook password'),
            )
    def handle(self, *args, **options):
        if set(('password', 'email')).issubset(options):
            config.FACEBOOK_USER_EMAIL = options['email']
            config.FACEBOOK_USER_PASSWORD = options['password']

