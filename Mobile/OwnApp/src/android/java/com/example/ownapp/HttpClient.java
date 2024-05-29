package com.example.ownapp;

import android.os.AsyncTask;
import android.util.Log;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class HttpClient extends AsyncTask<String, Void, String> {

    private static final String TAG = "HttpRequestTask";

    @Override
    protected String doInBackground(String... params) {
        String urlString = params[0];

        try {
            OkHttpClient client = new OkHttpClient.Builder()
                    .certificatePinner(new okhttp3.CertificatePinner.Builder()
                            .add("ownapp.ctf.bzh", "sha256/jdUcBmV4SClWUpavrOctB6mBKVB3CBIC4R0qxkD5RFo=")
                            .build())
                    .build();

            Request request = new Request.Builder()
                    .url(urlString)
                    .build();

            Response response = client.newCall(request).execute();

            // Vérifiez que la réponse a réussi (code 200)
            if (response.isSuccessful()) {
                return response.body().string();
            } else {
                Log.e(TAG, "Erreur lors de la requête HTTP: " + response.code());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la requête HTTP", e);
        }

        return null;
    }

    @Override
    protected void onPostExecute(String result) {
        // Le résultat de la requête est disponible ici
        if (result != null) {
            Log.d(TAG, "Réponse du serveur : " + result);
            // Faire quelque chose avec la réponse
        } else {
            Log.e(TAG, "La requête a échoué");
        }
    }
}
