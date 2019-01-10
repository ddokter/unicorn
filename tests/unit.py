from django.test import TestCase
from unicorn.models.unit import Unit
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

        for conv in paths[0]:

            print(conv)

        print("Precision: %.4f" % paths[0].precision)

        self.assertAlmostEqual(paths[0].factor, 8.45, 2)
