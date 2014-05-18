#include <Wire.h>

#define startbyte 0x0F
#define I2Caddress 0x07

int sv[6]={0,0,0,0,0,0};                 // servo positions: 0 = Not Used
int sd[6]={5,10,-5,-15,20,-20};                      // servo sweep speed/direction
byte lmbrake, rmbrake;                                // left and right motor brake (non zero value = brake)
byte devibrate=50;                                   // time delay after impact to prevent false re-triggering due to chassis vibration
int sensitivity=50;                                  // threshold of acceleration / deceleration required to register as an impact
int lowbat=550;                                      // adjust to suit your battery: 550 = 5.50V
byte i2caddr=7;                                      // default I2C address of T'REX is 7. If this is changed, the T'REX will automatically store new address in EEPROM
byte i2cfreq=0;                                      // I2C clock frequency. Default is 0=100kHz. Set to 1 for 400kHz

void setup()
{
  Serial.begin(9600);
  Wire.begin();                                      // no address - join the bus as master
}


void write(int left, int right)
{
                                                     // send data packet to T'REX controller 
  MasterSend(startbyte,2,left,lmbrake,right,rmbrake,sv[0],sv[1],sv[2],sv[3],sv[4],sv[5],devibrate,sensitivity,lowbat,i2caddr,i2cfreq);
  delay(50);
  MasterReceive();                                   // receive data packet from T'REX controller
  delay(50);
}

void brake()
{
  int i = 0;
  rmbrake=1;
  lmbrake=1;
    // send data packet to T'REX controller 
  MasterSend(startbyte,2,i,lmbrake,i,rmbrake,sv[0],sv[1],sv[2],sv[3],sv[4],sv[5],devibrate,sensitivity,lowbat,i2caddr,i2cfreq);
  delay(50);
  MasterReceive();                                   // receive data packet from T'REX controller
  delay(50);
  rmbrake=0;
  lmbrake=0;
}

void loop() {
  static int l = 0;
  static int r = 0;
  static int side = 0;
  static int multip = 1;
    if ( Serial.available()) {
      char ch = Serial.read();
  
      switch(ch) {
        case '0'...'9':
          if (side==0) {
            l = l * 10 + ch - '0';
            l = multip * abs(l);
          }else{
            r = r * 10 + ch - '0';
            r = multip * abs(r);
          }
          break;
        case '-':
          multip=-1;
          break;
        case ',':
          side = 1;
          multip=1;
          break;
        case 'S':
          Serial.println(l);
          Serial.println(r);
          write(l, r);
          l = 0;
          r = 0;
          side = 0;
          break;
        case 'B':
          brake();
          break;
      }
    }
  }
\



