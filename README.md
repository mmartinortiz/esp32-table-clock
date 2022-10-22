# ESP32 Table Clock

See how to build it at [Make Projects](https://makeprojects.com/project/table-clock?projectid=97666&r=qecwv).

## Credits

This project was possible to the following libraries:

- [tm1637](https://github.com/mcauser/micropython-tm1637)
- [Rotary encoder](https://github.com/miketeachman/micropython-rotary)

## Install

This program has been developed using Micro Python and runs in the ESP32 board. My first attempt was to make it run in a Raspberry Pico W, but I [run into problems](https://forums.raspberrypi.com/viewtopic.php?t=341203) with the timer. If you know how to solve it, please let me know.

For installing MicroPython into the ESP32 follow the [official documentation](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html). Once Micro Python is loaded into the ESP32, you can upload the project files with the `mpremote` tool. You can instal `mpremote` locally using [pipx](https://pypa.github.io/pipx/).

To upload the files, use:

```bash
mpremote cp main.py :
mpremote cp rotary.py :
mpremote cp rotary_irq.py :
mpremote cp tm1637.py :
```

Before you upload the file `secrets.txt`, edit the file and replace the current content with your WiFi SSID and your WiFi's password. **Make sure they are separated by a ,**.

```bash
mpremote cp secrets.txt :
```

For debugging, you can run the local copy of `main.py` into the ESP32 with the following command

```bash
mpremote run --follow main.py
```

Then you can see you debug traces with

```bash
mpremote
```

Enjoy!

