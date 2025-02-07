#!/bin/sh

# To be properl executed by maelstro initialization need the +x flag 
# so you need to add it with chmod and commit/push it

MAELSTRO_DIR=${1:-/app}
SNIPPET="<script src='https://cdn.jsdelivr.net/gh/georchestra/header@dist/header.js'></script><geor-header active-app='maelstro' style='height:90px'></geor-header>"

if grep -q "${SNIPPET}" "${MAELSTRO_DIR}/index.html"; then
  echo "[INFO] geOrchestra: header already present."
  exit 0
fi

echo "[INFO] geOrchestra: adding header in the main page..."
sed -i "s#<body>#<body>${SNIPPET}#" ${MAELSTRO_DIR}/index.html
