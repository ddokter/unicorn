import re
from django.core.management.base import BaseCommand
from unicorn.models.conversion import Conversion


CONV_PAT = re.compile(r"\s*(?P<amount_lh>[0-9\.]+)\s*(?P<unit_lh>\w+)\s*"
                      "\((?P<location_lh>\w+)\)\s*(?P<op>[=,\<,\>])\s*"
                      "(?P<amount_rh>[0-9\.]+)\s*(?P<unit_rh>\w+)\s*"
                      "\((?P<location_rh>\w+)\)\s*(?P<subs>.*)")

SUBCONV_PAT = re.compile(r"\s*(?P<op>[\-,+])\s*(?P<amount>[0-9\.]+)\s*"
                         "(?P<unit>\w+)\s*\((?P<location>\w+)\)")


class Command(BaseCommand):

    _usage = "import_conversions <filename>"
    args = "filename"
    help = """ Import conversions from text files

    %s
    """ % _usage

    def add_arguments(self, parser):

        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):

        with open(options['filename'], 'r') as of:
            for line in [line for line in of if line.strip()]:

                res = CONV_PAT.match(line)

                if res:
                    for sub in SUBCONV_PAT.finditer(res.group('subs')):

                        print(sub.group('op'))

                    # Find units

                    Conversion.objects.create(
                        from_amount=res.group('amount_lh'),
                        to_amount=res.group('amount_rh'),
                        from_unit=res.group('unit_lh'),
                        to_unit=res.group('unit_rh'),
                        marker=res.group('op')
                    )
