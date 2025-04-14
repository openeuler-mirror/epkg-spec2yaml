# static hash placeholder
owner: shengde

## steps
prefix_placeholder = 'iuohjklyt2372hrkjekjf'
env prefix_placeholder rpmbuild

make install
cd install dir
compute real_prefix = md5sum all rpm files
e.g.
gcc -> gcc.rpm, gcc.debug.rpm; gcc.src.rpm

sed in dir $prefix_placeholder => $real_prefix
create rpms

## options
- rpmbuild run stage step by step
- rpmbuild callback script
- rpmbuild normal rpm; compute hash; rpmbuild epkg rpm

# batch by spec source
owner: senlin

1. z9 create a dir contain all 3w xxx.spec in git form
2. grep common problems in the git workdirs
	run fixup.sh over all git
	grep hard coded /usr /etc ...
	classify
	fix problems in batches in fixup.sh

# batch by upstream code
owner: pengjie
TODO: create an extract/convert sh script

	port nixpkgs experiences to
		<class>/fixup-source.sh
		<app>/fixup-source.sh

	e.g.
	wfg@z9 /c/os/NixOS/nixpkgs/pkgs% gg -i sed|g /usr|wc -l
	384

	wfg@z9 /c/os/NixOS/nixpkgs/pkgs% gg -i substitu|g /usr|wc -l
	339

	wfg@z9 /c/os/NixOS/nixpkgs/pkgs% gg -i sed|g /usr|head
	applications/audio/AMB-plugins/default.nix:15:    sed -i 's@/usr/bin/install@install@g' Makefile
	applications/audio/AMB-plugins/default.nix:17:    sed -i 's@/usr/lib/ladspa@$(out)/lib/ladspa@g' Makefile
	applications/audio/FIL-plugins/default.nix:15:    sed -i 's@/usr/bin/install@install@g' Makefile
	applications/audio/FIL-plugins/default.nix:17:    sed -i 's@/usr/lib/ladspa@$(out)/lib/ladspa@g' Makefile
	applications/audio/MMA/default.nix:16:    sed -i 's@/usr/bin/aplaymidi@/${alsa-utils}/bin/aplaymidi@g' mma-splitrec
	applications/audio/MMA/default.nix:17:    sed -i 's@/usr/bin/aplaymidi@/${alsa-utils}/bin/aplaymidi@g' util/mma-splitrec.py
	applications/audio/MMA/default.nix:18:    sed -i 's@/usr/bin/arecord@/${alsa-utils}/bin/arecord@g' mma-splitrec
	applications/audio/MMA/default.nix:19:    sed -i 's@/usr/bin/arecord@/${alsa-utils}/bin/arecord@g' util/mma-splitrec.py
	applications/audio/MMA/default.nix:20:    sed -i 's@/usr/bin/timidity@/${timidity}/bin/timidity@g' mma-splitrec

	tools/virtualization/multipass/default.nix:53:    substituteInPlace ./src/network/network_access_manager.cpp \
	tools/virtualization/multipass/default.nix:56:    substituteInPlace ./src/platform/backends/lxd/lxd_virtual_machine.cpp \
	tools/virtualization/multipass/default.nix:59:    substituteInPlace ./src/platform/backends/lxd/lxd_request.h \
	tools/virtualization/multipass/default.nix:62:    substituteInPlace ./tests/CMakeLists.txt \
	tools/virtualization/nixos-container/default.nix:1:{ substituteAll
	tools/virtualization/nixos-container/default.nix:10:substituteAll {
	tools/virtualization/xe-guest-utilities/default.nix:21:    substituteInPlace mk/xen-vcpu-hotplug.rules \
	tools/wayland/proycon-wayout/default.nix:28:    substituteInPlace meson.build --replace "'werror=true'," "" # Build fails with -Werror, remove
	tools/wayland/sov/default.nix:18:    substituteInPlace src/sov/main.c --replace '/usr' $out
	tools/wayland/waynergy/default.nix:32:    substituteInPlace waynergy.desktop --replace "Exec=/usr/bin/waynergy" "Exec=$out/bin/waynergy"
	tools/wayland/wdomirror/default.nix:44:    substituteInPlace meson.build \
	tools/wayland/wl-clipboard-x11/default.nix:19:    substituteInPlace src/wl-clipboard-x11 \
	tools/wayland/wl-color-picker/default.nix:29:    substituteInPlace Makefile \
	tools/wayland/wl-gammactl/default.nix:27:    substituteInPlace meson.build --replace "git = find_program('git')" "git = 'false'"
	tools/wayland/wl-mirror/default.nix:46:    substituteInPlace CMakeLists.txt \

# batch submit job
owner: xueliang

- select spec git 
- select os version yum repos

wfg@z9 /srv/rpm/pub/openeuler-22.03-LTS/compatible/f36% sd
50G     .
18G     ./aarch64
17G     ./x86_64
16G     ./source

wfg@z9 /srv/rpm/pub/openeuler-22.03-LTS/compatible/f36/source% ls Packages|wc -l
13972

wfg@z9 /srv/rpm/pub/openeuler-22.03-LTS/compatible/f36/aarch64% ls Packages|wc -l
33222

os=2203 repos=f36

# run in compass
owner: shengde

- refer to LKP programs/rpmbuild
- select known good version 22.03 baseos/oepkg yum repos

yum install bash.src
rpmbuild bash
upload to central path # no incremental newrepo

- submit epkg build jobs to compass, using src.rpm

# batch account build errors

	cci jobs -e group_id=epkg.20240411

# resource doc
local dirs in z9:
- all os spec
- all upstream git
- all project git

