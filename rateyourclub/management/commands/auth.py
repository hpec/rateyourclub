import yaml, argparse, sys, os
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from rateyourclub import settings
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
        data = {}

        if set(('password', 'email')).issubset(options):
            if os.path.isfile(settings.CONFIGURATION_YAML):
                defaults = yaml.safe_load(file(settings.CONFIGURATION_YAML,'r'))
                if type(defaults) != type(None):
                    data.update(defaults)

            data['email'] = options['email']
            data['password']  = options['password']

            yaml.dump(data, file(settings.CONFIGURATION_YAML,'w') )

