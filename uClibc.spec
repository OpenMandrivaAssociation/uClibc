# disable stack protector, build doesn't work with it
%define _ssp_cflags     %{nil}

%define	uclibc_root	%{_prefix}/uclibc
%define	uclibc_cc	uclibc-gcc

%define	majorish	0.9.30
%define	minorish	2

%define snapshot	1
%if snapshot
%define	prerel		20091207
%define	libver		%{majorish}-git
%else
%define	libver		%{majorish}.%{minorish}
%endif

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	%{majorish}.%{minorish}
Release:	%mkrel 0.%{prerel}.1
License:	LGPL
Group:		System/Libraries
URL:		http://uclibc.org/
Source0:	http://uclibc.org/downloads/%{name}-%{?prerel}%{!?prerel:%{version}}.tar.bz2
%{!?prerel:
Source1:        http://uclibc.org/downloads/%{name}-%{version}.tar.bz2.sign
}
Source2:	uClibc-0.9.30.2-config
Patch1:		uClibc-0.9.30.2-lib64.patch
# http://lists.busybox.net/pipermail/uclibc/2009-September/043035.html
Patch2:		uClibc-0.9.30.2-add-rpmatch-function.patch
# http://svn.exactcode.de/t2/branches/7.0/package/base/uclibc/scanf-aflag.patch
Patch3:		uClibc-0.9.30.2-add-scanf-a-flag.patch
# (proyvind): the ABI isn't stable, so set it to current version
Patch4:		uClibc-0.9.30.2-unstable-abi.patch

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

%define	libname	%mklibname %{name} %{libver}
%package -n	%{libname}
Summary:	%{summary}
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}
Provides:	%mklibname %{name}
Obsoletes:	%{name} <= %{version}-%{release}
Obsoletes:      %{mklibname %{name}} <= %{version}-%{release}

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
%setup -q -n %{name}%{!?prerel:-%{version}}
%patch1 -p1 -b .lib64~
%patch2 -p1 -b .rpmatch~
%patch3 -p1 -b .a_flag~
%patch4 -p1 -b .abi_version~

%define arch %(echo %{_arch} | sed -e 's/ppc/powerpc/')
cat %{SOURCE2} |sed \
	-e "s|@CFLAGS@|-muclibc %{optflags}|g" \
	-e 's|@ARCH@|%{arch}|g' \
	-e 's|@LIB@|%{_lib}|g' \
	-e 's|@PREFIX@|%{uclibc_root}|g' \
	>> .config

%build
yes "" | %make oldconfig V=1

%make VERBOSE=1 CPU_CFLAGS=""

%check
ln -snf %{_includedir}/{asm,asm-generic,linux} test
ln -snf %{buildroot}%{uclibc_root} install_dir
# This test relies on /etc/ethers being present to pass, so we'll skip it by
# removing it
rm -f test/inet/tst-ethers*
%make check VERBOSE=1 || /bin/true 

%install
rm -rf %{buildroot}

%make VERBOSE=1 PREFIX=%{buildroot} install
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
gcc -muclibc \$@
EOF
chmod +x %{buildroot}%{_bindir}/%{uclibc_cc}

install -d %{buildroot}%{_sysconfdir}/rpm/macros.d
cat > %{buildroot}%{_sysconfdir}/rpm/macros.d/uclibc.macros << EOF
%%uclibc_root	%uclibc_root
%%uclibc_cc	%uclibc_cc
%%uclibc_cflags	%%{optflags} -g0 -Os -fno-stack-protector
EOF

#(peroyvind) rpm will make these symlinks relative
ln -snf %{_includedir}/{asm,asm-generic,linux} %{buildroot}%{uclibc_root}%{_includedir}

%clean
rm -rf %{buildroot}

%files -n %{libname}
%defattr(-,root,root)
%doc README
%dir %{uclibc_root}
%dir %{uclibc_root}%{_prefix}
%ifnarch %{sparcx}
%dir %{uclibc_root}/%{_lib}
%dir %{uclibc_root}%{_libdir}
%{uclibc_root}/%{_lib}/*-*%{libver}.so
%{uclibc_root}/%{_lib}/*.so.%{libver}
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
