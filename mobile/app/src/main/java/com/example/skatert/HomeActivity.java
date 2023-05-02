package com.example.skatert;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Type;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Collections;
import java.util.List;

public class HomeActivity extends AppCompatActivity implements OnTaskCompleted {
    Track[] trackList;

    Button getRecommendations, refresh;

    ListView listView;

    String host = "http://127.0.0.1:8000/";
    String getFavouriteTracksUrl = host + "music/getUserFavouriteTracks?nickname=";
    String getRecommendationsUrl = host + "music/getRecommendations?amount=10&nickname=";

    String nickname = "";

    public void onTaskCompleted(String result) {
        if(result != null) {
            Toast.makeText(getApplicationContext(), "Server data received.", Toast.LENGTH_SHORT).show();
            System.out.println("Server data: " + result);
            try {
                Gson gson = new Gson();
                Type songListType = new TypeToken<Track[]>() {
                }.getType();
                trackList = gson.fromJson(result, songListType);

                listView = findViewById(R.id.favouriteTracks);
                AdapterElements adapter = new AdapterElements(this);
                listView.setAdapter(adapter);
            } catch (Exception e) {
                Toast.makeText(getApplicationContext(), "Prepare view failed: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                System.out.println("Failed: " + e);
            }
        } else
            Toast.makeText(getApplicationContext(), "Connection with server failed.", Toast.LENGTH_SHORT).show();
    }

    void refresh() {
        new MyHttpGetTask(this).execute(getFavouriteTracksUrl + nickname);
    }

    void getRecommendations() {
        new MyHttpGetTask(this).execute(getRecommendationsUrl + nickname);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.home_activity);

        nickname = "thearcherfm";

        getRecommendations = findViewById(R.id.button1);
        getRecommendations.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) { getRecommendations(); }
        });

        refresh = findViewById(R.id.button2);
        refresh.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) { refresh(); }
        });

        refresh();
    }

    public class MyHttpGetTask extends AsyncTask<String, Void, String> {
        private OnTaskCompleted listener;

        public MyHttpGetTask(OnTaskCompleted listener) {
            this.listener = listener;
        }

        protected String doInBackground(String... urls) {
            System.out.println("Making get request on: " + urls[0]);
            int attempts = 20;
            for(int i = 0; i < attempts; ++i) {
                try {
                    URL url = new URL(urls[0]);
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("GET");
                    connection.setRequestProperty("Content-Type", "application/json");
                    connection.setConnectTimeout(5000);
                    connection.setReadTimeout(5000);

                    int responseCode = connection.getResponseCode();
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                        String inputLine;
                        StringBuilder response = new StringBuilder();
                        while ((inputLine = in.readLine()) != null)
                            response.append(inputLine);
                        in.close();
                        return response.toString();
                    } else {
                        connection.disconnect();
                        throw new RuntimeException("Response code is not OK.");
                    }
                } catch (Exception error) {
                    System.out.println("Warning: " + error);
                }
            }
            return null;
        }

        protected void onPostExecute(String result) {
            listener.onTaskCompleted(result);
        }
    }

    class AdapterElements extends ArrayAdapter<Object> {
        Activity context;

        public AdapterElements(Activity context) {
            super(context, R.layout.track, trackList);
            this.context = context;
        }

        public View getView(int position, View convertView, ViewGroup parent) {
            LayoutInflater inflater = context.getLayoutInflater();
            @SuppressLint({"ViewHolder", "InflateParams"}) View item = inflater.inflate(R.layout.track, null);

            TextView trackName = item.findViewById(R.id.song_title);
            trackName.setText(trackList[position].getName());

            TextView artist = item.findViewById(R.id.artist_name);
            artist.setText(trackList[position].getArtist());

            TextView album = item.findViewById(R.id.album_name);
            album.setText(trackList[position].getAlbum());

            return item;
        }
    }
}