# lifx-adapter

Lifx smart bulb adapter for Mozilla IoT Gateway.

Largely derived from https://github.com/mozilla-iot/tplink-adapter

There are no settings, the adapter will automatically discover any Lifx bulbs on the same local network, and you can then add them individually.

Bulb names are reported by the Lifx API, so they should automatically show up in the gateway web interface if you have set names for them in the Lifx app.


# Supported Devices

## Tested and Working

* A19 dusk-to-dawn
    * Represented as `dimmableColorLight`
        * `colorTemperature` property for white temperature
        * `level` property for brightness

## Untested but _Should Work_
 
* All other Lifx bulbs
    * Represented as `dimmableColorLight` or `dimmableLight` based on their self-reported color and white temperature abilities

# Requirements

If you're running this add-on outside of the official gateway image for the Raspberry Pi, i.e. you're running on a development machine, you'll need to do the following (adapt as necessary for non-Ubuntu/Debian):

```
sudo apt install python3-dev libnanomsg-dev
sudo pip3 install nnpy
sudo pip3 install git+https://github.com/mozilla-iot/gateway-addon-python.git
```


# Installing for development

Clone this repo inside `~/.mozilla-iot/addons/` and run the packaging script:

```
cd ~/.mozilla-iot/addons

git clone https://github.com/infincia/lifx-adapter.git

./package.sh
```

Then restart the gateway and the Lifx addon should be available. 

