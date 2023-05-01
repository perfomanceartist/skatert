package com.example.skatert;

import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class User {
    public String nickname;
    public String lastFmNickname;
    public int favouriteTracksAmount;
    public Map<String, Boolean> genres;
    public List<String> recommenders;

    public User() {}

    public String getNickname() {
        return nickname;
    }

    public void setNickname(String nickname) {
        this.nickname = nickname;
    }

    public String getLastFmNickname() {
        return lastFmNickname;
    }

    public void setLastFmNickname(String lastFmNickname) {
        this.lastFmNickname = lastFmNickname;
    }

    public int getFavouriteTracksAmount() {
        return favouriteTracksAmount;
    }

    public void setFavouriteTracksAmount(int favouriteTracksAmount) {
        this.favouriteTracksAmount = favouriteTracksAmount;
    }

    public Map<String, Boolean> getGenres() {
        return genres;
    }

    public void setGenres(Map<String, Boolean> genres) {
        this.genres = genres;
    }

    public List<String> getRecommenders() {
        return recommenders;
    }

    public void setRecommenders(List<String> recommenders) {
        this.recommenders = recommenders;
    }
}

