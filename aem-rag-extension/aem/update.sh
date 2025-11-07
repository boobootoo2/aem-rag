#!/bin/bash
# -----------------------------------------------------------------------------
# fix_aem_filters.sh
# Ensures AEM submodules have the correct filter.xml configuration
# for ui.apps, ui.config, and all modules to prevent overlapping roots.
# -----------------------------------------------------------------------------

set -e

echo "🔍 Verifying AEM filter.xml configurations..."

# --- ui.apps ---
UI_APPS_FILTER="ui.apps/src/main/content/META-INF/vault/filter.xml"
mkdir -p "$(dirname "$UI_APPS_FILTER")"
cat > "$UI_APPS_FILTER" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<workspaceFilter version="1.0">
  <filter root="/apps/aem-rag"/>
</workspaceFilter>
EOF
echo "✅ Updated $UI_APPS_FILTER"

# --- ui.config ---
UI_CONFIG_FILTER="ui.config/src/main/content/META-INF/vault/filter.xml"
mkdir -p "$(dirname "$UI_CONFIG_FILTER")"
cat > "$UI_CONFIG_FILTER" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<workspaceFilter version="1.0">
  <filter root="/apps/aem-rag/osgiconfig"/>
</workspaceFilter>
EOF
echo "✅ Updated $UI_CONFIG_FILTER"

# --- all ---
ALL_FILTER="all/src/main/content/META-INF/vault/filter.xml"
mkdir -p "$(dirname "$ALL_FILTER")"
cat > "$ALL_FILTER" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<workspaceFilter version="1.0">
  <filter root="/apps/aem-rag"/>
  <filter root="/conf/aem-rag"/>
  <filter root="/content/aem-rag"/>
</workspaceFilter>
EOF
echo "✅ Updated $ALL_FILTER"

# --- summary ---
echo
echo "🎯 All filters are aligned."
echo "Next step: Run Maven build"
echo
echo "  mvn clean install -rf :all"
echo
echo "💡 Tip: You can make this script executable via:"
echo "  chmod +x fix_aem_filters.sh"
