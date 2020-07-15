## Quick Tips !heading
In reviewing some of the most highly voted answers on Stack Overflow, I decided to collate a few:

### Don't Put Single % In Comments !heading
This happens [a](https://stackoverflow.com/a/14063974/836748) [*lot*](https://stackoverflow.com/a/18440679/836748). You need to double it with `%%` or a multi-line macro will only have the first line commented out!

### Extract All Files !heading
Use `rpm2cpio` with `cpio`:
```bash
$ rpm2cpio package-version.rpm | cpio -div
```

### Extract a Single File !heading
As noted [here](https://stackoverflow.com/a/16605713/836748), use `rpm2cpio` with `cpio --to-stdout`:
```bash
$ rpm2cpio package-3.8.3.rpm | cpio -iv --to-stdout ./usr/share/doc/package-3.8.3/README > /tmp/README
./usr/share/doc/package-3.8.3/README
2173 blocks
```

### Change (or No) Compression !heading
As noted [here](https://stackoverflow.com/a/10255406/836748):
```rpm-spec
%define _source_payload w0.gzdio
%define _binary_payload w0.gzdio
```
These will send `-0` to `gzip` to effectively not compress. The `0` can be 0-9 to change the level. The `gz` can be changed:
 * `bz` for bzip2
 * `xz` for XZ/LZMA (on some versions of RPM)

### Set Output of a Shell Command Into Variable !heading
As noted [here](https://stackoverflow.com/a/10694815/836748):
```rpm-spec
%global your_var %(your commands)
```

### Warn User if Wrong Distribution !heading
On a previous project, we had people install the CentOS 7 RPMs on a CentOS 6 box. Normally, this would fail because things like your C libraries won't match. But it was a `noarch` package... This was helpful; figured I would include it here; it is *very* CentOS-specific:
```rpm-spec
# Check if somebody is installing on the wrong platform (AV-721)
if [ -n "%{dist}" ]; then
  PKG_VER=`echo %{dist} | perl -ne '/el(\d)/ && print $1'`
  THIS_VER=`perl -ne '/release (\d)/ && print $1' /etc/redhat-release`
  if [ -n "${PKG_VER}" -a -n "${THIS_VER}" ]; then
    if [ ${PKG_VER} -ne ${THIS_VER} ]; then
      for i in `seq 20`; do echo ""; done
        echo "WARNING: This RPM is for CentOS${PKG_VER}, but you seem to be running CentOS${THIS_VER}" >&2
        echo "You might want to uninstall these RPMs immediately and get the CentOS${THIS_VER} version." >&2
      for i in `seq 5`; do echo "" >&2; done
    fi
  fi
fi
```
