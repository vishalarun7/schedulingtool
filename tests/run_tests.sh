#!/usr/bin/env bash
set -euo pipefail

BINARY="${1:-python3 ./render-schedule.py}"
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

# Each case: schedule_file from_time until_time
declare -A FROM
declare -A UNTIL

FROM[case1]="2026-11-06T17:00:00Z"; UNTIL[case1]="2026-11-27T17:00:00Z"
FROM[case2]="2026-11-10T09:00:00Z"; UNTIL[case2]="2026-11-15T12:00:00Z"
FROM[case3]="2026-11-20T17:00:00Z"; UNTIL[case3]="2026-12-11T17:00:00Z"
FROM[case4]="2026-11-06T17:00:00Z"; UNTIL[case4]="2026-11-20T17:00:00Z"
FROM[case5]="2026-11-08T12:00:00Z"; UNTIL[case5]="2026-11-12T00:00:00Z"
FROM[case6]="2026-11-06T17:00:00Z"; UNTIL[case6]="2026-11-13T17:00:00Z"
FROM[case7]="2026-11-07T00:00:00Z"; UNTIL[case7]="2026-11-08T12:00:00Z"
FROM[case8]="2026-11-01T00:00:00Z"; UNTIL[case8]="2026-11-10T00:00:00Z"
FROM[case9]="2026-11-06T09:00:00Z"; UNTIL[case9]="2026-11-09T09:00:00Z"

for case in case1 case2 case3 case4 case5 case6 case7 case8 case9; do
    dir="$TESTS_DIR/$case"
    from="${FROM[$case]}"
    until="${UNTIL[$case]}"

    actual=$("$BINARY" \
        --schedule="$dir/schedule.json" \
        --overrides="$dir/overrides.json" \
        --from="$from" \
        --until="$until" 2>&1)

    diff_output=$(diff \
        <(echo "$actual"      | jq -S .) \
        <(cat "$dir/expected.json" | jq -S .) \
        2>&1 || true)

    if [ -z "$diff_output" ]; then
        echo "PASS  $case"
        PASS=$((PASS + 1))
    else
        echo "FAIL  $case  (from=$from until=$until)"
        echo "$diff_output" | sed 's/^/      /'
        FAIL=$((FAIL + 1))
    fi
done

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]


