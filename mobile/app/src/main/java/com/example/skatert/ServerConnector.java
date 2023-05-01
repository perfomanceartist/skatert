package com.example.skatert;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.Type;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;
import java.util.LinkedList;
import java.util.Map;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

public class ServerConnector {
    private static final String serverHostAddress = "http://10.0.0.2:8000/music/";
    private static String output = null;

    public interface OnTaskCompleted {
        void onTaskCompleted(String result);
    }

    private static class HttpThread extends Thread {
        private final OnTaskCompleted mListener;
        private static final int attempts = 20;
        private URL url = null;

        public HttpThread(URL url, OnTaskCompleted listener) {
            mListener = listener;
            this.url = url;
        }

        @Override
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
                        mListener.onTaskCompleted(response.toString());
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

    private static String makeGetRequest(URL url) throws InterruptedException {
        new HttpThread(url, new OnTaskCompleted() {
            @Override
            public void onTaskCompleted(String result) {
//                output = result;
                System.out.println(result);
            }
        }).start();
        return "";
    }

    private String makePostRequest(URL url, String data) {
        return "";
    }

    public static User makeLastFmIntegration(String nickname, String lastFmNickname) {
        try {
            String data = "{ \"nickname\": " + nickname + ", \"lastFmNickname\": " + lastFmNickname + " }";
            URL url = new URL(serverHostAddress + "lastFM-integration/");
            Gson gson = new Gson();
            return gson.fromJson(HttpPostRequest.make(url, data), User.class);
        } catch (Exception e) {
            throw new RuntimeException("Failed to make the lastFm integration.");
        }
    }

    public static List<String> getFavouriteGenres(String nickname) {
        try {
            URL url = new URL(serverHostAddress + "getFavouriteGenres?nickname=" + nickname + "/");

            Gson gson = new Gson();
            Genres genres = gson.fromJson(makeGetRequest(url), Genres.class);

            LinkedList<String> result = new LinkedList<>();

            if(genres.hipHop) result.add("Hip Hop");
            if(genres.rock) result.add("Rock");
            if(genres.rap) result.add("Rap");
            if(genres.pop) result.add("Pop");
            if(genres.alternative) result.add("Alternative");
            if(genres.classic) result.add("Classic");
            if(genres.edm) result.add("EDM");

            return result;
        } catch (Exception e) {
            throw new RuntimeException("Failed to get user's favourite genres.");
        }
    }

    public static User setFavouriteGenres(String nickname, Map<String, Boolean> values) {
        try {
            String data = "";
            URL url = new URL(serverHostAddress + "setFavouriteGenres/");
            Gson gson = new Gson();
            return gson.fromJson(HttpPostRequest.make(url, data), User.class);
        } catch (Exception e) {
            throw new RuntimeException("Failed to change user's favourite genres.");
        }
    }

    public static Track[] getFavouriteTracks(String nickname) {
        try {
            String query = "getUserFavouriteTracks?nickname=" + nickname;
            URL url = new URL(serverHostAddress + query);

            Gson gson = new Gson();
            Type songListType = new TypeToken<Track[]>() {}.getType();
            return gson.fromJson(makeGetRequest(url), songListType);
        } catch (Exception e) {
            throw new RuntimeException("Failed to receive favourite genres: " + e.getMessage());
        }
    }

    public static List<User> getUsers() {
        try {
            URL url = new URL(serverHostAddress + "getUsers/");
            Gson gson = new Gson();
            Type userListType = new TypeToken<List<User>>(){}.getType();
            return gson.fromJson(makeGetRequest(url), userListType);
        } catch (Exception e) {
            throw new RuntimeException("Failed to change user's favourite genres.");
        }
    }

    public static Track[] getRecommendations(String nickname, int amount) {
        try {
            String query = "getRecommendations?nickname=" + nickname +
                    "&amount=" + String.valueOf(amount);
            URL url = new URL(serverHostAddress + query);

            Gson gson = new Gson();
            Type songListType = new TypeToken<Track[]>() {}.getType();
            return gson.fromJson(makeGetRequest(url), songListType);
        } catch (Exception e) {
            throw new RuntimeException("Failed to receive favourite genres: " + e.getMessage());
        }
    }
}
