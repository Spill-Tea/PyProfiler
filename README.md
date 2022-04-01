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
```python
from PyProfiler import Profiler

@Profiler(keyword='profile', filepath=None, mode='a')
def add(*args, profile: bool = False):
    return sum(*args)

add(1, 2, 5, 9, 10) # Function is not Profiled (default is False)
add(1, 2, 5, 9, 10, profile=False) # Function is not Profiled
add(1, 2, 5, 9, 10, profile=True)  # Function is Profiled
```

## Usage
### Multiple Decorators
When a function requires multiple decorators, use this Profiler decorator
as the bottom most layer, since its function depends on introspection of the
intended method.
```python
class Example:
    @staticmethod
    @Profiler(keyword='debug')
    def function(*args, debug=True):
        return sum(*args)
```

### Output
The profile streams to stdout by default (when filepath = None), but can be modified
to stream output to a file by altering the filepath attribute in the decorator. Furthermore,
you may change how the data is output (text or binary, write or append) via the mode attribute.
```python
class Example:
    @Profiler(keyword='debug', filepath='function.prof', mode='ab')
    def function(self, *args, debug=True):
        return sum(*args)
```

## License
[MIT](./LICENSE)