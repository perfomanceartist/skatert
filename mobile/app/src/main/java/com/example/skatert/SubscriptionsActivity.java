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

import com.android.volley.Header;
import com.android.volley.NetworkResponse;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.skatert.utility.SiteMap;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class SubscriptionsActivity extends AppCompatActivity {
    ImageButton closeSubscriptionsButton;
    RequestQueue volleyQueue = null;

    private ListView subscriptionList;

    String[] subscriptionNicknames;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.subscriptions_list);

        closeSubscriptionsButton = findViewById(R.id.closeSubscriptionsButton);
        closeSubscriptionsButton.setOnClickListener(v -> startActivity(new Intent(SubscriptionsActivity.this, HomeActivity.class)));

        volleyQueue = Volley.newRequestQueue(this);
        refresh();
    }

    SharedPreferences sharedPref;
    void refresh() {
        sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
        final String path = SiteMap.getSubscriptions + "?nickname=" + sharedPref.getString(getString(R.string.SharedPreferencesNickname), "");

        JsonArrayRequest jsonObjectRequest = new JsonArrayRequest(Request.Method.GET, path, null,
                response -> {
                    try {
                        subscriptionNicknames = new String[response.length()];
                        for (int i = 0; i < response.length(); ++i)
                            subscriptionNicknames[i] = response.getString(i);

                        subscriptionList = findViewById(R.id.subscriptionsList);
                        SubscriptionsActivity.SubscriptionsAdapter adapter = new SubscriptionsActivity.SubscriptionsAdapter(this);
                        subscriptionList.setAdapter(adapter);
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

    private void changeSubscription(String toUser, boolean makeSubscribed) {
        JSONObject data = new JSONObject();
        try {
            data.put("target_nickname", toUser);
            data.put("subscribed", makeSubscribed);
        } catch (JSONException ignored) {}

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, SiteMap.subscribe, data,
                response -> refresh(),
                error -> {
                    switch(sharedPref.getInt(getString(R.string.SharedPreferencesLastStatusCode), -1)) {
                        case 403:
                            startActivity(new Intent(SubscriptionsActivity.this, StartActivity.class));
                        case 404:
                            Toast.makeText(getApplicationContext(), "User is not found", Toast.LENGTH_SHORT).show(); break;
                        case 503:
                            Toast.makeText(getApplicationContext(), "Service Unavailable", Toast.LENGTH_SHORT).show(); break;
                        default:
                            Toast.makeText(getApplicationContext(), "Failed", Toast.LENGTH_SHORT).show(); break;
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

    class SubscriptionsAdapter extends ArrayAdapter<Object> {
        Activity context;

        public SubscriptionsAdapter(Activity context) {
            super(context, R.layout.subscription, subscriptionNicknames);
            this.context = context;
        }

        public View getView(int position, View convertView, ViewGroup parent) {
            LayoutInflater inflater = context.getLayoutInflater();

            @SuppressLint({"ViewHolder", "InflateParams"})
            View item = inflater.inflate(R.layout.subscription, null);

            TextView tv = item.findViewById(R.id.textView);
            tv.setText(subscriptionNicknames[position]);

            Button bt = item.findViewById(R.id.unsubscribeButton);
            bt.setOnClickListener(v -> {
                changeSubscription(tv.getText().toString(), false);
                Toast.makeText(getApplicationContext(), "Unsubscribed from '" + tv.getText(), Toast.LENGTH_SHORT).show();
            });

            return item;
        }
    }
}
