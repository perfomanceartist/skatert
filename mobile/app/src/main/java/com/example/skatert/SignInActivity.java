package com.example.skatert;


import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class SignInActivity extends AppCompatActivity {

    EditText usernameEditText;
    EditText emailEditText;
    EditText passwordEditText;
    Button loginButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.signup_activity);

        usernameEditText = findViewById(R.id.username_edit_text);
        emailEditText = findViewById(R.id.email_edit_text);
        passwordEditText = findViewById(R.id.password_edit_text);
        loginButton = findViewById(R.id.sign_up_button);

        loginButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    signIn();
                } catch (IllegalArgumentException iae) {
                    Toast.makeText(getApplicationContext(), iae.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void signIn() {
        String username = String.valueOf(usernameEditText.getText());
        if(username.length() == 0)
            throw new IllegalArgumentException("Please enter your username");

        String email = String.valueOf(emailEditText.getText());
        if(email.length() == 0)
            throw new IllegalArgumentException("Please enter your email");

        String password = String.valueOf(passwordEditText.getText());
        if(password.length() == 0)
            throw new IllegalArgumentException("Please enter your password");


        String authorizedAs = ServerConnection.initSignIn(username, email, password);
        Log.d("INFO", "Signed up as " + authorizedAs);
        Settings.setString(Settings.usernameKey, authorizedAs);

        Intent intent = new Intent(this, HomeActivity.class);
        startActivity(intent);
    }
}


