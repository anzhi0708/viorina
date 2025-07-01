import random

from .descriptor_basics import FloatTypeDescriptor


class Float(FloatTypeDescriptor):
    def __init__(
        self,
        max_decimal_places: int,
        min_decimal_places: int,
        max_value: float,
        min_value: float,
    ) -> None:
        if max_value < min_value or max_decimal_places < min_decimal_places:
            raise ValueError("Max value is smaller than min value")

        self.max_value: float = max_value
        self.min_value: float = min_value
        self.max_decimal_places: int = max_decimal_places
        self.min_decimal_places: int = min_decimal_places

    def get_value(self) -> float:
        random_float: float = random.uniform(self.min_value, self.max_value)
        decimal_places: int = random.randint(
            self.min_decimal_places, self.max_decimal_places
        )
        return round(random_float, decimal_places)

    def __get__(self, obj, tp) -> float:
        return self.get_value()

    def __set__(self, obj, value):
        raise AttributeError("this is a read-only random float field")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(min_value={self.min_value}, max_value={self.max_value}, min_decimal_places={self.min_decimal_places}, max_decimal_places={self.max_decimal_places})"
