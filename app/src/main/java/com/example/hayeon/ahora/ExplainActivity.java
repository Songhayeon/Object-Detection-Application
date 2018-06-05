package com.example.hayeon.ahora;

import android.app.Activity;
import android.net.Uri;
import android.os.Bundle;
import android.widget.VideoView;

public class ExplainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_explain);
        VideoView vv = (VideoView) findViewById(R.id.vv);

        String uriPath = "android.resource://" + getPackageName() + "/" + R.raw.tutorial;
        Uri uri = Uri.parse(uriPath);
        vv.setVideoURI(uri);
        vv.requestFocus();
        vv.start();
    }
}
