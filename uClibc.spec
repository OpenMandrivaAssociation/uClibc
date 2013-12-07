# disable stack protector, build doesn't work with it
%define _ssp_cflags %{nil}

%define uclibc_root %{_prefix}/uclibc
%define uclibc_cc uclibc-gcc

%define majorish 0.9.33
%define libname %mklibname %{name} %{majorish}
%define devname %mklibname %{name} -d

%bcond_with bootstrap

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	%{majorish}.2
Release:	33
License:	LGPLv2.1
Group:		System/Libraries
Url:		http://uclibc.org/
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.xz
Source1:	uclibc.macros
Source2:	uClibc-0.9.33.2-config
Patch1:		uClibc-0.9.33.2-lib64.patch
# http://lists.busybox.net/pipermail/uclibc/2009-September/043035.html
Patch2:		uClibc-0.9.32-rc3-add-rpmatch-function.patch
# http://svn.exactcode.de/t2/branches/7.0/package/base/uclibc/scanf-aflag.patch
Patch3:		uClibc-0.9.31-add-scanf-a-flag.patch
# (proyvind): the ABI isn't stable, so set it to current version
Patch4:		uClibc-0.9.33.2-unstable-abi.patch
# (bero): Don't mix asm instructions into C code... Put them where they belong
Patch5:		uClibc-0.9.33.2-arm-compile.patch
# from mga (rtp) add hacks for unwind symbol on arm (was picking glibc symbols
# so was trying to link together glibc&uClibc...)
Patch7:		uClibc-arm_hack_unwind.patch
Patch8:		uClibc-0.9.32-no-gstabs.patch
# http://lists.busybox.net/pipermail/uclibc/2011-March/045003.html
Patch9:		uClibc-0.9.33.2-origin.patch
Patch10:	uClibc-0.9.33-posix_fallocate.patch
Patch11:	uClibc-0.9.33-dup3.patch
Patch12:	uClibc-0.9.33.2-add-missing-make-rule-on-locale-header.patch
Patch13:	uClibc-0.9.33.2-sync-mount.h-with-glibc.patch
Patch14:	uClibc-0.9.33-add-execvpe.patch
Patch15:	uClibc-0.9.33-define-MSG_CMSG_CLOEXEC.patch
Patch16:	uClibc-0.9.33-argp-support.patch
Patch17:	uClibc-0.9.33-argp-headers.patch
Patch18:	uClibc-0.9.33.2-trim-slashes-for-libubacktrace-path-in-linker-script.patch
# from origin/0.9.33 branch
Patch100:	0001-librt-re-add-SIGCANCEL-to-the-list-of-blocked-signal.patch
Patch101:	0001-nptl-sh-fix-race-condition-in-lll_wait_tid.patch
# from origin/HEAD branch
Patch200:	0001-i386-bits-syscalls.h-allow-immediate-values-as-6th-s.patch
Patch201:	0001-bits-time.h-sync-with-glibc-2.16.patch
# (tpg) fix build with kernel 3.10
# http://git.mirror.nanl.de/?p=openwrt.git;a=blob;f=toolchain/uClibc/patches-0.9.33.2/970-add___kernel_long_and___kernel_ulong.patch
Patch202:	0001-Remove-pragma-weak-for-undeclared-symbol.patch
Patch203:	970-add___kernel_long_and___kernel_ulong-2.patch
BuildRequires:	locales-en

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
Provides:	%mklibname %{name} %{majorish}
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
BuildRequires:	gettext-devel >= 0.18.1.1-9
# get around build system issue..
%if "%(rpm -q --qf '%%{name}' gettext-devel)" == "gettext-devel"
%define	libintl	%(objdump -p %{uclibc_root}%{_libdir}/libintl.so|grep -e SONAME|sed -e 's#.*\\\(lib.*\\\)\$#\\\1#g')
Requires:	%(%{_rpmhome}/bin/rpmdeps --provides `readlink -f %{uclibc_root}/%{_lib}/%{libintl}`|grep %{libintl})
%endif
%endif
%rename		%{name}-devel
%rename		%{_lib}uClibc-static-devel
%rename		%{name}-static-devel
Provides:	libc-static

%description -n	%{devname}
Small libc for building embedded applications.

%prep
%setup -q
%patch1 -p1 -b .lib64~
%patch2 -p1 -b .rpmatch~
%patch3 -p1 -b .a_flag~
%patch4 -p1 -b .abi~
# breaks build if enabled on x86_64 at least...
%ifarch %{arm}
%patch5 -p1 -b .armasm~
%endif
%patch7 -p1 -b .unwind~
%patch8 -p1 -b .gstabs~
%patch9 -p1 -b .origin~
%patch10 -p1 -b .fallocate~
%patch11 -p1 -b .dup3~
%patch12 -p1 -b .locale~
%patch13 -p1 -b .mount~
%patch14 -p1 -b .execvpe~
%patch15 -p1 -b .cloexec~
%patch16 -p1 -b .argp_c~
%patch17 -p1 -b .argp_h~
%patch18 -p1 -b .trim_slashes~
%patch100 -p1 -b .sigcancel~
%patch101 -p1 -b .race_cond~
%patch200 -p1 -b .immediate_vals~
%patch201 -p1 -b .bits_time~
%patch202 -p1 -b .weak~
%patch203 -p1 -b .ulong

%define arch %(echo %{_arch} | sed -e 's/ppc/powerpc/' -e 's!mips*!mips!')

%ifarch %{arm}
%define arch_cflags -marm -Wa,-mimplicit-it=thumb -D__thumb2__
%endif
%ifarch %{ix86}
# -fvar-tracking-assignments creates sections uClibc's ld.so can't parse
%define arch_cflags -fno-var-tracking-assignments
%endif
%global	cflags %{optflags} -Os -std=gnu99 %{ldflags} -muclibc -Wl,-rpath=%{uclibc_root}/%{_lib} -Wl,-rpath=%{uclibc_root}%{_libdir} -fuse-ld=bfd %{?arch_cflags}

sed %{SOURCE2} \
%ifarch armv7l
	-e 's|.*\(UCLIBC_HAS_FPU\).*|# \1 is not set|g' \
%endif
%ifarch armv7hl
	-e 's|.*\(UCLIBC_HAS_FPU\).*|\1=y|g' \
%endif
	-e 's|^\(TARGET_[a-z].*\).*|# \1 is not set|g' \
	-e 's|.*\(TARGET_%{arch}\).*|\1=y|g' \
	-e 's|.*\(TARGET_ARCH\).*|\1=%{arch}|g' \
	-e 's|.*\(RUNTIME_PREFIX\).*|\1="%{uclibc_root}"|g' \
	-e 's|.*\(DEVEL_PREFIX\).*|\1="%{uclibc_root}%{_prefix}"|g' \
	-e 's|.*\(MULTILIB_DIR\).*|\1="%{_lib}"|g' \
	-e 's|.*\(UCLIBC_EXTRA_CFLAGS\)=.*|\1="%{cflags}"|g' \
	> .config
%ifarch %{arm}
echo -e "CONFIG_ARM_EABI=y\n# ARCH_WANTS_BIG_ENDIAN is not set\nARCH_WANTS_LITTLE_ENDIAN=y\nCOMPILE_IN_THUMB_MODE=y\nUSE_BX=y\nCONFIG_FPU=y\n" >> .config
%endif

%build
yes "" | %make oldconfig VERBOSE=2

%make CC="gcc -fuse-ld=bfd" VERBOSE=2 CPU_CFLAGS="" UCLIBC_EXTRA_CFLAGS="%{cflags}"

%check
exit 0
ln -snf %{_includedir}/{asm,asm-generic,linux} test
ln -snf %{buildroot}%{uclibc_root} install_dir
# This test relies on /etc/ethers being present to pass, so we'll skip it by
# removing it
rm -f test/inet/tst-ethers*
%make check VERBOSE=2 || /bin/true

%install
#(proyvind): to prevent possible interference...
export LD_LIBRARY_PATH=
make CC="gcc -fuse-ld=bfd" VERBOSE=2 CPU_CFLAGS="" UCLIBC_EXTRA_CFLAGS="%{cflags}" PREFIX=%{buildroot} install
make CC="gcc -fuse-ld=bfd" -C utils VERBOSE=2 CPU_CFLAGS="" UCLIBC_EXTRA_CFLAGS="%{cflags}" PREFIX=%{buildroot} utils_install

# be sure that we don't package any backup files
find %{buildroot} -name \*~|xargs rm -f

install -d %{buildroot}%{_bindir}
# using 'rpm --eval' here for multilib purposes..
#TODO: figure out binutils --sysroot + multilib in binutils package?
cat > %{buildroot}%{_bindir}/%{uclibc_cc} << EOF
#!/bin/sh
export C_INCLUDE_PATH="\$(rpm --eval %%{uclibc_root}%%{_includedir}):\$(gcc -print-search-dirs|grep install:|cut -d\  -f2)include"
#XXX: this should add rpath, but for some reason it no longer happens and we
# have to pass the -rpath option to the linker as well
export LD_RUN_PATH="\$(rpm --eval %%{uclibc_root}/%%{_lib}:%%{uclibc_root}%%{_libdir})"
export LIBRARY_PATH="\$LD_RUN_PATH"
%ifarch %{arm}
# avoid getting troubles. without it, linker is called with -lgcc -lgss_s and then
# pulls glibc. Typical example are the unwind symbols.
# It's a really nasty hack :(
UNWIND_HACK=-static-libgcc
%endif
exec gcc -muclibc \$UNWIND_HACK -Wl,-rpath="\$LD_RUN_PATH" -Wl,-nostdlib "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{uclibc_cc}

install -m644 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/rpm/macros.d/uclibc.macros

#(peroyvind) rpm will make these symlinks relative
ln -snf %{_includedir}/{asm,asm-generic,linux} %{buildroot}%{uclibc_root}%{_includedir}

# crack hack to get uclibc working with chroot within uclibc root..
#mkdir -p %{buildroot}%{uclibc_root}%{uclibc_root}
#ln -s ../../%{_lib} %{buildroot}%{uclibc_root}%{uclibc_root}/%{_lib}

%if "%{_lib}" == "lib64"
ln -s ld64-uClibc.so.%{majorish} %{buildroot}%{uclibc_root}/%{_lib}/ld64-uClibc.so.0
install -d %{buildroot}%{uclibc_root}{/lib,%{_prefix}/lib}
%else
ln -s ld-uClibc.so.%{majorish} %{buildroot}%{uclibc_root}/lib/ld-uClibc.so.0
%endif

for dir in /bin /sbin %{_prefix} %{_bindir} %{_sbindir}; do
	mkdir -p %{buildroot}%{uclibc_root}$dir
done

mkdir -p %{buildroot}%{uclibc_root}%{_sysconfdir}
touch %{buildroot}%{uclibc_root}%{_sysconfdir}/ld.so.{conf,cache}

%if !%{with bootstrap}
echo 'GROUP ( AS_NEEDED ( %{uclibc_root}/%{_lib}/%{libintl} ) )' >> %{buildroot}%{uclibc_root}%{_libdir}/libc.so
%endif

%ifarch %arm
for header in bits/atomic.h bits/byteswap.h bits/endian.h bits/environments.h bits/epoll.h bits/fcntl.h bits/mathdef.h bits/mathinline.h bits/mman.h bits/msq.h bits/pthreadtypes.h bits/select.h bits/sem.h bits/semaphore.h bits/setjmp.h bits/shm.h bits/sigcontext.h bits/stat.h bits/sysnum.h bits/uClibc_config.h bits/uClibc_locale_data.h bits/wchar.h bits/wordsize.h fpu_control.h sys/io.h sys/procfs.h sys/ucontext.h sys/user.h; do
        %{multiarch_includes %{buildroot}%{uclibc_root}%{_includedir}/$header}
done
%else
for header in bits/atomic.h bits/byteswap.h bits/endian.h bits/environments.h bits/epoll.h bits/fcntl.h bits/mathdef.h bits/mathinline.h bits/mman.h bits/msq.h bits/pthreadtypes.h bits/select.h bits/sem.h bits/semaphore.h bits/setjmp.h bits/shm.h bits/sigcontext.h bits/stat.h bits/sysnum.h bits/uClibc_config.h bits/wchar.h bits/wordsize.h fpu_control.h sys/debugreg.h sys/io.h sys/perm.h sys/procfs.h sys/reg.h sys/ucontext.h sys/user.h; do
        %{multiarch_includes %{buildroot}%{uclibc_root}%{_includedir}/$header}
done
%endif

%triggerposttransin -- %{uclibc_root}/lib/*.so.*, %{uclibc_root}/lib64/*.so.*, %{uclibc_root}%{_prefix}/lib/*.so.*, %{uclibc_root}%{_prefix}/lib64/*.so.*
%{uclibc_root}/sbin/ldconfig -X

%files
%doc README
%dir %{uclibc_root}/bin
%dir %{uclibc_root}/sbin
%dir %{uclibc_root}%{_bindir}
%{uclibc_root}%{_bindir}/iconv
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
%{uclibc_root}/%{_lib}/*.so.%{majorish}
%endif

%files -n %{devname}
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
%{uclibc_root}%{_libdir}/libuargp.so
%{uclibc_root}%{_libdir}/libubacktrace.so
%{uclibc_root}%{_libdir}/libutil.so
%endif
%{uclibc_root}%{_libdir}/lib*.a
%{uclibc_root}%{_libdir}/uclibc_nonshared.a

