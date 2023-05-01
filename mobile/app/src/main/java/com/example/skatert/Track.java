package com.example.skatert;

import com.google.gson.annotations.SerializedName;

import java.util.List;

public class Track {
    private String name;
    private String artist;

    @SerializedName("album")
    private String album;
    private List<Boolean> genres;
    private int listeners;
    private int recommended;

    // Конструкторы, геттеры и сеттеры

    public Track(String name, String artist, String album, List<Boolean> genres, int listeners, int recommended) {
        this.name = name;
        this.artist = artist;
        this.album = album;
        this.genres = genres;
        this.listeners = listeners;
        this.recommended = recommended;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getArtist() {
        return artist;
    }

    public void setArtist(String artist) {
        this.artist = artist;
    }

    public String getAlbum() {
        return album;
    }

    public void setAlbum(String album) {
        this.album = album;
    }

    public List<Boolean> getGenres() {
        return genres;
    }

    public void setGenres(List<Boolean> genres) {
        this.genres = genres;
    }

    public int getListeners() {
        return listeners;
    }

    public void setListeners(int listeners) {
        this.listeners = listeners;
    }

    public int getRecommended() {
        return recommended;
    }

    public void setRecommended(int recommended) {
        this.recommended = recommended;
    }
}
