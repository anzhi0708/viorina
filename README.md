```plaintext
  _     _ _             _             
(_)   (_|_)           (_)            
 _     _ _  ___   ____ _ ____  _____ 
| |   | | |/ _ \ / ___) |  _ \(____ |
 \ \ / /| | |_| | |   | | | | / ___ |
  \___/ |_|\___/|_|   |_|_| |_\_____|
                                     
Light-weight minimal API Fuzzer in Python
```

# Examples
```pycon
>>> import viorina
>>> from viorina import Auto
>>>
>>> app = viorina.Viorina()
>>>
>>> @app.payload
... class Root:
...     BranchA = Auto()
...     Name = "Anji"
...     
>>> @app.payload
... class BranchA:
...     Age = 233
...     
>>> app.build_dict()
{'Root': {'Name': 'Anji', 'BranchA': {'Age': 233}}}
>>> 
```
