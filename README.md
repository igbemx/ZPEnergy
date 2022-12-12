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

Attributes arithmetic:
Downstream values are more positive and the upstream are more negative, respectively.
Position = EnsambleAxis1_Position - dial_offset (device property)
Position = FocalDist + ZP_A0

Manual syncronization of the Tolek's STXM control and SoftiZPEnergy device numbers 
----------------------------------------------------------------------------------

- Tolek's STXM program changes only the 'Position' attribute of the SoftiZPEnergy tango device
- The A0 values doesn't have to be the same in both programs
- The easiest way to syncronize the programs is to:
  1) Select a certain energy, e.g. 700 eV in Tolek's program, so that the ZP move to the corresponding position.
  2) The 'Energy' value in SoftiZPEnergy device may deviate now from the value selected in Tolek's program.
  3) Adjust the A0, so that the currently displayed in the device energy would coincide with the actual energy selected at the beginning.
  4) That is it, the devices should be in sync now.

