import time
import struct
import board
from digitalio import DigitalInOut
import analogio
from circuitpython_nrf24l01.rf24 import RF24
import busio
import displayio
import adafruit_ssd1306
import keypad



#
# CONFIG SECTION
#

# Address must be the same line as in DaedalusProtogen/config.py
nrfAddress = [b"DAED1", b"DAED2"]

# packetID must also be the same as in DaedalusProtogen/config.py
packetID = "ALUS"

# change these (digital output) pins accordingly
# these are all set for the interposer board in the repo
CE_PIN  = DigitalInOut(board.D13)
CSN_PIN = DigitalInOut(board.D4) # change to D5 once hardware comes in
#BTN_PIN = DigitalInOut(board.D9)





SPI_BUS = board.SPI()  # init spi bus object

# initialize the nRF24L01 on the spi bus object
nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)

nrf.pa_level = -12

nrf.open_tx_pipe(nrfAddress[0])  # always uses pipe 0
nrf.open_rx_pipe(1, nrfAddress[1])  # using pipe 


payload = ["00"]




def master(count=0):  # count = 5 will only transmit 5 packets
    """Transmits an incrementing integer every second"""
    nrf.listen = False  # ensures the nRF24L01 is in TX mode
    with keypad.Keys(
        (board.D24, board.D6), value_when_pressed=False, pull=True) as buttons:
        while True:
            buttonsEvent = buttons.events.get()
            if buttonsEvent and buttonsEvent.pressed:
                buttonNumber = buttonsEvent.key_number
                if buttonNumber == 0:
                    # use struct.pack to structure your data
                    # into a usable payload
                    payload[0] = packetID + str(count)
                    buffer = struct.pack("<6s", payload[0])
                    # "<f" means a single little endian (4 byte) float value.
                    start_timer = time.monotonic_ns()  # start timer
                    result = nrf.send(buffer)
                    end_timer = time.monotonic_ns()  # end timer
                    if not result:
                        print("send() failed or timed out")
                    else:
                        print(
                            "Transmission successful! Time to Transmit:",
                            "{} s. Sent: {}".format((end_timer - start_timer) / 1000000000, payload[0]),
                        )

                    if (count >=3):
                        count = 0
                    else:
                        count += 1
            else:
              time.sleep(.1)

while (True):
    master()