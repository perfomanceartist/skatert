package com.example.skatert;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.NetworkResponse;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.Volley;
import com.example.skatert.utility.SiteMap;

import org.json.JSONArray;
import org.json.JSONObject;

public class RecommendationsActivity extends AppCompatActivity {
    RequestQueue volleyQueue = null;

    TextView toolbar = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.recommendations);

        ImageButton closeRecommendations = findViewById(R.id.closeRecommendationsButton);
        closeRecommendations.setOnClickListener(v -> startActivity(new Intent(RecommendationsActivity.this, HomeActivity.class)));

        Button updateButton = findViewById(R.id.updateButton);
        updateButton.setOnClickListener(v -> update());

        volleyQueue = Volley.newRequestQueue(this);
        update();
    }

    Track[] trackDescriptionList;

    void update() {
        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);

        final String path = SiteMap.getRecommendations + "?amount=15";
        JsonArrayRequest jsonObjectRequest = new JsonArrayRequest(Request.Method.GET, path, null,
                response -> {
                    trackDescriptionList = new Track[response.length()];
                    for (int i = 0; i < response.length(); ++i) {
                        try {
                            JSONObject track = response.getJSONObject(i);
                            trackDescriptionList[i] = new Track();
                            if(track.has("name"))
                                trackDescriptionList[i].name = track.getString("name");
                            if(track.has("artist"))
                                trackDescriptionList[i].artist = track.getString("artist");
                            if(track.has("album"))
                                trackDescriptionList[i].album = track.getString("album");
                        } catch (Exception t) {
                            Toast.makeText(getApplicationContext(), t.getMessage(), Toast.LENGTH_SHORT).show();
                        }
                    }
                    ListView recommendationsListView = findViewById(R.id.recommendationsTrackList);
                    RecommendationsAdapter adapter = new RecommendationsAdapter(this);
                    recommendationsListView.setAdapter(adapter);
                },
                error -> {
                    switch (sharedPref.getInt(getString(R.string.SharedPreferencesLastStatusCode), -1)) {
                        case 403:
                            startActivity(new Intent(RecommendationsActivity.this, StartActivity.class));
                        case 503:
                            Toast.makeText(getApplicationContext(), "Service Unavailable", Toast.LENGTH_SHORT).show();
                            break;
                        default:
                            Toast.makeText(getApplicationContext(), "Data loading failed", Toast.LENGTH_SHORT).show();
                    }
                }
        ) {
            @Override
            protected Response<JSONArray> parseNetworkResponse(NetworkResponse response) {
                SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                sharedPref.edit().putInt(getString(R.string.SharedPreferencesLastStatusCode), response.statusCode).apply();
                return super.parseNetworkResponse(response);
            }
        };
        volleyQueue.add(jsonObjectRequest);
    }

    class RecommendationsAdapter extends ArrayAdapter<Object> {
        Activity context;

        public RecommendationsAdapter(Activity context) {
            super(context, R.layout.track_list_item, trackDescriptionList);
            this.context = context;
        }

        public View getView(int position, View convertView, ViewGroup parent) {
            LayoutInflater inflater = context.getLayoutInflater();

            @SuppressLint({"ViewHolder", "InflateParams"})
            View item = inflater.inflate(R.layout.track_list_item, null);

            TextView trackName = item.findViewById(R.id.song_title);
            trackName.setText(trackDescriptionList[position].name);

            TextView artist = item.findViewById(R.id.artist_name);
            artist.setText(trackDescriptionList[position].artist);

            TextView album = item.findViewById(R.id.album_name);
            album.setText(trackDescriptionList[position].album);

            return item;
        }
    }
}
