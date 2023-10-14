## **Installing PBX Software**

You will need:

 - micro sd card
 - raspberry pi 4
 - computer that can write to a micro sd card (may require adapter)

### **Instructions**

 1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to your computer that can write to an sd card 
 2. Open Raspberry Pi Imager and insert your sd card
 3. Write the default Raspberry Pi Image to the sd card (Raspberry Pi OS 32 bit)
 4. Once done and verified safely eject the sd card and insert it into the Raspberry PI
 5. Plug your Raspberry Pi in with a 5V supply and a hdmi cable to a monitor. Go through the prompted setup.
 6. Once the Raspberry Pi has been setup open a Terminal program. 
 7. Perform a update `sudo apt update && sudo apt upgrade`
 8. ensure wget is installed `sudo apt install wget`
 9. Follow the guide [here](https://www.dslreports.com/forum/r30661088-PBX-FreePBX-for-the-Raspberry-Pi) to install the pbx software
 10. We used Vonage as a SIP provider adding the following config for [Asterisk PBX](https://developer.vonage.com/en/voice/sip/configure/asterisk)

