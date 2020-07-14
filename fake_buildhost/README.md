## Spoofing RPM Host Name !heading
### Reasoning
When distributing RPMs, you might not want people to know the build host. It shouldn't matter to the end user, and your security folks might not want internal hostnames or DNS information published for no good reason.

Newer versions of `rpmbuild` support defining `_buildhost`; I have not tested that capability myself.

### Recipe
This recipe requires you wrap your `rpmbuild` command with a script or `Makefile`. Using the `Makefile` below, you would have `make` call `$(SPOOF_HOSTNAME) rpmbuild ...`.

Edit the `Makefile` yourself where it says "`.myprojectname.proj`" - you can optionally _not_ have it use the `buildhost_<arch>` prefix as well.

Other usage notes are at the top of the `Makefile`.

[`Makefile`](fake_buildhost/Makefile):
```Makefile
#include "../fake_buildhost/Makefile.md"
```

### How It Works
It sets [`LD_PRELOAD`](view-source:https://man7.org/linux/man-pages/man8/ld.so.8.html) to intercept all 32- or 64-bit calls to [`gethostname()`](https://man7.org/linux/man-pages/man2/gethostname.2.html) and replace them with the text you provide.
