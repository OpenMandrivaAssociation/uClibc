# disable stack protector, build doesn't work with it
%define _ssp_cflags %{nil}

%define uclibc_root %{_prefix}/uclibc
%define uclibc_cc uclibc-gcc

%define majorish 0.9.33
%define libname %mklibname %{name} %{majorish}
%define devname %mklibname %{name} -d

%bcond_with	bootstrap

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	%{majorish}.3
%define	gitdate	20150520
Release:	0.%{gitdate}.5
License:	LGPLv2.1
Group:		System/Libraries
Url:		http://uclibc.org/
Source0:	http://uclibc.org/downloads/%{name}-%{version}%{?gitdate:-%{gitdate}}.tar.xz
Source1:	uclibc.macros
Source2:	uClibc-0.9.33.3-config
Source3:	uclibc-gcc.specs
Patch1:		uClibc-0.9.33.2-lib64.patch
# (proyvind): the ABI isn't stable, so set it to current version
Patch4:		uClibc-0.9.33.3-git-unstable-abi.patch
# (bero): Don't mix asm instructions into C code... Put them where they belong
Patch5:		uClibc-0.9.33.2-arm-compile.patch
# from mga (rtp) add hacks for unwind symbol on arm (was picking glibc symbols
# so was trying to link together glibc&uClibc...)
Patch7:		uClibc-arm_hack_unwind.patch
Patch8:		uClibc-0.9.32-no-gstabs.patch
# http://lists.busybox.net/pipermail/uclibc/2011-March/045003.html
Patch9:		uClibc-0.9.33.2-origin.patch
Patch12:	uClibc-0.9.33.2-add-missing-make-rule-on-locale-header.patch
Patch16:	uClibc-0.9.33-argp-support.patch
Patch17:	uClibc-0.9.33-argp-headers.patch
Patch18:	uClibc-0.9.33.2-trim-slashes-for-libubacktrace-path-in-linker-script.patch
Patch19:	uClibc-0.9.33.3-sync-timex.h-with-glibc-2.19.patch
Patch20:	uClibc-0.9.33.3-sync-netinet-ip.h-with-glibc-2.19.patch
Patch21:	uClibc-0.9.33.3-add-clock_adjtime-syscall.patch
Patch22:	0001-librt-Use-nodefaultlibs-instead-of-nostdlib.patch
Patch23:	0003-fcntl.h-Define-F_SETPIPE_SZ-and-F_GETPIPE_SZ.patch
Patch24:	0001-nptl-atfork-Hide-pthread_atfork-in-shared-versions.patch
Patch25:	0002-wire-setns-syscall.patch
Patch26:	0001-atexit_old-Do-not-add-it-to-shared-libc.patch
Patch27:	uClibc-0.9.33.3nptl-arm-Move-aeabi_read_tp-to-uclibc_nonshared.a.patch
Patch28:	uClibc-0.9.33.3-Add-eventfd_read-and-eventfd_write.patch
Patch29:	uClibc-0.9.33.3-add-AT_NO_AUTOMOUNT-AT_EMPTY_PATH-to-fcntl.patch
Patch30:	uClibc-0.9.33.3-static_assert.patch
Patch31:	uClibc-0.9.33.3-sync-sys-xattr-with-latest-glibc.patch
Patch32:	0001-add-O_PATH-O_TMPFILE.patch
Patch33:	uClibc-0.9.33.3-add-SCHED_IDLE-and-SCHED_RESET_ON_FORK.patch
Patch34:	uClibc-0.9.33.3-socket_h-add-AF_VSOCK.patch
Patch35:	uClibc-0.9.33.3-sync-brk-system-call-with-glibc.patch
Patch36:	uClibc-0.9.33.3-add-syncfs-function-for-new-syncfs-syscall.patch
Patch37:	uClibc-0.9.33.3-use-inline-syscall-getdents-from-glibc.patch

# from origin/HEAD branch
Patch202:	uClibc-0.9.33-buildsys-pass-correct-linker-to-compiler-driver.patch
Patch203:	uClibc-0.9.33.3-Fix-threaded-use-of-res_-functions.patch
Patch204:	0002-Make-res_init-thread-safe.patch
Patch205:	0001-fix-pthread_cancel-lead-to-segmentation-fault-for-x8.patch
Patch213:	0055-siginfo_h-add-a-missing-function-member.patch
Patch214:	0056-MIPS-set-_NSIG-to-128-not-129.-This-matches-glibc.patch
Patch215:	0056-siginfo_h-__SIGEV_PAD_SIZE-takes-__WORDSIZE-into-account.patch
Patch216:	0057-bits-waitstatus.h-correctly-interpret-status-0x007f-.patch
Patch217:	0058-test-tls-fix-build-with-newer-binutils.patch
Patch218:	0059-test-cater-for-config.patch
Patch219:	0060-test-Fix-math-c-dependency.patch
Patch220:	0062-ldso-libdl-Also-include-dl-tls.h-for-for-SHARED.patch
Patch221:	0062-nptl-remove-duplicate-vfork-in-libpthread.patch
Patch222:	0065-Do-not-include-__iconv_codesets-into-iconv-utility.patch
Patch223:	0001-stdlib-avoid-relocation.patch
Patch224:	0001-libc-Avoid-redundant-setting-of-ENOMEM.patch
Patch225:	0001-malloc-checked_request2size-failure-deadlocks.patch
Patch226:	0001-malloc-standard-Add-locking-to-malloc_trim.patch

#from origin/ldso-future branch
Patch300:	uClibc-0.9.33.3-fix-accessing-global-offset-table-on-x86.patch

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
# add this here as dependency on it has been removed from libz-devel package
# in order to not pull in uClibc stuff just for getting a toolchain to build
# kernel & kernel modules with
Requires:	uclibc-%{mklibname z 1}
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
%setup -q
%apply_patches

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
yes "" | %make oldconfig VERBOSE=2

%make VERBOSE=2 CPU_CFLAGS="" all utils || %make VERBOSE=2 CPU_CFLAGS="" all utils || make VERBOSE=2 CPU_CFLAGS="" all utils


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

for header in bits/atomic.h bits/byteswap.h bits/endian.h bits/environments.h bits/epoll.h bits/fcntl.h bits/mathdef.h bits/mathinline.h bits/mman.h bits/msq.h bits/pthreadtypes.h bits/select.h bits/sem.h bits/semaphore.h bits/setjmp.h bits/shm.h bits/sigcontext.h bits/stat.h bits/sysnum.h bits/uClibc_config.h bits/uClibc_locale_data.h bits/wchar.h bits/wordsize.h fpu_control.h \
%ifnarch %{arm}
sys/debugreg.h sys/perm.h sys/reg.h \
%endif
sys/io.h sys/procfs.h sys/ucontext.h sys/user.h; do
	%{multiarch_includes %{buildroot}%{uclibc_root}%{_includedir}/$header}
done

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
%dir %{uclibc_root}%{_datadir}
%{uclibc_root}%{_datadir}/gcc-spec-uclibc

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

