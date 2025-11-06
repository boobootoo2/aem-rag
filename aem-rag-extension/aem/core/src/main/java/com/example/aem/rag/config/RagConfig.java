package com.example.aem.rag.config;

import org.osgi.service.component.annotations.Component;
import org.osgi.service.metatype.annotations.AttributeDefinition;
import org.osgi.service.metatype.annotations.Designate;
import org.osgi.service.metatype.annotations.ObjectClassDefinition;

@ObjectClassDefinition(name = "AEM RAG Configuration", description = "RAG paths, keys, cron")
public @interface RagConfig {
    @AttributeDefinition(name="OpenAI API Key")
    String openai_api_key() default "";

    @AttributeDefinition(name="Index Paths (comma-separated)")
    String index_paths() default "/apps/core,/content/we-retail,/conf/we-retail,/content/dam";

    @AttributeDefinition(name="Index Storage Path")
    String index_storage() default "/var/rag-index";

    @AttributeDefinition(name="Chat Model")
    String model_chat() default "gpt-4o-mini";

    @AttributeDefinition(name="Max K Neighbors")
    int max_k() default 8;

    @AttributeDefinition(name="Scheduler Cron")
    String index_cron() default "0 0 3 * * ?";
}
