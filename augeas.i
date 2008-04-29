%define DOCSTRING
"Augeas

 * Copyright (C) 2007 Red Hat Inc.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
 *
 * Author: David Lutterkort <dlutter@redhat.com>

Augeas is a configuration editing tool. It parses configuration files 
in their native formats and transforms them into a tree. 
Configuration changes are made by manipulating this tree and saving it 
back into native config files.

Augeas goals:

    * Manipulate configuration files safely, safer than the ad-hoc techniques 
      generally used with grep, sed, awk and similar mechanisms in 
      scripting languages
    * Provide a local configuration API for Linux
    * Make it easy to integrate new config files into the Augeas tree

Instructions on how to explore the current implementation can be found on 
http://augeas.net/

"
%enddef

%module(docstring=DOCSTRING) augeas
%{
#include "augeas.h"
%}
// Type mapping for grabbing a FILE * from Python

%typemap(in) FILE * {
  if (!PyFile_Check($input)) {
      PyErr_SetString(PyExc_TypeError, "Need a file!");
      return NULL;
  }
  $1 = PyFile_AsFile($input);
}


%typemap(in, numinputs=0) char ***matches (char **tmp) %{
  $1 = &tmp;
%}

%typemap(argout) char ***matches %{
  int i;

  Py_XDECREF($result);
  $result = PyList_New(0);
  for (i=0; result > 0 && i < result; i++) {
        PyObject *o = PyString_FromString((char *)(*$1)[i]);
        PyList_Append($result, o);
        free((void*)(*$1)[i]) ; 
  }
  free((char *) *$1);
%}


%typemap(in, numinputs=0) const char **value (char *tmp) %{
  $1 = &tmp;
  tmp = NULL;
%}

%typemap(argout) const char **value {
    if ((result > 0) && (*$1)) {
        Py_XDECREF($result);
        $result = PyString_FromString(*$1);
    } else {
      	if (*$1) free((char *) *$1);
        Py_XDECREF($result);
        $result = Py_None;
    }
}


%include "augeas.h"

%pythoncode %{

class augeas:
    """
    """
    def __init__(self, root="/", loadpath=None, flags=AUG_NONE):
        """
        Use ROOT as the filesystem root. If ROOT is None, use the value of the
        environment variable AUGEAS_ROOT. If that doesn't exist eitehr, use "/".
        
        LOADPATH is a colon-spearated list of directories that modules should be
        searched in. This is in addition to the standard load path and the
        directories in AUGEAS_LENS_LIB
 
        FLAGS is a bitmask made up of values from:
           AUG_NONE
           AUG_SAVE_BACKUP  Keep the original file with a .augsave extension
           AUG_SAVE_NEWFILE Save changes into a file with
                            extension .augnew, and do not
                            overwrite the original file. Takes
                            precedence over AUG_SAVE_BACKUP
           AUG_TYPE_CHECK   Typecheck lenses; since it can be very
                            expensive it is not done by default 

        """
        self.__handler = _augeas.aug_init(str(root), str(loadpath), flags)
        if not self.__handler:
            raise ValueError

    def get(self, path):
        """
        Lookup the value associated with PATH. Returns None if PATH does not
        exist, or if it matches more than one node, or if that is the value
        associated with the single node matched by PATH.
        See 'exists' on how to tell these cases apart.
        """
        return _augeas.aug_get(self.__handler, str(path))

    def set(self, path, val):
        """
        Set the value associated with PATH to VAL. VAL is copied into the
        internal data structure. Intermediate entries are created if they don't
        exist. Return True on success, False on error. It is an error if more than one
        node matches PATH.
        """
        if (_augeas.aug_set(self.__handler, str(path), str(val)) == 0):
            return True
        else:
            return False
    
    def insert(self, path, lbl, before):
        """
        Create a new sibling LBL for PATH by inserting into the tree just
        before PATH if BEFORE == 1 or just after PATH if BEFORE == 0.
        PATH must match exactly one existing node in the tree, and LBL must be
        a label, i.e. not contain a '/', '*' or end with a bracketed index
        '[N]'.
        Return True on success, and False if the insertion fails.
        """
        if (_augeas.aug_insert(self.__handler, str(path), str(lbl), int(before)) == 0):
            return True
        else:
            return False

    def rm(self, path):
        """
        Remove path and all its children. Returns the number of entries removed.
        All nodes that match PATH, and their descendants, are removed.

        """
        return _augeas.aug_rm(self.__handler, str(path))

    def match(self, path):
        """
        Returns a list of paths which matches the PATH expression.

        Path expressions use a very simple subset of XPath: the path PATH
        consists of a number of segments, separated by '/'; each segment can
        either be a '*', matching any tree node, or a string, optionally
        followed by an index in brackets, matching tree nodes labelled with
        exactly that string. If no index is specified, the expression matches
        all nodes with that label; the index can be a positive number N, which
        matches exactly the Nth node with that label (counting from 1), or the
        special expression 'last()' which matches the last node with the given
        label. All matches are done in fixed positions in the tree, and nothing
        matches more than one path segment.
        """
        return _augeas.aug_match(self.__handler, str(path))
    
    def save(self):
        """
        Write all pending changes to disk. Return False if an error is encountered,
        True on success. Only files that had any changes made to them are written.
        
        If AUG_SAVE_NEWFILE is set in the FLAGS passed to AUG_INIT, create
        changed files as new files with the extension ".augnew", and leave teh
        original file unmodified.
        
        Otherwise, if AUG_SAVE_BACKUP is set in the FLAGS passed to AUG_INIT,
        move the original file to a new file with extension ".augsave".
        
        If neither of these flags is set, overwrite the original file.
        """
        if (_augeas.aug_save(self.__handler) == 0):
            return True
        else:
            return False

    def printnodes(self, out, path):
        """
        Print each node matching PATH and its descendants to file object OUT
        """
        return _augeas.aug_print(self.__handler, file(out), str(path))

    def __del__(self):
        """
	"""
        _augeas.aug_close(self.__handler)


__all__ = [ "augeas",
        "AUG_NONE",
        "AUG_SAVE_BACKUP",
        "AUG_SAVE_NEWFILE",
        "AUG_TYPE_CHECK",
        ]

%}


