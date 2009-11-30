%define _enable_debug_packages	%{nil}
%define debug_package		%{nil}

# disable stack protector, build doesn't work with it
%define _ssp_cflags	%{nil}

%define	uclibc_root	%{_prefix}/uclibc

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	0.9.30.1
Release:	%mkrel 3
License:	LGPL
Group:		System/Libraries
URL:		http://uclibc.org/
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2
Source1:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2.sign
Source2:	uClibc-0.9.30.2-config
Patch0:		uClibc-0.9.30.1-getline.patch
Patch1:		uClibc-0.9.30.1-lib64.patch

#Patches from uClibc buildroot:
Patch100:	uClibc-0.9.30.1-64bit-strtouq.patch
Patch101:	uClibc-0.9.30.1-arm-fix-linuxthreads-sysdep.patch
Patch102:	uClibc-0.9.30.1-c99-ldbl-math.patch
Patch103:	uClibc-0.9.30.1-dl-sysdep-inline.patch
Patch104:	uClibc-0.9.30.1-fix-getaddrinfo.patch
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

%define	libname	%mklibname %{name}
%package -n	%{libname}
Summary:	%{summary}
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}
Obsoletes:	%{name} <= 0.9.30.1-2

%description -n	%{libname}
%{desc}

%define	libdev	%mklibname %{name} -d
%package -n	%{libdev}
Summary:	Development files for uClibc
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{name}-devel <= 0.9.30.1-2

%description -n	%{libdev}
Small libc for building embedded applications.

%define	libstat	%mklibname %{name} -d -s
%package -n	%{libstat}
Summary:	Static uClibc libratries
Group:		Development/C
Requires:	%{libdev} = %{version}-%{release}
Provides:	libc-static
Provides:	%{name}-static-devel = %{version}-%{release}
Obsoletes:	%{name}-static-devel <= 0.9.30.1-2

%description -n	%{libstat}
Static uClibc libratries.

%prep
%setup -q
%patch0 -p1 -b .getline~
%patch1 -p1 -b .lib64~
%patch100 -p1 -b .64bit_strouq~
%patch101 -p1 -b .arm_linuxthreads~
%patch102 -p1 -b .c99_math~
%patch103 -p1 -b .dl_sysdep~
%patch104 -p1 -b .getaddrinfo~

%build
%define arch %(echo %{_arch} | sed -e 's/ppc/powerpc/')
cat %{SOURCE2} |sed \
	-e 's|@CFLAGS@|%{optflags} -Os|g' \
	-e 's|@ARCH@|%{arch}|g' \
	-e 's|@LIB@|%{_lib}|g' \
	-e 's|@PREFIX@|%{uclibc_root}|g' \
	>> .config
yes "" | %make oldconfig V=1

%make V=1 CPU_CFLAGS=""

%check
ln -snf %{_includedir}/{asm,asm-generic,linux} test
ln -snf %{buildroot}%{uclibc_root} install_dir
# This test relies on /etc/ethers being present to pass, so we'll skip it by
# removing it
rm -f test/inet/tst-ethers*
%make check V=1 || /bin/true 

%install
rm -rf %{buildroot}

make PREFIX=%{buildroot} install
# be sure that we don't package any backup files
find %{buildroot} -name \*~|xargs rm -f

install -d %{buildroot}%{_bindir}
# using 'rpm --eval' here for multilib purposes..
#TODO: figure out binutils --sysroot + multilib in binutils package?
cat > %{buildroot}%{_bindir}/uclibc-gcc << EOF
#!/bin/sh
gcc -B\$(rpm --eval "%{uclibc_root}%%{_libdir} -isystem %{uclibc_root}%%{_includedir}") \$@
EOF
chmod +x %{buildroot}%{_bindir}/uclibc-gcc
 
#(peroyvind) rpm will make these symlinks relative
ln -snf %{_includedir}/{asm,asm-generic,linux} %{buildroot}%{uclibc_root}%{_includedir}

%clean
rm -rf %{buildroot}

%files -n %{libname}
%defattr(-,root,root)
%doc README
%dir %{uclibc_root}
%dir %{uclibc_root}{_prefix}
%ifnarch %{sparcx}
%dir %{uclibc_root}/%{_lib}
%dir %{uclibc_root}%{_libdir}
%{uclibc_root}/%{_lib}/*-*%{version}.so
%{uclibc_root}/%{_lib}/*.so.0
%endif

%files -n %{libdev}
%defattr(-,root,root)
%doc docs/* Changelog TODO
%{_bindir}/uclibc-gcc
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

%files -n %{libstat}
%defattr(-,root,root)
%{uclibc_root}%{_libdir}/lib*.a
%{uclibc_root}%{_libdir}/uclibc_nonshared.a
