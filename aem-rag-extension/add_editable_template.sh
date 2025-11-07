#!/bin/bash
set -e

echo "📁 Creating editable template structure under /conf/aem-rag..."

BASE_DIR="$(pwd)"
AEM_DIR="$BASE_DIR/aem"

CONF_PATH="$AEM_DIR/ui.content/src/main/content/jcr_root/conf/aem-rag"
TEMPLATE_TYPE_PATH="$CONF_PATH/settings/wcm/template-types/page"
TEMPLATE_PATH="$CONF_PATH/settings/wcm/templates/page-content"
POLICIES_PATH="$CONF_PATH/settings/wcm/policies"

mkdir -p "$TEMPLATE_TYPE_PATH"
mkdir -p "$TEMPLATE_PATH/jcr:content"
mkdir -p "$POLICIES_PATH/aem-rag/components"

# --- Template Type Definition ---
cat > "$TEMPLATE_TYPE_PATH/.content.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<jcr:root
    xmlns:sling="http://sling.apache.org/jcr/sling/1.0"
    xmlns:cq="http://www.day.com/jcr/cq/1.0"
    xmlns:jcr="http://www.jcp.org/jcr/1.0"
    jcr:primaryType="cq:TemplateType"
    jcr:title="AEM RAG Page Template Type"
    allowedPaths="[/content(/.*)?]"
    ranking="{Long}100"/>
EOF

# --- Template Definition ---
cat > "$TEMPLATE_PATH/.content.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<jcr:root
    xmlns:sling="http://sling.apache.org/jcr/sling/1.0"
    xmlns:cq="http://www.day.com/jcr/cq/1.0"
    xmlns:jcr="http://www.jcp.org/jcr/1.0"
    jcr:primaryType="cq:Template"
    jcr:title="AEM RAG Content Page"
    jcr:description="Editable template for AEM RAG pages"
    allowedPaths="[/content/aem-rag(/.*)?]"
    cq:templateType="/conf/aem-rag/settings/wcm/template-types/page"
    ranking="{Long}100"/>
EOF

# --- Template Structure (Editable Area) ---
cat > "$TEMPLATE_PATH/jcr:content/.content.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<jcr:root
    xmlns:sling="http://sling.apache.org/jcr/sling/1.0"
    xmlns:cq="http://www.day.com/jcr/cq/1.0"
    xmlns:jcr="http://www.jcp.org/jcr/1.0"
    cq:designPath="/conf/aem-rag/settings/wcm/designs/default"
    jcr:primaryType="cq:PageContent"
    sling:resourceType="wcm/core/components/page/v3/page">
  <root
      jcr:primaryType="nt:unstructured"
      sling:resourceType="wcm/foundation/components/responsivegrid"/>
</jcr:root>
EOF

# --- Policy to Allow ragconsole ---
cat > "$POLICIES_PATH/aem-rag/components/.content.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<jcr:root
    xmlns:sling="http://sling.apache.org/jcr/sling/1.0"
    xmlns:cq="http://www.day.com/jcr/cq/1.0"
    xmlns:jcr="http://www.jcp.org/jcr/1.0"
    jcr:primaryType="cq:Policy"
    allowedComponents="[/apps/aem-rag/components/ragconsole]"/>
EOF

echo "✅ Editable template structure created under ui.content/src/main/content/jcr_root/conf/aem-rag"
echo "Next Steps:"
echo "1. Rebuild and deploy your AEM project: mvn clean install -PautoInstallPackage"
echo "2. Open http://localhost:4502/editor.html/conf/aem-rag/settings/wcm/templates/page-content/structure.html"
echo "3. You should now see and be able to use the RAG Console component!"
