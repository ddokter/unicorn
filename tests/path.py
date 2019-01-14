from django.test import TestCase
from unicorn.path import Path
from unicorn.models.conversion import Conversion
from unicorn.models.unit import Unit, LocalUnit
from unicorn.models.location import Location
from unicorn.models.material import Material


class TestPath(TestCase):

    def setUp(self):

        self.hop = Material.objects.filter(name="hop").first()

        delft = Location.objects.create(name="Delft")

        self.delftse_hoed = LocalUnit.objects.create(
            name="Hoed",
            location=delft)

        self.liter = Unit.objects.create(name="Liter")

        self.path = Path(self.delftse_hoed, self.liter, self.hop)

        self.conversion = Conversion.objects.create(
            from_unit=self.delftse_hoed,
            from_amount=1,
            to_unit=self.liter,
            to_amount=100)

    def test_init(self):

        self.assertEquals(self.path.precision, 1)
        self.assertEquals(self.path.factor, 1)

    def test_append(self):

        self.assertEquals(self.path.precision, 1)

        self.conversion.precision = 0.9

        self.path.append(self.conversion)

        self.assertEquals(self.path.precision, 0.9)

        self.path.append(self.conversion)

        self.assertEquals(self.path.precision, 0.81)

    def test_copy(self):

        self.conversion.precision = 0.9
        self.path.append(self.conversion)

        new = self.path.copy()
        self.assertNotEquals(id(self.path), id(new))

        self.assertEquals(len(self.path), len(new))

        self.assertEquals(self.path.material, new.material)
        self.assertEquals(self.path.precision, new.precision)
        self.assertEquals(self.path.factor, new.factor)
