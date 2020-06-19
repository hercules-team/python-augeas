"""
Augeas is a library for programmatically editing configuration files.
Augeas parses configuration files into a tree structure, which it exposes
through its public API. Changes made through the API are written back to
the initially read files.

The transformation works very hard to preserve comments and formatting
details. It is controlled by *lens* definitions that describe the file
format and the transformation into a tree.
"""

#
# Copyright (C) 2008 Nathaniel McCallum
# Copyright (C) 2008 Jeff Schroeder <jeffschroeder@computer.org>
# Copyright (C) 2009 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Author: Nathaniel McCallum <nathaniel@natemccallum.com>

from sys import version_info as _pyver

from augeas.ffi import ffi, lib

__author__ = "Nathaniel McCallum <nathaniel@natemccallum.com>"
__credits__ = """Jeff Schroeder <jeffschroeder@computer.org>
Harald Hoyer <harald@redhat.com> - initial python bindings, packaging
Nils Philippsen <nils@redhat.com>
"""
PY3 = _pyver >= (3,)
AUGENC = 'utf8'

if PY3:
    string_types = str
else:
    string_types = basestring


def enc(st):
    if st:
        return st.encode(AUGENC)
    else:
        return b''


def dec(st):
    if st:
        return st.decode(AUGENC)
    else:
        return b''


class AugeasIOError(IOError):
    def __init__(self, ec, fullmessage, msg, minor, details, *args):
        self.message = fullmessage
        super(AugeasIOError, self).__init__(fullmessage, *args)
        self.error = ec
        self.msg = msg
        self.minor = minor
        self.details = details


class AugeasRuntimeError(RuntimeError):
    def __init__(self, ec, fullmessage, msg, minor, details, *args):
        self.message = fullmessage
        super(AugeasRuntimeError, self).__init__(fullmessage, *args)
        self.error = ec
        self.msg = msg
        self.minor = minor
        self.details = details


class AugeasValueError(ValueError):
    def __init__(self, ec, fullmessage, msg, minor, details, *args):
        self.message = fullmessage
        super(AugeasValueError, self).__init__(fullmessage, *args)
        self.error = ec
        self.msg = msg
        self.minor = minor
        self.details = details


class Augeas(object):
    """
    Class wrapper for the Augeas library.
    """
    # Augeas Flags
    NONE = 0
    #: Keep the original file with a :samp:`.augsave` extension
    SAVE_BACKUP = 1 << 0
    #: Save changes into a file with extension :samp:`.augnew`, and do not
    #: overwrite the original file. Takes precedence over :attr:`SAVE_BACKUP`
    SAVE_NEWFILE = 1 << 1
    #: Typecheck lenses; since it can be very expensive it is not done by
    #: default
    TYPE_CHECK = 1 << 2
    #: Do not use the builtin load path for modules
    NO_STDINC = 1 << 3
    #: Make save a no-op process, just record what would have changed
    SAVE_NOOP = 1 << 4
    #: Do not load the tree from :func:`~augeas.Augeas`
    NO_LOAD = 1 << 5
    NO_MODL_AUTOLOAD = 1 << 6
    #: Track the span in the input of nodes
    ENABLE_SPAN = 1 << 7

    # Augeas errors
    AUG_NOERROR = 0
    AUG_ENOMEM = 1
    AUG_EINTERNAL = 2
    AUG_EPATHX = 3
    AUG_ENOMATCH = 4
    AUG_EMMATCH = 5
    AUG_ESYNTAX = 6
    AUG_ENOLENS = 7
    AUG_EMXFM = 8
    AUG_ENOSPAN = 9
    AUG_EMVDESC = 10
    AUG_ECMDRUN = 11
    AUG_EBADARG = 12
    AUG_ELABEL = 13
    AUG_ECPDESC = 14

    def _optffistring(self, cffistr):
        if cffistr == ffi.NULL:
            return None
        else:
            return dec(ffi.string(cffistr))

    def _raise_error(self, errorclass, errmsg, *args):
        ec = lib.aug_error(self.__handle)
        if ec == Augeas.AUG_ENOMEM:
            raise MemoryError()
        msg = self._optffistring(lib.aug_error_message(self.__handle))
        fullmessage = (errmsg + ": " + msg) % args
        minor = self._optffistring(lib.aug_error_minor_message(self.__handle))
        if minor:
            fullmessage += ": " + minor
        details = self._optffistring(lib.aug_error_details(self.__handle))
        if details:
            fullmessage += ": " + details
        raise errorclass(ec, fullmessage, msg, minor, details)

    def __init__(self, root=None, loadpath=None, flags=NONE):
        """
        Initialize the library.

        :param root: the filesystem root. If `root` is :py:obj:`None`, use the
                     value of the environment variable :envvar:`AUGEAS_ROOT`.
                     If that doesn't exist either, use :samp:`/`.
        :type root: str or None

        :param loadpath: a colon-separated list of directories that modules
                         should be searched in. This is in addition to the
                         standard load path and the directories in
                         :envvar:`AUGEAS_LENS_LIB`.
        :type loadpath: str or None

        :param flags: a combination of values of :attr:`SAVE_BACKUP`,
                      :attr:`SAVE_NEWFILE`, :attr:`TYPE_CHECK`,
                      :attr:`NO_STDINC`, :attr:`SAVE_NOOP`, :attr:`NO_LOAD`,
                      :attr:`NO_MODL_AUTOLOAD`, and :attr:`ENABLE_SPAN`.
        :type flags: int or :attr:`NONE`
        """

        # Sanity checks
        if not isinstance(root, string_types) and root is not None:
            raise TypeError("root MUST be a string or None!")
        if not isinstance(loadpath, string_types) and loadpath is not None:
            raise TypeError("loadpath MUST be a string or None!")
        if not isinstance(flags, int):
            raise TypeError("flag MUST be a flag!")

        root = enc(root) if root else ffi.NULL
        loadpath = enc(loadpath) if loadpath else ffi.NULL

        # Create the Augeas object
        self.__handle = ffi.gc(lib.aug_init(root, loadpath, flags),
                               lambda x: self.close)
        if not self.__handle:
            raise RuntimeError("Unable to create Augeas object!")

    def get(self, path):
        """
        Lookup the value associated with `path`.
        It is an error if more than one node matches `path`.

        :returns: the value at the path specified
        :rtype: str
        """

        # Sanity checks
        if not isinstance(path, string_types):
            raise TypeError("path MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Create the char * value
        value = ffi.new("char*[]", 1)

        # Call the function and pass value by reference (char **)
        ret = lib.aug_get(self.__handle, enc(path), value)
        if ret < 0:
            self._raise_error(AugeasValueError, "Augeas.get() failed")

        return self._optffistring(value[0])

    def label(self, path):
        """
        Lookup the label associated with `path`.
        It is an error if more than one node matches `path`.

        :returns: the label of the path specified
        :rtype: str
        """

        # Sanity checks
        if not isinstance(path, string_types):
            raise TypeError("path MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Create the char * value
        label = ffi.new("char*[]", 1)

        # Call the function and pass value by reference (char **)
        ret = lib.aug_label(self.__handle, enc(path), label)
        if ret < 0:
            self._raise_error(AugeasValueError, "Augeas.label() failed")

        return self._optffistring(label[0])

    def set(self, path, value):
        """
        Set the value associated with `path` to `value`.
        Intermediate entries are created if they don't exist.
        It is an error if more than one node matches `path`.
        """

        # Sanity checks
        if not isinstance(path, string_types):
            raise TypeError("path MUST be a string!")
        if not isinstance(value, string_types) and value is not None:
            raise TypeError("value MUST be a string or None!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_set(self.__handle, enc(path), enc(value))
        if ret != 0:
            self._raise_error(AugeasValueError, "Augeas.set() failed")

    def setm(self, base, sub, value):
        """
        Set the value of multiple nodes in one operation.
        Find or create a node matching `sub` by interpreting `sub`
        as a path expression relative to each node matching `base`.
        `sub` may be :py:obj:`None`, in which case all the nodes matching
        `base` will be modified.
        """

        # Sanity checks
        if type(base) != str:
            raise TypeError("base MUST be a string!")
        if type(sub) != str and sub is not None:
            raise TypeError("sub MUST be a string or None!")
        if type(value) != str and value is not None:
            raise TypeError("value MUST be a string or None!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_setm(
            self.__handle, enc(base), enc(sub), enc(value))
        if ret < 0:
            self._raise_error(AugeasValueError, "Augeas.setm() failed")
        return ret

    def text_store(self, lens, node, path):
        """
        Use the value of node `node` as a string and transform it into a tree
        using the lens `lens` and store it in the tree at `path`, which will be
        overwritten. `path` and `node` are path expressions.
        """

        # Sanity checks
        if not isinstance(lens, string_types):
            raise TypeError("lens MUST be a string!")
        if not isinstance(node, string_types):
            raise TypeError("node MUST be a string!")
        if not isinstance(path, string_types):
            raise TypeError("path MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_text_store(
            self.__handle, enc(lens), enc(node), enc(path))
        if ret != 0:
            self._raise_error(AugeasValueError, "Augeas.text_store() failed")
        return ret

    def text_retrieve(self, lens, node_in, path, node_out):
        """
        Transform the tree at `path` into a string using lens `lens` and store
        it in the node `node_out`, assuming the tree was initially generated
        using the value of node `node_in`. `path`, `node_in`, and `node_out`
        are path expressions.
        """

        # Sanity checks
        if not isinstance(lens, string_types):
            raise TypeError("lens MUST be a string!")
        if not isinstance(node_in, string_types):
            raise TypeError("node_in MUST be a string!")
        if not isinstance(path, string_types):
            raise TypeError("path MUST be a string!")
        if not isinstance(node_out, string_types):
            raise TypeError("node_out MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_text_retrieve(
            self.__handle, enc(lens), enc(node_in), enc(path), enc(node_out))
        if ret != 0:
            self._raise_error(AugeasValueError,
                              "Augeas.text_retrieve() failed")
        return ret

    def defvar(self, name, expr):
        """
        Define a variable `name` whose value is the result of
        evaluating `expr`. If a variable `name` already exists, its
        name will be replaced with the result of evaluating `expr`.

        If `expr` is :py:obj:`None`, the variable `name` will be removed if it
        is defined.

        Path variables can be used in path expressions later on by
        prefixing them with :samp:`$`.
        """

        # Sanity checks
        if type(name) != str:
            raise TypeError("name MUST be a string!")
        if type(expr) != str and expr is not None:
            raise TypeError("expr MUST be a string or None!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_defvar(self.__handle, enc(name), enc(expr))
        if ret < 0:
            self._raise_error(AugeasValueError, "Augeas.defvar() failed")
        return ret

    def defnode(self, name, expr, value):
        """
        Define a variable `name` whose value is the result of
        evaluating `expr`, which must not be :py:obj:`None` and evaluate to a
        nodeset. If a variable `name` already exists, its name will
        be replaced with the result of evaluating `expr`.

        If `expr` evaluates to an empty nodeset, a node is created,
        equivalent to calling ``set(expr, value)`` and `name` will be the
        nodeset containing that single node.
        """

        # Sanity checks
        if type(name) != str:
            raise TypeError("name MUST be a string!")
        if type(expr) != str:
            raise TypeError("expr MUST be a string!")
        if type(value) != str:
            raise TypeError("value MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_defnode(
            self.__handle, enc(name), enc(expr), enc(value), ffi.NULL)
        if ret < 0:
            self._raise_error(AugeasValueError, "Augeas.defnode() failed")
        return ret

    def move(self, src, dst):
        """
        Move the node `src` to `dst`. `src` must match exactly one node
        in the tree. `dst` must either match exactly one node in the
        tree, or may not exist yet. If `dst` exists already, it and all
        its descendants are deleted before moving `src` there. If `dst`
        does not exist yet, it and all its missing ancestors are created.
        """

        # Sanity checks
        if not isinstance(src, string_types):
            raise TypeError("src MUST be a string!")
        if not isinstance(dst, string_types):
            raise TypeError("dst MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_mv(self.__handle, enc(src), enc(dst))
        if ret != 0:
            self._raise_error(AugeasValueError, "Augeas.move() failed")

    def copy(self, src, dst):
        """
        Copy the node `src` to `dst`. `src` must match exactly one node
        in the tree. `dst` must either match exactly one node in the
        tree, or may not exist yet. If `dst` exists already, it and all
        its descendants are deleted before copying `src` there. If `dst`
        does not exist yet, it and all its missing ancestors are created.
        """

        # Sanity checks
        if not isinstance(src, string_types):
            raise TypeError("src MUST be a string!")
        if not isinstance(dst, string_types):
            raise TypeError("dst MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_cp(self.__handle, enc(src), enc(dst))
        if ret != 0:
            self._raise_error(AugeasValueError, "Augeas.copy() failed")

    def rename(self, src, dst):
        """
        Rename the label of all nodes matching `src` to `dst`.
        """

        # Sanity checks
        if not isinstance(src, string_types):
            raise TypeError("src MUST be a string!")
        if not isinstance(dst, string_types):
            raise TypeError("dst MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_rename(self.__handle, enc(src), enc(dst))
        if ret < 0:
            self._raise_error(AugeasValueError, "Augeas.rename() failed")
        return ret

    def insert(self, path, label, before=True):
        """
        Create a new sibling `label` for `path` by inserting into the tree
        just before `path` (if `before` is :py:obj:`True`) or just after `path`
        (if `before` is :py:obj:`False`).

        `path` must match exactly one existing node in the tree, and `label`
        must be a label, i.e. not contain a :samp:`/`, :samp:`*` or end with
        a bracketed index :samp:`[N]`.
        """

        # Sanity checks
        if not isinstance(path, string_types):
            raise TypeError("path MUST be a string!")
        if not isinstance(label, string_types):
            raise TypeError("label MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_insert(self.__handle, enc(path),
                             enc(label), before and 1 or 0)
        if ret != 0:
            self._raise_error(AugeasValueError, "Augeas.insert() failed")

    def remove(self, path):
        """
        Remove `path` and all its children. Returns the number of entries
        removed. All nodes that match `path`, and their descendants, are
        removed.
        """

        # Sanity checks
        if not isinstance(path, string_types):
            raise TypeError("path MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        return lib.aug_rm(self.__handle, enc(path))

    def match(self, path):
        """
        Return the matches of the path expression `path`. The returned paths
        are sufficiently qualified to make sure that they match exactly one
        node in the current tree.

        Path expressions use a very simple subset of XPath: the path `path`
        consists of a number of segments, separated by :samp:`/`; each segment
        can either be a :samp:`*`, matching any tree node, or a string,
        optionally followed by an index in brackets, matching tree nodes
        labelled with exactly that string. If no index is specified, the
        expression matches all nodes with that label; the index can be a
        positive number N, which matches exactly the *N*-th node with that
        label (counting from 1), or the special expression :samp:`last()` which
        matches the last node with the given label. All matches are done in
        fixed positions in the tree, and nothing matches more than one path
        segment.
        """

        # Sanity checks
        if not isinstance(path, string_types):
            raise TypeError("path MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        parray = ffi.new('char***')

        ret = lib.aug_match(self.__handle, enc(path), parray)
        if ret < 0:
            self._raise_error(AugeasRuntimeError,
                              "Augeas.match() failed: %s", path)

        # Loop through the string array
        array = parray[0]
        matches = []
        for i in range(ret):
            if array[i] != ffi.NULL:
                # Create a python string and append it to our matches list
                item = ffi.string(array[i])
                matches.append(dec(item))
                lib.free(array[i])
        lib.free(array)
        return matches

    def span(self, path):
        """
        Get the span according to input file of the node associated with
        `path`. If the node is associated with a file, a tuple of 7 elements is
        returned: ``(filename, label_start, label_end, value_start, value_end,
        span_start, span_end)``. If the node associated with `path` doesn't
        belong to a file or is doesn't exists, :py:obj:`ValueError` is raised.

        :rtype: tuple(str, int, int, int, int, int, int)
        """

        # Sanity checks
        if not isinstance(path, string_types):
            raise TypeError("path MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # TODO: Rewrite this

        filename = ffi.new('char **')
        label_start = ffi.new('unsigned int *')
        label_end = ffi.new('unsigned int *')
        value_start = ffi.new('unsigned int *')
        value_end = ffi.new('unsigned int *')
        span_start = ffi.new('unsigned int *')
        span_end = ffi.new('unsigned int *')

        ret = lib.aug_span(self.__handle, enc(path), filename,
                           label_start, label_end,
                           value_start, value_end,
                           span_start, span_end)
        if (ret < 0):
            self._raise_error(AugeasValueError, "Augeas.span() failed")
        fname = self._optffistring(filename[0])
        return (fname, int(label_start[0]), int(label_end[0]),
                int(value_start[0]), int(value_end[0]),
                int(span_start[0]), int(span_end[0]))

    def save(self):
        """
        Write all pending changes to disk. Only files that had any changes
        made to them are written.

        If :attr:`SAVE_NEWFILE` is set in the creation `flags`, create changed
        files as new files with the extension :samp:`.augnew`, and leave the
        original file unmodified.

        Otherwise, if :attr:`SAVE_BACKUP` is set in the creation `flags`, move
        the original file to a new file with extension :samp:`.augsave`.

        If neither of these flags is set, overwrite the original file.
        """

        # Sanity checks
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Call the function
        ret = lib.aug_save(self.__handle)
        if ret != 0:
            self._raise_error(AugeasIOError, "Augeas.save() failed")

    def load(self):
        """
        Load files into the tree. Which files to load and what lenses to use
        on them is specified under :samp:`/augeas/load` in the tree; each entry
        :samp:`/augeas/load/NAME` specifies a 'transform', by having itself
        exactly one child 'lens' and any number of children labelled 'incl' and
        'excl'. The value of :samp:`NAME` has no meaning.

        The 'lens' grandchild of :samp:`/augeas/load` specifies which lens to
        use, and can either be the fully qualified name of a lens
        :samp:`Module.lens` or :samp:`@Module`. The latter form means that the
        lens from the transform marked for autoloading in MODULE should be
        used.

        The 'incl' and 'excl' grandchildren of :samp:`/augeas/load` indicate
        which files to transform. Their value are used as glob patterns. Any
        file that matches at least one 'incl' pattern and no 'excl' pattern is
        transformed. The order of 'incl' and 'excl' entries is irrelevant.

        When AUG_INIT is first called, it populates :samp:`/augeas/load` with
        the transforms marked for autoloading in all the modules it finds.

        Before loading any files, :func:`load` will remove everything
        underneath :samp:`/augeas/files` and :samp:`/files`, regardless of
        whether any entries have been modified or not.
        """

        # Sanity checks
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        ret = lib.aug_load(self.__handle)
        if ret != 0:
            self._raise_error(AugeasRuntimeError, "Augeas.load() failed")

    def load_file(self, filename):
        # Sanity checks
        if not isinstance(filename, string_types):
            raise TypeError("filename MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        ret = lib.aug_load_file(self.__handle, enc(filename))
        if ret != 0:
            raise RuntimeError("aug_load_file() failed!")

    def source(self, path):
        # Sanity checks
        if not isinstance(path, string_types):
            raise TypeError("path MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        # Create the char * value
        value = ffi.new("char*[]", 1)

        ret = lib.aug_source(self.__handle, enc(path), value)
        if ret != 0:
            raise RuntimeError("aug_source() failed!")

        return self._optffistring(value[0])

    def srun(self, out, command):
        # Sanity checks
        if not hasattr(out, 'write'):
            raise TypeError("out MUST be a file!")
        if not isinstance(command, string_types):
            raise TypeError("path MUST be a string!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        ret = lib.aug_srun(self.__handle, out, enc(command))
        if ret < 0:
            raise RuntimeError("aug_srun() failed! (%d)" % ret)

    def clear_transforms(self):
        """
        Clear all transforms beneath :samp:`/augeas/load`. If :func:`load` is
        called right after this, there will be no files beneath :samp:`/files`.
        """
        self.remove("/augeas/load/*")

    def add_transform(self, lens, incl, name=None, excl=()):
        """
        Add a transform beneath :samp:`/augeas/load`.

        :param lens: the (file)name of the lens to use
        :type lens: str
        :param incl: one or more glob patterns for the files to transform
        :type incl: str or list(str)
        :param name: deprecated parameter
        :param excl: zero or more glob patterns of files to exclude from
                     transforming
        :type excl: str or list(str)
        """

        if name:
            import warnings
            warnings.warn("name is now deprecated in this function",
                          DeprecationWarning, stacklevel=2)
        if isinstance(incl, string_types):
            incl = [incl]
        if isinstance(excl, string_types):
            excl = [excl]

        for i in range(len(incl)):
            self.transform(lens, incl[i], False)
        for i in range(len(excl)):
            self.transform(lens, excl[i], True)

    def transform(self, lens, file, excl=False):
        """
        Add a transform for `file` using `lens`.

        `excl` specifies if this the file is to be included (:py:obj:`False`)
        or excluded (:py:obj:`True`) from the `lens`.
        The `lens` may be a module name or a full lens name.
        If a module name is given, then lns will be the lens assumed.
        """

        if not isinstance(lens, string_types):
            raise TypeError("lens MUST be a string!")
        if not isinstance(file, string_types):
            raise TypeError("file MUST be a string!")
        if not isinstance(excl, bool):
            raise TypeError("excl MUST be a boolean!")
        if not self.__handle:
            raise RuntimeError("The Augeas object has already been closed!")

        ret = lib.aug_transform(self.__handle, enc(lens), enc(file), excl)
        if ret != 0:
            self._raise_error(AugeasRuntimeError, "Augeas.transform() failed")

    def close(self):
        """
        Close this Augeas instance and free any storage associated with it.
        After this call, this Augeas instance is invalid and can not be used
        for any more operations.
        """

        # If we are already closed, return
        if not self.__handle or self.__handle == ffi.NULL:
            return

        # Call the function
        lib.aug_close(self.__handle)

        # Mark the object as closed
        self.__handle = None


# for backwards compatibility
# pylint: disable-msg=C0103
class augeas(Augeas):
    """
    Compat class, obsolete. Use class Augeas directly.

    :deprecated:
    """

    def __init__(self, *p, **k):
        import warnings
        warnings.warn("use Augeas instead of augeas", DeprecationWarning,
                      stacklevel=2)
        super(augeas, self).__init__(*p, **k)


__all__ = ['Augeas', 'augeas']
