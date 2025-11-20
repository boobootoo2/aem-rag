package com.example.aem.rag.services.impl;

import com.example.aem.rag.services.OpenAIService;
import org.osgi.service.component.annotations.Component;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;

@Component(service = OpenAIService.class)
public class OpenAIServiceImpl implements OpenAIService {
    private final Gson gson = new Gson();

    @Override
    public String complete(String prompt, String model) {
        String apiKey = System.getenv("OPENAI_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return "OpenAI key not configured";
        }
        try {
            HttpClient client = HttpClient.newHttpClient();
            String body = "{ \"model\": \"" + model + "\", \"messages\": [{\"role\":\"system\",\"content\":\"You are an AEM assistant.\"}, {\"role\":\"user\",\"content\":\"" + prompt.replace("\"","\\\"") + "\"}] }";
            HttpRequest req = HttpRequest.newBuilder()
                .uri(URI.create("https://api.openai.com/v1/chat/completions"))
                .header("Authorization", "Bearer " + apiKey)
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
            HttpResponse<String> resp = client.send(req, HttpResponse.BodyHandlers.ofString());
            return resp.body();
        } catch (Exception e) {
            return "Error calling OpenAI: " + e.getMessage();
        }
    }

    @Override
    public List<Double> embed(String input, String model) {
        String apiKey = System.getenv("OPENAI_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return Collections.emptyList();
        }
        try {
            HttpClient client = HttpClient.newHttpClient();
            String body = "{ \"model\": \"" + model + "\", \"input\": \"" + input.replace("\"","\\\"") + "\" }";
            HttpRequest req = HttpRequest.newBuilder()
                .uri(URI.create("https://api.openai.com/v1/embeddings"))
                .header("Authorization", "Bearer " + apiKey)
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
            HttpResponse<String> resp = client.send(req, HttpResponse.BodyHandlers.ofString());
            JsonObject json = gson.fromJson(resp.body(), JsonObject.class);
            JsonArray data = json.getAsJsonArray("data");
            if (data != null && data.size() > 0) {
                JsonArray embeddingArr = data.get(0).getAsJsonObject().getAsJsonArray("embedding");
                List<Double> vector = new ArrayList<>();
                for (JsonElement elem : embeddingArr) {
                    vector.add(elem.getAsDouble());
                }
                return vector;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return Collections.emptyList();
    }
}
