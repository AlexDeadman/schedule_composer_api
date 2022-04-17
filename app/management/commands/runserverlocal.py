from django.core.management import BaseCommand, call_command
from netifaces import ifaddresses, interfaces, AF_INET


class Command(BaseCommand):

    help = 'Run server in local network'

    def add_arguments(self, parser):
        parser.add_argument('--interface', type=int)

    def handle(self, *args, **options):

        pre_choose = options['interface']

        for ind, ifaceName in enumerate(interfaces()):
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr': 'No IP addr'}])]
            if not pre_choose:
                print('%s. %s: %s' % (ind + 1, ifaceName, ', '.join(addresses)))

        number = pre_choose if pre_choose else input("\nChoose network interface: ")
        ifaddr = ifaddresses(interfaces()[int(number) - 1])

        print()

        call_command('runserver', '--noreload', f'{ifaddr[2][0]["addr"]}:8000')
