#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "DHT.h"
#include "Arduino.h"

#define DHTPIN 2     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11   // DHT 11

#define BUTTON_PIN 3

typedef struct _misura {
  float min;
  float max;
  float avg;
  float act;
} Misura;

void resetMisura(Misura *m) {
  m->min = 1000;
  m->max = 0;
  m->avg = 0;
  m->act = 0;
}

void updateAvg(Misura *m, long n) {
  m->avg = (m->avg*n + m->act)/(n+1);
}

void updateMin(Misura *m) {
  if (m->min > m->act)
    m->min = m->act;
}

void updateMax(Misura *m) {
  if (m->max < m->act)
    m->max = m->act;
}

typedef struct _time_trigger {
  long last_shot;
  long delta;
} TimeTrigger;

typedef struct _print_misura {
  Misura *m;
  char label[5];
  char unit;
} PrintMisura;

// Set the LCD address to 0x27 for a 16 chars and 2 line display
LiquidCrystal_I2C lcd(0x3F, 16, 2);

// Connect pin 1 (on the left) of the sensor to +5V
// NOTE: If using a board with 3.3V logic like an Arduino Due connect pin 1
// to 3.3V instead of 5V!
// Connect pin 2 of the sensor to whatever your DHTPIN is
// Connect pin 4 (on the right) of the sensor to GROUND
// Connect a 10K resistor from pin 2 (data) to pin 1 (power) of the sensor

// Initialize DHT sensor.
// Note that older versions of this library took an optional third parameter to
// tweak the timings for faster processors.  This parameter is no longer needed
// as the current DHT reading algorithm adjusts itself to work on faster procs.
DHT dht(DHTPIN, DHTTYPE);

long n;

Misura temp, hum, hic;
TimeTrigger tReadData, tPrintData;
PrintMisura pTemp, pHumid, pHic, *nextToPrint;
boolean readOK;
int btnPrev, btnAct;

void setup()
{
  // initialize the LCD
  lcd.begin();

  // Turn on the blacklight and print a message.
  lcd.noBacklight();
  lcd.clear();
  
  dht.begin();

  n = 0;
  resetMisura(&temp);
  resetMisura(&hum);
  resetMisura(&hic);

  // initTimeTrigger(&tReadData, 2000);
  // initTimeTrigger(&tPrintData, 1500);
  tReadData.delta = 30000;
  tReadData.last_shot = 0;
  tPrintData.delta = 3000;
  tPrintData.last_shot = 0;

  // initPrintMisura(&pTemp, &temp, "Tmp:", 'C');
  pTemp.m = &temp;
  pTemp.unit = 'C';
  pTemp.label[0] = 'T';
  pTemp.label[1] = 'm';
  pTemp.label[2] = 'p';
  pTemp.label[3] = ':';
  pTemp.label[4] = '\0';
  // initPrintMisura(&pHumid, &hum, "Hum:", 'H');
  pHumid.m = &hum;
  pHumid.unit = '%';
  pHumid.label[0] = 'H';
  pHumid.label[1] = 'u';
  pHumid.label[2] = 'm';
  pHumid.label[3] = ':';
  pHumid.label[4] = '\0';
  // initPrintMisura(&pHic, &hic, "HIC:", 'C');
  pHic.m = &hic;
  pHic.unit = 'C';
  pHic.label[0] = 'H';
  pHic.label[1] = 'I';
  pHic.label[2] = 'C';
  pHic.label[3] = ':';
  pHic.label[4] = '\0';

  nextToPrint = &pTemp;

  readOK = true;

  pinMode(BUTTON_PIN, INPUT);
  btnPrev = LOW;
  btnAct = LOW;

  Serial.begin(9600);
}

void printMisura(Misura &m, char label[5], char unit) {
  lcd.setCursor(0,0);
  lcd.print(label);
  lcd.print(m.act);
  lcd.setCursor(9,0);
  lcd.print(unit);
  lcd.print(" ");
  lcd.print(m.avg);
  lcd.setCursor(15,0);
  lcd.print(unit);
  lcd.print(" ");

  lcd.setCursor(0,1);
  lcd.print("m:");
  lcd.print(m.min);
  lcd.setCursor(6,1);
  lcd.print(unit);
  lcd.print(" M:");
  lcd.print(m.max);
  lcd.setCursor(14,1);
  lcd.print(unit);
}

void loop() {
  boolean frontUp = false, frontDown = false;

  btnAct = digitalRead(BUTTON_PIN);
  if (btnAct == HIGH && btnPrev == LOW)
    frontUp = true;
  else if (btnAct == LOW && btnPrev == HIGH)
    frontDown = true;
  btnPrev = btnAct;

  // if (Serial.avaiable()) {
  //   delay(100); //wait the end
  //   long n = 0;
  //   while(Serial.avaiable()) {
  //     n = n*10 + Serial.read() - '0';
  //   }
  //   tReadData.delta = n;
  // }

  long time = millis();

  if (time - tReadData.last_shot >= tReadData.delta || tReadData.last_shot == 0) {
    tReadData.last_shot = time;

    // Reading temperature or humidity takes about 250 milliseconds!
    // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
    hum.act = dht.readHumidity();
    // Read temperature as Celsius (the default)
    temp.act = dht.readTemperature();

    // Check if any reads failed and exit early (to try again).
    if (isnan(hum.act) || isnan(temp.act)) {
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print(F("Failed to read"));
      lcd.setCursor(0,1);
      lcd.print(F("from DHT sensor!"));
      return;
    }

    // Compute heat index in Celsius (isFahreheit = false)
    hic.act = dht.computeHeatIndex(temp.act, hum.act, false);

    updateAvg(&temp, n);
    updateMin(&temp);
    updateMax(&temp);

    updateAvg(&hum, n);
    updateMin(&hum);
    updateMax(&hum);

    updateAvg(&hic, n);
    updateMin(&hic);
    updateMax(&hic);

    n++;

    if (Serial) {
      Serial.print("{");

      Serial.print("\"id\":");
      Serial.print(time);
      Serial.print(",");

      Serial.print("\"temperature\":{\"actual\":");
      Serial.print(temp.act);
      Serial.print(",\"average\":");
      Serial.print(temp.avg);
      Serial.print(",\"minimum\":");
      Serial.print(temp.min);
      Serial.print(",\"maximum\":");
      Serial.print(temp.max);
      Serial.print("},");
      
      Serial.print("\"humidity\":{\"actual\":");
      Serial.print(hum.act);
      Serial.print(",\"average\":");
      Serial.print(hum.avg);
      Serial.print(",\"minimum\":");
      Serial.print(hum.min);
      Serial.print(",\"maximum\":");
      Serial.print(hum.max);
      Serial.print("},");
      
      Serial.print("\"hic\":{\"actual\":");
      Serial.print(hic.act);
      Serial.print(",\"average\":");
      Serial.print(hic.avg);
      Serial.print(",\"minimum\":");
      Serial.print(hic.min);
      Serial.print(",\"maximum\":");
      Serial.print(hic.max);
      Serial.print("}");

      Serial.println("}");
    }
  }

  if (frontUp)
    lcd.backlight();
  if (frontDown)
    lcd.noBacklight();

  if (readOK && btnAct == HIGH && time - tPrintData.last_shot >= tPrintData.delta) {
    tPrintData.last_shot = time;
  // if (readOK && isToShot(&tPrintData, time)) {
    printMisura(*(nextToPrint->m), nextToPrint->label, nextToPrint->unit);

    if (nextToPrint == (&pTemp))
      nextToPrint = &pHumid;
    else if (nextToPrint == (&pHumid))
      nextToPrint = &pHic;
    else if (nextToPrint == (&pHic))
      nextToPrint = &pTemp;
  }




  // // Wait a few seconds between measurements.
  // delay(2000);

  // printData(temp.act, hum.act, hic.act, 0);

  // // printData(temp.avg, hum.avg, hic.avg, 1);
  // printMisura(temp, "Tmp:", 'C');
}
