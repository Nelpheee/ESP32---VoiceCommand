#include <WiFi.h>
#include <PubSubClient.h>

// Update these with values suitable for your network.

const char* ssid = "NVHH082";
const char* password = "nvhh0822401";
const char* mqtt_server = "broker.hivemq.com";

unsigned long lastMsg = 0;

#define LED1    2
#define LED2    12

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() { 
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA); 
  WiFi.begin(ssid, password); 

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  String LightState; 
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  if (String(topic) == "PTIT_26/Light/Control"){
    for (int i = 0; i < length; i++) { 
      LightState += (char)payload[i];
    }
    if(LightState == "on"){
      digitalWrite(LED1, HIGH);
      digitalWrite(LED2, HIGH);
    }
    else if(LightState == "off"){
      digitalWrite(LED1, LOW);
      digitalWrite(LED2, LOW);
    }
    else if(LightState == "one"){
      digitalWrite(LED1, !digitalRead(LED1));
    }
    else if(LightState == "two"){
      digitalWrite(LED2, !digitalRead(LED2));
    }
  }
  Serial.print(LightState);
}

void reconnect() { 
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("Connected to " + clientId);
      // Once connected, publish an announcement...
      // ... and resubscribe
      client.subscribe("PTIT_26/Light/Control"); 
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  pinMode(2, OUTPUT);
  pinMode(12, OUTPUT);
  Serial.begin(115200);
  setup_wifi(); 
  client.setServer(mqtt_server, 1883); 
  client.setCallback(callback); 
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 2000) { 
    lastMsg = now;
    if(digitalRead(LED1)==1){
      client.publish("PTIT_26/Light/State1", "on");
    }
    else{
      client.publish("PTIT_26/Light/State1", "off");
    }
    if(digitalRead(LED2)==1){
      client.publish("PTIT_26/Light/State2", "on");
    }
    else{
      client.publish("PTIT_26/Light/State2", "off");
    }
  }
}