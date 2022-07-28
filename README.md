# Zone plate energy tango device 

Tango device for the ZPEnergy tango device. This device can be placed on top of any other Tango motor.

This device has the following properties:

| Property | Description | Value example | Type |
| ------ | ------ | ------ | ------ |
| AbsXSign | Sign of the X sample axis (not fully implemented) | "-1" | "DevShort" |
| AbsYSign | Sign of the Y sample axis (not fully implemented) | "1" | "DevShort" |
| dial_offset | Dial position offset | "8.2" | "DevDouble" |
| zp_tango_motor | Tango device name of the upper layer motor | "B318A-EA01/CTL/EnsambleAxis1" | "DevString" |
| zp_unit_coeff | Position unit conversion coefficient | "1000.0" | "DevDouble" |
| PandaHost | PandaBox host name | "b-softimax-panda-0" | "DevString" |
| PandaPort | PandaBox control port number | "8888" | "DevShort" |


How to install
--------------

If you push your package on testing repo do:

```
  sudo yum makecache --enablerepo=maxiv-testing\*
  sudo yum install tangods-softimax-zpenergy --enablerepo=maxiv-testing\*
```

If you push on master branch do:

```
  sudo yum makecache
  sudo yum install tangods-softimax-zpenergy
```

How to run after package installation
-------------------------------------

After you install the package, on your terminal you can do:

```
  SoftiZPEnergy B318A-CTL
```
It is important that the following attribute properties are set manually in Jive:
- Defocus/__value 
- DialPos/__value
- Energy/__value
- FocalDist/__value
- Position/__value
- UserPos/__value
- ZP_A0/__value
- ZP_A1/__value
- ZP_Diam/__value
- ZP_width/__value


They have to be normally initiallized with the respective values before starting the device server for the very first time, after that they are updated via the device.

