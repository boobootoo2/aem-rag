#!/bin/bash
set -e

ZIP_PATH="$1"
ARTIFACT_ID="$2"

echo "📦 Uploading AEM package:"
echo "  Artifact: $ARTIFACT_ID"
echo "  File: $ZIP_PATH"
echo "---------------------------------------"

UPLOAD_RESPONSE=$(curl -s -u admin:admin \
     -F "file=@${ZIP_PATH}" \
     -F "name=${ARTIFACT_ID}" \
     -F "force=true" \
     -F "install=true" \
     "http://localhost:4502/crx/packmgr/service.jsp?cmd=upload")

echo "🪣 Upload response: $UPLOAD_RESPONSE"

if echo "$UPLOAD_RESPONSE" | grep -qi "Package imported"; then
  echo "✅ Package uploaded and installed successfully!"
else
  echo "⚠️ Upload may have failed. Check CRX Package Manager manually."
fi
