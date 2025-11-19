package com.example.aem.rag.services.impl;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class RagIndexServiceImplTest {

    private static RagIndexServiceImpl service;

    @BeforeAll
    static void setup() {
        service = new RagIndexServiceImpl();
    }

    @Test
    void testRetrieveContextStub() {
        String question = hello
