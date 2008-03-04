%define _enable_debug_packages	%{nil}
%define debug_package		%{nil}

# workaround some rpm bug
%define _requires_exceptions statically\\|linked\\|devel(/lib/libNoVersion)\\|bash

# disable stack protector, build doesn't work with it
%define _ssp_cflags %{nil}

%define	mainver	0.9.28
%define	subver	1

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	%{mainver}.%{subver}
Release:	%mkrel 3
License:	LGPL
Group:		System/Libraries
URL:		http://uclibc.org/
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2
Source1:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2.sign
Patch0:		uClibc-0.9.27-mdkconf.patch
Patch1:		uClibc-newsoname.patch
Patch2:		uClibc-alpha.patch
Patch3:		uClibc-toolchain-wrapper.patch
Patch4:		uClibc-targetcpu.patch
Patch5:		uClibc-O_DIRECT.patch
Patch6:		uClibc-sparc.patch
Patch7:		uClibc-x86_64.patch
BuildRequires:	which kernel-source
#Requires:	binutils gcc-cpp = %{gcc_version}
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
#Requires:	gcc = %{gcc_version}

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
#cp %SOURCE2 ldso/ldso/x86_64
%patch0 -p1 -b .mdkconf
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
#%patch6 -p1
%patch7 -p1

mkdir -p extra/gcc-uClibc
cp -a extra/gcc-uClibc extra/tmpgcc
 
find -name ".svn" | xargs rm -rf

%build
make defconfig TARGET_ARCH="%{_arch}" TARGET_CPU="%{_target_cpu}" KERNEL_SOURCE=%{_prefix} HOSTCFLAGS="%{optflags}" OPTIMIZATION="%{optflags} -Os" GCC_BIN="%{_bindir}/gcc"

rm -f include/bits/uClibc_config.h

%make TARGET_ARCH="%{_arch}" TARGET_CPU="%{_target_cpu}" KERNEL_SOURCE=%{_prefix} HOSTCFLAGS="%{optflags}" OPTIMIZATION="%{optflags} -Os" GCC_BIN="%{_bindir}/gcc"

%check
#cd test
#make

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_bindir}

make TARGET_ARCH="%{_arch}" TARGET_CPU="%{_target_cpu}" PREFIX=%{buildroot} install
make TARGET_ARCH="%{_arch}" TARGET_CPU="%{_target_cpu}" PREFIX=%{buildroot} -C extra/gcc-uClibc install

# We need to build a temporary compiler that looks into our
# build directory instead of /usr
pushd extra/tmpgcc
    perl -pi -e "s/^all:/DEVEL_PREFIX=\.\.\/\nall:/;" Makefile
    %make TARGET_ARCH="%{_arch}" TARGET_CPU="%{_target_cpu}" KERNEL_SOURCE=%{_prefix} HOSTCFLAGS="%{optflags}" OPTIMIZATION="%{optflags} -Os" GCC_BIN="%{_bindir}/gcc"
popd

# Utils don't build with regular GCC, we need to use the temporary
# compiler above.
pushd utils
    perl -pi -e "s/Rules\.mak/Rules\.mak\nCC=\.\.\/extra\/tmpgcc\/%{_target_cpu}-uclibc-gcc/;" Makefile
    perl -pi -e "s/-s \\\\/-s -static \\\\/g;" Makefile
    perl -pi -e "s/R_PREFIX/RUNTIME_PREFIX/g;" Makefile
    perl -pi -e "s|UCLIBC_RUNTIME_PREFIX \"|\"%{_prefix}/%{_target_cpu}-linux-uclibc/|g;" ../ldso/include/ld_elf.h
    perl -pi -e "s|UCLIBC_RUNTIME_PREFIX \"|\"%{_prefix}/%{_target_cpu}-linux-uclibc/|g;" ldd.c
    perl -pi -e "s|UCLIBC_RUNTIME_PREFIX \"|\"%{_prefix}/%{_target_cpu}-linux-uclibc/|g;" ldconfig.c
    %make TARGET_ARCH="%{_arch}" TARGET_CPU="%{_target_cpu}" KERNEL_SOURCE=%{_prefix} HOSTCFLAGS="%{optflags}" OPTIMIZATION="%{optflags} -Os" GCC_BIN="%{_bindir}/gcc"
    cp ldd %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/bin/%{_target_cpu}-uclibc-ldd
    ln -sf ../../bin/%{_target_cpu}-uclibc-ldd %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc%{_bindir}/ldd
    mkdir -p %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/sbin
    cp ldconfig %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/sbin
popd
mkdir -p %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/etc

# convenience function
cat > %{buildroot}%{_bindir}/uclibc << EOF
#!/bin/sh
export PATH=%{_prefix}/%{_target_cpu}-linux-uclibc%{_bindir}:\$PATH
\$@
EOF

%ifarch ppc ppc64
    ln -sf ppc-linux-uclibc %{buildroot}%{_prefix}/powerpc-linux-uclibc
%endif

# these links are *needed* (by stuff in bin/)
#for f in %{buildroot}%{_prefix}/%{_arch}-linux-uclibc%{_bindir}/* ; do
#    ln -sf ../../bin/%{_arch}-uclibc-`basename $f` $f
#done

#find %{buildroot}%{_prefix}/%{_arch}-linux-uclibc/include -name CVS | xargs rm -rf

# OE: don't ship these?
rm -rf %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/usr/include/asm
rm -rf %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/usr/include/linux
rm -rf %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/usr/include/scsi

#(peroyvind) rpm will make these symlinks relative
ln -snf /usr/include/asm %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/usr/include/asm
ln -snf /usr/include/linux %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/usr/include/linux
ln -snf /usr/include/scsi %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/usr/include/scsi

# at least nuke this one...
rm -rf %{buildroot}%{_prefix}/%{_target_cpu}-linux-uclibc/usr/include/linux/modules

%clean
rm -rf %{buildroot}

%files
%defattr(644,root,root,755)
%doc README
%dir %{_prefix}/%{_target_cpu}-linux-uclibc
%ifnarch %{sunsparc}
%dir %{_prefix}/%{_target_cpu}-linux-uclibc/lib
%dir %{_prefix}/%{_target_cpu}-linux-uclibc/etc
%dir %{_prefix}/%{_target_cpu}-linux-uclibc/sbin
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/sbin/*
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/ld-*
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/lib*%{mainver}.so
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/lib*.so.0
%endif
%ifarch ppc ppc64
%{_prefix}/powerpc-linux-uclibc
%endif

%files devel
%defattr(644,root,root,755)
%doc docs/* docs/uclibc.org/*.html COPYING.LIB Changelog TODO
%dir %{_prefix}/%{_target_cpu}-linux-uclibc/usr/bin
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/usr/bin/*
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/bin/*
%attr(0755,root,root) %{_bindir}/uclibc
#%{_prefix}/%{_target_cpu}-linux-uclibc/usr
#%{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/crt0.o
%{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/crt1.o
%{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/crti.o
%{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/crtn.o
%ifnarch %{sunsparc}
%{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/Scrt1.o
%{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/librt.so
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/libnsl.so
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/libpthread*.so*
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/libc.so
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/libcrypt.so
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/libdl.so
%attr(02755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/libm.so
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/libresolv.so
%attr(0755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/libutil.so
%endif
%{_prefix}/%{_target_cpu}-linux-uclibc/usr/include

%files static-devel
%defattr(644,root,root,755)
%{_prefix}/%{_target_cpu}-linux-uclibc/usr/lib/lib*.a


