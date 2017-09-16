/*
  Clignotement:
    LED 13 clignote dans boucle principale
    LED 12 clignote via débordement TIMER 2
  Différents examples sont testés en utilisant le langage Arduino
  la manipulation de bits ou l'accès direct aux registres.

  fréquence clignotement 1 Hz donc inversion LED en 500ms
  fréquence horloge Arduino UNO: 16MHz
  pré-diviseur: 256 ==> freq timer = 16MHz/256 = 62,5KHz
  durée cycle (1/freq) = 16 us (1/62.5k)
  500 ms = 500000 us
  donc il faut 500 000 / 16 = 31250 tic horloges

  on va faire compter le timer de 0 à 250, le tout 125 fois pour
  atteindre 31250 tic (250 * 125)

  cf. http://www.locoduino.org/spip.php?article84

  date: 03/06/2017
*/

// const byte led = 12;
volatile int compteur = 0;

/* 
 *  routine interruption débordement TIMER 2
 *  flag TOV2 du registre TIFR2
 */
ISR (TIMER2_COMPA_vect) {
  compteur++;
  if (compteur > 125) { // 125 * 4 ms = 500 ms (demi-période)
    compteur = 0;
    // inversion de la LED
    // digitalWrite (led, !digitalRead (led));
    // bitSet (PINB, PB4); "1" dans PINx inverse PORTx
    PORTB ^= (1 << PB4); //PORTB ^= (1<<4);
  }
}

void setup() {
  // initialisation des sorties.
  //pinMode(LED_BUILTIN, OUTPUT);
  // bitSet (DDRB, PB5); bit 5 du PORTB
  DDRB |= (1 << PB5); // DDRB |= (1<<5);
  //pinMode (led, OUTPUT);
  // bitSet (DDRB, PB4);
  DDRB |= (1 << PB4); // DDRB |= (1<<4);
  // autre option pour configurer les 2 LEDs en même temps
  // DDRB |= (1<<PB5) | (1<<PB4);

  // désactivation interruptions GIE pour programmer timer
  SREG &= ~(1 << 7); // bitClear (SREG, 7); //noInterrupts ();
  
  // mise en mode CTC TIMER 2 WGM20/2 à zéro et WGM21 à 1
  TCCR2A &= ~(1 << WGM20); // bitClear (TCCR2A, WGM20);
  TCCR2A |= (1 << WGM21); // bitSet (TCCR2A, WGM21);
  TCCR2B &= ~(1 << WGM22); // bitClear (TCCR2B, WGM22);

  // valeur du registre de comparaison
  OCR2A = 250;

  // active interruption sur comparaison
  TIMSK2 |= (1 << OCIE2A); // bitSet (TIMSK2,TOIE2); // TIMSK2 = 0b00000001;

  // prescaler à 256 et lance le timer  (CA22/1/0 = 0 timer stoppé)  TCCR2B |= (1<<CA222) | (1<<CA21);
  TCCR2B |= (1<<CS22) | (1<<CS21);
  //TCCR2B = 0b00000110;
  
  // réactivation interruption GIE
  SREG |= (1 << 7); // bitSet (SREG, 7); // interrupts ();
}

void loop() {
  // digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN));
  // bitSet (PINB, PB5); "1" dans PINx inverse PORTx
  PORTB ^= (1 << PB5);
  delay (500);
  //    }
  //  }
}
