## Process this file with automake to produce Makefile.in
## Created by Anjuta

SUBDIRS = src 

azucardocdir = ${prefix}/doc/azucar
azucardoc_DATA = \
	README\
	COPYING\
	AUTHORS\
	ChangeLog\
	INSTALL\
	NEWS


EXTRA_DIST = $(azucardoc_DATA)


# Remove doc directory on uninstall
uninstall-local:
	-rm -r $(azucardocdir)
