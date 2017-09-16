#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>

const byte led = 12;
volatile int counter = 0;

ISR (WDT_vect) {
  counter++;
}

void setup() {
  DDRB |= (1 << PB4); // pinMode (led, OUTPUT);
  PORTB &= ~(1 << PB4); // digitalWrite (led, LOW);

  /*** Setup the WDT ***/

  /* Clear the reset flag. */
  MCUSR &= ~(1 << WDRF);

  /* In order to change WDE or the prescaler, we need to
     set WDCE (This will allow updates for 4 clock cycles).
  */
  WDTCSR |= (1 << WDCE) | (1 << WDE);

  /* set new watchdog timeout prescaler value */
  WDTCSR = (1 << WDP0) | (1 << WDP3); /* 8.0 seconds */

  /* Enable the WD interrupt (note no reset). */
  WDTCSR |= _BV(WDIE);
}

void loop() {
  set_sleep_mode (SLEEP_MODE_PWR_DOWN);
  sleep_enable ();
  sleep_mode ();

  sleep_disable ();
  power_all_enable ();

  PORTB |= (1 << PB4); // digitalWrite (led, HIGH);
  delay (1000);
  PORTB &= ~(1 << PB4); //digitalWrite (led, LOW);
}
