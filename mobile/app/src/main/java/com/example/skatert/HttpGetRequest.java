package com.example.skatert;

import android.os.AsyncTask;

import java.io.DataOutputStream;
import java.io.InputStream;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.ConnectException;
import java.net.HttpURLConnection;

public class HttpGetRequest extends Thread {

    public
    private static final int attempts = 20;

    URL url = null;
    String response = null;
    private OnTaskCompleted listener;

    public HttpGetRequest(URL uri, OnTaskCompleted listener) {
        this.url = uri;
        this.listener = listener;
    }

    public void run() {
        for(int i = 0; i < attempts; ++i) {
            try {
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("GET");
                connection.setRequestProperty("Content-Type", "application/json");

                int responseCode = connection.getResponseCode();
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                    String inputLine;
                    StringBuilder response = new StringBuilder();
                    while ((inputLine = in.readLine()) != null)
                        response.append(inputLine);
                    in.close();
                    this.response = response.toString();
                } else {
                    connection.disconnect();
                    throw new RuntimeException("Response code is not OK.");
                }
            } catch (Exception error) {
                System.out.println("Warning: " + error);
            }
        }
        throw new RuntimeException("Connection to server failed.");
    }
}



