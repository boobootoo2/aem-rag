package com.example.aem.rag.services.impl;

import com.example.aem.rag.services.RagIndexService;
import com.example.aem.rag.services.RagEntry;
import com.example.aem.rag.services.OpenAIService;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Reference;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component(service = RagIndexService.class)
public class RagIndexServiceImpl implements RagIndexService {

    @Reference
    private OpenAIService openAIService;
    private static final String EMBED_MODEL = "text-embedding-ada-002";

    private Gson gson = new Gson();
    private List<RagEntry> entries = new ArrayList<>();

    @Activate
    public void activate() {
        InputStream is = getClass().getClassLoader().getResourceAsStream("aem_rag_index.json");
        Type listType = new TypeToken<List<RagEntry>>(){}.getType();
        entries = gson.fromJson(new InputStreamReader(is), listType);
    }

    @Override
    public void rebuildIndex() {
        System.out.println("[RAG] rebuildIndex invoked");
    }

    @Override
    public String retrieveContext(String question, int k) {
        List<Double> questionEmbed = openAIService.embed(question, EMBED_MODEL);
        Map<RagEntry, Double> simMap = new HashMap<>();
        for (RagEntry entry : entries) {
            double sim = cosineSimilarity(questionEmbed, entry.getVector());
            simMap.put(entry, sim);
        }
        List<Map.Entry<RagEntry, Double>> sorted = new ArrayList<>(simMap.entrySet());
        sorted.sort((a, b) -> Double.compare(b.getValue(), a.getValue()));
        List<RagEntry> top = new ArrayList<>();
        for (int i = 0; i < Math.min(k, sorted.size()); i++) {
            top.add(sorted.get(i).getKey());
        }
        Map<String, Object> result = new HashMap<>();
        result.put("question", question);
        result.put("entries", top);
        return gson.toJson(result);
    }

    private double cosineSimilarity(List<Double> v1, List<Double> v2) {
        double dot = 0.0, normA = 0.0, normB = 0.0;
        for (int i = 0; i < v1.size(); i++) {
            dot += v1.get(i) * v2.get(i);
            normA += v1.get(i) * v1.get(i);
            normB += v2.get(i) * v2.get(i);
        }
        return dot / (Math.sqrt(normA) * Math.sqrt(normB));
    }
}
