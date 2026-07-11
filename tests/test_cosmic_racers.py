import unittest
from src.games.cosmic_racers_game import Car


class TestCosmicRacersLogic(unittest.TestCase):
    def setUp(self):
        """Инициализация болида перед каждым тестом."""
        self.car = Car(start_lane=3, is_bot=False, difficulty="medium")

    def test_car_initialization(self):
        """Проверка правильности начальных параметров машины."""
        self.assertEqual(self.car.base_lane, 3)
        self.assertEqual(self.car.speed, 0.0)
        self.assertEqual(self.car.lap, 0)
        self.assertFalse(self.car.is_stunned)

    def test_acceleration_with_gas(self):
        """Проверка набора скорости при зажатом газе."""
        self.car.update(delta_time=0.1, is_pressing_space=True, total_length=1000)
        self.assertGreater(self.car.speed, 0.0)

    def test_friction_without_gas(self):
        """Проверка замедления болида под действием трения."""
        self.car.speed = 5.0
        self.car.update(delta_time=0.1, is_pressing_space=False, total_length=1000)
        self.assertLess(self.car.speed, 5.0)

    def test_lap_increment(self):
        """Проверка перехода на следующий круг при пересечении финиша."""
        total_length = 500
        self.car.distance = 499
        self.car.speed = 5.0
        self.car.update(delta_time=0.1, is_pressing_space=True, total_length=total_length)
        self.assertEqual(self.car.lap, 1)
