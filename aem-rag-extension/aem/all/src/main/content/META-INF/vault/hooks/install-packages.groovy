import org.slf4j.Logger
import org.slf4j.LoggerFactory
import javax.jcr.Session
import org.apache.jackrabbit.vault.packaging.JcrPackageManager
import org.apache.jackrabbit.vault.packaging.PackageException
import org.apache.jackrabbit.vault.packaging.PackageId
import org.apache.jackrabbit.vault.fs.io.ImportOptions

final Logger log = LoggerFactory.getLogger("install-packages.groovy")

def installPackage(session, packageManager, path) {
    try {
        log.info("Installing package at path: {}", path)
        def node = session.getNode(path)
        def pack = packageManager.open(node)
        if (pack != null) {
            def options = new ImportOptions()
            options.setDependencyHandling(ImportOptions.DependencyHandling.BEST_EFFORT)
            options.setAutoSaveThreshold(Integer.MAX_VALUE)
            packageManager.install(pack, options)
            log.info("Package installation completed: {}", path)
        } else {
            log.error("Failed to open package at path: {}", path)
        }
    } catch (Exception e) {
        log.error("Error installing package at path: {}", path, e)
    }
}

def run(session) {
    log.info("Starting installation of embedded packages")
    
    def packageManager = packaging.getPackageManager()
    
    // Install the packages in the correct order
    installPackage(session, packageManager, "/apps/aem-rag/install/ui.apps-1.0.0-SNAPSHOT.zip")
    installPackage(session, packageManager, "/apps/aem-rag/install/ui.config-1.0.0-SNAPSHOT.zip")
    
    log.info("Finished installing embedded packages")
    return true
}   