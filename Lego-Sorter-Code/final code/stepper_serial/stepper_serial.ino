
# define stepPin2 4
# define dirPin2 7

# define enable 8

# define stepPin 2
# define dirPin 5

int count = 0;
bool count_dir = true;

int carrier_pos = 0;
int car_goal_pos = 545;
int count2 = 0;
bool count_dir2 = true;
bool dir2 = true;
int digit = -10;
int speed = 55;

int timeout = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  
  pinMode(stepPin,OUTPUT);
  pinMode(dirPin, OUTPUT);
  digitalWrite(dirPin, LOW);

  pinMode(enable, OUTPUT);
  digitalWrite(enable, LOW);

  pinMode(stepPin2,OUTPUT);
  pinMode(dirPin2, OUTPUT);
  digitalWrite(dirPin2, HIGH);


  
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {

    char inByte = (Serial.read());
    //Serial.println(inByte);
    digit = inByte - '0';
    //Serial.println(digit*600);
    car_goal_pos = digit*565;
    speed = 55;
    
    
  }

  

  
  count += 1;
  count2 += 1;
  
  if (count > 75){
    count = 0;
    if (digit != -11){
        if (count_dir == true){
          digitalWrite(stepPin, HIGH);
          count_dir = false;
        }else{
          digitalWrite(stepPin, LOW);
          count_dir = true;
        }
    }
  }

  
  

  if (carrier_pos > car_goal_pos){
    if (count2 > speed){
      speed  -=0.0000018;
      count2 = 0;
      carrier_pos -=1;
      digitalWrite(dirPin2, LOW);
      if (count_dir2 == true){
        digitalWrite(stepPin2, HIGH);
        count_dir2 = false;
      }else{
        digitalWrite(stepPin2, LOW);
        count_dir2 = true;
      }
    }
  }
   
   if (carrier_pos < car_goal_pos){
    if (count2 > speed){
      speed  -=0.0000018;
      count2 = 0;
      carrier_pos +=1;
      digitalWrite(dirPin2, HIGH);
      if (count_dir2 == true){
        digitalWrite(stepPin2, HIGH);
        count_dir2 = false;
      }else{
        digitalWrite(stepPin2, LOW);
        count_dir2 = true;
      }
    }
  }

      

   

  

  
   
  
    

    
  


  


  

   

   

   
   
  

 
 

}
