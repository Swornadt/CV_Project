#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include "soc/soc.h"           // For Brownout
#include "soc/rtc_cntl_reg.h"  // For Brownout

// --- CONFIG ---
const char* ssid = "ESP-CAM-SDT";
const char* password = "sworna12345";

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
const char* STREAM_BOUNDARY = "123456789012345678901234567890";

void handle_stream() {
  WiFiClient client = server.client();
  client.print("HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace;boundary=");
  client.print(STREAM_BOUNDARY);
  client.print("\r\n\r\n");

  while (client.connected()) {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) continue;
    client.printf("--%s\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", STREAM_BOUNDARY, fb->len);
    client.write(fb->buf, fb->len);
    client.print("\r\n");
    esp_camera_fb_return(fb);
    delay(1); 
  }
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); 
  
  Serial.begin(115200);
  delay(500);

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
  
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QQVGA; 
  config.xclk_freq_hz = 5000000;  // Drop to 5MHz (Half speed)
  config.jpeg_quality = 20;
  config.fb_count = 1;
  config.fb_location = CAMERA_FB_IN_DRAM;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("CAMERA_FAIL");
    while(1);
  }

  pinMode(13, OUTPUT);
  panServo.attach(12);
  tiltServo.attach(14);
  
  // Start Access Point
  WiFi.softAP(ssid, password);
  
  server.on("/stream", handle_stream);
  server.begin();
  
  Serial.println("\n--- SYSTEM READY ---");
  Serial.println("1. Connect laptop to WiFi: ESP-CAM-SDT");
  Serial.println("2. Python URL: http://192.168.4.1/stream");
}

void loop() {
  server.handleClient();

  // Read the Serial Turret Commands
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    int xIdx = data.indexOf('X');
    int yIdx = data.indexOf('Y');
    int zIdx = data.indexOf('Z');
    if (xIdx != -1 && yIdx != -1) {
      panServo.write(constrain(data.substring(xIdx + 1, yIdx).toInt(), 0, 180));
      int yEnd = (zIdx != -1) ? zIdx : data.length();
      tiltServo.write(constrain(data.substring(yIdx + 1, yEnd).toInt(), 0, 180));
    }
    if (zIdx != -1) digitalWrite(13, data.substring(zIdx + 1).toInt() == 1 ? HIGH : LOW);
  }
}