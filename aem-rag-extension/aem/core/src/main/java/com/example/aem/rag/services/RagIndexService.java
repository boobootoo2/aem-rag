package com.example.aem.rag.services;

public interface RagIndexService {
    void rebuildIndex();
    String retrieveContext(String question, int k);
}
