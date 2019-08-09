from django.test import TestCase
from unicorn.models.unit import BaseUnit, LocalUnit
from unicorn.models.location import Location
from unicorn.models.conversion import Conversion
from unicorn.models.material import Material


class TestUnit(TestCase):

    def setUp(self):

        groningen = Location.objects.create(name="Groningen")
        utrecht = Location.objects.create(name="Utrecht")
        amersfoort = Location.objects.create(name="Amersfoort")
        delft = Location.objects.create(name="Delft")
        amsterdam = Location.objects.create(name="Amsterdam")

        mud = BaseUnit.objects.create(name="Mud")
        hoed = BaseUnit.objects.create(name="Hoed")
        pond = BaseUnit.objects.create(name="Pond")
        spond = BaseUnit.objects.create(name="Schippond")
        self.kilo = BaseUnit.objects.create(name="Kilo")
        self.liter = BaseUnit.objects.create(name="Liter")

        self.groningse_mud = LocalUnit.objects.create(
            unit=mud,
            location=groningen)

        self.utrechtse_mud = LocalUnit.objects.create(
            unit=mud,
            location=utrecht)

        self.amersfoortse_mud = LocalUnit.objects.create(
            unit=mud,
            location=amersfoort)

        self.delftse_hoed = LocalUnit.objects.create(
            unit=hoed,
            location=delft)

        self.groningse_pond = LocalUnit.objects.create(
            unit=pond,
            location=groningen)

        self.amsterdamse_schippond = LocalUnit.objects.create(
            unit=spond,
            location=amsterdam)

        self.amsterdamse_pond = LocalUnit.objects.create(
            unit=pond,
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

        self.assertAlmostEqual(paths[0].factor, 8.45, 2)
        self.assertAlmostEqual(paths[0].precision, 0.80, 2)
