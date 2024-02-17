/*
RaspiDevKit v1.0.0
This code is autogenerated by raspidevkit
The following libraries may be required to compile to code:

*/

$header

int currentCommand = -1;

void setup(){
    Serial.begin($baudrate);
    $setup
}

void loop(){
    if(currentCommand == -1){
        recieveCommand();
    } 
    
    $loop
}

/*
 * Recieve command from Raspberry Pi 
*/
void recieveCommand(){
    if(Serial.available()){
        int sent = Serial.readStringUntil("$cmd_terminator").toInt();
        Serial.print("ok$cmd_terminator");
        currentCommand = sent;
    }
}

/*
 * Recieve data from Raspberry Pi 
*/
String recieveData(){
    while(!Serial.available()){}
    String data = Serial.readStringUntil("$data_terminator");
    data.replace("$whitespace_sub", " ");
    Serial.print("ok$data_terminator");
    return data;
}

/*
 * Send response to Raspberry Pi 
*/
void sendResponse(String response){
    Serial.print(response + "$data_terminator");
}

$methods