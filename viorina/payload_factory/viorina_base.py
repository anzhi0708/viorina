from typing import Optional, Any, TypedDict
import inspect

from viorina.descriptors.descriptor_basics import ViorinaDescriptor


__all__ = (
    "Auto",
    "Viorina",
)


class NodeSchema(TypedDict):
    attrs: dict[str, Any]
    children: dict[type, "NodeSchema"]


class Auto(ViorinaDescriptor):
    """
    `Auto` is a context-aware descriptor that stores metadata for later resolution.

    For parsing and building correct parent-child relations (a graph),
    `Auto` collects the parent class(by type handler) and
    its maybe undefined child class(by class name, in string, through `__set_name__`)
    and sends them to the Viorina app instance.

    The communication/bind between `Auto` and the `Viorina` singleton app instance is possible
    because when using `Viorina.payload` decorator to mark a schema definition,
    the `Viorina` app instance was injected into the schema type.

    By the end of all schema definitions, the `Viorina` app instance will have all the
    needed type informations, thus resolve-by-class-name-string was made possible
    (forward declaration/lazy resolution).

    Example:

    ```python
    app = Viorina()

    @app.payload            # `Node` class will have `__viorina_app__` set to `app` instance
    class Node:
        name = Text(regex=r'[A-Z]')
        ChildNode = Auto()                  # class `ChildNode` will have parent node `Node`

    # A node can have multiple parent nodes
    @app.payload
    class AnotherNode:
        ChildNode = Auto()  # class `ChildNode` will add a parent node `AnotherNode`

    @app.payload
    class ChildNode:
        data = ...
    ```

    """

    def __init__(self) -> None:
        """
        ```
        @app.payload
        class ParentClass:
            ClassName = Auto()  # `Auto` detects `ClassName` and stores it as a string since **typeof ClassName**
                                # can be undefined during this stage (so that it could not be resolved as a type).
        ```
        """
        self.class_name: Optional[str] = None  # Attribute name, this is a string
        self.annotation_type: Optional[type] = None  # a type
        self.parent_class: Optional[type] = None  # also a type

    def __set_name__(self, parent_class: type, class_name: str):
        """
        Parent-child relationships are detected
        """
        self.parent_class = parent_class
        self.class_name = class_name
        annotation = inspect.get_annotations(self.parent_class, eval_str=True)
        self.annotation_type = annotation.get(self.class_name)

    def __get__(self, instance, owner_type) -> Optional[type]:
        """
        Returns the actual resolved type(handler) of a ClassName.
        """
        # A `Viorina` app instance uses `payload` method to inject itself to a schema class.
        app: Optional[Viorina] = getattr(self.parent_class, "__viorina_app__", None)

        if app is None:
            raise RuntimeError(
                f"{self.parent_class} is not associated with any Viorina instances"
            )

        if not self.class_name:
            raise RuntimeError("self.class_name not initialized")

        handler = app.get_type_handler_by_name(self.class_name)

        if handler is None:
            app._resolve_edges()
            handler = app.get_type_handler_by_name(self.class_name)
        
        if handler is None:
            raise LookupError(
                f"Could not find type {self.class_name!r} in registered types"
            )

        return handler


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
        self.__registered_types: dict[str, type] = {}
        self.__edges: set[tuple[type, type]] = (
            set()
        )  # Parent-child relationships are stored here
        self.__pending_edges: set[tuple[type, str]] = (
            set()
        )  # When have lazy evaluated types

    def _resolve_edges(self) -> None:
        if not self.__pending_edges:
            return
        for parent, child_name in list(self.__pending_edges):
            child_type_handler = self.get_type_handler_by_name(child_name)
            if child_type_handler:
                self.add_edge(parent, child_type_handler)
                self.__pending_edges.remove((parent, child_name))
            else:
                raise LookupError(f"{child_name!r} is not a registered schema type")

    def add_edge(self, parent: type, child: type) -> None:
        self.__edges.add((parent, child))

    def add_pending_edge(self, pending: tuple[type, str]) -> None:
        self.__pending_edges.add(pending)

    def build_tree(self) -> dict[type, NodeSchema]:
        self._resolve_edges()

        children_handlers = {c for _, c in self.__edges}
        root_handlers = [
            v for v in self.__registered_types.values() if v not in children_handlers
        ]

        def sub_tree(cls: type) -> NodeSchema:
            attrs: dict[str, Any] = {}
            children: dict[type, Any] = {}

            for name, val in cls.__dict__.items():
                # (1) Reference to other user-defined classes
                if isinstance(val, Auto):
                    assert val.class_name is not None
                    child_class_handler = self.get_type_handler_by_name(val.class_name)
                    assert child_class_handler is not None
                    children[child_class_handler] = sub_tree(child_class_handler)

                # (2) Other Viorina descriptors
                elif isinstance(val, ViorinaDescriptor):
                    attrs[name] = val.__get__(None, cls)

                # (3) Const values
                elif not name.startswith("__") and not callable(val):
                    attrs[name] = val

            # return {"attrs": attrs, "children": children}
            return NodeSchema(attrs=attrs, children=children)

        return {r: sub_tree(r) for r in root_handlers}

    def payload(self, cls):
        """
        Registers a class(type), also binds the `Viorina` instance to the type.

        1. User Defined Schema Class That Needs To Be Lazily Resoluted

            Marked with `Viorina.payload` decorator to be registered as a schema type.
            `Auto`s can be used to refer to other schema types that not yet exist.
            Registered to (2) and contains multiple (3)s.

        2. Viorina Singleton App Object That Collects All Types At the End

            Holds a bunch of (1)s and will be used by (3) to resolve to actual types.

        3. The `Auto` Descriptor That Carries (1)'s Type Name

            Included within (1) and depends on (2) to resolve actual types.

                ┌───────────────┐
                │ @app.payload  │
                │ class Schema: │
                └───────────────┘
                 ▲             │ registers
                 │contained    │ types to
                 │             ▼
        ┌───────────┐ ── resolve ─── ┌───────────────┐
        │ X = Auto()│     lookup     │app = Viorina()│
        └───────────┘ ─── holds ──── └───────────────┘

        """
        # Collects the actual type handler
        self.__registered_types[cls.__name__] = cls

        # Injects the app into schema class, can be considered a namespace-like thing
        # Through the app instance, an actual type can be found using its qualname(in string)
        # Because an `Auto` can only hold the string representation of a child schema class.
        #
        # 1. During class creation `Auto.__set_name__()` stores
        #    `self.parent_class = ParentSchema`.
        # 2. On first attribute access, `Auto.__get__()` does:
        #    app = self.parent_class.__viorina_app__
        #    handler = app.get_type_handler_by_name            <--- These 2 lines
        # 3. `app` looks up its registered types and
        #    gives back the actual type handler.
        cls.__viorina_app__ = self

        for name, attr in cls.__dict__.items():
            if isinstance(attr, Auto) and attr.class_name:
                self.__pending_edges.add((cls, attr.class_name))

        return cls

    def get_type_handler_by_name(self, tp_name_str: str) -> Optional[type]:
        return self.__registered_types.get(tp_name_str)

    def get_registered_types(self) -> dict[str, type]:
        return self.__registered_types

    def build_dict(self) -> dict:
        """
        将内部树状结构序列化为层级 JSON 字符串。

        返回示例（假设 Root → OrderInfo → Product）::

            {
              "Root": {
                "OrderInfo": {
                  "HblNo": "<Text>",
                  "Products": {
                    "Product": {
                      "ItemName": "<Text>",
                      "Price": "<Float>"
                    }
                  }
                }
              }
            }

        - ViorinaDescriptor 实例会被转成 ``"<DescriptorClassName>"`` 占位文本；
        - 常量会原样放入；
        - ``indent``/``ensure_ascii`` 直接透传给 ``json.dumps``。
        """
        tree = self.build_tree()

        def node_to_dict(ns: NodeSchema) -> dict[str, Any]:
            # 这里 attrs 里已经是最终值，直接拷贝
            out: dict[str, Any] = dict(ns["attrs"])

            # 递归 children
            for child_cls, child_ns in ns["children"].items():
                out[child_cls.__name__] = node_to_dict(child_ns)
            return out

        return {root.__name__: node_to_dict(ns) for root, ns in tree.items()}
