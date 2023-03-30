package com.example.skatert;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class LoginActivity extends AppCompatActivity {
    EditText usernameEditText;
    EditText passwordEditText;
    Button loginButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.login_activity);

        usernameEditText = findViewById(R.id.email_edit_text);
        passwordEditText = findViewById(R.id.password_edit_text);
        loginButton = findViewById(R.id.login_button);

        loginButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    logIn();
                } catch (IllegalArgumentException iae) {
                    Toast.makeText(getApplicationContext(), iae.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    void logIn() {
        String username = String.valueOf(usernameEditText.getText());
        if(username.length() == 0)
            throw new IllegalArgumentException("Please enter your username");
        String password = String.valueOf(passwordEditText.getText());
        if(password.length() == 0)
            throw new IllegalArgumentException("Please enter your password");

        String loggedAs = ServerConnection.initLogin(username, password);
        Log.d("INFO", "Logged as " + loggedAs);
        Settings.setString(Settings.usernameKey, loggedAs);

        Intent intent = new Intent(this, HomeActivity.class);
        startActivity(intent);
    }
}
