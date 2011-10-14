## Process this file with automake to produce Makefile.in
## Created by Anjuta

uidir = $(datadir)/azucar/ui
ui_DATA = ../data/azucar.ui

## The main script
bin_SCRIPTS = azucar.py

## Directory where .class files will be installed
azucardir = $(pythondir)/azucar

EXTRA_DIST = $(ui_DATA)

azucar_PYTHON = \
	azucar.py

# Remove ui directory on uninstall
uninstall-local:
	-rm -r $(uidir)
	-rm -r $(datadir)/azucar
