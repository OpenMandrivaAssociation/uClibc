# disable stack protector, build doesn't work with it
%define _ssp_cflags     %{nil}

%define	uclibc_root	%{_prefix}/uclibc
%define	uclibc_cc	uclibc-gcc

%define	majorish	0.9.30.1

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	%{majorish}
Release:	%mkrel 9
License:	LGPL
Group:		System/Libraries
URL:		http://uclibc.org/
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2
Source1:        http://uclibc.org/downloads/%{name}-%{version}.tar.bz2.sign
Source2:	uClibc-0.9.30.2-config
Patch0:		uClibc-0.9.30.1-getline.patch
Patch1:		uClibc-0.9.30.1-lib64.patch
# http://lists.busybox.net/pipermail/uclibc/2009-September/043035.html
Patch2:		uClibc-0.9.30.2-add-rpmatch-function.patch
# http://svn.exactcode.de/t2/branches/7.0/package/base/uclibc/scanf-aflag.patch
Patch3:		uClibc-0.9.30.1-add-scanf-a-flag.patch
# (proyvind): the ABI isn't stable, so set it to current version
Patch4:		uClibc-0.9.30.2-unstable-abi.patch

# backported patches from uClibc git:
Patch100:	uClibc-0.9.30.1-64bit-strtouq.patch
Patch101:	uClibc-0.9.30.1-arm-fix-linuxthreads-sysdep.patch
Patch102:	uClibc-0.9.30.1-c99-ldbl-math.patch
Patch103:	uClibc-0.9.30.1-dl-sysdep-inline.patch
Patch104:	uClibc-0.9.30.1-fix-getaddrinfo.patch
Patch105:	uClibc-0.9.30.1-enable-nanosecond-stat.patch
Patch106:	uClibc-0.9.30.1-add-missing-utime-defs.patch
Patch107:	uClibc-0.9.30.1-add-strverscmp-and-versionsort-64.patch
Patch108:	uClibc-0.9.30.1-libm-add-scalbf-gammaf-significandf-wrappers.patch
Patch109:	uClibc-0.9.30.1-test-stat-fix-compiling-the-memcmp-stat-test-when-__.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%define desc uclibc (pronounced yew-see-lib-see) is a c library for developing\
embedded linux systems. it is much smaller than the gnu c library,\
but nearly all applications supported by glibc also work perfectly\
with uclibc. porting applications from glibc to uclibc typically\
involves just recompiling the source code. uclibc even supports\
shared libraries and threading. it currently runs on standard\
linux and  mmu-less (also known as uclinux) systems with support\
for alpha, arm, cris, i386, i960, h8300, m68k, mips/mipsel,\
powerpc, sh, sparc, and v850 processors.\
\
if you are building an embedded linux system and you find that\
glibc is eating up too much space, you should consider using\
uclibc. if you are building a huge fileserver with 12 terabytes of\
storage, then using glibc may make more sense. unless, for\
example, that 12 terabytes will be network attached storage and\
you plan to burn linux into the system's firmware...

#' <- this is just to "close" to work around vim highlighting :p

%description
%{desc}

%define	libname	%mklibname %{name} %{version}
%package -n	%{libname}
Summary:	%{summary}
Group:		System/Libraries
Provides:	%mklibname %{name}
Obsoletes:      %{mklibname %{name}} <= %{version}-%{release}
Requires:	%{name}

%description -n	%{libname}
%{desc}

%define	libdev	%mklibname %{name} -d
%package -n	%{libdev}
Summary:	Development files & libraries for uClibc
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{name}-devel <= %{version}-%{release}
%define	libstat	%mklibname %{name} -d -s
Provides:	%{libstat} = %{version}-%{release}
Obsoletes:	%{libstat} <= %{version}-%{release}
Provides:	libc-static
Provides:	%{name}-static-devel = %{version}-%{release}
Obsoletes:	%{name}-static-devel <= %{version}-%{release}

%description -n	%{libdev}
Small libc for building embedded applications.

%prep
%setup -q
%patch0 -p1 -b .getline~
%patch1 -p1 -b .lib64~
%patch2 -p1 -b .rpmatch~
%patch3 -p1 -b .a_flag~
%patch4 -p1 -b .abi_version~

%patch100 -p1 -b .64bit_strouq~
%patch101 -p1 -b .arm_linuxthreads~
%patch102 -p1 -b .c99_math~
%patch103 -p1 -b .dl_sysdep~
%patch104 -p1 -b .getaddrinfo~
%patch105 -p1 -b .ns_stat~
%patch106 -p1 -b .utime_defs~
%patch107 -p1 -b .versionsort~
%patch108 -p1 -b .scalbf~
%patch109 -p1 -b .stat_check~

%define arch %(echo %{_arch} | sed -e 's/ppc/powerpc/')
cat %{SOURCE2} |sed \
	-e "s|@CFLAGS@|%{optflags}|g" \
	-e 's|@ARCH@|%{arch}|g' \
	-e 's|@LIB@|%{_lib}|g' \
	-e 's|@PREFIX@|%{uclibc_root}|g' \
	>> .config

%build
yes "" | %make oldconfig V=1

%make VERBOSE=1 CPU_CFLAGS="" all utils

%check
ln -snf %{_includedir}/{asm,asm-generic,linux} test
ln -snf %{buildroot}%{uclibc_root} install_dir
# This test relies on /etc/ethers being present to pass, so we'll skip it by
# removing it
rm -f test/inet/tst-ethers*
%make check VERBOSE=1 || /bin/true 

%install
[ -d "%{buildroot}" ] && chmod 777 -R %{buildroot}
rm -rf %{buildroot}

%make VERBOSE=1 PREFIX=%{buildroot} install
%make -C utils VERBOSE=1 PREFIX=%{buildroot} utils_install

# be sure that we don't package any backup files
find %{buildroot} -name \*~|xargs rm -f

install -d %{buildroot}%{_bindir}
# using 'rpm --eval' here for multilib purposes..
#TODO: figure out binutils --sysroot + multilib in binutils package?
cat > %{buildroot}%{_bindir}/%{uclibc_cc} << EOF
#!/bin/sh
export C_INCLUDE_PATH="\$(rpm --eval %%{uclibc_root}%%{_includedir}):\$(gcc -print-search-dirs|grep install:|cut -d\  -f2)/include"
export LD_RUN_PATH="\$(rpm --eval %%{uclibc_root}/%%{_lib}:%%{uclibc_root}%%{_libdir})"
export LIBRARY_PATH="\$LD_RUN_PATH"
export GCC_EXEC_PREFIX="\$LD_RUN_PATH"
gcc -muclibc \$(rpm --eval "-Wl,--dynamic-linker,%%{uclibc_root}/%%{_lib}/%%{_lib}-uClibc.so.0"|sed -e 's#lib-uClibc#ld-uClibc#g' -e 's#lib64-uClibc#ld64-uClibc#g') \$@
EOF
chmod +x %{buildroot}%{_bindir}/%{uclibc_cc}

install -d %{buildroot}%{_sysconfdir}/rpm/macros.d
cat > %{buildroot}%{_sysconfdir}/rpm/macros.d/uclibc.macros << EOF
%%uclibc_root	%uclibc_root
%%uclibc_cc	%uclibc_cc
%%uclibc_cflags	%%{optflags} -fno-stack-protector
EOF

#(peroyvind) rpm will make these symlinks relative
ln -snf %{_includedir}/{asm,asm-generic,linux} %{buildroot}%{uclibc_root}%{_includedir}

%if "%{_lib}" == "lib64"
ln -s ld64-uClibc.so.%{version} %{buildroot}%{uclibc_root}/lib64/ld64-uClibc.so.0
ln -s libc.so.%{version} %{buildroot}%{uclibc_root}/lib64/libc.so.0
# creating directory without listing permission to prevent ldconfig from messing with it
install -d -m300 %{buildroot}%{uclibc_root}{/lib,/usr/lib}
%endif

ln -s ld-uClibc.so.%{version} %{buildroot}%{uclibc_root}/lib/ld-uClibc.so.0
ln -s libc.so.%{version} %{buildroot}%{uclibc_root}/lib/libc.so.0

for dir in /bin /sbin %{_prefix} %{_bindir} %{_sbindir}; do
	mkdir -p %{buildroot}%{uclibc_root}$dir
done

%clean
[ -d "%{buildroot}" ] && chmod 777 -R %{buildroot}
rm -rf %{buildroot}

%files
%defattr(-,root,root,755)
%doc README
%dir %{uclibc_root}
%dir %{uclibc_root}/bin
%dir %{uclibc_root}/sbin
%dir %{uclibc_root}%{_prefix}
%dir %{uclibc_root}%{_bindir}
%dir %{uclibc_root}%{_sbindir}
%dir %{uclibc_root}/lib
%dir %{uclibc_root}%{_prefix}/lib
%{uclibc_root}%{_bindir}/ldd
%{uclibc_root}/sbin/ldconfig
%{uclibc_root}/lib/ld-uClibc.so.0
%{uclibc_root}/lib/libc.so.0
%if "%{_lib}" == "lib64"
%dir %{uclibc_root}/lib64
%dir %{uclibc_root}%{_prefix}/lib
%{uclibc_root}/lib64/libc.so.0
%{uclibc_root}/lib64/ld64-uClibc.so.0
%endif

%files -n %{libname}
%defattr(-,root,root)
%ifnarch %{sparcx}
%{uclibc_root}/%{_lib}/*-*%{version}.so
%{uclibc_root}/%{_lib}/*.so.%{version}
%endif

%files -n %{libdev}
%defattr(-,root,root)
%doc docs/* Changelog TODO
%{_bindir}/%{uclibc_cc}
%{_sysconfdir}/rpm/macros.d/uclibc.macros
%{uclibc_root}%{_includedir}
%{uclibc_root}%{_libdir}/crt1.o
%{uclibc_root}%{_libdir}/crti.o
%{uclibc_root}%{_libdir}/crtn.o
%ifnarch %{sparcx}
%{uclibc_root}%{_libdir}/Scrt1.o
%{uclibc_root}%{_libdir}/librt.so
%{uclibc_root}%{_libdir}/libnsl.so
%{uclibc_root}%{_libdir}/libpthread.so
%{uclibc_root}%{_libdir}/libc.so
%{uclibc_root}%{_libdir}/libcrypt.so
%{uclibc_root}%{_libdir}/libdl.so
%{uclibc_root}%{_libdir}/libm.so
%{uclibc_root}%{_libdir}/libresolv.so
%{uclibc_root}%{_libdir}/libutil.so
%endif
%defattr(-,root,root)
%{uclibc_root}%{_libdir}/lib*.a
%{uclibc_root}%{_libdir}/uclibc_nonshared.a
