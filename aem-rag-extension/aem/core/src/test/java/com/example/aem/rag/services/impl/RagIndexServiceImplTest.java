package com.example.aem.rag.services.impl;

import com.example.aem.rag.services.OpenAIService;
import com.example.aem.rag.services.RagEntry;
import com.example.aem.rag.services.impl.RagIndexServiceImpl;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonArray;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class RagIndexServiceImplTest {
    private static RagIndexServiceImpl service;
    private static Gson gson = new Gson();

    @BeforeAll
    static void setup() throws Exception {
        service = new RagIndexServiceImpl();
        // stub OpenAIService for embeddings
        OpenAIService stubAI = new OpenAIService() {
            @Override
            public String complete(String prompt, String model) { return null; }
            @Override
            public List<Double> embed(String input, String model) {
                // simple 2-d vector stub
                return Arrays.asList(1.0, 0.0);
            }
        };
        // inject stubAI
        Field aiField = RagIndexServiceImpl.class.getDeclaredField("openAIService");
        aiField.setAccessible(true);
        aiField.set(service, stubAI);
        // inject stub entries
        Field entriesField = RagIndexServiceImpl.class.getDeclaredField("entries");
        entriesField.setAccessible(true);
        RagEntry e1 = new RagEntry(); e1.setId("1"); e1.setContent("A"); e1.setVector(Arrays.asList(1.0, 0.0));
        RagEntry e2 = new RagEntry(); e2.setId("2"); e2.setContent("B"); e2.setVector(Arrays.asList(0.0, 1.0));
        entriesField.set(service, Arrays.asList(e1, e2));
    }

    @Test
    void testRetrieveContext() {
        String resultJson = service.retrieveContext("test", 2);
        JsonObject obj = gson.fromJson(resultJson, JsonObject.class);
        assertEquals("test", obj.get("question").getAsString());
        JsonArray arr = obj.getAsJsonArray("entries");
        assertEquals(2, arr.size());
        assertEquals("1", arr.get(0).getAsJsonObject().get("id").getAsString());
        assertEquals("2", arr.get(1).getAsJsonObject().get("id").getAsString());
    }
}
