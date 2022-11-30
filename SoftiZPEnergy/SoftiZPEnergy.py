# -*- coding: utf-8 -*-
#
# This file is part of the SoftiZPEnergy project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Zone plate energy motor

This device implements zone plate positioning for the selected energy.
"""

# PyTango imports
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import AttrQuality, DispLevel, DevState
from tango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(ZPEnergy.additionnal_import) ENABLED START #
import socket
import math
from scipy.constants import c, elementary_charge
from tango import Database
Planck = 4.136*10**(-15)
# PROTECTED REGION END #    //  ZPEnergy.additionnal_import

__all__ = ["SoftiZPEnergy", "main"]


class SoftiZPEnergy(Device):
    """
    This device implements zone plate positioning for the selected energy.

    **Properties:**

    - Device Property
        zp_tango_motor
            - Tango device of the ZP motor
            - Type:'DevString'
        zp_unit_coeff
            - ZP unit coefficient:\n[microns] = [motor_units] * zp_unit_coeff
            - Type:'DevDouble'
        dial_offset
            - Type:'DevDouble'
        PandaHost
            - Type:'DevString'
        PandaPort
            - Type:'DevShort'
        AbsXSign
            - Type:'DevShort'
        AbsYSign
            - Type:'DevShort'
    """
    # PROTECTED REGION ID(SoftiZPEnergy.class_variable) ENABLED START #
    def _get_panda_ctrl_socket(self):
        try:
            panda_ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            panda_ctrl_sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            panda_ctrl_sock.settimeout(1)
            panda_ctrl_sock.connect((self.PandaHost, self.PandaPort))
            return panda_ctrl_sock
        except Exception as e:
            print('Problem connecting to the PandaBox control port: ', e)

    def _read_block_value(self, argin, ctrl_socket=None):
        try:
            if not ctrl_socket:
                panda_ctrl_sock = self._get_panda_ctrl_socket()
            else:
                panda_ctrl_sock = ctrl_socket
            panda_ctrl_sock.sendall(bytes(argin + '\n', 'ascii'))
            argout = panda_ctrl_sock.recv(4096).decode()
            #log.debug(f'argout in _read_block_value is: {argout}')
            return argout
        except Exception as e:
            log.debug('A problem when sending a query to the PandaBox occured: {e}')
        finally:
            if not ctrl_socket:
                log.debug(f'Closing panda_ctrl_sock, {panda_ctrl_sock}')

    def _read_abs_pos(self, ctrl_socket):
        try:
            abs_x = self._read_block_value('INENC1.VAL?',
                                                    ctrl_socket=ctrl_socket)
            abs_y = self._read_block_value('INENC2.VAL?',
                                                    ctrl_socket=ctrl_socket)

            _, abs_x = abs_x.split('=')
            _, abs_y = abs_y.split('=')

            return (int(abs_x), int(abs_y))
        except Exception as e:
            log.debug(f'A problem in _read_abs_pos occured: {e}')

    def calc_focus(self, zp_diam, zone_width, enrg):
        # Calculates the focal distance for the given energy, ZP diam, and the outer zone width #
        try:
            focus = (enrg * zp_diam * zone_width) / (Planck * (c * 1 * 10**6))
            print('calc_focus() call', focus)
            return focus
        except Exception as e:
            print('calc_focus failed', e)
            focus = 0
        return focus

    def calc_energy(self, focus, zp_diam, zone_width):
        try:
            energy = (Planck * (c * 1 * 10**6) * focus) / (zp_diam * zone_width) # all should be in microns, including the c
            # print('calc_energy() call, energy:', energy)
            return energy
        except Exception as e:
            print (e)
            return 0

    def calc_a1(self, zp_diam, zone_width, energy=700):
        focal_dist = self.calc_focus(zp_diam, zone_width, energy)
        a1 = focal_dist / energy
        print(f'zp_diam: {zp_diam}, zone_width: {zone_width}, energy: {energy}')
        print(f'Calculated focal distance at {energy} eV is: {focal_dist}')
        print(f'Calculated A1 is: {a1}')
        return a1

    def read_attr_hardware(self, attrs):
        self.__position = (self.zp_dev.Position - self.dial_offset) * self.zp_unit_coeff
        # Read sample position from the interferometer
        abs_x, abs_y = self._read_abs_pos(self.panda_ctrl_sock)
        self.__sample_x, self.__sample_y = abs_x*self.AbsXSign/1000, abs_y*self.AbsYSign/1000 # all values in microns

    # PROTECTED REGION END #    //  SoftiZPEnergy.class_variable
    # -----------------
    # Device Properties
    # -----------------

    zp_tango_motor = device_property(
        dtype='DevString',
        default_value="B318A/CTL/DUMMY-01"
    )

    zp_unit_coeff = device_property(
        dtype='DevDouble',
        default_value=1000
    )

    dial_offset = device_property(
        dtype='DevDouble',
        default_value=0.0
    )

    PandaHost = device_property(
        dtype='DevString',
        default_value="b-softimax-panda-0"
    )

    PandaPort = device_property(
        dtype='DevShort',
        default_value=8888
    )

    AbsXSign = device_property(
        dtype='DevShort',
        default_value=1
    )

    AbsYSign = device_property(
        dtype='DevShort',
        default_value=1
    )

    # ----------
    # Attributes
    # ----------

    Position = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        unit="micron",
        memorized=True,
    )

    Energy = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
        unit="eV",
        memorized=True,
        hw_memorized=True,
    )

    FocalDist = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
        unit="micron",
        memorized=True,
    )

    ZP_A0 = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        unit="micron",
        memorized=True,
    )

    ZP_A1 = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        memorized=True,
        hw_memorized=True,
    )

    ZP_Diam = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        unit="micron",
        memorized=True,
        hw_memorized=True,
    )

    ZP_width = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        memorized=True,
        hw_memorized=True,
    )

    Defocus = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
        unit="micron",
        memorized=True,
    )

    SampleX = attribute(
        dtype='DevDouble',
    )

    SampleY = attribute(
        dtype='DevDouble',
    )

    XTiltCorrectVal = attribute(
        dtype='DevDouble',
    )

    TiltCorrectOn = attribute(
        dtype='DevBoolean',
        access=AttrWriteType.READ_WRITE,
    )

    XTilt = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
    )

    XTiltCorrectSign = attribute(
        dtype='DevShort',
        access=AttrWriteType.READ_WRITE,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the SoftiZPEnergy."""
        Device.init_device(self)
        # PROTECTED REGION ID(SoftiZPEnergy.init_device) ENABLED START #
        try:
            prop_names = ['Energy', 'DialPos', 'ZP_A0', 'ZP_A1']
            self.db = Database()
            props = self.db.get_device_attribute_property(self.get_name(), prop_names)
        except BaseException as e:
            print(e)
            print('Problem extracting the previous values from the database!')

        self.__energy = float(props['Energy']['__value'][0])
        # self.__focal_dist = 0.0
        self._zp__a0 = float(props['ZP_A0']['__value'][0])
        self._zp__a1 = float(props['ZP_A1']['__value'][0])
        self._zp__diam = 0.0
        self._zp_width = 0.0
        self.__position = 0.0
        self.__defocus = 0.0

        self._calc_a1 = 0.0

        self.__sample_x = 0.0
        self.__sample_y = 0.0

        self.__x_tilt_correct_sign = 1
        self.__x_tilt_correct_val = 0
        self.__x_tilt = 0
        self.__x_tilt_correct_on = False
        self.__sample_x_0 = 0
        self.__sample_dx = 0
        self.__x_tilt_correct_on = False

        try:
            self.zp_dev = tango.DeviceProxy(self.zp_tango_motor)
            print('motor position of the EnsembleAxis1 at the beginning is:', self.zp_dev.Position)
            print('motor position at the beginning with the dial offset (position  dial_offset):', self.zp_dev.Position - self.dial_offset)
        except BaseException as e:
            print(e)
            self.set_state(DevState.FAULT)
        
        self.__position_0 = (self.zp_dev.Position - self.dial_offset) * self.zp_unit_coeff

        try:
            self.panda_ctrl_sock = self._get_panda_ctrl_socket()
        except Exception as e:
            log.debug(f'Problem obtaining panda_ctrl_sock: {e}')

        self.set_state(DevState.ON)
        # PROTECTED REGION END #    //  SoftiZPEnergy.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(SoftiZPEnergy.always_executed_hook) ENABLED START #
        # self._calc_a1 = self.calc_a1(self._zp__diam, self._zp_width)
        self.__sample_dx = self.__sample_x - self.__sample_x_0
        self.__x_tilt_correct_val = self.__sample_dx * math.tan(math.radians(self.__x_tilt))
        if self.__x_tilt_correct_on:
            new_position = self.__position_0 + self.__x_tilt_correct_sign*self.__x_tilt_correct_val
            self.zp_dev.Position = new_position / self.zp_unit_coeff + self.dial_offset
        # PROTECTED REGION END #    //  SoftiZPEnergy.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(SoftiZPEnergy.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  SoftiZPEnergy.delete_device
    # ------------------
    # Attributes methods
    # ------------------

    def read_Position(self):
        # PROTECTED REGION ID(SoftiZPEnergy.Position_read) ENABLED START #
        """Return the Position attribute."""
        return self.__position
        # PROTECTED REGION END #    //  SoftiZPEnergy.Position_read

    def write_Position(self, value):
        # PROTECTED REGION ID(SoftiZPEnergy.Position_write) ENABLED START #
        """Set the Position attribute."""
        if self.__x_tilt_correct_on:
            correction_on = True
            self.__x_tilt_correct_on = False
        else:
            correction_on = False
        self.__position_0 = value
        self.zp_dev.Position = value / self.zp_unit_coeff + self.dial_offset
        self.__focal_dist = value - self._zp__a0 - self.__defocus
        self.db.put_device_attribute_property(self.get_name(), {'Position': {'Position': value}})
        if correction_on:
            self.__x_tilt_correct_on = True

        # PROTECTED REGION END #    //  SoftiZPEnergy.Position_write

    def read_Energy(self):
        # PROTECTED REGION ID(SoftiZPEnergy.Energy_read) ENABLED START #
        """Return the Energy attribute."""
        try:
            #energy = self.calc_energy(self.__focal_dist * -1, self._zp__diam, self._zp_width)
            self.__energy = self.__focal_dist / self._zp__a1 * -1
            return self.__energy
        except Exception as e:
            print('Error in read_Energy', e)
            return 0
        # PROTECTED REGION END #    //  SoftiZPEnergy.Energy_read

    def write_Energy(self, value):
        # PROTECTED REGION ID(SoftiZPEnergy.Energy_write) ENABLED START #
        """Set the Energy attribute."""
        self.__focal_dist = self._zp__a1 * value * -1
        self.zp_dev.Position = (self.__focal_dist + self._zp__a0 + self.__defocus) / self.zp_unit_coeff + self.dial_offset
        self.__energy = value
        # PROTECTED REGION END #    //  SoftiZPEnergy.Energy_write

    def read_FocalDist(self):
        # PROTECTED REGION ID(SoftiZPEnergy.FocalDist_read) ENABLED START #
        """Return the FocalDist attribute."""
        return self.__focal_dist
        # PROTECTED REGION END #    //  SoftiZPEnergy.FocalDist_read

    def write_FocalDist(self, value):
        # PROTECTED REGION ID(SoftiZPEnergy.FocalDist_write) ENABLED START #
        """Set the FocalDist attribute."""
        self.zp_dev.Position = (value + self._zp__a0 + self.__defocus) / self.zp_unit_coeff + self.dial_offset
        self.__focal_dist = value
        self.db.put_device_attribute_property(self.get_name(), {'FocalDist': {'FocalDist': value}})
        # PROTECTED REGION END #    //  SoftiZPEnergy.FocalDist_write

    def read_ZP_A0(self):
        # PROTECTED REGION ID(SoftiZPEnergy.ZP_A0_read) ENABLED START #
        """Return the ZP_A0 attribute."""
        return self._zp__a0
        # PROTECTED REGION END #    //  SoftiZPEnergy.ZP_A0_read

    def write_ZP_A0(self, value):
        # PROTECTED REGION ID(SoftiZPEnergy.ZP_A0_write) ENABLED START #
        """Set the ZP_A0 attribute."""
        self.zp_dev.Position = (self.__focal_dist + value + self.__defocus) / self.zp_unit_coeff + self.dial_offset
        self._zp__a0 = value
        # PROTECTED REGION END #    //  SoftiZPEnergy.ZP_A0_write

    def read_ZP_A1(self):
        # PROTECTED REGION ID(SoftiZPEnergy.ZP_A1_read) ENABLED START #
        """Return the ZP_A1 attribute."""
        return self._zp__a1
        # PROTECTED REGION END #    //  SoftiZPEnergy.ZP_A1_read

    def write_ZP_A1(self, value):
        # PROTECTED REGION ID(SoftiZPEnergy.ZP_A1_write) ENABLED START #
        """Set the ZP_A1 attribute."""
        self._zp__a1 = value
        # PROTECTED REGION END #    //  SoftiZPEnergy.ZP_A1_write

    def read_ZP_Diam(self):
        # PROTECTED REGION ID(SoftiZPEnergy.ZP_Diam_read) ENABLED START #
        """Return the ZP_Diam attribute."""
        return self._zp__diam
        # PROTECTED REGION END #    //  SoftiZPEnergy.ZP_Diam_read

    def write_ZP_Diam(self, value):
        # PROTECTED REGION ID(SoftiZPEnergy.ZP_Diam_write) ENABLED START #
        """Set the ZP_Diam attribute."""
        self._zp__diam = value
        # PROTECTED REGION END #    //  SoftiZPEnergy.ZP_Diam_write

    def read_ZP_width(self):
        # PROTECTED REGION ID(SoftiZPEnergy.ZP_width_read) ENABLED START #
        """Return the ZP_width attribute."""
        return self._zp_width
        # PROTECTED REGION END #    //  SoftiZPEnergy.ZP_width_read

    def write_ZP_width(self, value):
        # PROTECTED REGION ID(SoftiZPEnergy.ZP_width_write) ENABLED START #
        """Set the ZP_width attribute."""
        self._zp_width = value
        # PROTECTED REGION END #    //  SoftiZPEnergy.ZP_width_write

    def read_Defocus(self):
        # PROTECTED REGION ID(SoftiZPEnergy.Defocus_read) ENABLED START #
        """Return the Defocus attribute."""
        return self.__defocus
        # PROTECTED REGION END #    //  SoftiZPEnergy.Defocus_read

    def write_Defocus(self, value):
        # PROTECTED REGION ID(SoftiZPEnergy.Defocus_write) ENABLED START #
        """Set the Defocus attribute."""
        self.zp_dev.Position = (self.__focal_dist + self._zp__a0 + value) / self.zp_unit_coeff + self.dial_offset
        self.__defocus = value

        # PROTECTED REGION END #    //  SoftiZPEnergy.Defocus_write

    def read_SampleX(self):
        # PROTECTED REGION ID(SoftiZPEnergy.SampleX_read) ENABLED START #
        """Return the SampleX attribute."""
        return self.__sample_x
        # PROTECTED REGION END #    //  SoftiZPEnergy.SampleX_read

    def read_SampleY(self):
        # PROTECTED REGION ID(SoftiZPEnergy.SampleY_read) ENABLED START #
        """Return the SampleY attribute."""
        return self.__sample_y
        # PROTECTED REGION END #    //  SoftiZPEnergy.SampleY_read

    def read_XTiltCorrectVal(self):
        return self.__x_tilt_correct_val

    def read_TiltCorrectOn(self):
        return self.__x_tilt_correct_on

    def write_TiltCorrectOn(self, value):
        self.__x_tilt_correct_on = value
        if not value:
            self.write_Position(self.__position_0)

    def read_XTilt(self):
        return self.__x_tilt

    def write_XTilt(self, value):
        self.__x_tilt = value

    def read_XTiltCorrectSign(self):
        return self.__x_tilt_correct_sign

    def write_XTiltCorrectSign(self, value):
        self.__x_tilt_correct_sign = value

    # --------
    # Commands
    # --------

    @command(
        dtype_out='DevString',
        display_level=DispLevel.EXPERT,
    )
    @DebugIt()
    def Calc_A1(self):
        return ""

    @command(
    )
    @DebugIt()
    def GetXTiltZeroPnt(self):
        self.__sample_x_0 = self.__sample_x
        self.__position_0 = self.__position

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the SoftiZPEnergy module."""
    return run((SoftiZPEnergy,), args=args, **kwargs)


if __name__ == '__main__':
    main()
