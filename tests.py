from django.test import TestCase
from unicorn.models.unit import Unit
from unicorn.models.location import Location
from unicorn.models.conversion import Conversion
from unicorn.models.expression import SubConversion
from unicorn.models.material import Material


class TestUnit(TestCase):

    def setUp(self):

        groningen = Location.objects.create(name="Groningen")
        utrecht = Location.objects.create(name="Utrecht")
        amersfoort = Location.objects.create(name="Amersfoort")
        delft = Location.objects.create(name="Delft")
        amsterdam = Location.objects.create(name="Amsterdam")

        self.groningse_mud = Unit.objects.create(
            name="Mud",
            location=groningen)

        self.utrechtse_mud = Unit.objects.create(
            name="Mud",
            location=utrecht)

        self.amersfoortse_mud = Unit.objects.create(
            name="Mud",
            location=amersfoort)

        self.delftse_hoed = Unit.objects.create(
            name="Hoed",
            location=delft)

        self.liter = Unit.objects.create(name="Liter")

        self.groningse_pond = Unit.objects.create(
            name="Pond",
            location=groningen)

        self.kilo = Unit.objects.create(name="Kilo")

        self.amsterdamse_schippond = Unit.objects.create(
            name="Schippond",
            location=amsterdam)

        self.amsterdamse_pond = Unit.objects.create(
            name="Pond",
            location=amsterdam)

        Conversion.objects.create(
            from_unit=self.delftse_hoed,
            from_amount=1.0,
            to_unit=self.utrechtse_mud,
            to_amount=9)

        Conversion.objects.create(
            from_unit=self.delftse_hoed,
            from_amount=1.0,
            to_unit=self.amersfoortse_mud,
            to_amount=7.5)

        Conversion.objects.create(
            from_unit=self.delftse_hoed,
            from_amount=1.0,
            to_unit=self.liter,
            to_amount=1120)

        Conversion.objects.create(
            from_unit=self.utrechtse_mud,
            from_amount=1,
            to_unit=self.liter,
            to_amount=123)

        Conversion.objects.create(
            from_unit=self.groningse_pond,
            from_amount=1,
            to_unit=self.kilo,
            to_amount=0.494)

        Conversion.objects.create(
            from_unit=self.amsterdamse_pond,
            from_amount=1,
            to_unit=self.kilo,
            to_amount=0.494)

        Conversion.objects.create(
            from_unit=self.amsterdamse_schippond,
            from_amount=1,
            precision=1,
            to_unit=self.amsterdamse_pond,
            to_amount=300)

        Conversion.objects.create(
            from_unit=self.amsterdamse_schippond,
            from_amount=1,
            to_unit=self.utrechtse_mud,
            to_amount=13)

        Conversion.objects.create(
            from_unit=self.amsterdamse_schippond,
            from_amount=1,
            to_unit=self.amersfoortse_mud,
            to_amount=9)

        Conversion.objects.create(
            from_unit=self.groningse_mud,
            from_amount=1,
            to_unit=self.liter,
            to_amount=91.2)

    def test_y(self):

        hop = Material.objects.filter(name="hop").first()

        paths = self.groningse_mud.find_conversion_paths(self.kilo, hop)

        factor = 1
        precision = 1

        for conv in paths[0]:

            _factor = conv.resolve(hop)
            precision *= conv.get_precision()

            if conv.reverse:
                factor /= _factor
            else:
                factor *= _factor

            print("%s - r: %s -> %.4f (%.4f)" % (
                conv, conv.reverse, factor, conv.get_precision()))

        print("Precision: %.4f" % precision)

        self.assertAlmostEqual(factor, 8.45, 2)


class TestExpression(TestCase):

    def setUp(self):

        self.gerst = Material.objects.create(name="Gerst")

        gent = Location.objects.create(name="Gent")

        self.gentse_mud = Unit.objects.create(
            name="Mud",
            location=gent)

        gentse_halster = Unit.objects.create(
            name="Halster",
            location=gent)

        self.gentse_mueken = Unit.objects.create(
            name="Mueken",
            location=gent)

        self.gentse_mud_halster = Conversion.objects.create(
            from_unit=self.gentse_mud,
            to_unit=gentse_halster,
            to_amount=12)

        self.gentse_halster_mueken = Conversion.objects.create(
            from_unit=gentse_halster,
            to_unit=self.gentse_mueken,
            to_amount=4)

        self.gentse_mud_halster.material.add(self.gerst)
        self.gentse_halster_mueken.material.add(self.gerst)

        SubConversion.objects.create(
            amount=2,
            conversion=self.gentse_mud_halster,
            unit=self.gentse_mueken,
            operator="+"
        )

    def test_resolve(self):

        self.assertAlmostEqual(12.5, self.gentse_mud_halster.resolve(
            self.gerst), 2)
