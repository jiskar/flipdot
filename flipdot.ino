// Written by Jiskar (jiskar.nl), 2016

//
// Script for controlling a Krueger DOT-matric (flip-dot) sign using the IBIS protocol.
// Tested and working on a Krueger 16x80 from 2001 with an MX3 control board.
// This code is writting for a Particle Photon. 
// Connection to the board: the serial interface requires 19V logic. Photon pin D6 is connected to a transistor switching the data line between 19V and ground
//

#include "HttpClient/HttpClient.h"

int sendPin = D6;              // LED connected to D7
int LED = D7;
int i = 0;
int j =0;
String currentSentence = "";
HttpClient http;

// Headers currently need to be set at init, useful for API keys etc.
http_header_t headers[] = {
    //  { "Content-Type", "application/json" },
    //  { "Accept" , "application/json" },
    { "Accept" , "*/*"},
    { NULL, NULL } // NOTE: Always terminate headers will NULL
};

http_request_t request;
http_response_t response;


void setup() {
     pinMode(sendPin, OUTPUT);    // sets pin as output
     pinMode(LED, OUTPUT);    // sets pin as output
     Particle.subscribe("flipdotdirect", directControl);
     Particle.subscribe("flipdottext", setText);
     Particle.publish("flipdotboard has started");
}


void loop() {
    delay(2500);
    request.hostname = "flipdot.herokuapp.com";
    request.port = 80;
    // request.path = "/day/" + String(j);
    request.path = "/output";

    http.get(request, response, headers);
    if (response.body != currentSentence){
        currentSentence = response.body;
        setText("flipdottext", response.body);
    }

    //counter for looping through words
    // j++;  // counter
    // if (j == 10){
        // j=0;
    // }
}

void directControl(const char *event, const char *data) {
    // sends a give string directly to the board, usefull when doing external formatting
    i++;
    String sentence = String(data);
    Particle.publish("eventData:", sentence);
    Particle.publish("length:", String(sentence.length()));
    writeString(sentence, sentence.length());
}


void setText(const char *event, const char *data) {
    // adds formatting characters to a string and sends it to the board
    i++;
    String sentence = String(data);
    String controlchars;
    int length = sentence.length();

    //set number of lines and text size
    if (length < 10){
        controlchars = "\n.BI@MBI@M      ";   //single row, big font
    }else if (length < 13){
        controlchars = "\n.AI@MBI@M      ";   //single row, medium font   
    }else if (length < 16){
        controlchars = "\n.CI@MBI@M      ";   //single row, small font
    }else{
        String firstRow = sentence.substring(0,12);
        String secondRow = sentence.substring(12, 24);
        sentence = firstRow + "    " + secondRow;
        controlchars = "\n.IIAIBI@M      ";  // two rows
    }
    
    // length = sentence.length();
    sentence = "zA5" + sentence;  // add message type
    for (int h=0; h < (64 - length); h++){
        sentence += ' ';  // fill out with spaces until string is exactly 64 characters
    }
    sentence += controlchars;

    writeString(sentence, sentence.length());
    loop();
}


void writeString(String sentence, int length) {
    //sends a command-string to the flipdotboard
    
    char parity = 0x46;
    char parityByte = 0x7F; //parity calculation starts with 0x46 according to IBIS specs
    char current;
    
    for(int nnn=0; nnn < length; nnn++){
        current = sentence.charAt(nnn);
        writeByte(current);
        parityByte = parityByte ^ current;
    }
    
    writeByte(0x0D);
    parityByte = parityByte ^ 0x0D;
    // Particle.publish("PARITY:", String(parityByte));
    writeByte(parityByte);
}


void writeByte(uint8_t c) {
    // bitbangs byte out with 7bits, two stop bits and an even parity bit

    digitalWrite(LED, HIGH);  // to indicate sending
    int periodMicroSecs = 833;  // 1200 baud
    bool parity = 0;
    
    // start bit:
    writePin(LOW);
    delayMicroseconds(periodMicroSecs); 
    
    // 7 bits of data:
    for(uint8_t b = 0; b < 7; b++){
      writePin(c & 0x01);
      
      parity = parity ^ (c & 0x01);
      c >>= 1;
      delayMicroseconds(periodMicroSecs);
    }
    
    // even parity bit
    if(parity) {
        writePin(HIGH);
    }
    else {
        writePin(LOW);
    }
    delayMicroseconds(periodMicroSecs);
    
    // two stop bits
    writePin(HIGH);
    delayMicroseconds(periodMicroSecs*2);
    
    digitalWrite(LED, LOW);
    };
        
void writePin(bool value) {
      if(value)
      {
        pinResetFast(sendPin);
      }
      else
      {
        pinSetFast(sendPin);
      }
    };  