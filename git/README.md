## Git Problems and Tricks !heading
### Git Branch or Tag in Release !heading
and
### Monotonic Release Numbers !heading
and
### Embedding Source Hash in Description !heading
and
### Jenkins (or Any CI) Build Number in Release !heading
#### Overview
This "chapter" is very much intertwined, so you'll have to rip out the parts you want.

#### Reasoning
 * Branch or Tag in Release: When checking what version of your software is installed on a machine, it's nice to instantly be able to tell if it's one of your "release" versions or a development branch that somebody was working with.
 * Monotonic Release Numbers: Git hashes aren't easily sorted, so there's no way for `rpm`/`yum`/`dnf` to know that `7289cc5` is actually _newer_ than `7289cc5`.
 * Embedding Source Hash: There's nothing better than "ground truth" when somebody asks for help and they can tell you _exactly_ what RPMs they're dealing with thanks to  `rpm -qi yourpackage`.
 * Build Number in Release: When testing RPMs, it's easier to go back and see what build created the RPMs.

### How It Works
A little `git` command-line magic (along with some `perl` regex) gets us what we want. It's not obviously straight-forward because it works around various problematic scenarios that I've experienced:
 * Detached `HEAD` build (*e.g.* Jenkins)
 * It's in both a branch *and* a tag
 * `origin` has moved forward since the checkout happened, but _before_ our code is run, resulting in things like `mybranch~2`
 * The branch name is obnoxiously long because it has a prefix like `bugfix--BUG13`
   * *Any* prefix ending in `--` is stripped
 * The branch has `.` or other characters in it that are invalid for the RPM release field
 * A "release version" is in a specially named _branch_ (not tag) of the format `v1.0` or `v.1.1.3`

To compute the monotonic number, it counts the number of six-minute time periods that have passed since the last release (which requires a manual "bump" in the `Makefile`).

External information needed:
|    Variable    |         Default         |             Use Case             |
|:--------------:|:-----------------------:|:--------------------------------:|
| `project`      | myproject               | Base Name of the RPM             |
| `version`      | 0.1                     | Version of the RPM               |
| `release`      | snapshot<etc...>        | Release/ Build of the RPM        |
| `BUILD_NUMBER` | (n/a)                   | Job number from Jenkins          |
| `RPM_TEMP`     | `{CWD}/rpmbuild-tmpdir` | Temporary directory to build RPM |
#comment https://www.tablesgenerator.com/markdown_tables

Obviously, `BUILD_NUMBER` is Jenkins-specific. It could just as easily be `CI_JOB_ID` on [GitLab](https://docs.gitlab.com/ee/ci/variables/) or `TRAVIS_BUILD_NUMBER` for [Travis-CI](https://docs.travis-ci.com/user/environment-variables/#default-environment-variables).

#### Recipe
This recipe has two parts, a [`Makefile`](git/Makefile) and a [specfile](git/project.spec).

[`Makefile`](git/Makefile):
```Makefile
#include "../git/Makefile.md"
```

[specfile](git/project.spec):
```rpm-spec
#include "../git/project-spec.md"
```
