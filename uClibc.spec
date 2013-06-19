# disable stack protector, build doesn't work with it
%define	_ssp_cflags	%{nil}

%define	uclibc_root	%{_prefix}/uclibc
%define	uclibc_cc	uclibc-gcc

%define	majorish	0.9.33
%define	libname	%mklibname %{name} %{majorish}
%define	libdev	%mklibname %{name} -d

%bcond_with	bootstrap

Summary:	A C library optimized for size useful for embedded applications
Name:		uClibc
Version:	%{majorish}.2
Release:	26
License:	LGPLv2.1
Group:		System/Libraries
URL:		http://uclibc.org/
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
Patch202:	0001-Remove-pragma-weak-for-undeclared-symbol.patch
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

%package -n	%{libname}
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

%package -n	%{libdev}
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

%description -n	%{libdev}
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

%define arch %(echo %{_arch} | sed -e 's/ppc/powerpc/' -e 's!mips*!mips!')

%ifarch %{arm}
%define arch_cflags -marm -Wa,-mimplicit-it=thumb -D__thumb2__
%endif
%global	cflags	%{optflags} -Os -std=gnu99 %{ldflags} -muclibc -Wl,-rpath=%{uclibc_root}/%{_lib} -Wl,-rpath=%{uclibc_root}%{_libdir} -fuse-ld=bfd %{?arch_cflags}

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
make CC="gcc -fuse-ld=bfd" VERBOSE=2 PREFIX=%{buildroot} install
make CC="gcc -fuse-ld=bfd" -C utils VERBOSE=2 PREFIX=%{buildroot} utils_install

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

for header in bits/atomic.h bits/byteswap.h bits/endian.h bits/environments.h bits/epoll.h bits/fcntl.h bits/mathdef.h bits/mathinline.h bits/mman.h bits/msq.h bits/pthreadtypes.h bits/select.h bits/sem.h bits/semaphore.h bits/setjmp.h bits/shm.h bits/sigcontext.h bits/stat.h bits/sysnum.h bits/uClibc_config.h bits/wchar.h bits/wordsize.h fpu_control.h sys/debugreg.h sys/io.h sys/perm.h sys/procfs.h sys/reg.h sys/ucontext.h sys/user.h; do
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
%{uclibc_root}%{_libdir}/libuargp.so
%{uclibc_root}%{_libdir}/libubacktrace.so
%{uclibc_root}%{_libdir}/libutil.so
%endif
%{uclibc_root}%{_libdir}/lib*.a
%{uclibc_root}%{_libdir}/uclibc_nonshared.a

%changelog
* Sat Jan 12 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-24
- convert %%triggerin to %%triggerposttransin
- inline %%{arch_cflags} conditional

* Mon Jan  7 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-21
- fix multilib patch so that interpreter & utils searches MULTILIB_DIR

* Wed Dec 26 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-20
- disable arm patch on non-arm as it breaks build on at least x86_64..
- non-bootstrap rebuild

* Mon Dec 17 2012 Bernhard Rosenkraenzer <bero@bero.eu> 0.9.33.2-19
- Fix crash on startup on ARM
- Fix bogus arm_asm.h header and other compile issues on ARM

* Tue Dec 11 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-18
- bootstrap rebuild on ABF

* Sun Oct 28 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-17
+ Revision: 820214
- previous release got lost on i586..

* Sun Oct 28 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-16
+ Revision: 820139
- add back libintl to libc.so linker script

* Sun Oct 28 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-15
+ Revision: 820071
- disable libintl hack for bootstrapping as uclibc build of gettext isn't repos
  yet
- fix libintl linker script hack

* Tue Oct 23 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-14
+ Revision: 819613
- %%uclibc_configure should be fixed now..
- don't generate uclibc.macros during build, keep it as a separate file to
  install in stead
- pass --disable-silent-rules together with some various other configure options
  for setting paths to %%uclibc_configure

* Mon Oct 22 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-13
+ Revision: 819199
- create a %%uclibc_configure macro to make life a bit simpler
- Remove pragma weak for undeclared symbol (P202, backported from upstream)
- renumber patches from upstream git
- nptl: sh: fix race condition in lll_wait_tid (P22, from upstream)
- librt: re-add SIGCANCEL to the list of blocked signal in helper thread (P21,
  backported from upstream)
- sync bits/time.h with glibc 2.16, introducing CLOCK_MONOTONIC_RAW,
  CLOCK_REALTIME_COARSE & CLOCK_MONOTONIC_COARSE (P20 bakported from upstream)
- allow immediate values as 6th syscall arg (P19, backported from upstream)
- fix libuargp.so not getting added to libc.so linker script
- add libintl to libc.so linker script so that we'll automatically link it in
  when needed for stuff building with gettext, as most apps expect these
  functions to be available from the libc and we that way won't have to screw
  around with each and every package using gettext building against uclibc
- trim away double slashes to libubacktrace path in libc.so linker script (P18)

* Wed Oct 03 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-12
+ Revision: 818344
- fix filename & symlinks for libuargp

* Wed Oct 03 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-11
+ Revision: 818307
- pass -nostdlib to linker to prevent standard libraries getting linked

* Fri Sep 28 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-10
+ Revision: 817853
- add buildrequires on locale, otherwise build will break with locale enabled
- add argp interface (P16 & P17, from OE)
- add definition of MSG_WAITFORONE and MSG_CMSG_CLOEXEC (P15)
- add execvpe() (P14, from OE)
- sync mount.h with glibc (P13)
- enable nftw()
- fix multilib dir for libubacktrace.so (P13)
- add missing make rule on missing uClibc_locale_data.h header (P12)
- enable:
	FORCE_SHAREABLE_TEXT_SEGMENTS
	UCLIBC_HAS_LOCALE
	UCLIBC_BUILD_ALL_LOCALE
	UCLIBC_HAS_XLOCALE
	UCLIBC_HAS_GLIBC_DIGIT_GROUPING
	UCLIBC_HAS_SCANF_LENIENT_DIGIT_GROUPING
	DOASSERTS
	UCLIBC_HAS_BACKTRACE
- disable:
	UCLIBC_HAS_SSP
- automatically update .config from an existing one, changing any set/unset
  variables to the desired ones

* Wed Sep 05 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-7
+ Revision: 816384
- enable:
  UCLIBC_BUILD_NOW
  UCLIBC_HAS_ARC4RANDOM
  UCLIBC_HAS_FULL_RPC
- use bfd linker for now as gold has issues compiling uClibc if prelink support
  support is enabled
- add support for dup3() (P11)
- add support for posix_fallocate() (P10)
- add support for $ORIGIN (P9)
- increase verbosiveness
- enable UCLIBC_HAS_FOPEN_CLOSEEXEC_MODE
- parallel builds seems to be working just fine again :)
- enable sha256 & sha512 support

* Sat Jun 16 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-6
+ Revision: 805946
- for some reason rpath no longer gets added even if LD_RUN_PATH is set, so let's
  pass -rpath to the linker as well to ensure that it actually gets set

* Tue Jun 05 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-5
+ Revision: 802795
- add back '-Os' to %%{uclibc_cflags}

* Tue May 22 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-4
+ Revision: 800144
- make dependency on uClibc for devel package versioned

* Tue May 22 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-3
+ Revision: 800069
- enable prelink support (LDSO_PRELINK_SUPPORT)
- drop support for linux 2.4 modules
- enable dns resolver functions (UCLIBC_HAS_RESOLVER_SUPPORT)
- update config

* Tue May 22 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.33.2-2
+ Revision: 800040
- fix broken symlink to elf interpreter
- new version

* Fri Mar 09 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.32-5
+ Revision: 783468
- rebuild for fixed uClibc() deps

* Wed Mar 07 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.32-4
+ Revision: 782574
- get rid of gstabs symbols on ix86 (P8)
- fix bug in uclibc-gcc wrapper that gave problems with escaping

* Tue Jul 12 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.32-2
+ Revision: 689715
- provide a proper fix from upstream for the epoll/nptl build issue on x86 (P5)
- create 32 bit lib dirs on lib64 to prevent ldconfig errors when missing
- update config file:
	o enable rpmatch()
	o enable checking of ctype argument
- update to 0.9.32 final (where NPTL should be fully working on all archs)

  + Matthew Dawkins <mattydaw@mandriva.org>
    - p6 upstreamed
      rediffed p7
    - added arm support
    -p6 to fix build error with gcc 4.6.x
    -p7 taken from (rtp) mga and adapted spec changes

* Wed May 25 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.32-1.rc3.git.2
+ Revision: 679031
- add dependency on uClibc for library package to ensure interpreter symlink
  being present

* Thu May 19 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.32-1.rc3.git.1
+ Revision: 676135
- ditch symlink uclibc root hack

* Mon May 16 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.32-1.rc3.git.0
+ Revision: 675063
- revert epoll.c commits breaking build on %%{ix86}
- update to latest code from git to get it working with current binutils
- add some hackiness to get uClibc stuff working within chroot'ed uclibc root

* Fri Apr 29 2011 Funda Wang <fwang@mandriva.org> 0.9.32-0.rc3.2
+ Revision: 660668
- rebuild

* Thu Apr 21 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.32-0.rc3.1
+ Revision: 656531
- clean out old junk
- inherit %%description & %%summary from main package
- use %%rename macro
- fix dependency loop
- don't pass '-Wl,--dynamic-linker' to gcc in uclibc-gcc anymore, gcc sets it now
- link with %%{ldflags}
- update config
- use rpath
- add back ld*-uClibc.so.0 symlink
- don't do parallel build in %%install either..
- update to 0.9.32-rc3

* Sun Feb 13 2011 Funda Wang <fwang@mandriva.org> 0.9.30.3-3
+ Revision: 637548
- convert to rpm5 standard trigger

* Mon Nov 29 2010 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.3-2mdv2011.0
+ Revision: 603066
- be sure to own orphan /usr/uclibc/etc directory
- fix uclibc-gcc wrapper script exec prefix

* Mon Nov 29 2010 Oden Eriksson <oeriksson@mandriva.com> 0.9.30.3-1mdv2011.0
+ Revision: 603019
- 0.9.30.3
- dropped upstream added patches
- rediffed the lib64 patch

* Tue Aug 31 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 0.9.30.1-13mdv2011.0
+ Revision: 574955
- rebuild against gcc 4.5.1

* Tue Mar 23 2010 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-12mdv2010.1
+ Revision: 526921
- fix %%files list
- ditch feeble multilib hack...
- fix license
- fix double '/' in include path for uclibc-gcc wrapper, resulting in debugedit
  erroring out with "canonicalization unexpectedly shrank by one character"

* Sat Jan 30 2010 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-11mdv2010.1
+ Revision: 498464
- call correct ldconfig (#56934)

* Fri Jan 29 2010 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-10mdv2010.1
+ Revision: 498316
- fix ldconfig filetrigger filter match (#56934)

* Fri Dec 11 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-9mdv2010.1
+ Revision: 476575
- add /etc/ld.so.{cache,conf} & corresponding filetrigger script/filter
- add back -W,--dynamic-linker to wrapper for now
- move around symlinks created and fix ownership of directories
- ditch -Os from %%{uclibc_cflags} as __OPTIMIZE_SIZE__ which implies the same is
  already defined in %%{uclibc_root}%%{_includedir}/features.h
- don't disable debugging symbols in uclibc-gcc wrapper
- create a uClibc package required by library which contains ldconfig, ldd &
  symlink to elf interpreter at the location gcc has hardcoded with -muclibc
- git snapshot gave too many new issues to deal with.. cowardly revert.. :/
- don't pass -Wl,--dynamic-linker to gcc in the wrapper anymore
- drop o0ld patches
- ABI isn't stable, so change ABI major to version (P4)
- don't build with -fstack-protector, seems to break even though it shouldn't..:/
- trim double slashes
- enable debug packages
- enable ssp
  update to git snapshot to save a lot of trouble with wrappers etc..
- revert LDSO_BASE_FILENAME back to 'ld.so', as we're installing uclibc to a
  different chroot anyways...
- fix another typo in lib64 patch
- fix typo

* Mon Dec 07 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-8mdv2010.1
+ Revision: 474298
- add version to package name as cases where dynamic linking is preferred seems
  to exist :)
- fix build of memcmp-stat stet (P109, from git)
- add scalbf(), gammaf(), significandf() wrappers (P108, from git)
- add support for scanf %%a modifier (P3)
- enable some more glibc stdio compatibility
- fetch .config in %%prep rather than %%build
- enable LDSO_PRELOAD_FILE_SUPPORT
- set LDSO_BASE_FILENAME to "ld-uClibc.so"
- add -muclibc flag to uclic-gcc wrapper

* Sat Dec 05 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-7mdv2010.1
+ Revision: 473694
- add -g0 to %%{uclibc_cflags}
- enable wide character support
- add strverscmp() and versionsort[64]() (P107, backport from git)

* Thu Dec 03 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-6mdv2010.1
+ Revision: 472779
- merge static-devel & devel package

* Thu Dec 03 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-5mdv2010.1
+ Revision: 472773
- enable MALLOC_GLIBC_COMPAT
- make %%{uclibc_cflags} into a macro to be passed rather than part of wrapper
- set gcc options through environment variables where possible for wrapper script
- fix dynamic linking in wrapper script

* Tue Dec 01 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-4mdv2010.1
+ Revision: 472156
- add %%{uclibc_cc} & %%{uclibc_cflags} macros
- create a uclibc.macros
- backport nanosecond stat support from git
- force disabling of stack protector in uclibc-gcc wrapper
- add rpmatch() (P2, needed to build plymouth against uclibc)

* Mon Nov 30 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-3mdv2010.1
+ Revision: 471728
- be sure to own %%{uclibc_root}%%{_prefix}
- ditch COPYING.LIB, it (LGPL) comes with common-licenses already
- libify package (P1)
- remove _requires_exception, it's fixed in /usr/lib/rpm/find-requires now

* Mon Nov 30 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-2mdv2010.1
+ Revision: 471625
- don't hardcode 'x86_64' in wrapper
- be sure that we don't include any backup files
- set CPU_CFLAGS to "" so that it won't override -march=cpu from our %%optflags

* Sun Nov 29 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.30.1-1mdv2010.1
+ Revision: 471031
- pick up patches from buildroot project to solve various issues..
- fix architecture prefix for paths
- fix confic
  file SPECS/uClibc.spec modified
  file SOURCES/uClibc-0.9.30.1-arm-fix-linuxthreads-sysdep.patch added
  file SOURCES/uClibc-0.9.30.1-dl-sysdep-inline.patch added
  file SOURCES/uClibc-0.9.30.1-c99-ldbl-math.patch added
  file SOURCES/uClibc-0.9.30.1-config removed
  file SOURCES/uClibc-0.9.30.1-64bit-strtouq.patch added
  file SOURCES/uClibc-0.9.30.2-config added
  file SOURCES/uClibc-0.9.30.1-fix-getaddrinfo.patch added
- new release: 0.9.31
- replace the old & deprecated gcc wrapper with a simpler shell script
- run test suite
- clean up quite a bit

  + Funda Wang <fwang@mandriva.org>
    - rediff toolchain wrapper patch
    - rediff mdkconf patch

  + Antoine Ginies <aginies@mandriva.com>
    - rebuild

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 0.9.28.1-5mdv2009.0
+ Revision: 225895
- rebuild

* Mon Mar 24 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.9.28.1-4mdv2008.1
+ Revision: 189752
- rebuild against gcc 4.2.3
- s/-mtune=pentiumpro/-mtune=generic/

* Tue Mar 04 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.28.1-3mdv2008.1
+ Revision: 178883
- rebuild

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Aug 22 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 0.9.28.1-2mdv2008.0
+ Revision: 68745
- Rebuild, and disable _ssp_cflags as build doesn't work with it.

