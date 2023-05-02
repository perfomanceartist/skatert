package com.example.skatert;


import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Objects;

public class SignInActivity extends AppCompatActivity implements OnTaskCompleted {

    EditText usernameEditText;
    EditText emailEditText;
    EditText passwordEditText;
    Button loginButton;

    String lastResult = null;

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

    public void onTaskCompleted(String result) {
        if(Objects.equals(result, "CompletedFirst")) {
            Intent intent = new Intent(this, StartActivity.class);
            startActivity(intent);
        }
    }

    String host = "http://127.0.0.1:8000/";
    String register = host + "api/register";

    String authData;

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

        authData = "{ \"nickname\": \"" + username + "\", \"email\": \"" + email + "\", \"hash\": \"" + password + "\"}";
        System.out.println("Using string: " + authData);
        Toast.makeText(getApplicationContext(), authData, Toast.LENGTH_SHORT).show();

        new MyHttpPostTask(this).execute(register);

        if(Objects.equals(lastResult, "CompletedFirst")) {
            lastResult = "";

            new MyHttpPostTask(this).execute(register);
        }
    }

    public class MyHttpPostTask extends AsyncTask<String, Void, String> {
        private OnTaskCompleted listener;

        public MyHttpPostTask(OnTaskCompleted listener) {
            this.listener = listener;
        }

        protected String doInBackground(String... urls) {
            System.out.println("Making get request on: " + urls[0]);
            int attempts = 20;
            for(int i = 0; i < attempts; ++i) {
                try {
                    URL url = new URL(urls[0]);

                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("POST");
                    conn.setRequestProperty("Content-Type", "application/json;charset=UTF-8");
                    conn.setRequestProperty("Accept", "application/json");
                    conn.setDoOutput(true);

                    try(OutputStream os = conn.getOutputStream()) {
                        byte[] input = authData.getBytes("utf-8");
                        os.write(input, 0, input.length);
                    }


                    int status = conn.getResponseCode();
                    if(status != 200)
                        throw new RuntimeException("Registration failed: code" + String.valueOf(status));
                    return "CompletedFirst";
                } catch (Exception error) {
                    System.out.println("Warning: " + error);
                }
            }
            return "Failed";
        }

        protected void onPostExecute(String result) {
            listener.onTaskCompleted(result);
        }
    }
}


