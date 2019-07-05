# lifx-adapter

LIFX smart bulb adapter for Mozilla WebThings Gateway.

Largely derived from https://github.com/mozilla-iot/tplink-adapter

There are no settings, the adapter will automatically discover any LIFX bulbs on the same local network, and you can then add them individually.

Bulb names are reported by the LIFX API, so they should automatically show up in the gateway web interface if you have set names for them in the LIFX app.


# Supported Devices

## Tested and Working

* Mini Day & Dusk
* A19

## Untested but _Should Work_
 
* All other LIFX bulbs

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

# Troubleshooting

If you encounter a `DistutilsOptionError` when building the package, the error
is caused by the packaged version of `pip` that comes with Debian based Linux
distributions, including Raspbian.  The upstream version of `pip` does not have
this problem.

The simplest fix is to "upgrade" `pip`:

    pip3 install --upgrade pip

Note that this won't actually upgrade the *packaged* version, which will be left
alone, but will instead install the upstream version of `pip` to
`/usr/local/bin/pip3`. As long as `/usr/local/bin` appears first in `$PATH`,
scripts will use that upstream version instead.
