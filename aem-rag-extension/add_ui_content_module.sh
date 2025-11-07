#!/bin/bash
set -e

BASE_DIR="$(pwd)"
AEM_DIR="$BASE_DIR/aem"
UI_CONTENT_DIR="$AEM_DIR/ui.content"

echo "📁 Creating ui.content module structure..."
mkdir -p "$UI_CONTENT_DIR/src/main/content/META-INF/vault"
mkdir -p "$UI_CONTENT_DIR/src/main/content/jcr_root/content/aem-rag"

# Write ui.content/pom.xml
cat > "$UI_CONTENT_DIR/pom.xml" <<'EOF'
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <parent>
    <groupId>com.example</groupId>
    <artifactId>aem-rag-extension</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <relativePath>../pom.xml</relativePath>
  </parent>

  <artifactId>ui.content</artifactId>
  <packaging>content-package</packaging>
  <name>AEM RAG Extension - UI Content</name>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.jackrabbit</groupId>
        <artifactId>filevault-package-maven-plugin</artifactId>
        <extensions>true</extensions>
        <configuration>
          <packageType>content</packageType>
          <filterSource>src/main/content/META-INF/vault/filter.xml</filterSource>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
EOF

# Write filter.xml
cat > "$UI_CONTENT_DIR/src/main/content/META-INF/vault/filter.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<workspaceFilter version="1.0">
  <filter root="/content/aem-rag"/>
</workspaceFilter>
EOF

# Write .content.xml
cat > "$UI_CONTENT_DIR/src/main/content/jcr_root/content/aem-rag/.content.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<jcr:root
    xmlns:sling="http://sling.apache.org/jcr/sling/1.0"
    xmlns:jcr="http://www.jcp.org/jcr/1.0"
    jcr:primaryType="cq:Page">
  <jcr:content
      jcr:primaryType="cq:PageContent"
      jcr:title="AEM RAG Home"
      sling:resourceType="aem-rag/components/page"
      />
</jcr:root>
EOF

# Update parent POM
PARENT_POM="$AEM_DIR/pom.xml"
if ! grep -q "<module>ui.content</module>" "$PARENT_POM"; then
  echo "🧩 Adding ui.content module to parent pom.xml..."
  sed -i '' '/<modules>/a\
    <module>ui.content</module>
  ' "$PARENT_POM"
fi

# Update all/pom.xml
ALL_POM="$AEM_DIR/all/pom.xml"
if ! grep -q "ui.content" "$ALL_POM"; then
  echo "🧩 Adding ui.content dependency and embed to all/pom.xml..."
  sed -i '' '/<embeddeds>/a\
            <embedded>\
              <groupId>com.example</groupId>\
              <artifactId>ui.content</artifactId>\
              <type>zip</type>\
              <target>/apps/aem-rag/install</target>\
            </embedded>\
  ' "$ALL_POM"
  sed -i '' '/<dependencies>/a\
        <dependency>\
          <groupId>com.example</groupId>\
          <artifactId>ui.content</artifactId>\
          <version>${project.version}</version>\
          <type>zip</type>\
        </dependency>\
  ' "$ALL_POM"
fi

echo "✅ ui.content module created and parent/all POMs updated."
echo "Run: cd aem && mvn clean install -PautoInstallPackage"
