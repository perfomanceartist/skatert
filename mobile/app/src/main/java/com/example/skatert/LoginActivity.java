package com.example.skatert;

import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
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

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.skatert.utility.Hash;
import com.example.skatert.utility.SiteMap;

import org.json.JSONObject;

public class LoginActivity extends AppCompatActivity {
    EditText usernameEditText;
    EditText passwordEditText;
    Button loginButton;

    AlertDialog dialog = null;

    RequestQueue volleyQueue = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.login_activity);

        usernameEditText = findViewById(R.id.email_edit_text);
        usernameEditText.setText("Alexander");

        passwordEditText = findViewById(R.id.password_edit_text);
        passwordEditText.setText("Password");

        loginButton = findViewById(R.id.login_button);

        volleyQueue = Volley.newRequestQueue(this);

        loginButton.setOnClickListener(v -> {
            try {
                final String nickname = String.valueOf(usernameEditText.getText());
                if (nickname.length() == 0)
                    throw new IllegalArgumentException("Please enter your username");

                final String password = String.valueOf(passwordEditText.getText());
                if (password.length() == 0)
                    throw new IllegalArgumentException("Please enter your password");

                final JSONObject stepOneData = prepareStepOneData(nickname, password);
                JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, SiteMap.authStepOne, stepOneData,
                        response -> {
                                showEmailCodeDialog(nickname);
                        },
                        error -> {
                            Toast.makeText(getApplicationContext(), "Authorization failed", Toast.LENGTH_SHORT).show();
                        }
                );
                volleyQueue.add(jsonObjectRequest);
            } catch (Exception e) {
                Toast.makeText(getApplicationContext(), "Authorization failed", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private JSONObject prepareStepOneData(String nickname, String password) {
        JSONObject authData = new JSONObject();

        try {
            authData.put("nickname", nickname);
            authData.put("hash", Hash.makeHash(password));
        } catch (Exception ignored) {
            Log.println(Log.ERROR, "Authorization", "LogIn data preparation failed.");
        }

        return authData;
    }

    private JSONObject prepareStepTwoData(String nickname, String code) {
        JSONObject authData = new JSONObject();

        try {
            authData.put("nickname", nickname);
            authData.put("code", Integer.parseInt(code));
        } catch (Exception ignored) {
            Log.println(Log.ERROR, "Authorization", "LogIn data preparation failed.");
        }

        return authData;
    }


    public void showEmailCodeDialog(String nickname) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        LayoutInflater inflater = getLayoutInflater();

        View view = inflater.inflate(R.layout.email_integration, null);

        TextView titleTextView = view.findViewById(R.id.text_view_title);
        titleTextView.setText(R.string.VerificationCodeAction);

        EditText codeEditText = view.findViewById(R.id.edit_text_code);
        codeEditText.setFilters(new InputFilter[]{ new InputFilter.LengthFilter(6) });

        builder.setView(view).setPositiveButton("OK", (dialog, id) -> {
            try {
                final String code = codeEditText.getText().toString();
                if(code.isEmpty())
                    throw new IllegalArgumentException("Please enter your verification code");

                final JSONObject stepTwoData = prepareStepTwoData(nickname, code);
                JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, SiteMap.authStepTwo, stepTwoData,
                        response -> {
                            SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                            SharedPreferences.Editor editor = sharedPref.edit();
                            editor.putString(getString(R.string.SharedPreferencesNickname), nickname);
                            editor.apply();

                            startActivity(new Intent(LoginActivity.this, HomeActivity.class));
                        },
                        error -> {
                            Toast.makeText(getApplicationContext(), "Authorization failed", Toast.LENGTH_SHORT).show();
                        }
                );
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

        dialog = builder.create();
        dialog.show();
    }

}
