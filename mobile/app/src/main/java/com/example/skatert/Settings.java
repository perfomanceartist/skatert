package com.example.skatert;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.Resources;

import androidx.appcompat.app.AppCompatActivity;
public class Settings extends AppCompatActivity {
    SharedPreferences preferencesList;
    private static Settings instance;

    private Settings(SharedPreferences preferences) {
        preferencesList = preferences;
    }

    public static void init(Context context) {
        instance = new Settings(((Activity) context).getPreferences(Context.MODE_PRIVATE));
    }

    public static String usernameKey = "user_login";
    public static String emailKey = "user_email";

    public static String getSetting(String key) {
        if(instance.preferencesList.contains(key))
            return instance.preferencesList.getString(key, "");
        throw new Resources.NotFoundException("Setting '" + key + "' is not found.");
    }

    public static void setString(String key, String value) {
        SharedPreferences.Editor editor = instance.preferencesList.edit();
        editor.putString(key, value); editor.apply();
    }
}

