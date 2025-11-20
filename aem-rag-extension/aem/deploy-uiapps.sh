#!/bin/bash
# ==========================================================
# deploy-uiapps.sh
# Deploys the ui.apps package to AEM and verifies components
# ==========================================================

AEM_HOST="http://localhost:4502"
AEM_USER="admin"
AEM_PASS="admin"
PACKAGE_PATH="ui.apps/target/ui.apps-1.0.0-SNAPSHOT.zip"
PACKAGE_NAME="aem-rag-extension-ui.apps"

echo "🔧 Rebuilding ui.apps..."
mvn clean install -pl ui.apps -DskipTests

if [ ! -f "$PACKAGE_PATH" ]; then
  echo "❌ Package not found: $PACKAGE_PATH"
  exit 1
fi

echo "📦 Uploading and installing package into AEM..."
UPLOAD_RESPONSE=$(curl -s -u $AEM_USER:$AEM_PASS \
  -F file=@$PACKAGE_PATH \
  -F name="$PACKAGE_NAME" \
  -F force=true \
  -F install=true \
  "$AEM_HOST/crx/packmgr/service.jsp")

if echo "$UPLOAD_RESPONSE" | grep -q "<status code=\"200\">ok</status>"; then
  echo "✅ Package uploaded and installed successfully."
else
  echo "⚠️ Upload may have failed. Response:"
  echo "$UPLOAD_RESPONSE"
fi

echo "🔍 Verifying /apps/aem-rag/components in JCR..."
CHECK_RESPONSE=$(curl -s -u $AEM_USER:$AEM_PASS "$AEM_HOST/crx/server/crx.default/jcr:root/apps/aem-rag.json")

if echo "$CHECK_RESPONSE" | grep -q '"components"'; then
  echo "✅ Components folder found in AEM: /apps/aem-rag/components"
else
  echo "❌ Components folder not found. Check filter.xml or package content."
  echo "ℹ️ You can manually check at: $AEM_HOST/crx/de/index.jsp#/apps/aem-rag"
fi
