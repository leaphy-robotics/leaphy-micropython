"""
This module provides classes for controlling SSD1306 OLED displays 
using either I2C or SPI communication protocols. It includes 
functionality for initializing the display, setting contrast, 
inverting the display, displaying text and graphics, and managing 
the display's power state.
"""

import time
import framebuf
from micropython import const
from leaphymicropython.utils.i2c_helper import I2CDevice
from leaphymicropython.utils.i2c_helper import handle_i2c_errors

# pylint: disable=no-member,too-many-function-args,unnecessary-pass

# register definitions
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)


class SSD1306:
    """
    A class for the SSD1306 display
    """

    def __init__(self, width, height, external_vcc):
        """
        Initialize SSD1306 display with specified width, height, and external VCC configuration.
        :param width: int, width of the display
        :param height: int, height of the display
        :param external_vcc: bool, external VCC configuration
        """
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        # Note the subclass must initialize self.framebuf to a framebuffer.
        # This is necessary because the underlying data buffer is different
        # between I2C and SPI implementations (I2C needs an extra byte).
        self.poweron()

    def initialize_device(self):
        """
        Initialize the display and the addresses.
        """
        for cmd in (
            SET_DISP | 0x00,  # off
            # address setting
            SET_MEM_ADDR,
            0x00,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.height == 32 else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc
            # display
            SET_CONTRAST,
            0xFF,  # maximum
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            # charge pump
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        ):  # on
            self.write_cmd(cmd)

    @handle_i2c_errors
    def poweroff(self):
        """
        Turn off the display.
        """
        self.write_cmd(SET_DISP | 0x00)

    @handle_i2c_errors
    def contrast(self, contrast):
        """
        Adjust contrast of the display.
        :param contrast: int, contrast value
        """
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    @handle_i2c_errors
    def invert(self, invert):
        """
        Invert the display (or not).
        :param invert: int, 0 for normal display, 1 for inverted display
        """
        self.write_cmd(SET_NORM_INV | (invert & 1))

    @handle_i2c_errors
    def show(self):
        """
        Show the contents of the frame buffer on the display.
        """
        start_col = 0
        end_col = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            start_col += 32
            end_col += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(start_col)
        self.write_cmd(end_col)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_framebuf()

    @handle_i2c_errors
    def fill(self, col):
        """
        Fill the entire display with the specified color.
        :param col: int, color value (0 or 1)
        """
        self.framebuf.fill(col)

    @handle_i2c_errors
    def pixel(self, x_coor, y_coor, col):
        """
        Set a pixel at the specified position to the specified color.
        :param x: int, x-coordinate of the pixel
        :param y: int, y-coordinate of the pixel
        :param col: int, color value (0 or 1)
        """
        self.framebuf.pixel(x_coor, y_coor, col)

    @handle_i2c_errors
    def scroll(self, hor_delta, ver_delta):
        """
        Scroll the contents of the display by the specified deltas.
        :param dx: int, horizontal delta
        :param dy: int, vertical delta
        """
        self.framebuf.scroll(hor_delta, ver_delta)

    @handle_i2c_errors
    def text(self, string, x_coor, y_coor, col=1):
        """
        Display text on the screen starting from the specified position with the specified color.
        :param string: str, text to display
        :param x: int, x-coordinate of the starting position
        :param y: int, y-coordinate of the starting position
        :param col: int, color value (0 or 1)
        """
        self.framebuf.text(string, x_coor, y_coor, col)


class SSD1306I2C(SSD1306, I2CDevice):
    """
    A class for the ssd1306 I2C driver
    """

    # the following attribute is used by decorator handle_i2c_errors
    ADDRESS = 0x3C

    def __init__(
        self,
        width,
        height,
        external_vcc=False,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=0,
        show_warnings=True,
    ):
        """
        Initializes the SSD1306 I2C display.

        Args:
            width (int): The width of the display in pixels.
            height (int): The height of the display in pixels.
            external_vcc (bool, optional): Whether an external VCC is used. Defaults to False.
            channel (int, optional): The I2C multiplexer channel to select.
            Defaults to 255, indicating no multiplexer.
            sda_gpio_pin (int, optional): The GPIO pin connected to the SDA line. Defaults to 12.
            scl_gpio_pin (int, optional): The GPIO pin connected to the SCL line. Defaults to 13.
            bus_id (int, optional): Identifies a particular I2C peripheral,
            for example bus 0 or 1. Defaults to 0.
            show_warnings (bool, optional): If True, show warnings about device address not found.
            Defaults to True.
        """
        I2CDevice.__init__(
            self, channel, sda_gpio_pin, scl_gpio_pin, bus_id, show_warnings
        )
        self.find_device(show_warnings=self.show_warnings)

        self.temp = bytearray(2)
        # Add an extra byte to the data buffer to hold an I2C data/command byte
        # to use hardware-compatible I2C transactions.  A memoryview of the
        # buffer is used to mask this byte from the framebuffer operations
        # (without a major memory hit as memoryview doesn't copy to a separate
        # buffer).
        self.buffer = bytearray(((height // 8) * width) + 1)
        self.buffer[0] = 0x40  # Set first byte of data buffer to Co=0, D/C=1
        self.framebuf = framebuf.FrameBuffer1(
            memoryview(self.buffer)[1:], width, height
        )
        SSD1306.__init__(self, width, height, external_vcc)

    def initialize_device(self):
        """
        initialize device
        """
        SSD1306.initialize_device(self)

    def write_cmd(self, cmd):
        """
        Write a command to the display over I2C.
        :param cmd: int, command value
        """
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.ADDRESS, self.temp)

    def write_framebuf(self):
        """
        Write the frame buffer to the display over I2C.
        """
        # Blast out the frame buffer using a single I2C transaction to support
        # hardware I2C interfaces.
        self.i2c.writeto(self.ADDRESS, self.buffer)

    def poweron(self):
        """
        pass
        """
        pass


class SSD1306SPI(SSD1306):
    """
    SSD1306 implementation of spi
    """

    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        """
        Initialize SSD1306 display over SPI with specified
        width, height, SPI interface, data/command pin, reset pin,
        chip select pin, and external VCC configuration.
        :param width: int, width of the display
        :param height: int, height of the display
        :param spi: object, SPI interface
        :param dc: object, data/command pin
        :param res: object, reset pin
        :param cs: object, chip select pin
        :param external_vcc: bool, external VCC configuration
        """
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.data_pin = dc
        self.res = res
        self.chip_select_pin = cs
        self.buffer = bytearray((height // 8) * width)
        self.framebuf = framebuf.FrameBuffer1(self.buffer, width, height)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        """
        Write a command to the display over SPI.
        :param cmd: int, command value
        """
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.high()
        self.data_pin.low()
        self.chip_select_pin.low()
        self.spi.write(bytearray([cmd]))
        self.cs.high()

    def write_framebuf(self):
        """
        Write the frame buffer to the display over SPI.
        """
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.high()
        self.data_pin.high()
        self.chip_select_pin.low()
        self.spi.write(self.buffer)
        self.chip_select_pin.high()

    def poweron(self):
        """
        Turn on the display over SPI.
        """
        self.res.high()
        time.sleep_ms(1)
        self.res.low()
        time.sleep_ms(10)
        self.res.high()
