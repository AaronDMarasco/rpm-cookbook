### Symlinks to Latest !heading
#### Reasoning
This one is very specific to a workflow in an office I was in, and might not be "generically" useful. Their pre-RPM deployment method was to extract a tarball into a directory and then update a symlink that ended with `-latest` to point to it. For testing, you could simply manipulate that symlink to point to the versions you wanted to use.

This recipe allows you to build `compat` packages with the old libraries, similar to the official Fedora-recommended practice. However, the multiple version numbers in the RPM name can be confusing, so we replace the "." in the _original_ version with "p", *e.g.* `1.0.1` => `1p0p1`.

### How It Works
The [`Makefile`](multiple_versions/latest_symlink/Makefile) creates an array to generate 3 RPMs: `myproject`, `myproject-compat1p0p1` (1.0.1 compat), and `myproject-compat1p1` (1.1 compat). It will build the RPM(s) using the [specfile](multiple_versions/latest_symlink/project.spec).

**Warning**: The `Makefile` targets `test` and `clean` will use `sudo` to manipulate the demo RPMs to show the various effects of installation order, etc. It is recommended that you review the source before running it to ensure you are comfortable with the commands it is executing as `root` on your machine.

External information accepted:
| Variable    | Default                                             | Use Case                         |
|-------------|-----------------------------------------------------|----------------------------------|
| `rpm_names` | myproject myproject-compat1p0p1 myproject-compat1p1 | RPMs to Build                    |
| `version`   | 1.2                                                 | Version of the CURRENT Project   |
| `release`   | 1                                                   | Release/ Build of the RPM        |
| `RPM_TEMP`  | `{CWD}/rpmbuild-tmpdir`                             | Temporary directory to build RPM |
#comment https://www.tablesgenerator.com/markdown_tables

The `specfile` is where the "real" magic is; it will:
 * Determine the "base project name" (`%{base_project}`) by removing anything that comes after a "-"
 * Generate the "latest" symlink name (`%{target_link}`) to be used in various places
 * Decide if this is the "base" RPM or one of the compatible ones
   * `%if "%{name}" != "%{base_project}"`
 * If it determines this is a "compat" RPM, it will:
   * Generate the version number it is compatible with (`%{compat_version}`)
   * Automatically tell RPM that this RPM `Obsoletes` the original RPM with the same version numbers
   * Tells RPM that this RPM also `Provides` a specific _exact_ version of the base RPM
     * This is needed if you have other RPMs that depend explicitly on certain versions (which is why you're going through this trouble in the first place)
   * Generate a `%triggerpostun` stanza that will "take over" the symlink if the base RPM is removed and this one left behind
     * *Note*: If you have multiple compat versions, which one will perform this is nondeterministic!
 * Generate a `%post` section that will:
   * If it is **the base RPM**, will *always* point the symlink to itself
   * If it is **the first compat RPM**, will point *a new symlink* to itself *iff* one doesn't already exist
 * Generate a `%postun` section that will, if it's the _last_ RPM uninstalled (so updates will not trigger):
   * Will remove the symlink *iff* it points to the RPM being removed
   * If possible alternatives still exist (`/<orgdir>/<project>*`), will warn if the symlink is now missing, and will present a list of candidates

Any "business logic" in `%build`, `%install`, etc. should use the same comparison above (`%{name}` vs. `%{base_project}`) to determine which files should be used (along with `%{compat_version}`).

What it *doesn't* do (or does "wrong"):
 * It does _not_ declare the symlink as a `%ghost` file; this will cause it to _always_ be removed on _any_ package removal
   * Some more manipulations in `%preun` might be able to get around this, *e.g.* saving off a copy and then putting it back if it pointed elsewhere
 * It does not properly add the symlink to the RPM database:
   * No RPMs can depend on the exact path of the "latest" symlink
   * The RPM DB cannot be queried for it, *e.g.* `rpm -q --whatprovides /path/to/symlink`
 * It does not force the "compat" RPMs to `Require` the newest base; that is something you can choose to add

#### Recipe
This recipe has two parts, a [`Makefile`](multiple_versions/latest_symlink/Makefile) and a [specfile](multiple_versions/latest_symlink/project.spec).

[`Makefile`](multiple_versions/latest_symlink/Makefile):
```Makefile
#include "../multiple_versions/latest_symlink/Makefile.md"
```

[specfile](multiple_versions/latest_symlink/project.spec):
```rpm-spec
#include "../multiple_versions/latest_symlink/project-spec.md"
```
