%define apidocs 1
%define akonadi_subpkg 1
%define akonadi_version_min 1.9.0

%global akonadi_version %(pkg-config --modversion akonadi 2>/dev/null || echo %{akonadi_version_min})

Name: kdepimlibs
Summary: KDE PIM Libraries
Version: 4.10.5
Release: 3%{?dist}

# http://techbase.kde.org/Policies/Licensing_Policy
License: LGPLv2+
URL: http://www.kde.org/
%global revision %(echo %{version} | cut -d. -f3)
%if %{revision} >= 50
%global stable unstable
%else
%global stable stable
%endif
Source0: http://download.kde.org/%{stable}/%{version}/src/kdepimlibs-%{version}.tar.xz

Patch0: kdepimlibs-4.10.4-kimap_recursion.patch

## upstream patches

Requires: %{name}-kxmlrpcclient%{?_isa} = %{version}-%{release}
%if ! 0%{?akonadi_subpkg}
Obsoletes: %{name}-akonadi < %{version}-%{release}
Provides:  %{name}-akonadi = %{version}-%{release}
%{?_isa:Provides:  %{name}-akonadi%{_isa} = %{version}-%{release}}
Requires: akonadi%{?_isa} >= %{akonadi_version}
%endif
Requires: kdelibs4%{?_isa} >= %{version}
# for kio_smtp plain/login sasl plugins
Requires: cyrus-sasl-plain

BuildRequires: boost-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: gpgme-devel
BuildRequires: kdelibs4-devel >= %{version}
BuildRequires: openldap-devel
BuildRequires: libical-devel >= 0.33
BuildRequires: nepomuk-core-devel >= %{version}
BuildRequires: pkgconfig(akonadi) >= %{akonadi_version_min}
BuildRequires: pkgconfig(libxslt)
BuildRequires: pkgconfig(QJson)
BuildRequires: pkgconfig(uuid)
BuildRequires: pkgconfig(xpm) pkgconfig(xtst)
%if 0%{?fedora}
BuildRequires: prison-devel
%endif

%if 0%{?apidocs}
BuildRequires: doxygen
BuildRequires: graphviz
BuildRequires: qt4-doc
%endif

%description
Personal Information Management (PIM) libraries for KDE 4.

%package devel
Summary:  Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
%if 0%{?akonadi_subpkg}
Requires: %{name}-akonadi%{?_isa} = %{version}-%{release}
%endif
Obsoletes: kdepimlibs4-devel < %{version}-%{release}
Provides:  kdepimlibs4-devel = %{version}-%{release}
Requires: boost-devel
Requires: kdelibs4-devel
Requires: nepomuk-core-devel
%description devel
Header files for developing applications using %{name}.

%package akonadi
Summary: Akonadi runtime support for %{name}
# when pkg split occurrs, not sure if this is really needed, but... -- Rex
#Obsoletes: kdepimlibs < 4.2.0-3
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: akonadi%{?_isa} >= %{akonadi_version}
%description akonadi
%{summary}.

%package apidocs
Summary: kdepimlibs API documentation
Requires: kde-filesystem
BuildArch: noarch
%description apidocs
This package includes the kdepimlibs API documentation in HTML
format for easy browsing.

%package kxmlrpcclient
Summary: Simple XML-RPC Client support
# when spilt out
Conflicts: kdepimlibs < 4.9.2-5
License: BSD
%description kxmlrpcclient
This library contains simple XML-RPC Client support. It is used mainly
by the egroupware module of kdepim, but is a complete client and is
quite easy to use.


%prep
%setup -q

%patch0 -p1 -b .kimap_recursion

%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake_kde4} .. 
popd

make %{?_smp_mflags} -C %{_target_platform}

# build apidocs
%if 0%{?apidocs}
export QTDOCDIR=`pkg-config --variable=docdir Qt`
kde4-doxygen.sh --doxdatadir=%{_kde4_docdir}/HTML/en/common .
%endif


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

# hack around HTML doc multilib conflicts
for doxy_hack in kcontrol/kresources ; do
pushd %{buildroot}%{_kde4_docdir}/HTML/en/${doxy_hack}
bunzip2 index.cache.bz2
sed -i -e 's!<a name="id[a-z]*[0-9]*"></a>!!g' index.cache
bzip2 -9 index.cache
done
popd

# move devel symlinks
mkdir -p %{buildroot}%{_kde4_libdir}/kde4/devel
pushd %{buildroot}%{_kde4_libdir}
for i in lib*.so
do
  case "$i" in
# conflicts with kdelibs3
    libkabc.so | libkresources.so)
      linktarget=`readlink "$i"`
      rm -f "$i"
      ln -sf "../../$linktarget" "kde4/devel/$i"
      ;;
# conflicts with kdepim3 (compat)
    libkcal.so)
      linktarget=`readlink "$i"`
      rm -f "$i"
      ln -sf "../../$linktarget" "kde4/devel/$i"
      ;;
  esac
done
popd

# install apidocs
%if 0%{?apidocs}
mkdir -p %{buildroot}%{_kde4_docdir}/HTML/en
cp -prf kdepimlibs-%{version}%{?alphatag}-apidocs %{buildroot}%{_kde4_docdir}/HTML/en/kdepimlibs-apidocs
find %{buildroot}%{_kde4_docdir}/HTML/en/ -name 'installdox' -exec rm -fv {} ';'
%endif


%post -p /sbin/ldconfig

%postun
/sbin/ldconfig ||:
if [ $1 -eq 0 ] ; then
update-mime-database %{_kde4_datadir}/mime &> /dev/null
fi

%posttrans
update-mime-database %{_kde4_datadir}/mime >& /dev/null

%files
%{_kde4_appsdir}/kabc/
%{_kde4_datadir}/config.kcfg/recentcontactscollections.kcfg
%{_kde4_datadir}/config.kcfg/resourcebase.kcfg
%{_kde4_datadir}/config.kcfg/specialmailcollections.kcfg
%{_datadir}/dbus-1/interfaces/org.kde.KResourcesManager.xml
%{_datadir}/dbus-1/interfaces/org.kde.pim.IdentityManager.xml
%{_kde4_datadir}/kde4/services/*
%{_kde4_datadir}/kde4/servicetypes/*
%{_kde4_libdir}/libgpgme++-pth*.so.2*
%{_kde4_libdir}/libgpgme++.so.2*
%{_kde4_libdir}/libkabc.so.4*
%{_kde4_libdir}/libkabc_file_core.so.4*
%{_kde4_libdir}/libkblog.so.4*
%{_kde4_libdir}/libkcal.so.4*
%{_kde4_libdir}/libkcalcore.so.4*
%{_kde4_libdir}/libkcalutils.so.4*
%{_kde4_libdir}/libkholidays.so.4*
%{_kde4_libdir}/libkimap.so.4*
%{_kde4_libdir}/libkldap.so.4*
%{_kde4_libdir}/libkmbox.so.4*
%{_kde4_libdir}/libkmime.so.4*
%{_kde4_libdir}/libkontactinterface.so.4*
%{_kde4_libdir}/libkpimidentities.so.4*
%{_kde4_libdir}/libkpimtextedit.so.4*
%{_kde4_libdir}/libkpimutils.so.4*
%{_kde4_libdir}/libkresources.so.4*
%{_kde4_libdir}/libktnef.so.4*
%{_kde4_libdir}/libmicroblog.so.4*
%{_kde4_libdir}/libqgpgme.so.1*
%{_kde4_libdir}/libsyndication.so.4*
%{_kde4_libdir}/kde4/kabc_directory.so
%{_kde4_libdir}/kde4/kabc_file.so
%{_kde4_libdir}/kde4/kabc_ldapkio.so
%{_kde4_libdir}/kde4/kabc_net.so
%{_kde4_libdir}/kde4/kabcformat_binary.so
%{_kde4_libdir}/kde4/kcal_local.so
%{_kde4_libdir}/kde4/kcal_localdir.so
%{_kde4_libdir}/kde4/kcm_kresources.so
%{_kde4_libdir}/kde4/kio_imap4.so
%{_kde4_libdir}/kde4/kio_ldap.so
%{_kde4_libdir}/kde4/kio_mbox.so
%{_kde4_libdir}/kde4/kio_nntp.so
%{_kde4_libdir}/kde4/kio_pop3.so
%{_kde4_libdir}/kde4/kio_sieve.so
%{_kde4_libdir}/kde4/kio_smtp.so
%{_kde4_libdir}/kde4/plugins/designer/kholidayswidgets.so
%{_kde4_docdir}/HTML/en/kcontrol/
%{_kde4_docdir}/HTML/en/kioslave/
%{_kde4_appsdir}/libkholidays/
%{_kde4_datadir}/mime/packages/kdepimlibs-mime.xml

%if 0%{?akonadi_subpkg}
%exclude %{_kde4_datadir}/kde4/services/kcm_mailtransport.desktop
%exclude %{_kde4_datadir}/kde4/services/akonadicontact_actions.desktop

%post akonadi -p /sbin/ldconfig

%postun akonadi
/sbin/ldconfig ||:
if [ $1 -eq 0 ] ; then
update-mime-database %{_kde4_datadir}/mime &> /dev/null
fi

%posttrans akonadi
update-mime-database %{_kde4_datadir}/mime >& /dev/null

%files akonadi
%endif
%{_kde4_libdir}/libakonadi-calendar.so.4*
%{_kde4_libdir}/libakonadi-contact.so.4*
%{_kde4_libdir}/libakonadi-kabc.so.4*
%{_kde4_libdir}/libakonadi-kcal.so.4*
%{_kde4_libdir}/libakonadi-kde.so.4*
%{_kde4_libdir}/libakonadi-kmime.so.4*
%{_kde4_libdir}/libakonadi-notes.so.4*
%{_kde4_libdir}/libakonadi-socialutils.so.4*
%{_kde4_appsdir}/akonadi/
%{_kde4_appsdir}/akonadi-kde/
%{_kde4_libdir}/libkalarmcal.so.2*
%{_kde4_libdir}/libmailtransport.so.4*
%{_kde4_libdir}/kde4/akonadi_serializer_socialfeeditem.so
%{_kde4_libdir}/kde4/kcm_mailtransport.so
%{_kde4_libdir}/kde4/kcm_akonadicontact_actions.so
%{_kde4_datadir}/config.kcfg/mailtransport.kcfg
%{_kde4_appsdir}/kconf_update/mailtransports.upd
%{_kde4_appsdir}/kconf_update/migrate-transports.pl
%{_kde4_datadir}/kde4/services/kcm_mailtransport.desktop
%{_kde4_datadir}/kde4/services/akonadicontact_actions.desktop
%{_kde4_datadir}/mime/packages/x-vnd.akonadi.socialfeeditem.xml

%files devel
%{_kde4_appsdir}/cmake/modules/*
%{_kde4_includedir}/*
%{_kde4_libdir}/kde4/devel/lib*.so
%{_kde4_libdir}/lib*.so
%{_kde4_libdir}/cmake/KdepimLibs*
%{_kde4_libdir}/gpgmepp/

%if 0%{?apidocs}
%files apidocs
%{_kde4_docdir}/HTML/en/kdepimlibs-apidocs/
%endif

%post kxmlrpcclient -p /sbin/ldconfig
%postun kxmlrpcclient -p /sbin/ldconfig

%files kxmlrpcclient
%doc kxmlrpcclient/README 
%{_kde4_libdir}/libkxmlrpcclient.so.4*


%changelog
* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 4.10.5-3
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 4.10.5-2
- Mass rebuild 2013-12-27

* Sun Jun 30 2013 Than Ngo <than@redhat.com> - 4.10.5-1
- 4.10.5

* Mon Jun 24 2013 Daniel Vrátil <dvratil@redhat.com> - 4.10.4-3
- install akonadicontact_actions.desktop (#977025)

* Wed Jun 05 2013 Martin Briza <mbriza@redhat.com> - 4.10.4-2
- fixed infinite recursion on ssl handshake error in akonadi_imap_resource (#891620)

* Sat Jun 01 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.10.4-1
- 4.10.4

* Fri May 24 2013 Rex Dieter <rdieter@fedoraproject.org> 4.10.3-2
- rebuild (libical)

* Mon May 06 2013 Than Ngo <than@redhat.com> - 4.10.3-1
- 4.10.3

* Sun Mar 31 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.10.2-1
- 4.10.2

* Sat Mar 02 2013 Rex Dieter <rdieter@fedoraproject.org> 4.10.1-1
- 4.10.1

* Sun Feb 10 2013 Denis Arnaud <denis.arnaud_fedora@m4x.org> - 4.10.0-4
- Rebuild for Boost-1.53.0

* Sat Feb 09 2013 Denis Arnaud <denis.arnaud_fedora@m4x.org> - 4.10.0-3
- Rebuild for Boost-1.53.0

* Wed Feb 06 2013 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.10.0-2
- restore documentation multilib hack for now as per IRC discussion with tosky

* Thu Jan 31 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.10.0-1
- 4.10.0

* Tue Jan 22 2013 Rex Dieter <rdieter@fedoraproject.org> 4.9.98-2
- drop apidoc multilib hacks

* Sun Jan 20 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.9.98-1
- 4.9.98

* Fri Jan 04 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.9.97-1
- 4.9.97

* Sat Dec 22 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.95-3
- drop Find-NepomukCore-if-not-found-yet.patch, breaks kdepim-runtime.

* Fri Dec 21 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9.95-2
- nepomuk-core related upstream patches
- -devel: Requires: nepomuk-core-devel

* Wed Dec 19 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9.95-1
- 4.9.95
- BR: nepomuk-core
- fix/prune changelog

* Mon Dec 03 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.90-1
- 4.9.90 (4.10beta2)

* Mon Dec 03 2012 Than Ngo <than@redhat.com> - 4.9.4-1
- 4.9.4

* Mon Nov 26 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.3-2
- cherry-pick a few upstream patches (#815047)

* Fri Nov 02 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.3-1
- 4.9.3

* Thu Nov 1 2012 Lukáš Tinkl<ltinkl@redhat.com> 4.9.2-6
- build against prison only under Fedora

* Mon Oct 29 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.2-5
- -kxmlrpcclient subpkg (#855930)

* Mon Oct 29 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.2-4
- remove .spec cruft

* Fri Oct 26 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.2-3
- fix FTBFS against akonadi-1.8.1 

* Thu Oct 04 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.2-2
- fix/update HTML docbook multilib hack (#862388)

* Fri Sep 28 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9.2-1
- 4.9.2

* Wed Sep 26 2012 Tomas Mraz <tmraz@redhat.com> - 4.9.1-4
- drop libgpgme++-pth.so.2 as gpgme does not ship the pth-linked library
  anymore

* Mon Sep 17 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9.1-3
- Update holiday_sg_en-gb (#857877, kde#306924)
- Update Argentina holidays rule file (kde#306347)
- kmail cannot display html messages with images refered (kde#205791)
- transportlistview: resize to content 

* Sun Sep 16 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.1-2
- BR: libuuid-devel

* Mon Sep 03 2012 Than Ngo <than@redhat.com> - 4.9.1-1
- 4.9.1

* Mon Jul 30 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.0-2
- rebuild (boost)

* Thu Jul 26 2012 Lukas Tinkl <ltinkl@redhat.com> - 4.9.0-1
- 4.9.0

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.8.97-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 11 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.8.97-1
- 4.8.97

* Thu Jun 28 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8.95-2
- akonadi_version_min 1.7.90

* Wed Jun 27 2012 Radek Novacek <rnovacek@redhat.com> - 4.8.95-1
- 4.8.95

* Fri Jun 08 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.90-1
- 4.8.90

* Fri Jun 01 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.80-2
- respin

* Sat May 26 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.80-1
- 4.8.80

* Mon Apr 30 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.3-1
- 4.8.3

* Fri Mar 30 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.2-1
- 4.8.2

* Wed Mar 21 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8.1-3
- drop libkalarmcal.so.2 from base pkg (#804360)

* Sun Mar 18 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8.1-2
- kdepimlibs pulling in kdepimlibs-akonadi (#804360)
- add mime scriptlet

* Mon Mar 05 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.1-1
- 4.8.1
- remove dovecot patch, upstream

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.8.0-2
- Rebuilt for c++ ABI breakage

* Fri Jan 20 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.0-1
- 4.8.0

* Wed Jan 04 2012 Radek Novacek <rnovacek@redhat.com> - 4.7.97-1
- 4.7.97
- drop upstreamed patch for bug kde#289693

* Thu Dec 29 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.95-2
- Kmail crash on exit (kde#289693)

* Wed Dec 21 2011 Radek Novacek <rnovacek@redhat.com> - 4.7.95-1
- 4.7.95

* Fri Dec 16 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.90-2
- kio_imap APPEND omits message size without flags (kde#289084)

* Sat Dec 03 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.90-1
- 4.7.90

* Sat Nov 26 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.80-2
- kmail does not work with dovecot (#757295,kde#249992)

* Fri Nov 18 2011 Jaroslav Reznik <jreznik@redhat.com> 4.7.80-1
- 4.7.80 (beta 1)

* Sat Oct 29 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.3-1
- 4.7.3

* Thu Oct 27 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.2-2
- pkgconfig-style deps
- "Mimetype tree is not a DAG!" errors + crashes when using SMI 0.91 (#749618)

* Tue Oct 04 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.2-1
- 4.7.2

* Fri Sep 02 2011 Than Ngo <than@redhat.com> - 4.7.1-1
- 4.7.1

* Tue Jul 26 2011 Jaroslav Reznik <jreznik@redhat.com> 4.7.0-1
- 4.7.0

* Thu Jul 21 2011 Rex Dieter <rdieter@fedoraproject.org> 4.6.95-2
- rebuild (boost)

* Fri Jul 08 2011 Jaroslav Reznik <jreznik@redhat.com> - 4.6.95-1
- 4.6.95 (rc2)

* Tue Jun 28 2011 Than Ngo <than@redhat.com> - 4.6.90-1
- 4.6.90 (rc1)

* Mon Jun 27 2011 Rex Dieter <rdieter@fedoraproject.org> 4.6.80-2
- Requires: cyrus-sasl-plain

* Fri May 27 2011 Jaroslav Reznik <jreznik@redhat.com> 4.6.80-1
- 4.6.80 (beta1)
- add BR prison-devel

* Thu Apr 28 2011 Rex Dieter <rdieter@fedoraproject.org> 4.6.3-1
- 4.6.3

* Wed Apr 06 2011 Jaroslav Reznik <jreznik@redhat.com> 4.6.2-1
- 4.6.2

* Sat Feb 26 2011 Rex Dieter <rdieter@fedoraproject.org> 4.6.1-1
- 4.6.1

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.6.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan 21 2011 Jaroslav Reznik <jreznik@redhat.com> 4.6.0-1
- 4.6.0

* Thu Jan 20 2011 Rex Dieter <rdieter@fedoraproject.org> 4.5.95-2
- avoid overlapping memcpy in kio_imap

* Wed Jan 05 2011 Jaroslav Reznik <jreznik@redhat.com> 4.5.95-1
- 4.5.95 (4.6rc2)

* Wed Dec 22 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5.90-1
- 4.5.90 (4.6rc1)

* Wed Dec 08 2010 Thomas Janssen <thomasj@fedoraproject.org> 4.5.85-2
- respun upstream tarball

* Sat Dec 04 2010 Thomas Janssen <thomasj@fedoraproject.org> 4.5.85-1
- 4.5.85 (4.6beta2)

* Tue Nov 23 2010 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.5.80-2
- respun tarball

* Sat Nov 20 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.5.80-1
- 4.5.80 (4.6beta1)

* Fri Nov 12 2010 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.5.3-2
- fix Austrian cultural/regional/religious November holidays (kde#245123)

* Sun Oct 31 2010 Than Ngo <than@redhat.com> - 4.5.3-1
- 4.5.3

* Fri Oct 01 2010 Rex Dieter <rdieter@fedoraproject.org> -  4.5.2-1
- 4.5.2

* Fri Aug 27 2010 Jaroslav Reznik <jreznik@redhat.com> - 4.5.1-1
- 4.5.1

* Mon Aug 23 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.5.0-3
- apidocs: remove (executable) installdox

* Mon Aug 23 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.5.0-2
- akonadi_version_min 1.4.0

* Tue Aug 03 2010 Than Ngo <than@redhat.com> - 4.5.0-1
- 4.5.0

* Tue Jul 27 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.4.95-2
- rebuild (boost)

* Sun Jul 25 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.4.95-1
- 4.5 RC3 (4.4.95)

* Wed Jul 07 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.4.92-1
- 4.5 RC2 (4.4.92)

* Mon Jun 28 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.4.90-2
- kdepimlibs pulling in kdepimlibs-akonadi (#608863)

* Fri Jun 25 2010 Jaroslav Reznik <jreznik@redhat.com> - 4.4.90-1
- 4.5 RC1 (4.4.90)

* Mon Jun 07 2010 Jaroslav Reznik <jreznik@redhat.com> - 4.4.85-1
- 4.5 Beta 2 (4.4.85)

* Fri May 21 2010 Jaroslav Reznik <jreznik@redhat.com> - 4.4.80-1
- 4.5 Beta 1 (4.4.80)

* Fri Apr 30 2010 Jaroslav Reznik <jreznik@redhat.com> - 4.4.3-1
- 4.4.3

* Mon Mar 29 2010 Lukas Tinkl <ltinkl@redhat.com> - 4.4.2-1
- 4.4.2

* Tue Mar 02 2010 Lukas Tinkl <ltinkl@redhat.com> - 4.4.1-2
- tarball respin

* Sat Feb 27 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.4.1-1
- 4.4.1

* Tue Feb 09 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.4.0-2
- akonadi_version 1.3.1

* Fri Feb 05 2010 Than Ngo <than@redhat.com> - 4.4.0-1
- 4.4.0

* Sun Jan 31 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.3.98-1
- KDE 4.3.98 (4.4rc3)

* Wed Jan 20 2010 Lukas Tinkl <ltinkl@redhat.com> - 4.3.95-1
- KDE 4.3.95 (4.4rc2)

* Sat Jan 16 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.3.90-4 
- rebuild (boost)

* Wed Jan 06 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.3.90-3
- revive -akonadi

* Wed Jan 06 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.3.90-2
- akonadi_ver 1.2.90

* Wed Jan 06 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.3.90-1
- 4.3.90 (4.4 rc1)
- drop -akonadi subpkg

* Fri Dec 18 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.85-1
- 4.3.85 (4.4 beta2)
- tighten deps

* Wed Dec 16 2009 Jaroslav Reznik <jreznik@redhat.com> - 4.3.80-2
- Repositioning the KDE Brand (#547361)

* Tue Dec  1 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.3.80-1
- KDE 4.4 beta1 (4.3.80)

* Sat Nov 21 2009 Ben Boeckel <MathStuf@gmail.com> - 4.3.75-0.1.svn1048496
- Update to 4.3.75 snapshot

* Wed Nov 18 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-3
- rebuild (qt-4.6.0-rc1, fc13+)

* Fri Nov 13 2009 Than Ngo <than@redhat.com> - 4.3.3-2
- rhel cleanup, remove Fedora<=9 conditionals

* Sat Oct 31 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-1
- 4.3.3

* Mon Oct 05 2009 Than Ngo <than@redhat.com> - 4.3.2-1
- 4.3.2

* Fri Aug 28 2009 Than Ngo <than@redhat.com> - 4.3.1-1
- 4.3.1

* Tue Aug 04 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.0-2
- akonadi_version 1.2.0

* Thu Jul 30 2009 Than Ngo <than@redhat.com> - 4.3.0-1
- 4.3.0

* Wed Jul 29 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.98-3
- Conflicts: kdepim < 4.2.90

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.98-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Than Ngo <than@redhat.com> - 4.2.98-1
- 4.3rc3

* Thu Jul 16 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.96-2
- License: LGPLv2+

* Sat Jul 11 2009 Than Ngo <than@redhat.com> - 4.2.96-1
- 4.3rc2

* Thu Jul 02 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.95-3
- akonadi_version 1.1.95

* Mon Jun 29 2009 Than Ngo <than@redhat.com> - 4.2.95-2
- respin

* Thu Jun 25 2009 Than Ngo <than@redhat.com> - 4.2.95-1
- 4.3 RC1

* Wed Jun 03 2009 Rex Dieter <rdieter@fedoraproject.org> 4.2.90-1
- KDE-4.3 beta2 (4.2.90)

* Sun May 24 2009 Rex Dieter <rdieter@fedoraproject.org> 4.2.85-2
- (min) akonadi_version 1.1.85

* Mon May 11 2009 Than Ngo <than@redhat.com> 4.2.85-1
- 4.2.85

* Mon Apr 06 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.2.2-3
- fix libkcal devel symlink hack

* Thu Apr 02 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.2-2
- -apidocs noarch (f10+)
- package %%_kde4_appsdir/akonadi-kde only once

* Tue Mar 31 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.2-1
- KDE 4.2.2

* Mon Mar 09 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.2.1-4
- disable CMake debugging, #475876 should be fixed now

* Tue Mar 03 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.1-2
- avoid libkcal conflict with kdepim3

* Fri Feb 27 2009 Than Ngo <than@redhat.com> - 4.2.1-1
- 4.2.1

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 Than Ngo <than@redhat.com> - 4.2.0-4
- enable akonadi subpkg

* Mon Feb 16 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.0-3
- include toggle for -akonadi subpkg (not enabled)
- Provides: -akonadi

* Mon Feb 16 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.0-2
- multilib conflicts (#485659)
- kde4/devel symlinks: blacklist only known conflicts

* Thu Jan 22 2009 Than Ngo <than@redhat.com> - 4.2.0-1
- 4.2.0
- exclude kdepimlibs-apidocs from main pkg

* Thu Jan 08 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.96-2
- fix build on Fedora 10 (cmake < 2.6.3 seems to have a different
  behaviour here)

* Wed Jan 07 2009 Than Ngo <than@redhat.com> - 4.1.96-1
- 4.2rc1

* Wed Dec 17 2008 Rex Dieter <rdieter@fedoraproject.org> - 4.1.85-2
- versioned akonadi(-devel) deps

* Thu Dec 11 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.85-1
- KDE 4.2beta2

* Wed Dec 10 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.82-2
- add --debug-output to our cmake call, that should fix a reproducible
  bug with cmake and ppc builds (this work-around should be
  removed anyway)

* Tue Dec 09 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.82-1
- 4.1.82

* Tue Dec 02 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.80-3
- -devel: Requires: libical-devel

* Thu Nov 20 2008 Than Ngo <than@redhat.com> 4.1.80-2
- merged

* Thu Nov 20 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.80-1
- 4.1.80
- BR cmake 2.6
- make install/fast

* Wed Nov 12 2008 Than Ngo <than@redhat.com> 4.1.3-1
- 4.1.3

* Sat Nov 01 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.2-4
- turn off system libical for now, crashes KOrganizer (#469228)

* Tue Oct 28 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.2-3
- build against the system libical (F10+ only for now)

* Sun Sep 28 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-2
- make VERBOSE=1
- respin against new(er) kde-filesystem

* Fri Sep 26 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-1
- 4.1.2

* Fri Sep 05 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.1-2
- invitations crasher/regression (kde #170203, rh#462103)

* Thu Aug 28 2008 Than Ngo <than@redhat.com> 4.1.1-1
- 4.1.1

* Tue Aug 05 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.0-2
- -devel: Requires: boost-devel

* Wed Jul 23 2008 Than Ngo <than@redhat.com> 4.1.0-1
- 4.1.0

* Fri Jul 18 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.99-1
- 4.0.99

* Thu Jul 10 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.98-1
- 4.0.98

* Sun Jul 06 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.85-1
- 4.0.85

* Fri Jun 27 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.84-1
- 4.0.84

* Tue Jun 24 2008 Than Ngo <than@redhat.com> 4.0.83-2
- respun

* Thu Jun 19 2008 Than Ngo <than@redhat.com> 4.0.83-1
- 4.0.83 (beta2)

* Sat Jun 14 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.82-1
- 4.0.82

* Mon May 26 2008 Than Ngo <than@redhat.com> 4.0.80-1
- 4.1 beta1

* Mon May 05 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.0.72-2
- add BR akonadi-devel
- update file list

* Fri May 02 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.0.72-1
- update to 4.0.72 (4.1 alpha 1)

* Thu Apr 03 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-3
- rebuild (again) for the fixed %%{_kde4_buildtype}

* Mon Mar 31 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-2
- rebuild for NDEBUG and _kde4_libexecdir

* Fri Mar 28 2008 Than Ngo <than@redhat.com> 4.0.3-1
- 4.0.3
- -apidocs: Drop Requires: %%name
- include noarch build hooks (not enabled)

* Thu Mar 06 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.2-2
- build apidocs and put them into an -apidocs subpackage (can be turned off)
- BR doxygen, graphviz and qt4-doc when building apidocs

* Thu Feb 28 2008 Than Ngo <than@redhat.com> 4.0.2-1
- 4.0.2

* Wed Jan 30 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.1-2
- don't delete kconf_update script, it has been fixed to do the right thing

* Wed Jan 30 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.1-1
- 4.0.1

* Mon Jan 07 2008 Than Ngo <than@redhat.com> 4.0.0-1
- 4.0.0
