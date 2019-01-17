from django.test import TestCase
from unicorn.models.unit import BaseUnit, LocalUnit
from unicorn.models.location import Location
from unicorn.models.conversion import Conversion
from unicorn.models.expression import SubConversion
from unicorn.models.material import Material


class TestSubConversion(TestCase):

    def setUp(self):

        self.gerst = Material.objects.create(name="Gerst")

        gent = Location.objects.create(name="Gent")
        mud = BaseUnit.objects.create(name="Mud")
        halster = BaseUnit.objects.create(name="Halster")
        mueken = BaseUnit.objects.create(name="Mueken")

        self.gentse_mud = LocalUnit.objects.create(
            unit=mud,
            location=gent)

        gentse_halster = LocalUnit.objects.create(
            unit=halster,
            location=gent)

        self.gentse_mueken = LocalUnit.objects.create(
            unit=mueken,
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
