#!/bin/bash

set -euo pipefail

ROLE="${1:-Unknown Role}"
COMPANY="${2:-Unknown Company}"
TITLE="Job Scout"

if [[ "${DRY_RUN:-}" == "1" ]]; then
  TITLE="Job Scout [DRY RUN]"
fi

osascript <<EOF
display notification "Applied to ${ROLE} at ${COMPANY}" with title "${TITLE}"
EOF
