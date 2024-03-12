# Requirements

The test suite *must* be run against a fresh Isidore installation. If there are
any hosts or tags (other than the special `all` and `ungrouped` tags) in
Isidore, it will cause test failures.

There is no guarantee that the Isidore database that is used for testing will
be preserved. It should be assumed that this is a desctructive test suite.

# Tips

1. *Always* examine the first failure first. The later tests are dependent on
   the functionality in the earlier tests, so any single test failure is liable
   to cause any and all subsequent teste to fail, regardless of whether or not
   the subsequent portion of Isidore under test is functioning correctly.

# Running the Test Suite

The test suite is run using the `run.sh` script. When run without any
arguments, the system's Isidore installation is checked against known good
baseline results. Supported arguments are as follows:

* `-b`: create baseline test results to compare subsequent tests aginst
* `-c`: run the tests and compare the results against the baseline results
* `-i <path>`: the path to the Isidore binary to use for testing. Can also be
  set via the `ISIDORE` enrionment variable
* `-m <dir>`: specify the directoruy that the baseline results reside in. Has
  an effect only when used in conjunction with `-c`. Defaults to
  `results/expected`.
* `-r <dir>`: specify the directory to store the test results in. Defaults to
  `results/actual`
* `-t <dir>`: specify the directory that the test cases are in. Defaults to
  `tests`

Note: the `-b` and `-c` flags are mutually exclusive.

