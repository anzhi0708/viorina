from dataclasses import dataclass
from typing import Optional
import inspect

from viorina.descriptors.descriptor_basics import ViorinaDescriptor


class Auto(ViorinaDescriptor):

    def __init__(self) -> None:
        self.relationships: dict = {}

    def __set_name__(self, obj, name):
        ann: dict = inspect.get_annotations(obj, eval_str=True)
        tp: Optional[type] = ann.get(name)
        if tp is None:  # If no annotation provided, then see it as a reference to other user-defined class
            pass
        raise NotImplementedError("TODO")
            

@dataclass
class Attribute:
    name: str
    annotation: Optional[type]
    value: ViorinaDescriptor

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "annotation": self.annotation,
            "value": self.value
        }


class ViorinaAttribute(Attribute): ...


class NonViorinaAttribute(Attribute): ...


class Viorina:
    """

    ```python
    from viorina.descriptors import Text, Float
    from viorina.payload_factory import Auto, List, Viorina
    

    app = Viorina()

    @app.payload
    class Root:  # class name `Root` will be translated into element/node/key.
        '''
        This will generate something like:
        
        ```xml
        <Root>
            <OrderInfo>
                <HblNo></HblNo>
                <Products>
                    <Product></Product>
                    <Product></Product>
                </Products>
            </OrderInfo>
        </Root>
        ```

        or equivlant JSON data, depend on which method was called.
        '''
        OrderInfo = Auto()


    @app.payload
    class Product:
        ItemName = Text(regex=r'[a-zA-Z]+')
        Price = Float(min_value=0.0, max_value=999.99, min_decimal_places=2, max_decimal_places=3)


    @app.payload
    class OrderInfo:
        HblNo =  Text(regex=r'[0-9A-Z]{5,10}')
        Products: list[Product] = List(max_repeat=5)


    app.build_xml()  # or `root.build_json()`
    ```
    """
    def __init__(self) -> None:
        self.__elements: dict[str, list[Attribute]] = {}

    def payload(self, cls) -> type:
        """
        A class decorator for designing payload schema.
        """
        cls.__viorina_children__ = []
        
        # Initialize a node/element/field
        if cls.__qualname__ not in self.__elements.keys():
            self.__elements[cls.__qualname__] = []
            
        for name, value in cls.__dict__.items():
            if name.startswith("__"):  # Skip if it's private
                continue

            if isinstance(value, ViorinaDescriptor):
                element = \
                    ViorinaAttribute(
                        name = name,
                        value = value,
                        annotation = inspect.get_annotations(cls, eval_str=True).get(name)
                    )
            else:
                element = \
                    NonViorinaAttribute(
                        name = name,
                        value = value,
                        annotation = inspect.get_annotations(cls, eval_str=True).get(name)
                    )

            self.__elements[cls.__qualname__].append(element)

        return cls

    def inspect(self) -> dict:
        return self.__elements
