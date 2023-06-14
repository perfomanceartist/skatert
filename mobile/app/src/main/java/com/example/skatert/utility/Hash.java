package com.example.skatert.utility;

import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class Hash {
    public static String makeHash(String password) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            final byte[] hashBytes = digest.digest(password.getBytes());
            return String.format("%0" + (hashBytes.length * 2) + "X", new BigInteger(1, hashBytes));
        } catch (NoSuchAlgorithmException e1) {
            throw new RuntimeException("Hash aggregation failed.");
        }
    }
}
