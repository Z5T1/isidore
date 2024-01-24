#!/bin/sh

VERSION=$1

sed -i lib/Makefile -e "/^VERSION=/c VERSION=$VERSION"
sed -i lib/pyproject.toml -e "/^version = /c\\version = \"$VERSION\""
sed -i lib/src/isidore/libIsidoreCmdline.py -e"/^    _version = /c\\    _version = '$VERSION'"
sed -i lib/src/isidore/libIsidore.py -e"/^    _version = /c\\    _version = '$VERSION'"
sed -i db/create_db.sql -e "/'version', /c\\	('version', '$VERSION')"

