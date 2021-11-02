import os
import sys
import subprocess

from cffi import FFI

def get_include_dirs():
    XML2_CONFIG = os.environ.get('XML2_CONFIG', 'xml2-config')
    PKG_CONFIG = os.environ.get('PKG_CONFIG', 'pkg-config')
    try:
        stdout = subprocess.check_output([XML2_CONFIG, '--cflags'])
    except (OSError, subprocess.CalledProcessError):
        try:
            stdout = subprocess.check_output([PKG_CONFIG, '--cflags', 'libxml-2.0'])
        except (OSError, subprocess.CalledProcessError):
            stdout = b''
    cflags = stdout.decode('utf-8').split()
    return [cflag[2:] for cflag in cflags if cflag.startswith('-I')]

if sys.platform == "darwin":
    _libaugeas = "libaugeas.dylib"
else:
    _libaugeas = "libaugeas.so"


ffi = FFI()
ffi.set_source("_augeas",
               """
               #include <augeas.h>
               """,
               libraries=[_libaugeas],
               include_dirs=get_include_dirs())

ffi.cdef("""
typedef struct augeas augeas;

augeas *aug_init(const char *root, const char *loadpath, unsigned int flags);
int aug_defvar(augeas *aug, const char *name, const char *expr);
int aug_defnode(augeas *aug, const char *name, const char *expr,
                const char *value, int *created);
int aug_get(const augeas *aug, const char *path, const char **value);
int aug_label(const augeas *aug, const char *path, const char **label);
int aug_set(augeas *aug, const char *path, const char *value);
int aug_setm(augeas *aug, const char *base, const char *sub,
             const char *value);
int aug_span(augeas *aug, const char *path, char **filename,
        unsigned int *label_start, unsigned int *label_end,
        unsigned int *value_start, unsigned int *value_end,
        unsigned int *span_start, unsigned int *span_end);
int aug_insert(augeas *aug, const char *path, const char *label, int before);
int aug_rm(augeas *aug, const char *path);
int aug_mv(augeas *aug, const char *src, const char *dst);
int aug_cp(augeas *aug, const char *src, const char *dst);
int aug_rename(augeas *aug, const char *src, const char *lbl);
int aug_match(const augeas *aug, const char *path, char ***matches);
int aug_save(augeas *aug);
int aug_load(augeas *aug);
int aug_text_store(augeas *aug, const char *lens, const char *node,
                   const char *path);
int aug_text_retrieve(struct augeas *aug, const char *lens,
                      const char *node_in, const char *path,
                      const char *node_out);
int aug_transform(augeas *aug, const char *lens, const char *file, int excl);
int aug_source(const augeas *aug, const char *path, char **file_path);
int aug_srun(augeas *aug, FILE *out, const char *text);
int aug_load_file(augeas *aug, const char *file);
int aug_preview(augeas *aug, const char *path, char **out);
int aug_ns_attr(const augeas* aug, const char *var, int i,
                const char **value, const char **label, char **file_path);
int aug_ns_label(const augeas *aug, const char *var, int i,
                 const char **label, int *index);
int aug_ns_value(const augeas *aug, const char *var, int i,
                 const char **value);
int aug_ns_count(const augeas *aug, const char *var);
int aug_ns_path(const augeas *aug, const char *var, int i, char **path);



void aug_close(augeas *aug);
int aug_error(augeas *aug);
const char *aug_error_message(augeas *aug);
const char *aug_error_minor_message(augeas *aug);
const char *aug_error_details(augeas *aug);

void free(void *);
""")

if __name__ == "__main__":
    ffi.compile(verbose=True)
