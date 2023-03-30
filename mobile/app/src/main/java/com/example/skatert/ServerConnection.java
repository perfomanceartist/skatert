package com.example.skatert;

public class ServerConnection {
    private static ServerConnection instance;

    private ServerConnection() {}

    private static synchronized ServerConnection getInstance() {
        if (instance == null)
            instance = new ServerConnection();
        return instance;
    }

    /* Initialises Log in process. Returns username. Stub for now. */
    public static String initLogin(String username, String password) {
        return "User";
    }

    /* Initialises Sign up process. Returns username. Stub for now. */
    public static String initSignIn(String username, String email, String password) {
        return "User";
    }
}

