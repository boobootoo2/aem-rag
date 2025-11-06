package com.example.aem.rag.scheduler;

import com.example.aem.rag.services.RagIndexService;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Reference;

@Component(
    service = Runnable.class,
    property = {
        "scheduler.name=AEM RAG Indexer",
        "scheduler.expression=0 0 3 * * ?",
        "scheduler.concurrent=false"
    }
)
public class RagIndexerScheduler implements Runnable {

    @Reference
    private RagIndexService indexService;

    @Override
    public void run() {
        indexService.rebuildIndex();
    }
}
