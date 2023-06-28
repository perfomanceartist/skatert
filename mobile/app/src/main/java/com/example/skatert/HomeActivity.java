package com.example.skatert;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

import com.android.volley.DefaultRetryPolicy;
import com.android.volley.NetworkResponse;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.skatert.utility.SiteMap;

import org.json.JSONArray;
import org.json.JSONObject;

public class HomeActivity extends AppCompatActivity {
    private DrawerLayout drawerLayout;
    RequestQueue volleyQueue = null;

    TextView toolbar = null;

    SharedPreferences sharedPref = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.home_activity);

        drawerLayout = findViewById(R.id.drawer_layout);

        ImageButton imageButton = findViewById(R.id.button);
        imageButton.setOnClickListener(v -> drawerLayout.openDrawer(GravityCompat.START));

        Button refreshButton = findViewById(R.id.homeRefreshButton);
        refreshButton.setOnClickListener(v -> reload());

        Button lastFmIntegrateButton = findViewById(R.id.homeLastFmButton);
        lastFmIntegrateButton.setOnClickListener(v -> makeLastFmIntegration());

        Button listSubscriptionsButton = findViewById(R.id.homeGetSubscriptionsButton);
        listSubscriptionsButton.setOnClickListener(v ->
                startActivity(new Intent(HomeActivity.this, SubscriptionsActivity.class)));

        Button listRecommendationsButton = findViewById(R.id.homeGetRecommendationsButton);
        listRecommendationsButton.setOnClickListener(v ->
                startActivity(new Intent(HomeActivity.this, RecommendationsActivity.class)));

        Button logOutButton = findViewById(R.id.homeLogOutButton);
        logOutButton.setOnClickListener(v -> logout());

        toolbar = findViewById(R.id.homeActivityToolbar);

        sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);

        volleyQueue = Volley.newRequestQueue(this);
        reload();
    }

    private void makeLastFmIntegration() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        LayoutInflater inflater = getLayoutInflater();

        View view = inflater.inflate(R.layout.lastfm_integration, null);
        EditText codeEditText = view.findViewById(R.id.lastfm_edit_text_code);

        builder.setView(view).setPositiveButton("OK", (dialog, id) -> {
            try {
                final String lastFmNickname = codeEditText.getText().toString();
                if(lastFmNickname.isEmpty())
                    throw new IllegalArgumentException("Please enter your LastFM nickname");

                JSONObject data = new JSONObject();
                try {
                    data.put("nickname", getSharedPreferences(
                            getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE)
                            .getString(getString(R.string.SharedPreferencesNickname), ""));
                    data.put("lastFmNickname", lastFmNickname);
                } catch (org.json.JSONException ignored) {}

                JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, SiteMap.lastFmIntegration, data,
                    response -> {
                        reload();
                        Toast.makeText(getApplicationContext(), "Integration completed", Toast.LENGTH_SHORT).show();
                    },
                    error -> {
                        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                        switch(sharedPref.getInt(getString(R.string.SharedPreferencesLastStatusCode), -1)) {
                            case 403:
                                startActivity(new Intent(HomeActivity.this, StartActivity.class));
                            case 503:
                                Toast.makeText(getApplicationContext(), "Service Unavailable", Toast.LENGTH_SHORT).show(); break;
                            default:
                                Toast.makeText(getApplicationContext(), "LastFM integration failed", Toast.LENGTH_SHORT).show();
                        }
                    }
                ) {
                    @Override
                    protected Response<JSONObject> parseNetworkResponse(NetworkResponse response) {
                        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                        sharedPref.edit().putInt(getString(R.string.SharedPreferencesLastStatusCode), response.statusCode).apply();
                        return super.parseNetworkResponse(response);
                    }
                };
                jsonObjectRequest.setRetryPolicy(new DefaultRetryPolicy(0, DefaultRetryPolicy.DEFAULT_MAX_RETRIES, DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));
                volleyQueue.add(jsonObjectRequest);

            } catch (IllegalArgumentException iae) {
                Toast.makeText(getApplicationContext(), iae.getMessage(), Toast.LENGTH_SHORT).show();
            }
            catch (Exception re) {
                Log.println(Log.ERROR, "Authorization", re.toString());
            }
            dialog.dismiss();
        })
        .setNegativeButton("Cancel", (dialog, id) -> dialog.cancel());

        AlertDialog dialog = builder.create();
        dialog.show();
    }

    private void reload() {
        final String path = SiteMap.getUserFavouriteTracks +"/?nickname=" + sharedPref.getString(getString(R.string.SharedPreferencesNickname), "");

        JsonArrayRequest jsonArrayRequest = new JsonArrayRequest(Request.Method.GET, path, null,
                response -> {
                    favouriteTracksDescriptionList = new Track[response.length()];
                    for (int i = 0; i < response.length(); ++i) {
                        try {
                            JSONObject track = response.getJSONObject(i);
                            favouriteTracksDescriptionList[i] = new Track(true);
                            if(track.has("name"))
                                favouriteTracksDescriptionList[i].name = track.getString("name");
                            if(track.has("artist"))
                                favouriteTracksDescriptionList[i].artist = track.getString("artist");
                            if(track.has("album"))
                                favouriteTracksDescriptionList[i].album = track.getString("album");
                        } catch (Exception t) {
                            Toast.makeText(getApplicationContext(), t.getMessage(), Toast.LENGTH_SHORT).show();
                        }
                    }
                    rewrite();
                    toolbar.setText(getString(R.string.HomeActivityToolbarPattern, response.length()));
                },
                error -> {
                    if(!(error instanceof com.android.volley.AuthFailureError)) {
                        switch (sharedPref.getInt(getString(R.string.SharedPreferencesLastStatusCode), -1)) {
                            case 403:
                                startActivity(new Intent(HomeActivity.this, StartActivity.class));
                            case 503:
                                Toast.makeText(getApplicationContext(), "Service Unavailable", Toast.LENGTH_SHORT).show();
                                break;
                            default:
                                Toast.makeText(getApplicationContext(), "Data loading failed", Toast.LENGTH_SHORT).show();
                        }
                    } else logout();
                }
        ) {
            @Override
            protected Response<JSONArray> parseNetworkResponse(NetworkResponse response) {
                SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                sharedPref.edit().putInt(getString(R.string.SharedPreferencesLastStatusCode), response.statusCode).apply();
                return super.parseNetworkResponse(response);
            }
        };
        volleyQueue.add(jsonArrayRequest);
    }

    private void rewrite() {
        ListView favouriteTracksListView = findViewById(R.id.favouriteTracks);
        favouriteTracksListView.setAdapter(new AdapterElements(this));
    }

    private void logout() {
        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.remove(getString(R.string.SharedPreferencesNickname)).apply();
        startActivity(new Intent(HomeActivity.this, StartActivity.class));
    }

    private void likeTrack(String nickname, int trackPosition) {
        JSONObject data = new JSONObject();
        try {
            data.put("nickname", nickname);
            data.put("song_name", favouriteTracksDescriptionList[trackPosition].name);
            data.put("song_artist", favouriteTracksDescriptionList[trackPosition].artist);
        } catch (org.json.JSONException ignored) {}

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, SiteMap.likeTrack, data,
                response -> {
                    favouriteTracksDescriptionList[trackPosition].liked = true;
                    rewrite();
                    Toast.makeText(getApplicationContext(), "Track disliked", Toast.LENGTH_SHORT).show();
                },
                error -> {
                    SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                    switch(sharedPref.getInt(getString(R.string.SharedPreferencesLastStatusCode), -1)) {
                        case 403:
                            startActivity(new Intent(HomeActivity.this, StartActivity.class));
                        case 503:
                            Toast.makeText(getApplicationContext(), "Service Unavailable", Toast.LENGTH_SHORT).show(); break;
                        default:
                            Toast.makeText(getApplicationContext(), "Operation failed", Toast.LENGTH_SHORT).show();
                    }
                }
        ) {
            @Override
            protected Response<JSONObject> parseNetworkResponse(NetworkResponse response) {
                SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                sharedPref.edit().putInt(getString(R.string.SharedPreferencesLastStatusCode), response.statusCode).apply();

                if (response.statusCode == 200 && response.data.length == 0)
                    response = new NetworkResponse(response.statusCode, new JSONObject().toString().getBytes(), response.headers, response.notModified);
                return super.parseNetworkResponse(response);
            }
        };
        volleyQueue.add(jsonObjectRequest);
    }

    private void dislikeTrack(String nickname, int trackPosition) {
        JSONObject data = new JSONObject();
        try {
            data.put("nickname", nickname);
            data.put("song_name", favouriteTracksDescriptionList[trackPosition].name);
            data.put("song_artist", favouriteTracksDescriptionList[trackPosition].artist);
        } catch (org.json.JSONException ignored) {}

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, SiteMap.dislikeTrack, data,
                response -> {
                    favouriteTracksDescriptionList[trackPosition].liked = false;
                    rewrite();
                    Toast.makeText(getApplicationContext(), "Track disliked", Toast.LENGTH_SHORT).show();
                },
                error -> {
                    SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                    switch(sharedPref.getInt(getString(R.string.SharedPreferencesLastStatusCode), -1)) {
                        case 403:
                            startActivity(new Intent(HomeActivity.this, StartActivity.class));
                        case 503:
                            Toast.makeText(getApplicationContext(), "Service Unavailable", Toast.LENGTH_SHORT).show(); break;
                        default:
                            Toast.makeText(getApplicationContext(), "Operation failed", Toast.LENGTH_SHORT).show();
                    }
                }
        ) {
            @Override
            protected Response<JSONObject> parseNetworkResponse(NetworkResponse response) {
                SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                sharedPref.edit().putInt(getString(R.string.SharedPreferencesLastStatusCode), response.statusCode).apply();

                if (response.statusCode == 200 && response.data.length == 0)
                    response = new NetworkResponse(response.statusCode, new JSONObject().toString().getBytes(), response.headers, response.notModified);
                return super.parseNetworkResponse(response);
            }
        };
        volleyQueue.add(jsonObjectRequest);
    }

    Track[] favouriteTracksDescriptionList;
    class AdapterElements extends ArrayAdapter<Object> {
        Activity context;

        public AdapterElements(Activity context) {
            super(context, R.layout.track_list_item, favouriteTracksDescriptionList);
            this.context = context;
        }

        public View getView(int position, View convertView, ViewGroup parent) {
            LayoutInflater inflater = context.getLayoutInflater();

            @SuppressLint({"ViewHolder", "InflateParams"})
            View item = inflater.inflate(R.layout.track_list_item, null);

            TextView trackName = item.findViewById(R.id.song_title);
            trackName.setText(favouriteTracksDescriptionList[position].name);

            TextView artist = item.findViewById(R.id.artist_name);
            artist.setText(favouriteTracksDescriptionList[position].artist);

            TextView album = item.findViewById(R.id.album_name);
            album.setText(favouriteTracksDescriptionList[position].album);

            ImageButton likeDislikeButton = item.findViewById(R.id.likeDislikeButton);
            if(favouriteTracksDescriptionList[position].liked)
                likeDislikeButton.setImageResource(R.drawable.heart);
            else likeDislikeButton.setImageResource(R.drawable.heart_off);
            likeDislikeButton.setOnClickListener(v -> {
                if(favouriteTracksDescriptionList[position].liked)
                    dislikeTrack(sharedPref.getString(getString(R.string.SharedPreferencesNickname), ""), position);
                else likeTrack(sharedPref.getString(getString(R.string.SharedPreferencesNickname), ""), position);
            });
            return item;
        }
    }
}
