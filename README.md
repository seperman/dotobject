# DotObject v1.2.0
Dot Notation Object

![Python Versions](https://img.shields.io/pypi/pyversions/dotobject.svg?style=flat)
[![Documentation Status](https://readthedocs.org/projects/dotobject/badge/?version=latest)](http://dotobject.readthedocs.org/en/latest/?badge=latest)
![License](https://img.shields.io/pypi/l/dotobject.svg?version=latest)
[![Build Status](https://travis-ci.org/seperman/dotobject.svg?branch=master)](https://travis-ci.org/seperman/dotobject)

Dot lets you define objects in dot notation format that can be loaded/saved to external resources when needed.

## Background

Dot Notation object was originally designed to be the base library for a Redis client for Python. Thus the names 'load' and 'save' come from. The idea was to have python object that simply by writing obj.item="value", it sets the redis key "obj.item" with "value" value.
And as soon as it detects you are retrieving the value, it gets the latest version from Redis. But in the mean time, it gives you a lazy object till it actually needs the value from Redis.
So the Dot notation object is basically a lazy object that once its "load" and "save" methods are defined, it will run those methods when the object is saved or retrieved.


## Installation

### Install from PyPi:

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

## Documentation

<http://dotobject.readthedocs.org/en/latest/>

## Author

Seperman (Sep Ehr)

Github:  <https://github.com/seperman>
Linkedin:  <http://www.linkedin.com/in/sepehr>
ZepWorks:   <http://www.zepworks.com>
