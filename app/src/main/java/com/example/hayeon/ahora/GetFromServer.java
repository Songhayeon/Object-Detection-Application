package com.example.hayeon.ahora;

import android.app.Activity;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.os.StrictMode;
import android.view.View;
import android.widget.ImageView;

import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;


public class GetFromServer extends Activity {
    //  TCP연결 관련
    private Socket clientSocket;
    private BufferedReader socketIn;
    private PrintWriter socketOut;
    private int port = 9999;
    private String ip = "";
    private MyThread myThread;
    Handler handler;
    private ImageView image;
    ImageView btn;

    static JSONObject jObj = null;

    @Override
    public void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_get_from_server);

        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);

        Bundle extras = getIntent().getExtras();

        ip = extras.getString("ip");


        try {
            clientSocket = new Socket(ip, port); //소켓만들기
            socketOut = new PrintWriter(clientSocket.getOutputStream(), true);

        } catch (Exception e) {
            e.printStackTrace();
        }

        myThread = new MyThread();
        handler = new Handler();

        btn = (ImageView) findViewById(R.id.btn);
        image = (ImageView) findViewById(R.id.image);

        myThread.start();

        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                socketOut.println("GET");
            }
        });

    }

    public class MyThread extends Thread {

        @Override
        public void run() {

            System.out.println("start thread");
            BufferedInputStream bis = null;

            try {
                bis = new BufferedInputStream(clientSocket.getInputStream());
            } catch (IOException e) {
                e.printStackTrace();
            }

            byte[] imagebuffer = null;
            int size = 0;

            byte[] buffer = new byte[10240];

            int read;

            try {
                while((read = bis.read(buffer)) != -1 ) { //파일을 읽어오기 시작함

                    if (imagebuffer == null) {
                        //이미지버퍼 배열에 저장한다
                        imagebuffer = new byte[read];
                        System.arraycopy(buffer, 0, imagebuffer, 0, read);

                    } else {

                        //이미지버퍼 배열에 계속 이어서 저장한다
                        byte[] preimagebuffer = imagebuffer.clone();
                        imagebuffer = new byte[read + preimagebuffer.length];
                        System.arraycopy(preimagebuffer, 0, imagebuffer, 0, preimagebuffer.length);
                        System.arraycopy(buffer, 0, imagebuffer, imagebuffer.length - read, read);
                    }
                }
                if(read  == -1 ) {

                    Bundle bundle = new Bundle();
                    bundle.putByteArray("Data", imagebuffer);

                    Message msg = mResultHandler.obtainMessage();
                    msg.setData(bundle);
                    mResultHandler.sendMessage(msg);

                }


            } catch (IOException e) {
                e.printStackTrace();
            }

        }
    }

    //byte배열을 숫자로 바꾼다
    private int getInt(byte[] data) {
        int s1 = data[0] & 0xFF;
        int s2 = data[1] & 0xFF;
        int s3 = data[2] & 0xFF;
        int s4 = data[3] & 0xFF;

        return ((s1 << 24) + (s2 << 16) + (s3 << 8) + (s4 << 0));
    }

    //이미지뷰에 비트맵을 넣는다
    public Handler mResultHandler = new Handler() {
        public void handleMessage(Message msg) {
            byte[] data = msg.getData().getByteArray("Data");
            ((ImageView) findViewById(R.id.image)).setImageBitmap(BitmapFactory.decodeByteArray(data, 0, data.length));
        }
    };

}

