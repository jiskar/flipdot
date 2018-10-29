// Written by Jiskar (jiskar.nl), 2016

//
// Script for controlling a Krueger DOT-matrix (flip-dot) sign with a Particle Photon.
// The interface to the board is a 19V serial interface (one direction) using the IBIS protocol.
// Hardware: the serial interface requires 19V logic. Photon pin D6 is connected to a transistor switching the data line between 19V and ground
// Tested and working on a 2001 Krueger 16x80 with an MX3 control board.
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
    { "Accept" , "*/*"},
    { NULL, NULL } // NOTE: Always terminate headers will NULL
};

http_request_t request;
http_response_t response;


void setup() {
     pinMode(sendPin, OUTPUT);    // serial interface to the krueger board
     pinMode(LED, OUTPUT);
     Particle.subscribe("flipdotdirect", directControl, MY_DEVICES);
     Particle.subscribe("flipdottext", setText, MY_DEVICES);
     Particle.publish("flipdotboard has started");
}


// main loop
void loop() {

    // poll my server for a textstring:
    request.hostname = "flipdot.herokuapp.com";
    request.port = 80;
    request.path = "/output";
    http.get(request, response, headers);
    Particle.publish("http response:", response.body); // for debugging

    // if the string was updated, send it to the board:
    if (response.body != currentSentence){
        currentSentence = response.body;
        setText("flipdottext", response.body);
    }

    delay(2500);

}

void directControl(const char *event, const char *data){
    // sends a given string directly to the board, usefull when doing external formatting. NB: will only work if you include the correct control characters.
    i++;
    String sentence = String(data);
    Particle.publish("eventData:", sentence);
    Particle.publish("length:", String(sentence.length()));
    writeString(sentence, sentence.length());
}


void setText(const char *event, const char *data){
    // sends a string to the board. This function adds all the needed control characters and then calls the serial routines to transmit the data to the board.

    String sentence = String(data);
    String controlchars;
    int length = sentence.length();
    Particle.publish("setting text:", sentence);

    //determine text size and number of lines
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
        controlchars = "\n.IIAIBI@M      ";  // two rows. UPDATE 2018: seems broken :(
    }
    Particle.publish("sentence:", sentence);
    sentence = "zA5" + sentence;  // add message type
    for (int h=0; h < (64 - length); h++){
        sentence += ' ';  // fill out with spaces until string is exactly 64 characters
    }
    sentence += controlchars;

    writeString(sentence, sentence.length());  // send data to board
    loop(); // return to main loop
}



void writeString(String sentence, int length){
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


void writeByte(uint8_t c){
    // bitbangs a byte out with 7bits, two stop bits and an even parity bit

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


void writePin(bool value)
    // sends a bit to the serial pin
    {
      if(value)
      {
        pinResetFast(sendPin);
      }
      else
      {
        pinSetFast(sendPin);
      }
    };