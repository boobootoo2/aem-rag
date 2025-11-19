package com.example.aem.rag.services;

import java.util.List;

/**
 * A simple POJO representing a RAG index entry.
 */
public class RagEntry {
    private String id;
    private String source;
    private String content;
    private List<Double> vector;

    public RagEntry() {
        // Default constructor for JSON deserialization
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public List<Double> getVector() {
        return vector;
    }

    public void setVector(List<Double> vector) {
        this.vector = vector;
    }
}