package com.example.skatert;


import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.skatert.utility.Hash;
import com.example.skatert.utility.SiteMap;

import org.json.JSONObject;

public class SignInActivity extends AppCompatActivity {
    EditText usernameEditText;
    EditText emailEditText;
    EditText passwordEditText;
    Button loginButton;

    RequestQueue volleyQueue = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.signup_activity);

        usernameEditText = findViewById(R.id.username_edit_text);
        emailEditText = findViewById(R.id.email_edit_text);
        passwordEditText = findViewById(R.id.password_edit_text);
        loginButton = findViewById(R.id.sign_up_button);
        volleyQueue = Volley.newRequestQueue(this);

        loginButton.setOnClickListener(v -> {
            try {
                final String nickname = String.valueOf(usernameEditText.getText());
                if(nickname.length() == 0)
                    throw new IllegalArgumentException("Please enter your username");

                final String email = String.valueOf(emailEditText.getText());
                if(email.length() == 0)
                    throw new IllegalArgumentException("Please enter your email");

                final String password = String.valueOf(passwordEditText.getText());
                if(password.length() == 0)
                    throw new IllegalArgumentException("Please enter your password");

                final JSONObject jsonData = prepareData(nickname, email, password);
                JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, SiteMap.registration, jsonData,
                        response -> {
                            SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                            SharedPreferences.Editor editor = sharedPref.edit();
                            editor.putString(getString(R.string.SharedPreferencesNickname), nickname);
                            editor.apply();

                            startActivity(new Intent(SignInActivity.this, HomeActivity.class));
                        },
                        error -> {
                            Toast.makeText(getApplicationContext(), "Authorization failed", Toast.LENGTH_SHORT).show();
                        }
                );
                volleyQueue.add(jsonObjectRequest);

            } catch (IllegalArgumentException iae) {
                Toast.makeText(getApplicationContext(), iae.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private static JSONObject prepareData(String username, String email, String password) {
        JSONObject data = new JSONObject();

        try {
            data.put("nickname", username);
            data.put("email", email);
            final String hash = Hash.makeHash(password);
            data.put("hash", hash);
        } catch (Exception e) {
            Log.println(Log.ERROR, "Authorization", "LogIn data preparation failed.");
        }

        return data;
    }
}


