## Importing a Pre-Existing File Tree !heading
### Reasoning
This is probably one of the most common questions on Stack Overflow. It might be because you don't know enough about RPMs to "do it right" or you just want to "get it done."

I'm a little reluctant to include this, because doing it the "right way" isn't all that hard.

**This is not recommended** but sometimes inevitable:
 * The build system is too complicated (seldom)
 * You're packaging something already installed that...
   * ... you have no control over
   * ... was installed by a GUI installer and you want to repackage for local usage
   * ... you don't have source code for

### How It Works
The `Makefile` takes various variables and generates a temporary tarball as well as a file listing that are used by the specfile. It uses that to build the `%files` directive and has an empty `%build` phase.

| Variable         | Default                 | Use Case                                             |
|------------------|-------------------------|------------------------------------------------------|
| `INPUT`          | `/opt/project`          | Source Tree to Copy                                  |
| `OUTPUT`         | `/opt/project`          | Destination on Target Machine                        |
| `PROJECT`        | myproject               | Base Name of the RPM                                 |
| `VERSION`        | 0.1                     | Version of the RPM                                   |
| `RELEASE`        | 1                       | Release/ Build of the RPM                            |
| `EXTRA_SOURCES`  | (n/a)                   | Space-separated list of other files to add to source |
| `OUTPUTSPECFILE` | `project.spec`          | RPM Specfile to use                                  |
| `TARBALL`        | `{PROJECT}.tar`         | Temporary tarball used to build                      |
| `RPM_TEMP`       | `{CWD}/rpmbuild-tmpdir` | Temporary directory to build RPM                     |
#comment https://www.tablesgenerator.com/markdown_tables

### Recipe
This recipe has two parts, a [`Makefile`](pre-existing_file_tree/Makefile) and a [specfile](pre-existing_file_tree/project.spec). There is also an example [`.gitignore`](pre-existing_file_tree/.gitignore) that might be useful as well.

If you have other files you want included, you can use `EXTRA_SOURCES` and then refer to them in your specfile, _e.g._ `Source1: myfile`. They are _not_ in the tarball itself, so they are _not_ automatically added to the file list. If you expect to package them, you can also add them to the `%files` stanza yourself, _e.g._ `%{source1}`. I personally used this feature to create a nice listing of plugins that were pre-baked into the RPM and then included them in the description.

#### Optional Usage 1
If you don't want to package an entire directory tree, but instead a subset, in the `Makefile` you can comment out `filelist-$(PROJECT).txt` from the `.PHONY` flag as well as its recipe. Then generate `filelist-$(PROJECT).txt` manually (_e.g._ by trimming the automatically created one). Only those files will then be packaged. Don't forget to force-add the file to your version control, because it is normally ephemeral and ignored.

#### Optional Usage 2
If your particular source tree may contain files that are identical and the user won't need to edit any of them, uncomment the two lines in the specfile referring to `hardlink`. This will cause any duplicate files within the RPM to be [hardlinked](https://en.wikipedia.org/wiki/Hard_link) to save space (_e.g._ older versions of python with identical `.pyc` and `.pyo` files). This utility is not available on all OSs.

[`Makefile`](pre-existing_file_tree/Makefile):
```Makefile
#include "../pre-existing_file_tree/Makefile.md"
```

[specfile](pre-existing_file_tree/project.spec):
```rpm-spec
#include "../pre-existing_file_tree/project-spec.md"
```
