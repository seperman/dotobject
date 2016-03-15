# DotObject v1.0.0
Dot Notation Object

![Python Versions](https://img.shields.io/pypi/pyversions/dotobject.svg?style=flat)
![Doc](https://readthedocs.org/projects/dotobject/badge/?version=latest)
![License](https://img.shields.io/pypi/l/dotobject.svg?version=latest)
[![Build Status](https://travis-ci.org/seperman/dotobject.svg?branch=master)](https://travis-ci.org/seperman/dotobject)

Dot lets you define objects in dot notation format.

You need to subclass Dot and define your own load and save methods in order to use it.


##Installation

###Install from PyPi:

    pip install dotobject

## Examples

Defining your own Dot.
This is done by subclassing Dot class and defining at least the load method.


```python
>>> from dot import Dot
>>> class This(Dot):
...     def __init__(self, *args, **kwargs):
...         super(This, self).__init__(*args, **kwargs)
...         self.items = {}
...     def load(self, paths):
...         return {i: self.items[i] if i in self.items else "value %s" % i for i in paths}
...     def save(self, path, value):
...         self.items[path] = value
... 
```

### Creating a Dot object

```python
>>> this = This()
>>> aa = this.part1.part2.part3.part4
>>> aa
<Lazy object: this.part1.part2.part3.part4>
>>> print(aa)
value this.part1.part2.part3.part4
>>> aa
value this.part1.part2.part3.part4
```

### Dot objects get evaluated in a batch

```python
>>> this = This()
>>> aa = this.part1
>>> aa
<Lazy object: this.part1>
>>> bb = this.part2
>>> bb
<Lazy object: this.part2>
>>> print(aa)
value this.part1
>>> aa
value this.part1
>>> bb
value this.part2
```

### Dealing with paths that have integers as a part

```python
>>> bb = this.part1.part2.i120
>>> bb
<Lazy object: this.part1.part2.120>
>>> print bb
value this.part1.part2.120
```

### Dealing with Dots like dictionary keys

```python
>>> cc = this['part1.part2.part4']
>>> cc
<Lazy object: this.part1.part2.part4>
>>> dd = this['part1.%s.part4' % 100]
>>> dd
<Lazy object: this.part1.100.part4>
```

### Saving Dots

```python
>>> this.part1.part2.part3.part4 = "new value"
>>> zz = this.part1.part2.part3.part4
>>> zz
new value
```

### Changing Root name without redefining Dot object

```python
>>> class That(This):
...    pass
>>> that = That()
>>> aa = that.something
>>> print(aa)
value that.something
>>> bb = this.something
>>> bb
<Lazy object: this.something>
```

### Flushing cache

```python
>>> aa = this.part1
>>> print aa
value this.part1
>>> bb = this.part1 # reads from the cache
>>> this.flush()
>>> bb = this.part1 # Will evaluate this.part1 again
```