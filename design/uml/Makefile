.PHONY: all

define DEFAULTTARGET :=
	$(MAKE) -C .. $@ $(MAKECMDGOALS)
endef

all:
	${DEFAULTTARGET}

%:
	${DEFAULTTARGET}
