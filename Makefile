#####################
# Makefile support
# (C) 2012 Paul W. Frields <stickster@gmail.com>
# Licensed uner the GNU General Public License, v2 or later.
#

ifndef LANGUAGES
LANGUAGES:=$(shell ls po/*.po | sed 's/po\/\(.*\).po/\1/')
endif

DOMAIN=pulsecaster
PYTHON=$(shell which python)
TX=$(shell which tx)
PWD=$(shell pwd)
GIT=$(shell which git)

LATEST_TAG=$(shell git describe --tags --abbrev=0)
LATEST_VERSION=$(shell $(PYTHON) -c 'from pulsecaster.config import VERSION; print "%s" % (VERSION)')

all::
.PHONY:: vars
vars::
	@echo LATEST_TAG = $(LATEST_TAG)
	@echo LATEST_VERSION = $(LATEST_VERSION)


#####################

.PHONY:: all clean

#####################
# L10n support
.PHONY:: po
all:: po
po: $(foreach L,$(LANGUAGES),po/$(L).po)

define PO_template =
PO_FILES+= po/$(1).po
po/$(1).po: po/$(DOMAIN).pot
	$(PYTHON) setup.py update_catalog -l $(1) -i po/$(DOMAIN).pot -o po/$(1).po -D $(DOMAIN) >/dev/null
endef
$(foreach L,$(LANGUAGES),$(eval $(call PO_template,$(L))))
vars::
	@echo PO_FILES = $(PO_FILES)

.PHONY:: mo
all:: mo
mo: $(foreach L,$(LANGUAGES),po/$(L).mo)

define MO_template =
MO_FILES+= po/$(1).mo
po/$(1).mo: po/$(1).po
	mkdir -p locale/$(1)/LC_MESSAGES && $(PYTHON) setup.py compile_catalog -l $(1) -i po/$(1).po -o po/$(1).mo -D $(DOMAIN) >/dev/null
clean::
	rm -f po/$(1).mo
endef
$(foreach L,$(LANGUAGES),$(eval $(call MO_template,$(L))))
vars::
	@echo MO_FILES = $(MO_FILES)
#####################

#####################
# Release stuff
release:: $(DOMAIN)-$(LATEST_VERSION).tar.gz
$(DOMAIN)-$(LATEST_VERSION).tar.gz::
ifneq ($(LATEST_TAG),$(LATEST_VERSION))
	@echo Version=$(LATEST_VERSION), latest git tag=$(LATEST_TAG), either fix config.py or tag repo
else
	$(PYTHON) setup.py sdist
	@echo Tarball is in dist/$@
endif
