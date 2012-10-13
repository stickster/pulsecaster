ifndef LANGUAGES
LANGUAGES := $(shell ls po/*.po | sed 's/po\/\(.*\).po/\1/')
endif

DOMAIN = pulsecaster

PO_FILES = $(wildcard po/*.po)
MO_FILES = $(PO_FILES:.po=.mo)

PYTHON = $(shell which python)
TX = $(shell which tx)
PWD = $(shell pwd)

.PHONY: all mo po clean

all: mo
	@echo -n

mo: $(foreach L,$(LANGUAGES),po/$(L).mo)

define MO_template =
po/$(1).mo: po/$(1).po
	mkdir -p locale/$(1)/LC_MESSAGES && $(PYTHON) setup.py compile_catalog -l $(1) -i po/$(1).po -o po/$(1).mo -D $(DOMAIN) >/dev/null
endef
$(foreach L,$(LANGUAGES),$(eval $(call MO_template,$(L))))

po: $(foreach L,$(LANGUAGES),po/$(L).po)

define PO_template =
po/$(1).po: po/$(DOMAIN).pot
	$(PYTHON) setup.py update_catalog -l $(1) -i po/$(DOMAIN).pot -o po/$(1).po -D $(DOMAIN) >/dev/null
endef
$(foreach L,$(LANGUAGES),$(eval $(call PO_template,$(L))))


clean:
	rm -rf po/*.mo
