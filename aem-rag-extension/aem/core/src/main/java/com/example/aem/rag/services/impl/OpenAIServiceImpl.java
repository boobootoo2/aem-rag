package com.example.aem.rag.services.impl;

import com.example.aem.rag.services.OpenAIService;
import org.osgi.service.component.annotations.Component;
import java.net.http.*;
import java.net.URI;

@Component(service = OpenAIService.class)
public class OpenAIServiceImpl implements OpenAIService {
    @Override
    public String complete(String prompt, String model) {
        // NOTE: For a production build, inject API key via OSGi config
        String apiKey = System.getenv("OPENAI_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return "OpenAI key not configured";
        }
        try {
            HttpClient client = HttpClient.newHttpClient();
            String body = "{ \"model\":\"" + model + "\", \"messages\":[{\"role\":\"system\",\"content\":\"You are an AEM assistant.\"},{\"role\":\"user\",\"content\":\"" + prompt.replace("\"","\\\"") + "\"}] }";
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
}
