package com.example.skatert;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.Header;
import com.android.volley.NetworkResponse;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.Volley;
import com.example.skatert.utility.SiteMap;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class SubscriptionsActivity extends AppCompatActivity {
    ImageButton closeSubscriptionsButton;
    RequestQueue volleyQueue = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.subscriptions_list);

        closeSubscriptionsButton = findViewById(R.id.closeSubscriptionsButton);
        closeSubscriptionsButton.setOnClickListener(v -> startActivity(new Intent(SubscriptionsActivity.this, HomeActivity.class)));

        volleyQueue = Volley.newRequestQueue(this);

        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
        final String path = SiteMap.getSubscriptions + "?nickname=" + sharedPref.getString(getString(R.string.SharedPreferencesNickname), "");

        JsonArrayRequest jsonObjectRequest = new JsonArrayRequest(Request.Method.GET, path, null,
                response -> {
                    try {
                        List<String> subscriptions = new ArrayList<>(response.length());
                        for (int i = 0; i < response.length(); ++i)
                            subscriptions.add(response.getString(i));
                    } catch (org.json.JSONException ignored) {
                        Toast.makeText(getApplicationContext(), "Sorry", Toast.LENGTH_SHORT).show();
                    }
                },
                error -> {
                    switch(sharedPref.getInt(getString(R.string.SharedPreferencesLastStatusCode), -1)) {
                        case 403:
                            startActivity(new Intent(SubscriptionsActivity.this, StartActivity.class));
                        case 503:
                            Toast.makeText(getApplicationContext(), "Service Unavailable", Toast.LENGTH_SHORT).show(); break;
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
}
