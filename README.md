# PyProfiler
[![build status][buildstatus-image]][buildstatus-url]

[buildstatus-image]: https://github.com/Spill-Tea/PyProfiler/actions/workflows/python-package.yml/badge.svg?branch=main
[buildstatus-url]: https://github.com/Spill-Tea/PyProfiler/actions?query=branch%3Amain

A Simple cProfiler Wrapper to debug Functions toggled by user defined Keyword Argument

1. [About](#about)
2. [Example](#example)
3. [Usage](#usage)
    1. [Multiple Decorators](#multiple-decorators)
    2. [Output](#output)
4. [License](#license)

## About
PyProfiler is A Simple cProfile Wrapper to debug any Python Function.
Profiling is toggled by an argument of the function it wraps. By default,
the keyword argument is `debug`, but may be modified according to user
specification. If the user defined keyword is an argument in the
wrapped function and is set to True (either by default or during use),
the function will be profiled (and provide output).

## Example
Here is a simple example of a function which adds two elements.
```python
from PyProfiler import Profiler

@Profiler(keyword='profile', filepath=None, mode='a')
def add(a, b, profile: bool = True):
    return a + b

print(add(1, 2) == 3)  # Function is Profiled (default is True)
print(add(1, 2, False) == 3)  # Function is Not Profiled (Positional Argument)
print(add(1, 2, profile=False) == 3)  # Function is Not Profiled (Keyword Argument)

```

## Usage
### Multiple Decorators
When a function requires multiple decorators, use this Profiler decorator
as the bottom most layer, since its function depends on introspection of the
intended method (i.e. make certain PyProfiler.Profile is the first wrapper).

```python
from PyProfiler import Profiler

class Example:
    _class_attribute = []
    def __init__(self, arg: int):
        self.arg = arg

    @staticmethod
    @Profiler(keyword='debug')
    def add(debug, *args):
        return sum(args)

    @classmethod
    @Profiler(keyword='profile')
    def new(cls, arg: int, profile=True):
        cls._class_attribute.append(arg)
        print(cls._class_attribute)
        return cls(arg)

# Show Behavior of Staticmethod
example = Example(1)
result = example.add(True, 10, 5, 15)  # Function is Profiled, Returns 30
result_static = Example.add(True, 10, 5, 15)  # Still behaves as static, Returns 30

# Show Behavior of ClassMethod
example_2 = example.new(arg=2, profile=True)  # Profiled. Still accesses intended class attributes
print(isinstance(example_2, Example))

```

### Output
The profile streams to stdout by default (when filepath = None), but can be modified
to stream output to a file by altering the filepath attribute in the decorator. Furthermore,
you may change how the data is output (text or binary, write or append) via the mode attribute.
```python
from PyProfiler import Profiler

class Example:
    @Profiler(keyword='debug', filepath='function.prof', mode='ab')
    def function(self, debug, *args):
        return sum(args)

```

## License
[MIT](./LICENSE)