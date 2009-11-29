%define _enable_debug_packages	%{nil}
%define debug_package		%{nil}

# workaround some rpm bug
%define _requires_exceptions statically\\|linked\\|devel(/lib/libNoVersion)\\|bash

# disable stack protector, build doesn't work with it
%define _ssp_cflags %{nil}

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	0.9.30.1
Release:	%mkrel 1
License:	LGPL
Group:		System/Libraries
URL:		http://uclibc.org/
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2
Source1:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2.sign
Source2:	uClibc-0.9.30.2-config
Patch0:		uClibc-0.9.30.1-getline.patch

#Patches from uClibc buildroot:
Patch100:	uClibc-0.9.30.1-64bit-strtouq.patch
Patch101:	uClibc-0.9.30.1-arm-fix-linuxthreads-sysdep.patch
Patch102:	uClibc-0.9.30.1-c99-ldbl-math.patch
Patch103:	uClibc-0.9.30.1-dl-sysdep-inline.patch
Patch104:	uClibc-0.9.30.1-fix-getaddrinfo.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
uClibc (pronounced yew-see-lib-see) is a C library for developing
embedded Linux systems. It is much smaller than the GNU C Library,
but nearly all applications supported by glibc also work perfectly
with uClibc. Porting applications from glibc to uClibc typically
involves just recompiling the source code. uClibc even supports
shared libraries and threading. It currently runs on standard
Linux and  MMU-less (also known as uClinux) systems with support
for alpha, ARM, cris, i386, i960, h8300, m68k, mips/mipsel,
PowerPC, SH, SPARC, and v850 processors.

If you are building an embedded Linux system and you find that
glibc is eating up too much space, you should consider using
uClibc. If you are building a huge fileserver with 12 Terabytes of
storage, then using glibc may make more sense. Unless, for
example, that 12 Terabytes will be Network Attached Storage and
you plan to burn Linux into the system's firmware...

%package	devel
Summary:	Development files for uClibc
Group:		Development/C
Requires:	%{name} = %{version}-%{release}

%description	devel
Small libc for building embedded applications.

%package	static-devel
Summary:	Static uClibc libratries
Group:		Development/C
Requires:	%{name}-devel = %{version}-%{release}
Provides:	libc-static

%description	static-devel
Static uClibc libratries.

%prep
%setup -q
%patch0 -p1 -b .getline~
%patch100 -p1 -b .64bit_strouq~
%patch101 -p1 -b .arm_linuxthreads~
%patch102 -p1 -b .c99_math~
%patch103 -p1 -b .dl_sysdep~
%patch104 -p1 -b .getaddrinfo~

%build
arch=$(echo %{_arch}=y | sed -e 's/ppc/powerpc/')
echo "TARGET_$arch=y" >.config
echo "TARGET_ARCH=\"$arch\"" >>.config
cat %{SOURCE2} |sed -e 's|^.*UCLIBC_EXTRA_CFLAGS.*$|UCLIBC_EXTRA_CFLAGS="%{optflags} -Os"|g'>> .config
yes "" | %make oldconfig V=1

%make V=1 

%check
ln -snf %{_includedir}/{asm,asm-generic,linux} test
ln -snf %{buildroot}%{_prefix}/%{_arch}-linux-uclibc install_dir
# This test relies on /etc/ethers being present to pass, so we'll skip it by
# removing it
rm -f test/inet/tst-ethers*
%make check V=1 || /bin/true 

%install
rm -rf %{buildroot}

make PREFIX=%{buildroot} install

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{_arch}-linux-uclibc-gcc << EOF
#!/bin/sh
gcc -B%{_prefix}/%{_arch}-linux-uclibc/usr/lib -isystem /usr/x86_64-linux-uclibc/usr/include \$@
EOF
chmod +x %{buildroot}%{_bindir}/%{_arch}-linux-uclibc-gcc
 
%ifarch ppc ppc64
    ln -sf ppc-linux-uclibc %{buildroot}%{_prefix}/powerpc-linux-uclibc
%endif

#(peroyvind) rpm will make these symlinks relative
ln -snf /usr/include/{asm,asm-generic,linux} %{buildroot}%{_prefix}/%{_arch}-linux-uclibc/usr/include/

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README
%dir %{_prefix}/%{_arch}-linux-uclibc
%ifnarch %{sparcx}
%dir %{_prefix}/%{_arch}-linux-uclibc/lib
%{_prefix}/%{_arch}-linux-uclibc/lib/*-*%{version}.so
%{_prefix}/%{_arch}-linux-uclibc/lib/*.so.0
%endif
%ifarch ppc ppc64
%{_prefix}/powerpc-linux-uclibc
%endif

%files devel
%defattr(-,root,root)
%doc docs/* COPYING.LIB Changelog TODO
%{_bindir}/%{_arch}-linux-uclibc-gcc
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/crt1.o
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/crti.o
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/crtn.o
%ifnarch %{sparcx}
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/Scrt1.o
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/librt.so
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/libnsl.so
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/libpthread.so
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/libc.so
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/libcrypt.so
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/libdl.so
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/libm.so
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/libresolv.so
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/libutil.so
%endif
%{_prefix}/%{_arch}-linux-uclibc/usr/include

%files static-devel
%defattr(-,root,root)
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/lib*.a
%{_prefix}/%{_arch}-linux-uclibc/usr/lib/uclibc_nonshared.a


