# Uses fpm (https://github.com/jordansissel/fpm) to build a CentOS 6 RPM

vendor="Sam Clements <sam.clements@datasift.com>"
sources=$(shell find supermann -name '*.py') setup.py README.rst

define fpm
	@mkdir -p dist
	fpm -s python -t rpm --package $@ --vendor ${vendor} --epoch 1
endef


default:
	@echo "Usage:"
	@echo "  make all - build a generic RPM, source distribution and wheel"
	@echo "  make el6 - build CentOS 6 Supermann RPM"
	@echo "  make el5 - build CentOS 5 Supermann and blinker RPM"


version=$(shell python setup.py --version)
release=2

all: \
	dist/supermann-${version}-${release}.noarch.rpm \
	dist/supermann-${version}-py2-none-any.whl \
	dist/supermann-${version}.tar.gz \

dist/supermann-${version}.tar.gz: ${sources}
	python setup.py sdist

dist/supermann-${version}-py2-none-any.whl: ${sources}
	python setup.py bdist_wheel

dist/supermann-${version}-${release}.noarch.rpm: ${sources}
	${fpm} --version ${version} --iteration ${release} \
	--no-python-fix-name setup.py


el5: supermann.el5 blinker.el5

supermann.el5: dist/supermann-${version}-${release}.el5.noarch.rpm

dist/supermann-${version}-${release}.el5.noarch.rpm: ${sources}
	${fpm} --version ${version} --iteration ${release}.el5 \
	--python-package-name-prefix python26 \
	--no-python-fix-name \
	--no-python-dependencies \
	--depends 'python(abi) = 2.6' \
	--depends 'python26-argparse >= 1.1' \
	--depends 'python26-blinker >= 1.1' \
	--depends 'python26-psutil >= 0.6.1' \
	--depends 'python26-riemann-client >= 4.0.0' \
	--depends 'supervisor = 3.0' \
	setup.py

blinker_version=1.1
blinker_release=2

blinker.el5: \
	dist/python26-blinker-${blinker_version}-${blinker_release}.el5.noarch.rpm

dist/python26-blinker-${blinker_version}-${blinker_release}.el5.noarch.rpm:
	${fpm} --version ${blinker_version} --iteration ${blinker_release}.el5 \
	--python-package-name-prefix python26 \
	blinker


el6: supermann.el6

supermann.el6: dist/supermann-${version}-${release}.el6.noarch.rpm

dist/supermann-${version}-${release}.el6.noarch.rpm: ${sources}
	${fpm} --version ${version} --iteration ${release}.el6 \
	--no-python-fix-name \
	--no-python-dependencies \
	--depends 'python(abi) = 2.6' \
	--depends 'python-argparse >= 1.1' \
	--depends 'python-blinker >= 1.1' \
	--depends 'python-psutil >= 0.6.1' \
	--depends 'python-riemann-client >= 4.0.0' \
	--depends 'supervisor = 3.0' \
	setup.py


.PHONY: default all el5 supermann.el5 blinker.el5 el6 supermann.el6
