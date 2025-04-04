# disable stack protector, build doesn't work with it
%define _ssp_cflags %{nil}
# Same for LTO
%define _disable_lto 1

%define uclibc_root %{_prefix}/%(echo %{_target_platform}|cut -d- -f1-3)-uclibc
%define uclibc_cc uclibc-gcc

%define libname %mklibname %{name}
%define devname %mklibname %{name} -d

%global optflags %{optflags} -ffreestanding -fcommon

%bcond_without	bootstrap

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	1.0.51
Release:	1
License:	LGPLv2.1
Group:		System/Libraries
Url:		https://uclibc-ng.org/
Source0:	https://downloads.uclibc-ng.org/releases/%{version}/uClibc-ng-%{version}.tar.xz
Source1:	uclibc.macros
Source2:	uclibc-gcc.specs
Source10:	uClibc-common.config
Source11:	uClibc-x86_64.config
Source12:	uClibc-aarch64.config
Patch1:		ldconfig-_dl_auxvt.patch

BuildRequires:	locales-en kernel-headers

%description
uClibc (pronounced yew-see-lib-see) is a c library for developing
embedded linux systems. it is much smaller than the gnu c library,
but nearly all applications supported by glibc also work perfectly
with uclibc. porting applications from glibc to uclibc typically
involves just recompiling the source code. uclibc even supports
shared libraries and threading. it currently runs on standard
linux and  mmu-less (also known as uclinux) systems with support
for alpha, arm, cris, i386, i960, h8300, m68k, mips/mipsel,
powerpc, sh, sparc, and v850 processors.

if you are building an embedded linux system and you find that
glibc is eating up too much space, you should consider using
uclibc. if you are building a huge fileserver with 12 terabytes of
storage, then using glibc may make more sense. unless, for
example, that 12 terabytes will be network attached storage and
you plan to burn linux into the system's firmware...

%package -n %{libname}
Summary:	%{summary}
Group:		System/Libraries
Requires:	uClibc >= %{EVRD}
%rename		%{_lib}uClibc

%description -n	%{libname}
uClibc (pronounced yew-see-lib-see) is a c library for developing
embedded linux systems. it is much smaller than the gnu c library,
but nearly all applications supported by glibc also work perfectly
with uclibc. porting applications from glibc to uclibc typically
involves just recompiling the source code. uclibc even supports
shared libraries and threading. it currently runs on standard
linux and  mmu-less (also known as uclinux) systems with support
for alpha, arm, cris, i386, i960, h8300, m68k, mips/mipsel,
powerpc, sh, sparc, and v850 processors.

if you are building an embedded linux system and you find that
glibc is eating up too much space, you should consider using
uclibc. if you are building a huge fileserver with 12 terabytes of
storage, then using glibc may make more sense. unless, for
example, that 12 terabytes will be network attached storage and
you plan to burn linux into the system's firmware...

%package -n %{devname}
Summary:	Development files & libraries for uClibc
Group:		Development/C
Requires:	%{libname} = %{EVRD}
# as the libc.so linker scripts adds a AS_NEEDED dependency on libintl.so to
# workaround issue with packages that expects to find some of it's functionality
# in glibc, we need to add a dependency on it
# XXX: should dependency generator pick up dependencies from linker scripts?
%if !%{with bootstrap}
BuildRequires:	uclibc-gettext-devel >= 0.18.1.1-9
BuildRequires:	uclibc-gmp-devel
BuildRequires:	uclibc-libmpc-devel
BuildRequires:	uclibc-mpfr-devel
BuildRequires:	uclibc-zlib-devel
Requires:	%{dlopen_req gmp %{uclibc_root}/lib}
Requires:	%{dlopen_req intl %{uclibc_root}/lib}
Requires:	%{dlopen_req mpc %{uclibc_root}/lib}
Requires:	%{dlopen_req mpfr %{uclibc_root}/lib}
Requires:	%{dlopen_req z %{uclibc_root}/lib}
%if "%(rpm -q --qf '%%{name}' gettext-devel)" == "gettext-devel"
%define	libintl	%(objdump -p %{uclibc_root}%{_libdir}/libintl.so|grep -e SONAME|sed -e 's#.*\\\(lib.*\\\)\$#\\\1#g')
%endif
%endif
%rename		%{name}-devel
%rename		%{_lib}uClibc-static-devel
%rename		%{name}-static-devel
Provides:	libc-static

%description -n	%{devname}
Small libc for building embedded applications.

%prep
%autosetup -p1 -n uClibc-ng-%{version}

%define arch %(echo %{_arch} | sed -e 's/ppc/powerpc/' -e 's!mips*!mips!')

%ifarch %{arm}
%define arch_cflags -marm -Wa,-mimplicit-it=thumb -D__thumb2__
%endif
%ifarch %{ix86}
# -fvar-tracking-assignments creates sections uClibc's ld.so can't parse
%define arch_cflags -fno-var-tracking-assignments
%endif
%global	cflags %{optflags} -Oz -std=gnu99 %{ldflags} -muclibc -Wl,-rpath=%{uclibc_root}/lib %{?arch_cflags}

cat %{S:10} %{_sourcedir}/uClibc-%{_arch}.config >.config
cat >>.config <<EOF
RUNTIME_PREFIX="%{uclibc_root}"
DEVEL_PREFIX="%{uclibc_root}"
MULTILIB_DIR="lib"
UCLIBC_EXTRA_CFLAGS="%{cflags}"
EOF
make oldconfig

%build
%make_build all utils

%install
%make_install install_utils

# be sure that we don't package any backup files
find %{buildroot} -name \*~|xargs rm -f


%define gcc_path %(realpath %(gcc -print-search-dirs|grep install:|cut -d' '  -f2)/..)

install -d %{buildroot}%{_datadir}
sed -e 's#@UCLIBC_ROOT@#%{uclibc_root}#g' -e 's#@PREFIX@#%{_prefix}#g' -e 's#@GCC_PATH@#%{gcc_path}#g' -e 's#@MULTILIB@#%{multilib}#g' %{S:2} > %{buildroot}%{_datadir}/gcc-spec-uclibc

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{uclibc_cc} << EOF
#!/bin/sh
exec gcc -muclibc -specs="%{_datadir}/gcc-spec-uclibc" "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{uclibc_cc}

install -m644 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/rpm/macros.d/uclibc.macros

#(peroyvind) rpm will make these symlinks relative
ln -snf %{_includedir}/{asm,asm-generic,linux} %{buildroot}%{uclibc_root}/include

mkdir -p %{buildroot}%{uclibc_root}%{_sysconfdir}
touch %{buildroot}%{uclibc_root}%{_sysconfdir}/ld.so.{conf,cache}

%if !%{with bootstrap}
echo 'GROUP ( AS_NEEDED ( %{uclibc_root}/lib/%{libintl} ) )' >> %{buildroot}%{uclibc_root}/lib/libc.so
%endif

%triggerin -- %{uclibc_root}/lib/*.so.*
%{uclibc_root}/sbin/ldconfig -X

%files
%doc README
%dir %{uclibc_root}%{_sysconfdir}
%verify(not md5 size mtime) %config(noreplace) %{uclibc_root}%{_sysconfdir}/ld.so.conf
%ghost %{uclibc_root}%{_sysconfdir}/ld.so.cache
%{uclibc_root}/bin/iconv
%{uclibc_root}/bin/getconf
%{uclibc_root}/bin/ldd
%{uclibc_root}/sbin/ldconfig
%{uclibc_root}/lib/ld*-uClibc.so.0
%{uclibc_root}/bin/locale

%files -n %{libname}
%{uclibc_root}/lib/ld*-uClibc-%{version}.so
%{uclibc_root}/lib/ld*-uClibc.so.1
%{uclibc_root}/lib/libc.so.0
%{uclibc_root}/lib/libc.so.1
%{uclibc_root}/lib/libuClibc-%{version}.so

%files -n %{devname}
%doc docs/*
%{_bindir}/%{uclibc_cc}
%{_datadir}/gcc-spec-uclibc
%{_sysconfdir}/rpm/macros.d/uclibc.macros
%{uclibc_root}/include/*
%{uclibc_root}/lib/crt1.o
%{uclibc_root}/lib/crti.o
%{uclibc_root}/lib/crtn.o
%{uclibc_root}/lib/Scrt1.o
%{uclibc_root}/lib/libc.so
%{uclibc_root}/lib/lib*.a
%{uclibc_root}/lib/uclibc_nonshared.a
%{uclibc_root}/lib/rcrt1.o
