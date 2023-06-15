package com.example.skatert;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Resources;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import androidx.appcompat.app.AppCompatActivity;

import java.net.CookieHandler;
import java.net.CookieManager;
import java.net.CookiePolicy;
import java.util.Set;

public class StartActivity extends AppCompatActivity {
    Button loginButton;
    Button registerButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        CookieManager manager = new CookieManager();
        CookieHandler.setDefault(manager);

        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
        if(!sharedPref.getString(getString(R.string.SharedPreferencesNickname), "").equals(""))
            startActivity(new Intent(StartActivity.this, HomeActivity.class));

        setContentView(R.layout.start_activity);

        loginButton = findViewById(R.id.setup_login_button);
        loginButton.setOnClickListener(v -> startActivity(new Intent(StartActivity.this, LoginActivity.class)));

        registerButton = findViewById(R.id.setup_sign_in_button);
        registerButton.setOnClickListener(v -> startActivity(new Intent(StartActivity.this, SignInActivity.class)));
    }
}