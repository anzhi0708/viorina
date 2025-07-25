```plaintext
  _     _ _             _             
(_)   (_|_)           (_)            
 _     _ _  ___   ____ _ ____  _____ 
| |   | | |/ _ \ / ___) |  _ \(____ |
 \ \ / /| | |_| | |   | | | | / ___ |
  \___/ |_|\___/|_|   |_|_| |_\_____|
                                     
Light-weight minimal API Fuzzer in Python
```
![PyPI](https://img.shields.io/pypi/v/viorina)

**Viorina** is a minimalist, lightweight API-fuzzing tool.  
Describe your payload once—Viorina generates compliant, random test data for you.

#### It stays tiny

* **Declarative schemas** – Register any model with `@Viorina.payload` (FastAPI-style, zero boiler-plate).  
* **Descriptor magic** – Python’s descriptor protocol auto-wires parent/child fields, so you don’t have to.  
* **Accurate text fuzzing** – Uses the Rust crate **`regex-generate`** to create strings that match your exact pattern.

# Installation
```bash
pip install viorina
```

# Examples
#### Use `@app.payload` to register
- Describe your payload structure and call `Viorina.build_dict()` at the end
```python
import viorina            # For `app = viorina.Viorina()`
from viorina import Auto
# `Auto`: A placeholder for an attribute whose schema may be defined later. Useful for recursive or deferred schema definitions.

app = viorina.Viorina()


# Use `app.payload` to register
@app.payload
class Root:           # ... its child node `BranchA` not defined yet ...
    BranchA = Auto()  # => {"Root": { "BranchA": { ... } } }
    Name = "Anji"     # => {"Root": { "Name": "Anji", "BranchA": { ... } } }
    

@app.payload
class BranchA:        # ... the node `BranchA` defined later ...
    Age = 233         # => { "BranchA": { "Age": 233 } }
    

p = app.build_dict()  # ... build payload

# 
# {'Root': 
#     {'Name': 'Anji', 
#      'BranchA': {'Age': 233}
#     }
# }
```
#### Use descriptors to generate random data for fuzz testing
- Use `Float`, `Text`, `Integer`, `Auto` descriptors to generate **random** mock values
```python
# Available descriptors: `Float`, `Text`, `Integer`, `Auto`
from viorina import Text, Integer, Auto, Viorina


app = Viorina()


@app.payload
class Root:

    SomeNode = Auto()  # `Auto`: A placeholder for an attribute whose schema may be defined later. Useful for recursive or deferred schema definitions.

    RandomValue = Integer(min_value=233, max_value=235)

    # Note: When using `Auto`, the attribute name must correspond to an existing or non-existing Python class that can be registered as a payload.
    # This allows `Auto` to act as a forward reference to nested or recursive schemas.

@app.payload
class SomeNode:

    RandomName = Text(regex=r'[AEIOU][aeiou][rnmlv][aeiou]{2}')  # The `Text` descriptor takes a regex pattern

    ChildNode = Auto()

    RandomValue = Integer(min_value=0, max_value=9)  # The `Integer` descriptor


@app.payload
class ChildNode:

    ConstValue: int = 233  # A regular integer


# -----------------------------------------

if __name__ == "__main__":
    import pprint
    
    for _ in range(3):
        pprint.pp(app.build_dict())
        
# Output:
        
# {'Root': {'RandomValue': 235,
#           'SomeNode': {'RandomName': 'Eolee',
#                        'RandomValue': 5,
#                        'ChildNode': {'ConstValue': 233}}}}
# {'Root': {'RandomValue': 235,
#           'SomeNode': {'RandomName': 'Aarei',
#                        'RandomValue': 7,
#                        'ChildNode': {'ConstValue': 233}}}}
# {'Root': {'RandomValue': 234,
#           'SomeNode': {'RandomName': 'Uovai',
#                        'RandomValue': 1,
#                        'ChildNode': {'ConstValue': 233}}}}
```

### Available Descriptors
| Descriptor                                                               | Description                                                                                                                       | Parameters                                                                                   |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `Auto()`                                                                 | A placeholder for an attribute whose schema may be defined later. Useful for recursive or deferred schema definitions.            | *(No parameters)*                                                                            |
| `Integer(*, min_value, max_value)`                                       | Generates a random integer within the specified range (inclusive).                                                                | `min_value: int`, `max_value: int`                                                           |
| `Float(*, min_value, max_value, min_decimal_places, max_decimal_places)` | Generates a float within the range, with a random number of decimal places between `min_decimal_places` and `max_decimal_places`. | `min_value: float`, `max_value: float`, `min_decimal_places: int`, `max_decimal_places: int` |
| `Text(*, regex)`                                                         | Generates a random string that matches the given regular expression.                                                              | `regex: str`                                                                                 |
