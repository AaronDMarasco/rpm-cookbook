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

|  Variable  |         Default         |             Use Case             |
|:----------:|:-----------------------:|:--------------------------------:|
| `INPUT`    | `/opt/project`          | Source Tree to Copy              |
| `OUTPUT`   | `/opt/project`          | Destination on Target Machine    |
| `PROJECT`  | myproject               | Base Name of the RPM             |
| `VERSION`  | 0.1                     | Version of the RPM               |
| `RELEASE`  | 1                       | Release/ Build of the RPM        |
| `TARBALL`  | `{PROJECT}.tar`         | Temporary tarball used to build  |
| `RPM_TEMP` | `{CWD}/rpmbuild-tmpdir` | Temporary directory to build RPM |
#comment https://www.tablesgenerator.com/markdown_tables

### Recipe
This recipe has two parts, a [`Makefile`](pre-existing_file_tree/Makefile) and a [specfile](pre-existing_file_tree/project.spec). There is also an example [`.gitignore`](pre-existing_file_tree/.gitignore) that might be useful as well.

[`Makefile`](pre-existing_file_tree/Makefile):
```Makefile
#include "../pre-existing_file_tree/Makefile.md"
```

[specfile](pre-existing_file_tree/project.spec):
```rpm-spec
#include "../pre-existing_file_tree/project-spec.md"
```
