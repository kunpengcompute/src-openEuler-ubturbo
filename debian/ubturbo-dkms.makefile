# Top-level Makefile for ubturbo-dkms (built on target by DKMS).
# Builds the SMAP driver, tiering and ucache kernel modules in order,
# propagating drivers' Module.symvers to tiering.
KERNELDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

.PHONY: modules clean
modules:
	$(MAKE) -C $(KERNELDIR) M=$(PWD)/drivers KERNEL_VERSION=velinux modules
	install -d $(PWD)/tiering/depends
	cp $(PWD)/drivers/Module.symvers $(PWD)/tiering/depends/
	$(MAKE) -C $(KERNELDIR) M=$(PWD)/tiering KERNEL_VERSION=velinux modules
	$(MAKE) -C $(KERNELDIR) M=$(PWD)/ucache modules
	$(MAKE) -C $(KERNELDIR) M=$(PWD)/ubdma KERNELDIR=$(KERNELDIR) modules

clean:
	$(MAKE) -C $(KERNELDIR) M=$(PWD)/drivers clean || true
	$(MAKE) -C $(KERNELDIR) M=$(PWD)/tiering clean || true
	$(MAKE) -C $(KERNELDIR) M=$(PWD)/ucache clean || true
	$(MAKE) -C $(KERNELDIR) M=$(PWD)/ubdma clean || true
