#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

const char* ssid = "DESKTOP-7MC2SRJ 1932";
const char* password = "244466666";

// Camera Pins (Standard AI-Thinker)
#define PWDN_GPIO_NUM  32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM   0
#define SIOD_GPIO_NUM  26
#define SIOC_GPIO_NUM  27
#define Y9_GPIO_NUM    35
#define Y8_GPIO_NUM    34
#define Y7_GPIO_NUM    39
#define Y6_GPIO_NUM    36
#define Y5_GPIO_NUM    21
#define Y4_GPIO_NUM    19
#define Y3_GPIO_NUM    18
#define Y2_GPIO_NUM     5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM  23
#define PCLK_GPIO_NUM  22

Servo panServo, tiltServo;
WebServer server(80);

void processSerial() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    if (data.startsWith("X")) {
      int xIdx = data.indexOf('X');
      int yIdx = data.indexOf('Y');
      int zIdx = data.indexOf('Z');
      
      if (xIdx != -1 && yIdx != -1 && zIdx != -1) {
        int panVal = data.substring(xIdx + 1, yIdx).toInt();
        int tiltVal = data.substring(yIdx + 1, zIdx).toInt();
        int fireVal = data.substring(zIdx + 1).toInt();

        panServo.write(constrain(panVal, 0, 180));
        tiltServo.write(constrain(tiltVal, 0, 180));
        digitalWrite(14, fireVal);
      }
    }
  }
}

void handle_stream() {
  WiFiClient client = server.client();
  client.print("HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace;boundary=frame\r\n\r\n");
  
  while (client.connected()) {
    // Check serial INSIDE the stream loop so servos move while video runs
    processSerial();

    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) continue;
    
    client.printf("--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", fb->len);
    client.write(fb->buf, fb->len);
    client.print("\r\n");
    
    esp_camera_fb_return(fb);
    // Use a tiny delay to give the processor a break without lagging the stream
    delay(1); 
  }
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); 
  Serial.begin(115200);
  // CRITICAL: Set serial timeout to 10ms so it doesn't hang the video
  Serial.setTimeout(10); 

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✓ Connected!");

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM; config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM; config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM; config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM; config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM; config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM; config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM; config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM; config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12; // Slightly higher quality
  config.fb_count = 1;
  config.fb_location = CAMERA_FB_IN_PSRAM;

  esp_camera_init(&config);

  panServo.attach(12);
  tiltServo.attach(13);
  pinMode(14, OUTPUT); // Laser/Trigger
  
  panServo.write(90);
  tiltServo.write(90);

  server.on("/stream", handle_stream);
  server.begin();
}

void loop() {
  server.handleClient();
  processSerial(); // Also check serial when no one is watching the stream
}