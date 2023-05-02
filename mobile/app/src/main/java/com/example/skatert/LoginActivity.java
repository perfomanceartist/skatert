package com.example.skatert;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.text.InputFilter;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Objects;

public class LoginActivity extends AppCompatActivity implements OnTaskCompleted {
    EditText usernameEditText;
    EditText passwordEditText;
    Button loginButton;


    String host = "http://127.0.0.1:8000/";
    String authStepOne = host + "api/login_pass";
    String authStepTwo = host + "api/login_email";

    String lastFmIntegration = host + "music/lastFM-integration";

    String lastResult;

    String nickname;

    String code;

    String authData;

    public void onTaskCompleted(String result) {
        if(Objects.equals(result, "CompletedFirst")) {
            lastResult = result;

            showEmailCodeDialog(nickname);

            authData = "{ \"nickname\": \"" + nickname + "\", \"code\": " + String.valueOf(code) + " }";
            new MyHttpPostTask(this).execute(authStepTwo);
        }

        if(Objects.equals(result, "CompletedSecond")) {
            authData = "{\n" +
                    "    \"nickname\": \"" + nickname + "\",\n" +
                    "    \"lastFmNickname\": \"" + nickname + "\"\n" +
                    "}";
            new MyHttpPostTask(this).execute(lastFmIntegration);
            Intent intent = new Intent(this, HomeActivity.class);
            startActivity(intent);
        }
    }

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
        nickname = String.valueOf(usernameEditText.getText());
        if(nickname.length() == 0)
            throw new IllegalArgumentException("Please enter your username");
        String password = String.valueOf(passwordEditText.getText());
        if(password.length() == 0)
            throw new IllegalArgumentException("Please enter your password");

        authData = "{ \"nickname\": \"" + nickname + "\", \"hash\": \"" + password + "\"}";
        System.out.println("Using string: " + authData);
        Toast.makeText(getApplicationContext(), authData, Toast.LENGTH_SHORT).show();

        new MyHttpPostTask(this).execute(authStepOne);
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
                    if(urls[0].contains(authStepOne)) {
                        System.out.println("First step completed.");
                        return "CompletedFirst";
                    }
                    else
                        return "CompletedSecond";
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

    public void showEmailCodeDialog(String nickname) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        LayoutInflater inflater = getLayoutInflater();

        // Загрузка макета для диалогового окна
        View view = inflater.inflate(R.layout.email_integration, null);

        // Настройка заголовка окна
        TextView titleTextView = view.findViewById(R.id.text_view_title);
        titleTextView.setText("Enter verification code");

        // Настройка поля ввода кода
        EditText codeEditText = view.findViewById(R.id.edit_text_code);
        codeEditText.setFilters(new InputFilter[]{new InputFilter.LengthFilter(6)});

        // Создание диалогового окна
        builder.setView(view).setPositiveButton("OK", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int id) {
                        code = codeEditText.getText().toString();
                        System.out.println("Code received.");
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        dialog.cancel();
                    }
                });

        AlertDialog dialog = builder.create();
        dialog.show();
    }

}
