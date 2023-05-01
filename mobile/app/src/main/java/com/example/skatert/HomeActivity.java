package com.example.skatert;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.util.Collections;
import java.util.List;

public class HomeActivity extends AppCompatActivity {
    Track[] trackList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.home_activity);

        try {
            trackList = ServerConnector.getFavouriteTracks("Meljiee999");
            final ListView listView = findViewById(R.id.favouriteTracks);
            listView.setAdapter(new AdapterElements(this));
        } catch (Exception e) {
            Toast.makeText(getApplicationContext(), "The connection to the server was interrupted", Toast.LENGTH_SHORT).show();
        }

//        this.okButton = findViewById(R.id.homeOkButton);
//        okButton.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View v) {
//                Toast.makeText(getApplicationContext(), "That's all for now", Toast.LENGTH_SHORT).show();
//            }
//        });
//
//        try {
//            String message = "Logged as " + Settings.getSetting(Settings.usernameKey);
//            Toast.makeText(getApplicationContext(), message, Toast.LENGTH_SHORT).show();
//        } catch (Exception ignored) {};
    }

    class AdapterElements extends ArrayAdapter<Object> {
        Activity context;

        public AdapterElements(Activity context) {
            super(context, R.layout.track, trackList);
            this.context = context;
        }

        public View getView(int position, View convertView, ViewGroup parent) {
            LayoutInflater inflater = context.getLayoutInflater();
            @SuppressLint({"ViewHolder", "InflateParams"}) View item = inflater.inflate(R.layout.track, null);

            TextView trackName = item.findViewById(R.id.song_title);
            trackName.setText(trackList[position].getName());

            TextView artist = item.findViewById(R.id.artist_name);
            artist.setText(trackList[position].getArtist());

            TextView album = item.findViewById(R.id.album_name);
            album.setText(trackList[position].getAlbum());

            return item;
        }
    }
}

