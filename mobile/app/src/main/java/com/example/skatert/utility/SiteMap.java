package com.example.skatert.utility;

public class SiteMap {
    public static final String host = "http://10.0.2.2:8000/"; //"http://46.23.96.41:80/"; //
    public static final String authStepOne = host + "api/login_pass";
    public static final String authStepTwo = host + "api/login_email";
    public static final String registration = host + "api/register";
    public static final String lastFmIntegration = host + "music/lastFM-integration/";
    public static final String getUserFavouriteTracks = host + "music/getUserFavouriteTracks";
    public static final String subscribe = host + "users/subscribe";
    public static final String getSubscriptions = host + "users/subscriptions";
    public static final String getRecommendations = host + "music/getRecommendations";
}
