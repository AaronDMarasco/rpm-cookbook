## Filtering Requires and Provides !heading
### Reasoning
The dependency management system is _usually_ pretty good, but sometimes it's not perfect. For example, I had to package a version of `python2` for some other software for a project. We didn't want to tell the RPM database that our `libpython2.7.so` was available to just _anybody_, but we don't want to just say "`AutoReqProv: no`" which is almost _never_ the right answer and often downright overkill.

### How It Works
For both `Requires` and `Provides`, RPM provides a hook _before_ the processing, which gives you filenames it will analyze, and a hook _after_ the processing, which gives you strings like `liblua-5.3.so()(64bit)`.

The macros you use to add the filters are `filter_(provides|requires)_in` and `filter_from_(provides|requires)`. The `_in` version allows the `-P` parameter to tell `grep` to use Perl-like regular expressions.

Lastly, once you use these macros to set internal variables, you call `%filter_setup` to read them in and create the full macros.

### Recipe
Unlike other recipes, this chapter only provides blurbs; not a full working example. Again, these were from a custom packaging of python.

These all filter _filenames_ that are fed into the `/usr/lib/rpm/rpmdeps` executable for analysis, which are given to `grep` so with my `perl` background, I use `grep -P` expressions:
```rpm-spec
%global short_version 2.7
# Don't announce to the rest of the system that they can use our python packages or shared library:
%filter_provides_in -P /side-packages/.*\.so
%filter_provides_in -P libpython%{short_version}*\.so

# This reduces the number of unimportant files looped over considerably (13K => <600, or 30min+ => 5min)
# (e.g. we know that python scripts included will need python; the no-suffix versions in bin/ should catch "our" python)
# The second backslash is important or nothing will be needed (all files excluded if they have 'c' or 'h' in them)
%global ignore_suffices .*\\.(pyc?o?|c|h|txt|rc|rst|mat|dat|decTest|pxd|html?|aiff|wav|xml|bmp|gif|jpe?g|pbm|pgm|png|ppm|ras|tiff|xbm)
%filter_requires_in -P %{ignore_suffices}
%filter_provides_in -P %{ignore_suffices}

# scipy/numpy require openblas and gfortran, which they they provide themselves:
%filter_requires_in -P .*/site-packages/(sci|num)py/.*
```

These filter _after_ the analysis of the files and are `sed` commands, so it's _usually_ a pattern with a `d` (delete) command:
```rpm-spec
# Ourselves (because we will not "provide" it) - but check OUR system library requirements first, so don't pre-filter them
%filter_from_requires /libypthon%{short_version}/d
```

I have found that generating the `filter_from` macros from `bash` is easy to iterate over things by concatenating strings starting with `;` -- `sed` skips over the initial empty statement:
```bash
for f in FILES_TO_SKIP; do
  FILTER_STRING+=";/${f}/d"
done
...
rpmbuild --define="filterstring ${FILTER_STRING}" ...
```

**Don't forget you need `%filter_setup` at the end to implement these filters.**

One last thing that helped me with some debugging was modifying the default macros that `filter_setup` calls to see what the files were, for example why it was taking so long as noted above. I manually expanded what that macro did, while adding that single `tee` call to the `__deploop` macro. The other macros are what get set by the helpers above. **Don't distribute spec files with these hacks in them!**
```rpm-spec
%global _use_internal_dependency_generator 0
%global __deploop() while read FILE; do echo "${FILE}" | tee /dev/fd/2 | /usr/lib/rpm/rpmdeps -${1}; done | /bin/sort -u
%global __find_provides /bin/sh -c "${?__filter_prov_cmd} %{__deploop P} %{?__filter_from_prov}"
%global __find_requires /bin/sh -c "%{?__filter_req_cmd}  %{__deploop R} %{?__filter_from_req}"
```
