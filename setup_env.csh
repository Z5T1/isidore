# Source this file to set up your shell to use the Isidore libraries found
# under ./lib/src, not the ones that pip installed. Useful when you want to
# test changes without having to reinstall the libraries.

if (! $?PYTHONPATH) then
	set PYTHONPATH=""
endif
setenv PYTHONPATH "$PWD/lib/src:$PYTHONPATH"

