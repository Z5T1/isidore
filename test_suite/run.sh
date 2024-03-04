#!/bin/sh

cd "$(dirname $0)"
RESULT_DIR=${RESULT_DIR:-results/actual}
TEST_DIR=${TEST_DIR:-tests}
COMPARE_DIR=${COMPARE_DIR:-results/expected}
ISIDORE=${ISIDORE:-isidore}
CHECK=true
BASELINE=false

args=`getopt bci:t:r: $*`
if [ $? -ne 0 ]; then
	echo "Usage: run.sh [-bcitr]"
	exit 1
fi
set -- $args

while :; do
	case "$1" in
		-b)
			BASELINE=true
			CHECK=false
			shift
			;;
		-c)
			CHECK=true
			BASELINE=false
			shift
			;;
		-i)
			ISIDORE="$2"
			shift; shift
			;;
		-m)
			COMPARE_DIR="$2"
			shift; shift
			;;
		-t)
			TEST_DIR="$2"
			shift; shift
			;;
		-r)
			RESULT_DIR="$2"
			shift; shift
			;;
		--)
			shift
			break
			;;
	esac
done

mkdir -p "$RESULT_DIR"

PASS=0
FAIL=0
for test in $(ls "$TEST_DIR"); do
	echo -n "[....] $test" >&2
	eval $ISIDORE < "$TEST_DIR/$test" > "$RESULT_DIR/$test" 2>&1
	if [ $CHECK = true ]; then
		diff "$RESULT_DIR/$test" "$COMPARE_DIR/$test" > /dev/null
		if [ $? -eq 0 ]; then
			echo -e "\r[PASS] $test"
			PASS=$(expr $PASS + 1)
		else
			echo -e "\r[FAIL] $test"
			FAIL=$(expr $FAIL + 1)
		fi
	else
		echo -e "\r[DONE] $test" >&2
	fi
done

echo All tests complete
if [ $CHECK = true ]; then
	echo -e "\nResult summary:\nPassed: $PASS   Failed: $FAIL"
fi

