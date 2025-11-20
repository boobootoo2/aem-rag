package com.example.aem.rag.services;

import java.util.List;

public interface OpenAIService {
    String complete(String prompt, String model);
    List<Double> embed(String input, String model);
}
