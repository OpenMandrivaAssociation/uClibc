--- uClibc-0.9.33.3/include/sys/xattr.h.xattr~	2014-09-23 09:54:35.000000000 +0200
+++ uClibc-0.9.33.3/include/sys/xattr.h	2014-12-10 13:32:29.000000000 +0100
@@ -1,4 +1,4 @@
-/* Copyright (C) 2002 Free Software Foundation, Inc.
+/* Copyright (C) 2002-2014 Free Software Foundation, Inc.
    This file is part of the GNU C Library.
 
    The GNU C Library is free software; you can redistribute it and/or
@@ -12,9 +12,8 @@
    Lesser General Public License for more details.
 
    You should have received a copy of the GNU Lesser General Public
-   License along with the GNU C Library; if not, write to the Free
-   Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
-   02111-1307 USA.  */
+   License along with the GNU C Library; if not, see
+   <http://www.gnu.org/licenses/>.  */
 
 #ifndef _SYS_XATTR_H
 #define _SYS_XATTR_H	1
@@ -27,6 +26,7 @@ __BEGIN_DECLS
 
 /* The following constants should be used for the fifth parameter of
    `*setxattr'.  */
+#ifndef __USE_KERNEL_XATTR_DEFS
 enum
 {
   XATTR_CREATE = 1,	/* set value, fail if attr already exists.  */
@@ -34,51 +34,52 @@ enum
   XATTR_REPLACE = 2	/* set value, fail if attr does not exist.  */
 #define XATTR_REPLACE	XATTR_REPLACE
 };
+#endif
 
 /* Set the attribute NAME of the file pointed to by PATH to VALUE (which
    is SIZE bytes long).  Return 0 on success, -1 for errors.  */
-extern int setxattr (__const char *__path, __const char *__name,
-		     __const void *__value, size_t __size, int __flags)
+extern int setxattr (const char *__path, const char *__name,
+		     const void *__value, size_t __size, int __flags)
 	__THROW;
 
 /* Set the attribute NAME of the file pointed to by PATH to VALUE (which is
    SIZE bytes long), not following symlinks for the last pathname component.
    Return 0 on success, -1 for errors.  */
-extern int lsetxattr (__const char *__path, __const char *__name,
-		      __const void *__value, size_t __size, int __flags)
+extern int lsetxattr (const char *__path, const char *__name,
+		      const void *__value, size_t __size, int __flags)
 	__THROW;
 
 /* Set the attribute NAME of the file descriptor FD to VALUE (which is SIZE
    bytes long).  Return 0 on success, -1 for errors.  */
-extern int fsetxattr (int __fd, __const char *__name, __const void *__value,
+extern int fsetxattr (int __fd, const char *__name, const void *__value,
 		      size_t __size, int __flags) __THROW;
 
 /* Get the attribute NAME of the file pointed to by PATH to VALUE (which is
    SIZE bytes long).  Return 0 on success, -1 for errors.  */
-extern ssize_t getxattr (__const char *__path, __const char *__name,
+extern ssize_t getxattr (const char *__path, const char *__name,
 			 void *__value, size_t __size) __THROW;
 
 /* Get the attribute NAME of the file pointed to by PATH to VALUE (which is
    SIZE bytes long), not following symlinks for the last pathname component.
    Return 0 on success, -1 for errors.  */
-extern ssize_t lgetxattr (__const char *__path, __const char *__name,
+extern ssize_t lgetxattr (const char *__path, const char *__name,
 			  void *__value, size_t __size) __THROW;
 
 /* Get the attribute NAME of the file descriptor FD to VALUE (which is SIZE
    bytes long).  Return 0 on success, -1 for errors.  */
-extern ssize_t fgetxattr (int __fd, __const char *__name, void *__value,
+extern ssize_t fgetxattr (int __fd, const char *__name, void *__value,
 			  size_t __size) __THROW;
 
 /* List attributes of the file pointed to by PATH into the user-supplied
    buffer LIST (which is SIZE bytes big).  Return 0 on success, -1 for
    errors.  */
-extern ssize_t listxattr (__const char *__path, char *__list, size_t __size)
+extern ssize_t listxattr (const char *__path, char *__list, size_t __size)
 	__THROW;
 
 /* List attributes of the file pointed to by PATH into the user-supplied
    buffer LIST (which is SIZE bytes big), not following symlinks for the
    last pathname component.  Return 0 on success, -1 for errors.  */
-extern ssize_t llistxattr (__const char *__path, char *__list, size_t __size)
+extern ssize_t llistxattr (const char *__path, char *__list, size_t __size)
 	__THROW;
 
 /* List attributes of the file descriptor FD into the user-supplied buffer
@@ -88,16 +89,16 @@ extern ssize_t flistxattr (int __fd, cha
 
 /* Remove the attribute NAME from the file pointed to by PATH.  Return 0
    on success, -1 for errors.  */
-extern int removexattr (__const char *__path, __const char *__name) __THROW;
+extern int removexattr (const char *__path, const char *__name) __THROW;
 
 /* Remove the attribute NAME from the file pointed to by PATH, not
    following symlinks for the last pathname component.  Return 0 on
    success, -1 for errors.  */
-extern int lremovexattr (__const char *__path, __const char *__name) __THROW;
+extern int lremovexattr (const char *__path, const char *__name) __THROW;
 
 /* Remove the attribute NAME from the file descriptor FD.  Return 0 on
    success, -1 for errors.  */
-extern int fremovexattr (int __fd, __const char *__name) __THROW;
+extern int fremovexattr (int __fd, const char *__name) __THROW;
 
 __END_DECLS
 
