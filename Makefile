version=$(shell python setup.py --version)
release=$(shell grep Release supermann.spec | awk '{ print $$2 }')

package=supermann-${version}-${release}.noarch.rpm
tarball=${HOME}/rpmbuild/SOURCES/supermann-${version}.tar.gz

dist/${package}: supermann.spec ${tarball}
	rpmbuild -ba supermann.spec
	rsync -a ${HOME}/rpmbuild/RPMS/noarch/${package} dist/${package}

${tarball}: $(shell find supermann)
	tar -zcf ${tarball} . --exclude-vcs --transform='s/./supermann-${version}/'
