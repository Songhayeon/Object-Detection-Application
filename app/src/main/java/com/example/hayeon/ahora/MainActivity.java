package com.example.hayeon.ahora;


import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;

public class MainActivity extends Activity {

    ImageView detect_btn;
    ImageView explain_btn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        detect_btn  = (ImageView) findViewById(R.id.btn_detect);
        explain_btn  = (ImageView) findViewById(R.id.btn_explain);
    }

    public void detectClicked(View v) {
        Intent intent = new Intent(getBaseContext(), DetectActivity.class);
        startActivity(intent);
    }
    public void explainClicked(View v) {
        //해야함
        Intent intent = new Intent(getBaseContext(), ExplainActivity.class);
        startActivity(intent);
    }


}