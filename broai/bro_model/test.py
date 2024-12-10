# # this is just for an idea testing

# from abc import ABCMeta, abstractmethod
# from typing import Any

# class ModelMetaClass(ABCMeta):
#     def __new__(cls, cls_name:str, bases:tuple, namespaces:dict, **kwargs:Any):
#         for i in [cls_name, bases, namespaces]:
#             print(type(i))
#         return super().__new__(cls, cls_name, bases, namespaces, **kwargs)
    

# from typing import overload, Union

# @overload
# def test(a: int) -> int: ...
# @overload
# def test(a: str) -> str: ...
# @overload
# def test(a: float) -> float: ...

# # Actual implementation
# def test(a: Union[int, str, float]):
#     return a

# tstr = test("a")
# tint = test(1)
# tfloat = test(0.5)

# from typing_extensions import Literal, TypeAlias, Unpack, deprecated

# from typing_extensions import Literal

# def set_status(status: Literal["active", "inactive", "pending"]) -> str:
#     return f"Status set to {status}"

# print(set_status("active"))    # Works
# print(set_status("inactive"))  # Works
# print(set_status("unknown")) # Type checker error: Invalid value

# from typing_extensions import TypeAlias

# # Define an alias for a complex type
# Coordinates: TypeAlias = tuple[float, float]

# def get_distance(point1: Coordinates, point2: Coordinates) -> float:
#     # Dummy calculation for distance
#     return ((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)**0.5

# point_a: Coordinates = (0.0, 0.0)
# point_b: Coordinates = (3.0, 4.0)

# print(get_distance(point_a, point_b))  # Output: 5.0

# from typing_extensions import Unpack, TypedDict

# class Person(TypedDict):
#     name: str
#     age: int

# def greet(**info: Unpack[Person]) -> str:
#     return f"Hello, {info['name']}! You are {info['age']} years old."

# print(greet(name="Alice", age=30))  # Output: Hello, Alice! You are 30 years old.

# from typing_extensions import deprecated

# @deprecated("Use 'new_function' instead.")
# def old_function() -> None:
#     print("This function is deprecated.")

# def new_function() -> None:
#     print("Use this function instead.")

# old_function()  # Works but will show a warning
# new_function()  # This is the preferred function
