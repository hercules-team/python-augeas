"""Pure python bindings for the augeas library

Augeas is a library for programmatically editing configuration files. 
Augeas parses configuration files into a tree structure, which it exposes 
through its public API. Changes made through the API are written back to 
the initially read files.

The transformation works very hard to preserve comments and formatting
details. It is controlled by ``lens'' definitions that describe the file
format and the transformation into a tree.

"""

#
# Copyright (C) 2008 Nathaniel McCallum
# Copyright (C) 2008 Jeff Schroeder <jeffschroeder@computer.org>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#
# Author: Nathaniel McCallum <nathaniel@natemccallum.com>

__author__ = "Nathaniel McCallum <nathaniel@natemccallum.com>"
__credits__ = """Jeff Schroeder <jeffschroeder@computer.org>
Harald Hoyer <harald@redhat.com> - initial python bindings, packaging
"""

import ctypes
import ctypes.util
from sys import version_info as _pyver

def _dlopen(*args):
    """Search for one of the libraries given as arguments and load it.
    Returns the library.
    """
    libs = [l for l in [ ctypes.util.find_library(a) for a in args ] if l]
    lib  = reduce(lambda x, y: x or ctypes.cdll.LoadLibrary(y), libs, None)
    if not lib: 
        raise ImportError, "Unable to import lib%s!" % args[0]
    return lib

class Augeas(object):
    "Class wrapper for the augeas library"

    # Load libpython (for 'PyFile_AsFile()' and 'PyMem_Free()')
    # pylint: disable-msg=W0142
    _libpython = _dlopen(*["python" + v % _pyver[:2] 
                           for v in ("%d.%d", "%d%d")])
    _libpython.PyFile_AsFile.restype = ctypes.c_void_p

    # Load libaugeas
    _libaugeas = _dlopen("augeas")
    _libaugeas.aug_init.restype = ctypes.c_void_p

    # Augeas Flags
    NONE         = (     0)
    SAVE_BACKUP  = (1 << 0)
    SAVE_NEWFILE = (1 << 1)
    TYPE_CHECK   = (1 << 2)

    def __init__(self, root=None, loadpath=None, flags=NONE):
        """Initialize the library.

        Use 'root' as the filesystem root. If 'root' is None, use the value of 
        the environment variable AUGEAS_ROOT. If that doesn't exist either, 
        use "/".

        'loadpath' is a colon-spearated list of directories that modules 
        should be searched in. This is in addition to the standard load path 
        and the directories in AUGEAS_LENS_LIB.

        'flags' is a bitmask made up of values from AUG_FLAGS."""

        # Sanity checks
        if type(root) != str and root != None:
            raise TypeError, "root MUST be a string or None!"
        if type(loadpath) != str and loadpath != None:
            raise TypeError, "loadpath MUST be a string or None!"
        if type(flags) != int:
            raise TypeError, "flag MUST be a flag!"

        # Create the Augeas object
        self.__handle = Augeas._libaugeas.aug_init(root, loadpath, flags)
        if not self.__handle:
            raise RuntimeError, "Unable to create Augeas object!"

    def __del__(self):
        self.close()

    def get(self, path):
        """Lookup the value associated with 'path'.
        Returns the value at the path specified.  
        It is an error if more than one node matches 'path'."""

        # Sanity checks
        if type(path) != str:
            raise TypeError, "path MUST be a string!"
        if not self.__handle:
            raise RuntimeError, "The Augeas object has already been closed!"

        # Create the char * value
        value = ctypes.c_char_p()

        # Call the function and pass value by reference (char **)
        ret = Augeas._libaugeas.aug_get(self.__handle, path, 
                                        ctypes.byref(value))
        if ret > 1:
            raise ValueError, "path specified had too many matches!"

        return value.value

    def set(self, path, value):
        """Set the value associated with 'path' to 'value'.
        Intermediate entries are created if they don't exist. 
        It is an error if more than one node matches 'path'."""

        # Sanity checks
        if type(path) != str:
            raise TypeError, "path MUST be a string!"
        if type(value) != str:
            raise TypeError, "value MUST be a string!"
        if not self.__handle:
            raise RuntimeError, "The Augeas object has already been closed!"

        # Call the function
        ret = Augeas._libaugeas.aug_set(self.__handle, path, value)
        if ret != 0:
            raise ValueError, "Unable to set value to path!"

    def move(self, src, dst):
        """Move the node 'src' to 'dst'. 'src' must match exactly one node
           in the tree. 'dst' must either match exactly one node in the
           tree, or may not exist yet. If 'dst' exists already, it and all
           its descendants are deleted before moving 'src' there. If 'dst'
           does not exist yet, it and all its missing ancestors are created."""

        # Sanity checks
        if type(src) != str:
            raise TypeError, "src MUST be a string!"
        if type(dst) != str:
            raise TypeError, "dst MUST be a string!"
        if not self.__handle:
            raise RuntimeError, "The Augeas object has already been closed!"

        # Call the function
        ret = Augeas._libaugeas.aug_mv(self.__handle, src, dst)
        if ret != 0:
            raise ValueError, "Unable to move src to dst!"

    def insert(self, path, label, before=True):
        """Create a new sibling 'label' for 'path' by inserting into the tree 
        just before 'path' (if 'before' is True) or just after 'path' 
        (if 'before' is False).

        'path' must match exactly one existing node in the tree, and 'label' 
        must be a label, i.e. not contain a '/', '*' or end with a bracketed 
        index '[N]'."""

        # Sanity checks
        if type(path) != str:
            raise TypeError, "path MUST be a string!"
        if type(label) != str:
            raise TypeError, "label MUST be a string!"
        if not self.__handle:
            raise RuntimeError, "The Augeas object has already been closed!"

        # Call the function
        ret = Augeas._libaugeas.aug_insert(self.__handle, path, 
                                           label, before and 1 or 0)
        if ret != 0:
            raise ValueError, "Unable to insert label!"

    def remove(self, path):
        """Remove 'path' and all its children. Returns the number of entries
        removed. All nodes that match 'path', and their descendants, are 
        removed."""

        # Sanity checks
        if type(path) != str:
            raise TypeError, "path MUST be a string!"
        if not self.__handle:
            raise RuntimeError, "The Augeas object has already been closed!"

        # Call the function
        return Augeas._libaugeas.aug_rm(self.__handle, path)

    def match(self, path):
        """Return the matches of the path expression 'path'. The returned paths
        are sufficiently qualified to make sure that they match exactly one 
        node in the current tree.

        Path expressions use a very simple subset of XPath: the path 'path'
        consists of a number of segments, separated by '/'; each segment can
        either be a '*', matching any tree node, or a string, optionally
        followed by an index in brackets, matching tree nodes labelled with
        exactly that string. If no index is specified, the expression matches
        all nodes with that label; the index can be a positive number N, which
        matches exactly the Nth node with that label (counting from 1), or the
        special expression 'last()' which matches the last node with the given
        label. All matches are done in fixed positions in the tree, and nothing
        matches more than one path segment."""

        # Sanity checks
        if type(path) != str:
            raise TypeError, "path MUST be a string!"
        if not self.__handle:
            raise RuntimeError, "The Augeas object has already been closed!"

        # Create a void ** (this is so python won't mangle the char **,
        # when we free it)
        array = ctypes.POINTER(ctypes.c_void_p)()

        # Call the function and pass the void ** by reference (void ***)
        ret = Augeas._libaugeas.aug_match(self.__handle, path, 
                                          ctypes.byref(array))
        if ret < 0:
            raise RuntimeError, "Error during match procedure!"

        # Loop through the string array
        matches = []
        for i in range(ret):
            if array[i]:
                # Create a python string and append it to our matches list
                matches.append(str(ctypes.cast(array[i], 
                                               ctypes.c_char_p).value))

                # Free the string at this point in the array
                Augeas._libpython.PyMem_Free(array[i])

        # Free the array itself
        Augeas._libpython.PyMem_Free(array)

        return matches        

    def save(self):
        """Write all pending changes to disk. Only files that had any changes 
        made to them are written.

        If SAVE_NEWFILE is set in the creation 'flags', create changed files as
        new files with the extension ".augnew", and leave the original file 
        unmodified.

        Otherwise, if SAVE_BACKUP is set in the creation 'flags', move the 
        original file to a new file with extension ".augsave".

        If neither of these flags is set, overwrite the original file."""

        # Sanity checks
        if not self.__handle:
            raise RuntimeError, "The Augeas object has already been closed!"

        # Call the function
        ret = Augeas._libaugeas.aug_save(self.__handle)
        if ret != 0:
            raise IOError, "Unable to save to file!"

    def close(self):
        """Close this Augeas instance and free any storage associated with it. 
        After this call, this Augeas instance is invalid and can not be used 
        for any more operations."""

        # If we are already closed, return
        if not self.__handle:
            return

        # Call the function
        Augeas._libaugeas.aug_close(self.__handle)

        # Mark the object as closed
        self.__handle = None       

# for backwards compatibility
# pylint: disable-msg=C0103
class augeas(Augeas):
    "Compat class, obsolete. Use class Augeas directly."
