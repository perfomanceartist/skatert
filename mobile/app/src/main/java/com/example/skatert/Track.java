package com.example.skatert;

import java.util.Optional;

public class Track {
    public String name = "Unknown";
    public Optional<String> artist = Optional.empty();
    public Optional<String> album = Optional.empty();

    Track() {}
    Track(String withName) { name = name; }
    Track(String withName, String withArtist) { name = name; artist = artist; }
    Track(String withName, String withArtist, String withAlbum) { name = name; artist = artist; album = album; }
}
