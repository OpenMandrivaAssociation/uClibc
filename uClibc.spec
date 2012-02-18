# disable stack protector, build doesn't work with it
%define _ssp_cflags     %{nil}

%define	uclibc_root	%{_prefix}/uclibc
%define	uclibc_cc	uclibc-gcc

%define	majorish	0.9.32
%define	libname	%mklibname %{name} %{version}
%define	libdev	%mklibname %{name} -d

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	%{majorish}
Release:	3
License:	LGPLv2.1
Group:		System/Libraries
URL:		http://uclibc.org/
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.xz
Source2:	uClibc-0.9.32-config
Patch1:		uClibc-0.9.30.1-lib64.patch
# http://lists.busybox.net/pipermail/uclibc/2009-September/043035.html
Patch2:		uClibc-0.9.32-rc3-add-rpmatch-function.patch
# http://svn.exactcode.de/t2/branches/7.0/package/base/uclibc/scanf-aflag.patch
Patch3:		uClibc-0.9.31-add-scanf-a-flag.patch
# (proyvind): the ABI isn't stable, so set it to current version
Patch4:		uClibc-0.9.32-unstable-abi.patch
Patch5:		uClibc-0.9.32-fix-nptl-build-on-x86.patch
# from mga (rtp) add hacks for unwind symbol on arm (was picking glibc symbols
# so was trying to link together glibc&uClibc...)
Patch7:		uClibc-arm_hack_unwind.patch


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

%package -n	%{libname}
Summary:	%{summary}
Group:		System/Libraries
Requires:	uClibc
%rename	%{_lib}uClibc

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

%package -n	%{libdev}
Summary:	Development files & libraries for uClibc
Group:		Development/C
Requires:	%{libname} = %{EVRD}
%rename		%{name}-devel
%rename		%{_lib}uClibc-static-devel
%rename		%{name}-static-devel
Provides:	libc-static

%description -n	%{libdev}
Small libc for building embedded applications.

%prep
%setup -q
#%%patch1 -p1 -b .lib64~
%patch2 -p1 -b .rpmatch~
%patch3 -p1 -b .a_flag~
%patch4 -p1 -b .abi~
%patch5 -p1 -b .epoll~
%patch7 -p1 -b .unwind

%define arch %(echo %{_arch} | sed -e 's/ppc/powerpc/' -e 's!mips*!mips!')
%ifarch %arm
echo -e "CONFIG_ARM_EABI=y\n# ARCH_WANTS_BIG_ENDIAN is not set\nARCH_WANTS_LITTLE_ENDIAN=y\n" >> .config
cat %{SOURCE2} |sed \
	-e "s!UCLIBC_HAS_FPU=y!# UCLIBC_HAS_FPU is not set!g" \
	-e "s|@CFLAGS@|%{optflags}|g" \
%else
cat %{SOURCE2} |sed \
	-e "s|@CFLAGS@|%{optflags} %{ldflags} -muclibc -Wl,-rpath=%{uclibc_root}/%{_lib} -Wl,-rpath=%{uclibc_root}%{_libdir}|g" \
%endif
	-e "s|@ARCH@|%{arch}|g" \
	-e "s|@LIB@|%{_lib}|g" \
	-e "s|@PREFIX@|%{uclibc_root}|g" \
	>> .config

%build
yes "" | make oldconfig V=1

# parallel build breaks..
make VERBOSE=1 CPU_CFLAGS="" all utils

%check
exit 0
ln -snf %{_includedir}/{asm,asm-generic,linux} test
ln -snf %{buildroot}%{uclibc_root} install_dir
# This test relies on /etc/ethers being present to pass, so we'll skip it by
# removing it
rm -f test/inet/tst-ethers*
%make check VERBOSE=1 || /bin/true 

%install
#(proyvind): to prevent possible interference...
export LD_LIBRARY_PATH=
make VERBOSE=1 PREFIX=%{buildroot} install
make -C utils VERBOSE=1 PREFIX=%{buildroot} utils_install

# be sure that we don't package any backup files
find %{buildroot} -name \*~|xargs rm -f

install -d %{buildroot}%{_bindir}
# using 'rpm --eval' here for multilib purposes..
#TODO: figure out binutils --sysroot + multilib in binutils package?
cat > %{buildroot}%{_bindir}/%{uclibc_cc} << EOF
#!/bin/sh
export C_INCLUDE_PATH="\$(rpm --eval %%{uclibc_root}%%{_includedir}):\$(gcc -print-search-dirs|grep install:|cut -d\  -f2)include"
export LD_RUN_PATH="\$(rpm --eval %%{uclibc_root}/%%{_lib}:%%{uclibc_root}%%{_libdir})"
export LIBRARY_PATH="\$LD_RUN_PATH"
%ifarch %arm
# avoid getting troubles. without it, linker is called with -lgcc -lgss_s and then
# pulls glibc. Typical example are the unwind symbols.
# It's a really nasty hack :(
UNWIND_HACK=-static-libgcc
%endif
exec gcc -muclibc \$UNWIND_HACK "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{uclibc_cc}

install -d %{buildroot}%{_sysconfdir}/rpm/macros.d
cat > %{buildroot}%{_sysconfdir}/rpm/macros.d/uclibc.macros << EOF
%%uclibc_root	%{uclibc_root}
%%uclibc_cc	%{uclibc_cc}
%%uclibc_cflags	%%{optflags} -fno-stack-protector
EOF

#(peroyvind) rpm will make these symlinks relative
ln -snf %{_includedir}/{asm,asm-generic,linux} %{buildroot}%{uclibc_root}%{_includedir}

# crack hack to get uclibc working with chroot within uclibc root..
#mkdir -p %{buildroot}%{uclibc_root}%{uclibc_root}
#ln -s ../../%{_lib} %{buildroot}%{uclibc_root}%{uclibc_root}/%{_lib}

%if "%{_lib}" == "lib64"
ln -s ld64-uClibc.so.%{version} %{buildroot}%{uclibc_root}/%{_lib}/ld64-uClibc.so.0
install -d %{buildroot}%{uclibc_root}{/lib,%{_prefix}/lib}
%else
ln -s ld-uClibc.so.%{version} %{buildroot}%{uclibc_root}/lib/ld-uClibc.so.0
%endif

for dir in /bin /sbin %{_prefix} %{_bindir} %{_sbindir}; do
	mkdir -p %{buildroot}%{uclibc_root}$dir
done

mkdir -p %{buildroot}%{uclibc_root}%{_sysconfdir}
touch %{buildroot}%{uclibc_root}%{_sysconfdir}/ld.so.{conf,cache}

%post -p %{uclibc_root}/sbin/ldconfig

%triggerin -- %{uclibc_root}/lib/*.so.*, %{uclibc_root}/lib64/*.so.*, %{uclibc_root}%{_prefix}/lib/*.so.*, %{uclibc_root}%{_prefix}/lib64/*.so.*
%{uclibc_root}/sbin/ldconfig -X

%files
%doc README
%dir %{uclibc_root}/bin
%dir %{uclibc_root}/sbin
%dir %{uclibc_root}%{_bindir}
%dir %{uclibc_root}%{_sbindir}
%dir %{uclibc_root}%{_sysconfdir}
%verify(not md5 size mtime) %config(noreplace) %{uclibc_root}%{_sysconfdir}/ld.so.conf
%ghost %{uclibc_root}%{_sysconfdir}/ld.so.cache
%{uclibc_root}%{_bindir}/getconf
%{uclibc_root}%{_bindir}/ldd
%{uclibc_root}/sbin/ldconfig
#%dir %{uclibc_root}%{uclibc_root}
#%dir %{uclibc_root}%{uclibc_root}/%{_lib}
%if "%{_lib}" == "lib64"
%{uclibc_root}/%{_lib}/ld64-uClibc.so.0
#%{uclibc_root}%{uclibc_root}/%{_lib}/ld64-uClibc.so.0
%else
%{uclibc_root}/lib/ld-uClibc.so.0
#%{uclibc_root}%{uclibc_root}/lib/ld-uClibc.so.0
%endif

%files -n %{libname}
%dir %{uclibc_root}
%dir %{uclibc_root}%{_prefix}
%if "%{_lib}" == "lib64"
%dir %{uclibc_root}/lib
%dir %{uclibc_root}%{_prefix}/lib
%endif
%dir %{uclibc_root}/%{_lib}
%dir %{uclibc_root}%{_libdir}
%ifnarch %{sparcx}
%{uclibc_root}/%{_lib}/*-*%{version}.so
%{uclibc_root}/%{_lib}/*.so.%{version}
%endif

%files -n %{libdev}
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
%{uclibc_root}%{_libdir}/lib*.a
%{uclibc_root}%{_libdir}/uclibc_nonshared.a
