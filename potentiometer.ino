const int potPin = 4;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  int potValue = analogRead(potPin);
  
  Serial.print("Potentiometer Value: ");
  //prints actual value it has read
  Serial.println(potValue);
  delay(250);
}
