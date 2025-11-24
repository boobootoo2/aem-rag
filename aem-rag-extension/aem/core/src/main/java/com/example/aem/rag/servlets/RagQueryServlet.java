package com.example.aem.rag.servlets;

import com.example.aem.rag.services.RagIndexService;
import com.example.aem.rag.services.OpenAIService;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.apache.sling.api.SlingHttpServletRequest;
import org.apache.sling.api.SlingHttpServletResponse;
import org.apache.sling.api.servlets.SlingAllMethodsServlet;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.servlet.Servlet;
import javax.servlet.ServletException;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

@Component(
    service = {Servlet.class},
    property = {
        "sling.servlet.methods=POST",
        "sling.servlet.methods=GET",
        "sling.servlet.paths=/bin/aemrag/query",
        "sling.auth.requirements=-/bin/aemrag/query"  // Allow anonymous access
    }
)
public class RagQueryServlet extends SlingAllMethodsServlet {
    
    private static final Logger LOG = LoggerFactory.getLogger(RagQueryServlet.class);
    private static final int DEFAULT_TOP_K = 5;
    
    @Reference(cardinality = ReferenceCardinality.OPTIONAL)
    private volatile RagIndexService ragIndexService;
    
    @Reference(cardinality = ReferenceCardinality.OPTIONAL)
    private volatile OpenAIService openAIService;
    
    private Gson gson = new Gson();
    
    // Simple in-memory cache
    private Map<String, CachedResponse> queryCache = new HashMap<>();
    private int totalRequests = 0;
    private int cacheHits = 0;
    private static final int MAX_CACHE_SIZE = 1000;

    @Override
    protected void doGet(SlingHttpServletRequest request, SlingHttpServletResponse response)
            throws ServletException, IOException {
        
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        
        // Handle special query parameters for stats and cache management
        String queryParam = request.getParameter("query");
        
        if ("_stats".equals(queryParam)) {
            JsonObject stats = new JsonObject();
            stats.addProperty("cacheSize", queryCache.size());
            stats.addProperty("maxCacheSize", MAX_CACHE_SIZE);
            stats.addProperty("hitRate", String.format("%.1f%%", totalRequests > 0 ? (100.0 * cacheHits / totalRequests) : 0.0));
            stats.addProperty("totalRequests", totalRequests);
            response.getWriter().write(gson.toJson(stats));
            return;
        }
        
        if ("_clear".equals(queryParam)) {
            queryCache.clear();
            cacheHits = 0;
            totalRequests = 0;
            JsonObject result = new JsonObject();
            result.addProperty("status", "Cache cleared");
            response.getWriter().write(gson.toJson(result));
            return;
        }
        
        // Default response for GET without special params
        JsonObject error = new JsonObject();
        error.addProperty("error", "Use POST method to query the RAG system");
        response.getWriter().write(gson.toJson(error));
    }

    @Override
    protected void doPost(SlingHttpServletRequest request, SlingHttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        
        // Check if services are available
        if (ragIndexService == null || openAIService == null) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "RAG services not available. Please check bundle status.");
            error.addProperty("ragIndexService", ragIndexService != null ? "available" : "missing");
            error.addProperty("openAIService", openAIService != null ? "available" : "missing");
            response.setStatus(503);
            response.getWriter().write(gson.toJson(error));
            return;
        }
        
        totalRequests++;

        try {
            // Read JSON body from request
            String body = request.getReader().lines().collect(Collectors.joining(System.lineSeparator()));
            LOG.info("Received RAG query request: {}", body);

            // Parse the incoming JSON (using Gson 2.8.5 compatible API)
            JsonParser parser = new JsonParser();
            JsonObject json = parser.parse(body).getAsJsonObject();
            String query = json.has("query") ? json.get("query").getAsString() : "";

            if (query.isEmpty()) {
                JsonObject error = new JsonObject();
                error.addProperty("error", "Query parameter is required");
                error.addProperty("query", "");
                error.addProperty("answer", "");
                error.addProperty("cached", false);
                response.setStatus(400);
                response.getWriter().write(gson.toJson(error));
                return;
            }

            // Check cache
            if (queryCache.containsKey(query)) {
                cacheHits++;
                CachedResponse cached = queryCache.get(query);
                JsonObject result = new JsonObject();
                result.addProperty("query", query);
                result.addProperty("answer", cached.answer);
                result.addProperty("cached", true);
                result.add("sources", gson.toJsonTree(cached.sources));
                response.getWriter().write(gson.toJson(result));
                LOG.info("Returned cached response for query");
                return;
            }

            // Retrieve relevant context from RAG index
            String contextJson = ragIndexService.retrieveContext(query, DEFAULT_TOP_K);
            LOG.debug("Retrieved context: {}", contextJson);
            
            // Build prompt with context
            String prompt = buildPrompt(query, contextJson);
            
            // Get completion from OpenAI
            String answer = openAIService.complete(prompt, "gpt-3.5-turbo");
            
            // Extract sources from context
            JsonParser contextParser = new JsonParser();
            JsonObject contextObj = contextParser.parse(contextJson).getAsJsonObject();
            JsonArray sources = contextObj.has("entries") ? contextObj.getAsJsonArray("entries") : new JsonArray();
            
            // Cache the response
            if (queryCache.size() < MAX_CACHE_SIZE) {
                queryCache.put(query, new CachedResponse(answer, sources));
            }
            
            // Return response
            JsonObject result = new JsonObject();
            result.addProperty("query", query);
            result.addProperty("answer", answer);
            result.addProperty("cached", false);
            result.add("sources", sources);
            
            response.getWriter().write(gson.toJson(result));
            LOG.info("Successfully processed RAG query");

        } catch (Exception e) {
            LOG.error("Error processing RAG query", e);
            JsonObject error = new JsonObject();
            error.addProperty("error", "Failed to process query: " + e.getMessage());
            error.addProperty("query", "");
            error.addProperty("answer", "");
            error.addProperty("cached", false);
            response.setStatus(500);
            response.getWriter().write(gson.toJson(error));
        }
    }
    
    private String buildPrompt(String question, String contextJson) {
        JsonParser promptParser = new JsonParser();
        JsonObject context = promptParser.parse(contextJson).getAsJsonObject();
        JsonArray entries = context.has("entries") ? context.getAsJsonArray("entries") : new JsonArray();
        
        StringBuilder contextText = new StringBuilder();
        for (int i = 0; i < entries.size(); i++) {
            JsonObject entry = entries.get(i).getAsJsonObject();
            if (entry.has("content")) {
                contextText.append(entry.get("content").getAsString()).append("\n\n");
            }
        }
        
        return "You are a helpful assistant answering questions about AEM (Adobe Experience Manager). " +
               "Use the following context to answer the question. If the answer is not in the context, " +
               "say so politely.\n\nContext:\n" + contextText.toString() + 
               "\n\nQuestion: " + question + "\n\nAnswer:";
    }
    
    private static class CachedResponse {
        String answer;
        JsonArray sources;
        
        CachedResponse(String answer, JsonArray sources) {
            this.answer = answer;
            this.sources = sources;
        }
    }
}
