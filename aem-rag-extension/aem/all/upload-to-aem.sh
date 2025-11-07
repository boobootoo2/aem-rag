#!/bin/bash
set -e

ZIP_PATH="$1"
ARTIFACT_ID="$2"
AEM_HOST="${3:-localhost}"
AEM_PORT="${4:-4502}"
AEM_USER="${5:-admin}"
AEM_PASSWORD="${6:-admin}"

echo "🔍 Debug Information:"
echo "  Script: $0"
echo "  Working Directory: $(pwd)"
echo "  Artifact ID: $ARTIFACT_ID"
echo "  ZIP Path: $ZIP_PATH"
echo "  AEM Host: $AEM_HOST"
echo "  AEM Port: $AEM_PORT"
echo "  AEM User: $AEM_USER"
echo "---------------------------------------"

# Check if file exists
if [ ! -f "$ZIP_PATH" ]; then
    echo "❌ Error: Package file not found at: $ZIP_PATH"
    echo "📂 Current directory contents:"
    ls -la "$(dirname "$ZIP_PATH")" 2>/dev/null || echo "Directory does not exist"
    exit 1
fi

# Get file size (macOS and Linux compatible)
if [[ "$OSTYPE" == "darwin"* ]]; then
    FILE_SIZE=$(stat -f%z "$ZIP_PATH" 2>/dev/null)
else
    FILE_SIZE=$(stat -c%s "$ZIP_PATH" 2>/dev/null)
fi
echo "✅ Package file found (Size: ${FILE_SIZE:-unknown} bytes)"

# Check if AEM is accessible
echo "🔌 Testing AEM connectivity..."
if curl -s -u "$AEM_USER:$AEM_PASSWORD" --connect-timeout 5 \
   "http://$AEM_HOST:$AEM_PORT/system/console/bundles.json" > /dev/null 2>&1; then
    echo "✅ AEM is accessible at http://$AEM_HOST:$AEM_PORT"
else
    echo "⚠️  Warning: Cannot connect to AEM at http://$AEM_HOST:$AEM_PORT"
    echo "   Make sure AEM is running on port $AEM_PORT"
    echo "   Attempting upload anyway..."
fi

echo "---------------------------------------"
echo "📦 Uploading AEM package..."

# Upload with verbose output
UPLOAD_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
     -u "$AEM_USER:$AEM_PASSWORD" \
     -F "file=@${ZIP_PATH}" \
     -F "name=${ARTIFACT_ID}" \
     -F "force=true" \
     -F "install=true" \
     "http://$AEM_HOST:$AEM_PORT/crx/packmgr/service.jsp?cmd=upload")

# Extract HTTP status
HTTP_STATUS=$(echo "$UPLOAD_RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
RESPONSE_BODY=$(echo "$UPLOAD_RESPONSE" | sed '/HTTP_STATUS:/d')

echo "🌐 HTTP Status: $HTTP_STATUS"
echo "🪣 Upload response:"
echo "$RESPONSE_BODY"
echo "---------------------------------------"

# Check for success
if echo "$RESPONSE_BODY" | grep -qi "Package imported"; then
    echo "✅ Package uploaded and installed successfully!"
    
    # Extract package info (macOS compatible - using sed instead of grep -P)
    if echo "$RESPONSE_BODY" | grep -q "<name>"; then
        PACKAGE_NAME=$(echo "$RESPONSE_BODY" | sed -n 's/.*<name>\(.*\)<\/name>.*/\1/p' | head -1)
        PACKAGE_VERSION=$(echo "$RESPONSE_BODY" | sed -n 's/.*<version>\(.*\)<\/version>.*/\1/p' | head -1)
        echo "📦 Package: $PACKAGE_NAME v$PACKAGE_VERSION"
    fi
    
    exit 0
elif [ "$HTTP_STATUS" = "200" ]; then
    echo "⚠️  Upload completed with HTTP 200, but 'Package imported' message not found"
    echo "   Check the response above for details"
    exit 0
else
    echo "❌ Upload failed with HTTP status: $HTTP_STATUS"
    echo "   Check CRX Package Manager manually at:"
    echo "   http://$AEM_HOST:$AEM_PORT/crx/packmgr/index.jsp"
    exit 1
fi