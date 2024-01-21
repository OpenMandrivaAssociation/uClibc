# disable stack protector, build doesn't work with it
%define _ssp_cflags %{nil}
# Same for LTO
%define _disable_lto 1

%define uclibc_root %{_prefix}/uclibc
%define uclibc_cc uclibc-gcc

%define libname %mklibname %{name}
%define devname %mklibname %{name} -d

%global optflags %{optflags} -ffreestanding -fcommon

%bcond_without	bootstrap

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	1.0.45
Release:	1
License:	LGPLv2.1
Group:		System/Libraries
Url:		http://uclibc-ng.org/
Source0:	https://downloads.uclibc-ng.org/releases/%{version}/uClibc-ng-%{version}.tar.xz
Source1:	uclibc.macros
Source2:	uClibc-0.9.33.3-config
Source3:	uclibc-gcc.specs

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
Requires:	%{dlopen_req gmp %{uclibc_root}%{_libdir}}
Requires:	%{dlopen_req intl %{uclibc_root}%{_libdir}}
Requires:	%{dlopen_req mpc %{uclibc_root}%{_libdir}}
Requires:	%{dlopen_req mpfr %{uclibc_root}%{_libdir}}
Requires:	%{dlopen_req z %{uclibc_root}%{_libdir}}
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
%global	cflags %{optflags} -Oz -std=gnu99 %{ldflags} -muclibc -Wl,-rpath=%{uclibc_root}/%{_lib} -Wl,-rpath=%{uclibc_root}%{_libdir}  %{?arch_cflags}

sed %{SOURCE2} \
%ifarch armv7l
	-e 's|.*\(UCLIBC_HAS_FPU\).*|# \1 is not set|g' \
%endif
%ifarch armv7hl armv7hln armv7hnl
	-e 's|.*\(UCLIBC_HAS_FPU\).*|\1=y|g' \
%endif
	-e 's|^\(TARGET_[a-z].*\).*|# \1 is not set|g' \
	-e 's|.*\(TARGET_%{arch}\).*|\1=y|g' \
	-e 's|.*\(TARGET_ARCH\).*|\1=%{arch}|g' \
%ifarch %{ix86}
	-e 's|.*\(TARGET_SUBARCH\).*|\1="%{_target_cpu}"\nCONFIG_586=y\n|g' \
%endif
	-e 's|.*\(RUNTIME_PREFIX\).*|\1="%{uclibc_root}"|g' \
	-e 's|.*\(DEVEL_PREFIX\).*|\1="%{uclibc_root}%{_prefix}"|g' \
	-e 's|.*\(MULTILIB_DIR\).*|\1="%{_lib}"|g' \
	-e 's|.*\(UCLIBC_EXTRA_CFLAGS\)=.*|\1="%{cflags}"|g' \
	> .config
%ifarch %{arm}
echo -e "CONFIG_ARM_EABI=y\n# ARCH_WANTS_BIG_ENDIAN is not set\nARCH_WANTS_LITTLE_ENDIAN=y\nCOMPILE_IN_THUMB_MODE=y\nUSE_BX=y\nCONFIG_FPU=y\n" >> .config
%endif

%build
make oldconfig VERBOSE=2 </dev/null

%make_build VERBOSE=2 CPU_CFLAGS="" all utils

%install
#(proyvind): to prevent possible interference...
export LD_LIBRARY_PATH=
%make VERBOSE=2 CPU_CFLAGS="" PREFIX=%{buildroot} install install_utils

# be sure that we don't package any backup files
find %{buildroot} -name \*~|xargs rm -f


%define gcc_path %(realpath %(gcc -print-search-dirs|grep install:|cut -d' '  -f2)/..)
%if "%{_lib}" == "lib64"
%define multilib %%{!m32:64}
%else
%define multilib %{nil}

%endif

install -d %{buildroot}%{uclibc_root}%{_datadir}
sed -e 's#@UCLIBC_ROOT@#%{uclibc_root}#g' -e 's#@PREFIX@#%{_prefix}#g' -e 's#@GCC_PATH@#%{gcc_path}#g' -e 's#@MULTILIB@#%{multilib}#g' %{SOURCE3} > %{buildroot}%{uclibc_root}%{_datadir}/gcc-spec-uclibc

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{uclibc_cc} << EOF
#!/bin/sh
exec gcc -muclibc -specs="%{uclibc_root}%{_datadir}/gcc-spec-uclibc" "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{uclibc_cc}

cat > %{buildroot}%{uclibc_root}%{_includedir}/sys/auxv.h << EOF
#warning no auxv.h in uClibc yet!
#undef _SYS_AUXV_H
#undef HAVE_SYS_AUXV_H
EOF

install -m644 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/rpm/macros.d/uclibc.macros

#(peroyvind) rpm will make these symlinks relative
ln -snf %{_includedir}/{asm,asm-generic,linux} %{buildroot}%{uclibc_root}%{_includedir}

# crack hack to get uclibc working with chroot within uclibc root..
#mkdir -p %{buildroot}%{uclibc_root}%{uclibc_root}
#ln -s ../../%{_lib} %{buildroot}%{uclibc_root}%{uclibc_root}/%{_lib}

for dir in /bin /sbin %{_prefix} %{_bindir} %{_sbindir}; do
	mkdir -p %{buildroot}%{uclibc_root}$dir
done

mkdir -p %{buildroot}%{uclibc_root}%{_sysconfdir}
touch %{buildroot}%{uclibc_root}%{_sysconfdir}/ld.so.{conf,cache}

%if !%{with bootstrap}
echo 'GROUP ( AS_NEEDED ( %{uclibc_root}/%{_lib}/%{libintl} ) )' >> %{buildroot}%{uclibc_root}%{_libdir}/libc.so
%endif

%triggerin -- %{uclibc_root}/lib/*.so.*, %{uclibc_root}/lib64/*.so.*, %{uclibc_root}%{_prefix}/lib/*.so.*, %{uclibc_root}%{_prefix}/lib64/*.so.*
%{uclibc_root}/sbin/ldconfig -X

%files
%doc README
%dir %{uclibc_root}/bin
%dir %{uclibc_root}/sbin
%dir %{uclibc_root}%{_bindir}
%{uclibc_root}%{_bindir}/iconv
%dir %{uclibc_root}%{_sysconfdir}
%verify(not md5 size mtime) %config(noreplace) %{uclibc_root}%{_sysconfdir}/ld.so.conf
%ghost %{uclibc_root}%{_sysconfdir}/ld.so.cache
%{uclibc_root}%{_bindir}/getconf
%{uclibc_root}%{_bindir}/ldd
%{uclibc_root}/sbin/ldconfig
%if "%{_lib}" == "lib64"
%{uclibc_root}/%{_lib}/ld64-uClibc.so.0
%else
%{uclibc_root}/lib/ld-uClibc.so.0
%endif
%dir %{uclibc_root}%{_datadir}
%{uclibc_root}%{_datadir}/gcc-spec-uclibc
%{uclibc_root}%{_bindir}/locale

%files -n %{libname}
%dir %{uclibc_root}
%dir %{uclibc_root}%{_prefix}
%dir %{uclibc_root}/%{_lib}
%dir %{uclibc_root}%{_libdir}
%{uclibc_root}/%{_lib}/ld64-uClibc-%{version}.so
%{uclibc_root}/%{_lib}/ld64-uClibc.so.1
%{uclibc_root}/%{_lib}/libc.so.0
%{uclibc_root}/%{_lib}/libc.so.1
%{uclibc_root}/%{_lib}/libuClibc-1.0.45.so

%files -n %{devname}
%doc docs/*
%{_bindir}/%{uclibc_cc}
%{_sysconfdir}/rpm/macros.d/uclibc.macros
%{uclibc_root}%{_includedir}
%{uclibc_root}%{_libdir}/crt1.o
%{uclibc_root}%{_libdir}/crti.o
%{uclibc_root}%{_libdir}/crtn.o
%{uclibc_root}%{_libdir}/Scrt1.o
%{uclibc_root}%{_libdir}/libc.so
%{uclibc_root}%{_libdir}/lib*.a
%{uclibc_root}%{_libdir}/uclibc_nonshared.a
%{uclibc_root}%{_libdir}/rcrt1.o
