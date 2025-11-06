package com.example.aem.rag.servlets;

import com.example.aem.rag.services.RagIndexService;
import com.example.aem.rag.services.OpenAIService;
import org.apache.sling.api.servlets.SlingAllMethodsServlet;
import org.apache.sling.api.SlingHttpServletRequest;
import org.apache.sling.api.SlingHttpServletResponse;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Reference;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

@Component(service = javax.servlet.Servlet.class,
    property = {
        "sling.servlet.paths=/bin/ragquery",
        "sling.servlet.methods=POST"
    })
public class RagQueryServlet extends SlingAllMethodsServlet {

    @Reference
    private RagIndexService indexService;

    @Reference
    private OpenAIService openAI;

    @Override
    protected void doPost(SlingHttpServletRequest request, SlingHttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String question = request.getParameter("question");
        if (question == null || question.trim().isEmpty()) {
            question = new String(request.getRequestBodyAsBytes(), StandardCharsets.UTF_8);
        }

        String context = indexService.retrieveContext(question, 8);
        String prompt = "Context:\n" + context + "\n\nQuestion:\n" + question;

        String answer = openAI.complete(prompt, "gpt-4o-mini");
        response.getWriter().write("{\"answer\":" + toJson(answer) + "}");
    }

    private String toJson(String s) {
        if (s == null) return "null";
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\"";
    }
}
