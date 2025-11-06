package com.example.aem.rag.services;

public interface OpenAIService {
    String complete(String prompt, String model);
}
