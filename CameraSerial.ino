#include "esp_camera.h"
#include "soc/soc.h"           // 1. ADD THIS for power control
#include "soc/rtc_cntl_reg.h"  // 2. ADD THIS for power control

// Standard ESP32-S / AI-Thinker Pins
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

void setup() {
  // 3. CRITICAL: Disable brownout detector immediately
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); 
  
  Serial.begin(460800); // Back to 115200 for maximum reliability while testing power
  Serial.setDebugOutput(true);
  
  // Give the laptop port a moment to stabilize voltage
  delay(500); 

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  
  config.xclk_freq_hz = 10000000;       // Keep it slow (10MHz)
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QQVGA;  // Keep it small (160x120)
  config.jpeg_quality = 15;             // Lower quality = lower current spike
  config.fb_count = 1;
  config.fb_location = CAMERA_FB_IN_DRAM; 

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  Serial.println("CAMERA_SUCCESS");
}

void loop() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) return;

  // Header
  Serial.write(0xAA); 
  Serial.write(0xBB);
  
  // Size (Big Endian)
uint32_t size = fb->len;
  Serial.write((uint8_t)((size >> 24) & 0xFF));
  Serial.write((uint8_t)((size >> 16) & 0xFF));
  Serial.write((uint8_t)((size >> 8) & 0xFF));
  Serial.write((uint8_t)(size & 0xFF));

  Serial.write(fb->buf, fb->len);
  esp_camera_fb_return(fb);
  
  // Small delay to prevent flooding the Serial buffer at low baud rates
  delay(100); 
}