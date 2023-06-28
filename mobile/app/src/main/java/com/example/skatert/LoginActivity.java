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

import com.android.volley.NetworkResponse;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.skatert.utility.Hash;
import com.example.skatert.utility.SiteMap;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Objects;

public class LoginActivity extends AppCompatActivity {
    EditText usernameEditText, passwordEditText;
    Button loginButton;
    RequestQueue volleyQueue = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.login_activity);

        usernameEditText = findViewById(R.id.nickname_edit_text);
        usernameEditText.setText("Alexander");

        passwordEditText = findViewById(R.id.password_edit_text);
        passwordEditText.setText("hello");

        loginButton = findViewById(R.id.login_button);

        volleyQueue = Volley.newRequestQueue(this);

        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.remove(getString(R.string.SharedPreferencesNickname));
        editor.remove(getString(R.string.SharedPreferencesToken)).apply();

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
                            try {
                                final String token = response.getString("token");
                                if(!token.equals("-")) {
                                    editor.putString(getString(R.string.SharedPreferencesNickname), nickname);
                                    editor.putString(getString(R.string.SharedPreferencesToken), token).apply();
                                    startActivity(new Intent(LoginActivity.this, HomeActivity.class));
                                } else
                                    showEmailCodeDialog(nickname);
                            } catch (JSONException e) {
                                Toast.makeText(getApplicationContext(), "Authorization failed (3)", Toast.LENGTH_SHORT).show();
                            }
                        },
                        error -> {
                            if (!(error instanceof com.android.volley.NoConnectionError)) {
                                switch (sharedPref.getInt(getString(R.string.SharedPreferencesLastStatusCode), -1)) {
                                    case 225:
                                        Toast.makeText(getApplicationContext(), "Password is incorrect", Toast.LENGTH_SHORT).show();
                                        break;
                                    case 224:
                                        Toast.makeText(getApplicationContext(), "Such user is not found", Toast.LENGTH_SHORT).show();
                                        break;
                                    case 223:
                                        Toast.makeText(getApplicationContext(), "Bad request", Toast.LENGTH_SHORT).show();
                                        break;
                                    default:
                                        Toast.makeText(getApplicationContext(), "Authorization failed", Toast.LENGTH_SHORT).show();
                                        break;
                                }
                            } else
                                Toast.makeText(getApplicationContext(), "Server is unreachable", Toast.LENGTH_SHORT).show();
                        }
                ) {
                    @Override
                    protected Response<JSONObject> parseNetworkResponse(NetworkResponse response) {
                        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                        sharedPref.edit().putInt(getString(R.string.SharedPreferencesLastStatusCode), response.statusCode).apply();

                        JSONObject object = new JSONObject();
                        try {
                            object.put("StatusCode", response.statusCode);
                        } catch (JSONException ignored) {}

                        if (response.data.length == 0)
                            response = new NetworkResponse(response.statusCode, object.toString().getBytes(), response.headers, response.notModified);
                        return super.parseNetworkResponse(response);
                    }
                };
                volleyQueue.add(jsonObjectRequest);
            } catch (IllegalArgumentException iae) {
                Toast.makeText(getApplicationContext(), iae.getMessage(), Toast.LENGTH_SHORT).show();
            }
            catch (Exception e) {
                Toast.makeText(getApplicationContext(), "Authorization failed (1)", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private JSONObject prepareStepOneData(String nickname, String password) {
        JSONObject authData = new JSONObject();

        try {
            authData.put("nickname", nickname);
            password = Hash.makeHash(password);
            authData.put("hash", password);
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
        EditText codeEditText = view.findViewById(R.id.mail_edit_text_code);
        codeEditText.setFilters(new InputFilter[]{ new InputFilter.LengthFilter(6) });

        builder.setView(view).setPositiveButton("OK", (dialog, id) -> {
            try {
                final String code = codeEditText.getText().toString();
                if(code.isEmpty())
                    throw new IllegalArgumentException("Please enter your verification code");

                final JSONObject stepTwoData = prepareStepTwoData(nickname, code);
                JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, SiteMap.authStepTwo, stepTwoData,
                        response -> {
                            try {
                                SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                                SharedPreferences.Editor editor = sharedPref.edit();
                                editor.putString(getString(R.string.SharedPreferencesNickname), nickname)
                                        .putString(getString(R.string.SharedPreferencesToken), response.getString("token"))
                                        .apply();
                                startActivity(new Intent(LoginActivity.this, HomeActivity.class));
                            } catch (JSONException e) {
                                throw new RuntimeException(e);
                            }
                        },
                        error -> {
                            try {
                                if (Objects.requireNonNull(error.getMessage()).contains("Failed to connect"))
                                    Toast.makeText(getApplicationContext(), "Server is unreachable", Toast.LENGTH_SHORT).show();
                            } catch (Exception e) {
                                Toast.makeText(getApplicationContext(), "Authorization failed", Toast.LENGTH_SHORT).show();
                            }
                        }
                ) {
                    @Override
                    protected Response<JSONObject> parseNetworkResponse(NetworkResponse response) {
                        SharedPreferences sharedPref = getSharedPreferences(getString(R.string.SharedPreferencesList), Context.MODE_PRIVATE);
                        sharedPref.edit().putInt(getString(R.string.SharedPreferencesLastStatusCode), response.statusCode).apply();
                        return super.parseNetworkResponse(response);
                    }
                };
                volleyQueue.add(jsonObjectRequest);
            } catch (IllegalArgumentException iae) {
                Toast.makeText(getApplicationContext(), iae.getMessage(), Toast.LENGTH_SHORT).show();
            }
            catch (Exception re) {
                Log.println(Log.ERROR, "Authorization", re.toString());
            }
            dialog.dismiss();
        }).setNegativeButton("Cancel", (dialog, id) -> dialog.cancel());

        AlertDialog dialog = builder.create();
        dialog.show();
    }
}
