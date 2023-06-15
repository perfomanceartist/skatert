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

import com.android.volley.Header;
import com.android.volley.NetworkResponse;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.example.skatert.utility.Hash;
import com.example.skatert.utility.SiteMap;

import org.json.JSONObject;

import java.net.CookieHandler;
import java.net.CookieManager;
import java.net.CookiePolicy;
import java.net.CookieStore;
import java.net.HttpCookie;
import java.util.Map;
import java.util.Objects;

public class SignInActivity extends AppCompatActivity {
    EditText usernameEditText, emailEditText, passwordEditText;
    Button loginButton;

    RequestQueue volleyQueue = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.signup_activity);

        usernameEditText = findViewById(R.id.username_edit_text);
        usernameEditText.setText("Alexander");

        emailEditText = findViewById(R.id.email_edit_text);
        emailEditText.setText("al.lvov777@gmail.com");

        passwordEditText = findViewById(R.id.password_edit_text);
        passwordEditText.setText("hello");

        loginButton = findViewById(R.id.sign_up_button);
        volleyQueue = Volley.newRequestQueue(this);

        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.remove(getString(R.string.SharedPreferencesNickname)).apply();

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
                StringRequest jsonObjectRequest = new StringRequest(Request.Method.POST, SiteMap.registration, response -> {
                    if(!sharedPref.getString(getString(R.string.SharedPreferencesNickname), "").equals(""))
                        startActivity(new Intent(SignInActivity.this, HomeActivity.class));
                    else {
                        switch(sharedPref.getInt(getString(R.string.SharedPreferencesLastStatusCode), -1)) {
                            case 222:
                                Toast.makeText(getApplicationContext(), "Nickname is taken", Toast.LENGTH_SHORT).show(); break;
                            case 223:
                                Toast.makeText(getApplicationContext(), "Bad request", Toast.LENGTH_SHORT).show(); break;
                            default:
                                Toast.makeText(getApplicationContext(), "Registration failed", Toast.LENGTH_SHORT).show(); break;
                        }
                    }
                },  error -> {}) {
                    @Override
                    public byte[] getBody() { return jsonData.toString().getBytes(); }

                    @Override
                    protected Response<String> parseNetworkResponse(NetworkResponse response) {
                        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                        SharedPreferences.Editor editor = sharedPref.edit();

                        if(response.statusCode == 200) {
                            editor.putString(getString(R.string.SharedPreferencesNickname), nickname).apply();
                            for(Header header: response.allHeaders)
                                if(Objects.equals(header.getName(), "token"))
                                    editor.putString(getString(R.string.SharedPreferencesToken), header.getValue()).apply();
                        } else
                            editor.putInt(getString(R.string.SharedPreferencesLastStatusCode), response.statusCode).apply();
                        return super.parseNetworkResponse(response);
                    }
                };
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
            password = Hash.makeHash(password);
            data.put("hash", password);
        } catch (Exception e) {
            Log.println(Log.ERROR, "Authorization", "LogIn data preparation failed.");
        }

        return data;
    }
}


