package com.example.aem.rag.servlets;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.apache.sling.api.SlingHttpServletRequest;
import org.apache.sling.api.SlingHttpServletResponse;
import org.apache.sling.api.servlets.SlingAllMethodsServlet;
import org.osgi.service.component.annotations.Component;

import javax.servlet.Servlet;
import javax.servlet.ServletException;
import java.io.IOException;
import java.util.stream.Collectors;

@Component(
    service = {Servlet.class},
    property = {
        "sling.servlet.methods=POST",
        "sling.servlet.paths=/bin/ragquery"
    }
)
public class RagQueryServlet extends SlingAllMethodsServlet {

    @Override
    protected void doPost(SlingHttpServletRequest request, SlingHttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("application/json");

        // Read JSON body
        String body = request.getReader().lines().collect(Collectors.joining(System.lineSeparator()));

        // Parse the incoming JSON
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();
        String query = json.has("query") ? json.get("query").getAsString() : "No query provided";

        // Example: create response
        JsonObject result = new JsonObject();
        result.addProperty("response", "Received: " + query);

        // Write JSON output
        response.getWriter().write(result.toString());
    }
}
