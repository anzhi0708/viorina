from regex_generate_py import generate

from .descriptor_basics import TextTypeDescriptor


class Text(TextTypeDescriptor):
    def __init__(self, regex: str):
        self.regex: str = regex

    def regex_generate(self) -> str:
        return generate(self.regex)

    def get_value(self) -> str:
        return self.regex_generate()

    def __get__(self, obj, tp) -> str:
        return self.get_value()

    def __set__(self, obj, value):
        raise AttributeError("read-only descriptor field")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(regex={self.regex})"
