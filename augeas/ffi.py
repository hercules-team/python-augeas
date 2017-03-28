from cffi import FFI

ffi = FFI()
ffi.set_source("augeas",
               """
               #include <augeas.h>
               """,
               libraries=['augeas'],
               include_dirs=["/usr/include/libxml2"])

ffi.cdef("""
typedef struct augeas augeas;

augeas *aug_init(const char *root, const char *loadpath, unsigned int flags);
int aug_defvar(augeas *aug, const char *name, const char *expr);
int aug_defnode(augeas *aug, const char *name, const char *expr,
                const char *value, int *created);
int aug_get(const augeas *aug, const char *path, const char **value);
int aug_label(const augeas *aug, const char *path, const char **label);
int aug_set(augeas *aug, const char *path, const char *value);
int aug_setm(augeas *aug, const char *base, const char *sub, const char *value);
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
void aug_close(augeas *aug);

void free(void *);
""")

lib = ffi.dlopen("augeas")
