#include <Arduino.h>
#include <ArduinoBLE.h>
#include <String.h>
#define NUMBER_OF_SENSORS 1
char result[16]; // Buffer big enough for 7-character float

union sniff_data
{
  struct __attribute__( ( packed ) )
  {
    char values[10];
  };
  signed char bytes[ NUMBER_OF_SENSORS * sizeof( char ) ];
};
union sniff_data sniffTimeData;


BLEService OdorService("19B10000-E8F2-537E-4F6C-D104768A1214"); // BLE Service
//BLEService SensorService("b7290ca4-186a-46f7-b9ac-f4763557788b"); // BLE Service
BLEService SniffingService("e82f4441-15dc-44c9-93de-36014d4cee8c"); // BLE Service
//Temp Read
//humidity Read
//pressure Read
//odor on or off Read/Write
//CheckIR Read/Write
//SniffingValue Read
//SniffTime Read/write

// BLE LED Switch Characteristic - custom 128-bit UUID, read and writable by central
BLECharCharacteristic OdorSwitchCharacteristic("19B10001-E8F2-537E-4F6C-D104768A1214", BLERead | BLEWriteWithoutResponse);
BLECharCharacteristic OdorValveCharacteristic("19B10002-E8F2-537E-4F6C-D104768A1214", BLERead | BLEWriteWithoutResponse);
//BLEByteCharacteristic TempCharacteristic("b7290ca5-186a-46f7-b9ac-f4763557788b", BLERead | BLENotify);
//BLEByteCharacteristic HumidityCharacteristic("b7290ca6-186a-46f7-b9ac-f4763557788b", BLERead | BLENotify);
//BLEByteCharacteristic PressureCharacteristic("b7290ca7-186a-46f7-b9ac-f4763557788b", BLERead | BLENotify);
BLECharCharacteristic IRSwitchCharacteristic("e82f4442-15dc-44c9-93de-36014d4cee8c",  BLERead | BLEWriteWithoutResponse);
BLECharacteristic SniffTimeCharacteristic("e82f4443-15dc-44c9-93de-36014d4cee8c", BLERead | BLENotify, 16);
BLECharacteristic SniffCritCharacteristic("e82f4444-15dc-44c9-93de-36014d4cee8c", BLERead | BLEWriteWithoutResponse, 8);
BLECharCharacteristic IRReadyCharacteristic("e82f4445-15dc-44c9-93de-36014d4cee8c", BLERead | BLEWriteWithoutResponse);

const int OdorPin = LED_BUILTIN; // pin to use for the LED
long sniffTime=1000;
char ActDeactivate;
float pin;
int irpin=10;
long waittime;
long IRstart;
int exitflag;
int globalflag;
int myvalue;
long pokeStart;
float sniff;
char newSniffCrit[8];
//char pinValue[8];
char myPin;



void setup() {
  //Serial.begin(9600);
  //while (!Serial);

  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  // set advertised local name and service UUID:
  /////////////////////////////////////////////////
  BLE.setLocalName("Olfactometer3");
  ////////////////////////////////////////////////
  BLE.setAdvertisedService(OdorService);
  //BLE.setAdvertisedService(SensorService);
  BLE.setAdvertisedService(SniffingService);

//  pinMode(RED_PIN, OUTPUT); 
  //digitalWrite(RED_PIN, LOW);
  pinMode(irpin, INPUT_PULLUP);
  
  // add the characteristic to the service
  OdorService.addCharacteristic(OdorSwitchCharacteristic);
  OdorService.addCharacteristic(OdorValveCharacteristic);
  //SensorService.addCharacteristic(TempCharacteristic);
  //SensorService.addCharacteristic(HumidityCharacteristic);
  //SensorService.addCharacteristic(PressureCharacteristic);
  SniffingService.addCharacteristic(IRSwitchCharacteristic);
  SniffingService.addCharacteristic(SniffTimeCharacteristic);
  SniffingService.addCharacteristic(IRReadyCharacteristic);
  SniffingService.addCharacteristic(SniffCritCharacteristic);

  // add service
  BLE.addService(OdorService);
 // BLE.addService(SensorService);
  BLE.addService(SniffingService);

  // set the initial value for the characeristic:
  OdorSwitchCharacteristic.writeValue('0');
  IRSwitchCharacteristic.writeValue('0');
  IRReadyCharacteristic.writeValue('0');
  
  strncpy(result, "NEW", 16);
  //result [0]='0';
  SniffTimeCharacteristic.writeValue((unsigned char *)result, 16);

  // start advertising
  BLE.advertise();

  Serial.println("Olfactometer 1 Advertising");
}

void loop() {
  // listen for BLE peripherals to connect:
//  digitalWrite(RED_PIN, LOW);
  BLEDevice central = BLE.central();

  // if a central is connected to peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    // print the central's MAC address:
    Serial.println(central.address());

    // while the central is still connected to peripheral:
    while (central.connected()) {
      
      // Look for an Odor valve activation Request
      if (OdorSwitchCharacteristic.written()) {
          ActDeactivate = OdorSwitchCharacteristic.value();
          
          if (ActDeactivate=='1'){
            Serial.print("Turn ON ");
            ActivateValve();
          }
          
          else if (ActDeactivate=='2'){
            Serial.print("Turn OFF ");
            DeactivateValve();
          }
          else if (ActDeactivate=='0'){
            Serial.println("Turn all OFF");
            DeactivateAll();
          }
          } 

      checkIR();
      //Look for a sniff and update sniff time
//      if (IRSwitchCharacteristic.written()) {
//        if (IRSwitchCharacteristic.value()=='1'){
//          Serial.println("UpdatingIR");
//            IRReadyCharacteristic.writeValue('0');
//            checkIR();
//        }
//        }

      
      //Update the Sniff Criterion
      if (SniffCritCharacteristic.written()){
        SniffCritCharacteristic.readValue(newSniffCrit, 8);
        sniffTime=atof(newSniffCrit);
        Serial.println(sniffTime);
        
      }
   
      }
    }
  

    // when the central disconnects, print it out:
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());
  }


void ActivateValve()
  {
  myPin=OdorValveCharacteristic.value();
  //OdorValveCharacteristic.readValue(pinValue, 8);
  //myPin=atof(pinValue);
  Serial.println(myPin);
  
  if (myPin=='1'){
      pin=A3;
    }
   else if(myPin=='2'){
      pin=A2;
    }
   else if(myPin=='3'){
      pin=A1;
    }
   else if(myPin=='4'){
      pin=A0;
    }
   else if(myPin=='5'){
      pin=13;
    }
   else if(myPin=='6'){
      pin=12;
    }

    else if(myPin=='7'){
      pin=2;
    }
    else if(myPin=='8'){
      pin=3;
    }
    else if(myPin=='9'){
      pin=4;
    }
    else if(myPin=='a'){
      pin=5;
    }
    else if(myPin=='b'){
      pin=6;
    }
    else if(myPin=='c'){
      pin=7;
    }
    else if(myPin=='d'){
      pin=8;
    }
    else if(myPin=='e'){
      pin=9;
    }
  pinMode(pin, OUTPUT);
  digitalWrite(pin, HIGH);  
}


void DeactivateValve()
{
  //Serial.println("Valve to Deactivate");
   
  myPin=OdorValveCharacteristic.value();
 // OdorValveCharacteristic.readValue(pinValue, 8);
  //myPin=atof(pinValue);
  Serial.println(myPin);
  
  if (myPin=='1'){
      pin=A3;
    }
   else if(myPin=='2'){
      pin=A2;
    }
   else if(myPin=='3'){
      pin=A1;
    }
   else if(myPin=='4'){
      pin=A0;
    }
   else if(myPin=='5'){
      pin=13;
    }
   else if(myPin=='6'){
      pin=12;
    }

    else if(myPin=='7'){
      pin=2;
    }
    else if(myPin=='8'){
      pin=3;
    }
    else if(myPin=='9'){
      pin=4;
    }
    else if(myPin=='a'){
      pin=5;
    }
    else if(myPin=='b'){
      pin=6;
    }
    else if(myPin=='c'){
      pin=7;
    }
     else if(myPin=='d'){
      pin=8;
    }
    else if(myPin=='e'){
      pin=9;
    }
    
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
}


void DeactivateAll()
{
 digitalWrite(A3, LOW);
 digitalWrite(A2,LOW);
 digitalWrite(A1,LOW);
 digitalWrite(A0,LOW);
 digitalWrite(13,LOW);
 digitalWrite(12,LOW);
 digitalWrite(2,LOW);
 digitalWrite(3,LOW);
 digitalWrite(4,LOW);
 digitalWrite(5,LOW);
 digitalWrite(6,LOW);
 digitalWrite(7,LOW);
 digitalWrite(8,LOW);
 digitalWrite(9,LOW);
}


void checkIR(){
  waittime=5;
  exitflag=0;
  IRstart=millis();
  globalflag=0;

  while (exitflag==0){
  
  if (millis()-IRstart> waittime){
    //sniff=0;
    //sprintf(result,"%f", sniff);
    //SniffTimeCharacteristic.writeValue((unsigned char *)result, 16);
    //Serial.println(SniffTimeCharacteristic.value());
    //Serial.println(result);
    //IRReadyCharacteristic.writeValue('1');
    //sniffTimeData.values[0]=1;
    //SniffTimeCharacteristic.writeValue(sniffTimeData.bytes, sizeof sniffTimeData.bytes);
    //SniffTimeCharacteristic.writeValue('1');
    exitflag=1;
  }
  
  if(digitalRead(irpin)==LOW){
    pokeStart=millis(); //Record Time of start of poke
    //Serial.println("Started a poke");
    exitflag=0;
    //Go into a loop unitl
    while (exitflag==0){
    
    //Dog either removes their nose 
      if (digitalRead(irpin)==HIGH){
        //Print out the length of nose hold
        Serial.println(millis()-pokeStart);
        sniff=millis()-pokeStart;
        sprintf(result,"%f", sniff);
        SniffTimeCharacteristic.writeValue((unsigned char *)result, 16);
        IRReadyCharacteristic.writeValue('1');
        //sniffTimeData.values[0]=sniff;
        //SniffTimeCharacteristic.writeValue(sniffTimeData.bytes, sizeof sniffTimeData.bytes);
        //SniffTimeCharacteristic.writeValue(sniff);
        //Serial.println(SniffTimeCharacteristic.value());
        Serial.println(result);
        exitflag=1;
        }
    
    //or Holds nose in 4s 
      if (millis()-pokeStart>sniffTime){ 
        //Print out the length of nose hold
        Serial.println(millis()-pokeStart);
        sniff=millis()-pokeStart;
        sprintf(result,"%f", sniff);

        //sniffTimeData.values[0]=sniff;
        SniffTimeCharacteristic.writeValue((unsigned char *)result, 16);
        //SniffTimeCharacteristic.writeValue(sniffTimeData.bytes, sizeof sniffTimeData.bytes);
        //Serial.println(SniffTimeCharacteristic.value());
        Serial.println(result);
        IRReadyCharacteristic.writeValue('1');
        exitflag=1;
      }
      }}
      //Signal sent to stop

      }}
