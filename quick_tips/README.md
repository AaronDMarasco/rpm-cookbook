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

### Set Output of a Random Shell Command Into Variable !heading
As noted [here](https://stackoverflow.com/a/10694815/836748):
```rpm-spec
%global your_var %(shell your commands)
```
