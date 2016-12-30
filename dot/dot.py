#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

"""
Subclass Dot to use this module
"""
from collections import MutableMapping

from dot.borrowed_lazy import LazyObject, empty

import re
import threading
import abc
import weakref

# Workaround for http://bugs.python.org/issue12370
_super = super

NATIVE_ATTRS = frozenset({"_wrapped", "_item_key", "_registry", "_load_wrapper",
                          "_save", "_threadLock", "_native_attrs", "_is_setup"})


class LazyDot(LazyObject):

    "LazyDot is the actual object that gets passed around."

    def __init__(self, item, registry, load_wrapper, save):
        # Note: if you are adding attributes here, make sure to add it
        # to exceptions in __setattr__ too.
        # Otherwise you will get error: AttributeError: 'NoneType' object has
        # no attribute
        self._save = save
        self._registry = registry
        self._item_key = "%s.%s" % (registry.root_name, item)
        self._threadLock = threading.Lock()

        self._threadLock.acquire()
        self._registry.object_to_eval[id(self)] = self
        self._threadLock.release()

        self._load_wrapper = load_wrapper
        self._wrapped = empty
        _super(LazyDot, self).__init__()

    def __getattr__(self, name):
        if name in NATIVE_ATTRS:
            result = self.__dict__[name]
        elif self._wrapped is empty:
            name = self._registry._checkint(name)
            self._item_key = "%s.%s" % (self._item_key, name)

            self._threadLock.acquire()
            self._registry.object_to_eval[id(self)] = self
            self._threadLock.release()

            result = self
        else:
            try:
                result = getattr(self._wrapped, name)
            except KeyError:
                raise AttributeError(
                    "LazyDot object has no attribute '%s'" % name)
        return result

    def __setattr__(self, name, value):
        if name in NATIVE_ATTRS:
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__[name] = value
        else:
            self._item_key = "%s.%s" % (self._item_key, name)
            try:
                self._save(self._item_key, value)
            except:
                raise
            else:
                self._registry.evaluated_items[self._item_key] = value

    def __setitem__(self, item, value):
        if self._wrapped is empty:
            self._setup()
        self._wrapped[item] = value

    def __getitem__(self, item):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped[item]

    def __repr__(self):
        if self._wrapped is empty:
            # maybe object is already evaluted:
            try:
                repr_attr = self._wrapped = self._registry.evaluated_items[
                    self._item_key]
            except KeyError:
                repr_attr = '<Lazy object: %s>' % self._item_key
        else:
            repr_attr = self._wrapped
        return '%s' % repr_attr

    def _setup(self):
        try:
            self._wrapped = self._registry.evaluated_items[self._item_key]
        except KeyError:
            self._load_wrapper()
            self._wrapped = self._registry.evaluated_items[self._item_key]


class Registry(object):

    'Instance of Registry contains all lazy and retrieved objects per Dot object.'

    def __init__(self, root_name, int_starts_with):
        # dict of {'id': obj } for items to be evaluated eventually.
        self.object_to_eval = weakref.WeakValueDictionary()
        self.evaluated_items = {}  # dict of {'path': evaluated object}
        self.root_name = root_name
        self.int_regex = re.compile('^{}([\d]+)$'.format(int_starts_with))

    def __repr__(self):
        return '''object_to_eval: %s \n evaluated_items: %s''' % (
            [i._item_key for i in self.object_to_eval.values()],
            self.evaluated_items)

    def _checkint(self, item):
        """
        Gets int value from item name.
        Bascially Python does not let you have attribute names
        that are integer.
        Here we check to see if the attribute name is `int_starts_with` + integer.
        Then extract the integer part.
        """
        try:
            item = self.int_regex.search(item).group(1)
        except AttributeError:
            pass
        return item


class Dot(object):

    r"""
    Dot Notation Object.

    Dot lets you define objects in dot notation format and load/save them to external resource when needed.

    **Background**

    Dot Notation object was originally designed to be the base library for a Redis client for Python. Thus the names 'load' and 'save' come from. The idea was to have python object that simply by writing obj.item="value", it sets the redis key "obj.item" with "value" value.
    And as soon as it detects you are retrieving the value, it gets the latest version from Redis. But in the mean time, it gives you a lazy object till it actually needs the value from Redis.

    So the Dot notation object is basically a lazy object that once its "load" and "save" methods are defined, it will run those methods when the object is saved or retrieved.

    **Parameters**

    root_name : String, Optional.
        It is used to overwrite the Dot object root name.

    int_starts_with: String, Optional. Default: i
        It is used to idefntify integer parts since Python does not let integers as attributes.

    **Returns**

    A lazy object that will be evaluated when it is actually used.

    **Examples**

    Defining your own Dot
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

    Creating a Dot object
        >>> this = This()
        >>> aa = this.part1.part2.part3.part4
        >>> aa
        <Lazy object: this.part1.part2.part3.part4>
        >>> print(aa)
        value this.part1.part2.part3.part4
        >>> aa
        value this.part1.part2.part3.part4

    Dot objects get evaluated in a batch
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

    Dealing with paths that have integers as a part
        >>> bb = this.part1.part2.i120
        >>> bb
        <Lazy object: this.part1.part2.120>
        >>> print bb
        value this.part1.part2.120

    Dealing with Dots like dictionary keys
        >>> cc = this['part1.part2.part4']
        >>> cc
        <Lazy object: this.part1.part2.part4>
        >>> dd = this['part1.%s.part4' % 100]
        >>> dd
        <Lazy object: this.part1.100.part4>

    Saving Dots
        >>> this.part1.part2.part3.part4 = "new value"
        >>> zz = this.part1.part2.part3.part4
        >>> zz
        new value

    Changing Root name
        >>> class That(This):
        ...    pass
        >>> that = That()
        >>> aa = that.something
        >>> print(aa)
        value that.something
        >>> bb = this.something
        >>> bb
        <Lazy object: this.something>

    Flushing cache
        >>> aa = this.part1
        >>> print aa
        value this.part1
        >>> bb = this.part1 # reads from the cache
        >>> this.flush()
        >>> bb = this.part1 # Will evaluate this.part1 again
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, root_name=None, int_starts_with='i'):
        root_name = root_name if root_name else self.__class__.__name__.lower()
        self._registry = Registry(
            root_name=root_name, int_starts_with=int_starts_with)
        self._threadLock = threading.Lock()
        self._is_setup = False

    def setup(self):
        """
        Add current items in self to native attrs so
        they are handled properly vs. attributes added later
        which are dot notation objects as immediate children
        of dot.
        """
        global NATIVE_ATTRS
        NATIVE_ATTRS = frozenset(NATIVE_ATTRS | set(self.__dict__.keys()))
        self._is_setup = True

    def _lazyget(self, item):
        item = self._registry._checkint(item)
        child = LazyDot(
            item, registry=self._registry, load_wrapper=self._load_wrapper, save=self.save)
        return child

    def _lazyset_immediate_child(self, item, value):
        item = self._registry._checkint(item)
        item = "%s.%s" % (self._registry.root_name, item)
        try:
            self.save(item, value)
        except:
            raise
        else:
            self._registry.evaluated_items[item] = value

    def __getattr__(self, item):
        return self._lazyget(item)

    def __getitem__(self, item):
        return self._lazyget(item)

    def __setattr__(self, item, value):
        if item in NATIVE_ATTRS or not self._is_setup:
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__[item] = value
        else:
            self._lazyset_immediate_child(item, value)

    __setitem__ = __setattr__

    def _load_wrapper(self):
        self._threadLock.acquire()
        paths_to_eval = tuple(
            set(i._item_key for i in self._registry.object_to_eval.values()))
        self._registry.object_to_eval = weakref.WeakValueDictionary()

        new_items = self.load(paths_to_eval)

        if isinstance(new_items, MutableMapping):
            self._registry.evaluated_items.update(new_items)
            self._threadLock.release()
        else:
            self._threadLock.release()
            raise Exception(
                "load method needs to return a dictionary of {path: value}")

    @abc.abstractmethod
    def load(self, paths):
        """
        Must be implemented by subclasses.
        All Dot objects are lazy loaded. Once the object needs to actually be used,
        it gets evaluated. The load method here is what is used to evaluate a batch
        of object paths.

        **Parameters**

        paths : List of paths.
            The load method should get a list of paths to be loaded and return a dictionary
            of {path: value}
        """
        return

    def save(self, path, value):
        """
        Must be implemented by subclasses.

        The save method is called to save a value for a path.

        **Parameters**

        path : String.

        value: Can be any Python object.
        """
        raise Exception(
            "Save function must be implemented before you can use it.")

    def flush(self):

        "Emptys the Dot cache"

        self._registry.evaluated_items = {}

if __name__ == "__main__":
    import doctest
    doctest.testmod()
