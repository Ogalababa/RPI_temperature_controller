import time
import smbus

# import logx
# import #logging
BUS = smbus.SMBus(1)
LCD_ADDR = 0x27
BLEN = 1  # turn on/off background light


def turn_light(key):
    global BLEN
    BLEN = key
    if key == 1:
        BUS.write_byte(LCD_ADDR, 0x08)
        # logging.info('LCD executed turn on BLight')
    else:
        BUS.write_byte(LCD_ADDR, 0x00)
        # logging.info('LCD executed turn off BLight')


def write_word(addr, data):
    global BLEN
    temp = data
    if BLEN == 1:
        temp |= 0x08
    else:
        temp &= 0xF7
    BUS.write_byte(addr, temp)


def send_command(comm):
    # Send bit7-4 firstly
    buf = comm & 0xF0
    buf |= 0x04  # RS = 0, RW = 0, EN = 1
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB  # Make EN = 0
    write_word(LCD_ADDR, buf)

    # Send bit3-0 secondly
    buf = (comm & 0x0F) << 4
    buf |= 0x04  # RS = 0, RW = 0, EN = 1
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB  # Make EN = 0
    write_word(LCD_ADDR, buf)


def send_data(data):
    # Send bit7-4 firstly
    buf = data & 0xF0
    buf |= 0x05  # RS = 1, RW = 0, EN = 1
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB  # Make EN = 0
    write_word(LCD_ADDR, buf)

    # Send bit3-0 secondly
    buf = (data & 0x0F) << 4
    buf |= 0x05  # RS = 1, RW = 0, EN = 1
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB  # Make EN = 0
    write_word(LCD_ADDR, buf)


def init_lcd():
    try:
        send_command(0x33)  # Must initialize to 8-line mode at first
        time.sleep(0.005)
        send_command(0x32)  # Then initialize to 4-line mode
        time.sleep(0.005)
        send_command(0x28)  # 2 Lines & 5*7 dots
        time.sleep(0.005)
        send_command(0x0C)  # Enable display without cursor
        time.sleep(0.005)
        send_command(0x01)  # Clear Screen
        # logging.info('LCD init over')
        BUS.write_byte(LCD_ADDR, 0x08)
        # logging.info('LCD turning on BLight')
    except:
        return False
    else:
        return True


def clear_lcd():
    send_command(0x01)  # Clear Screen


def print_lcd(x, y, str):
    if x < 0:
        x = 0
    if x > 19:
        x = 19
    if y < 0:
        y = 0
    if y > 3:
        y = 3

    # Move cursor
    # addr = 0x80 + 0x40 * y + x
    if y == 0:
        addr = 0x80 + x
    elif y == 1:
        addr = 0xc0 + x
    elif y == 2:
        addr = 0x94 + x
    elif y == 3:
        addr = 0xd4 + x
    send_command(addr)

    for chr in str:
        send_data(ord(chr))


# LCD.print_lcd( 0-3列、0-3行、'文字内容')，
# 如果屏幕是1602，则最多能显示16列(0-15列)，2行(0-1行)。
# 如果屏幕是2004，则最多能显示20列(0-19列)、4行(0-3行）
if __name__ == '__main__':
    init_lcd()
    print_lcd(0, 0, 'LCD1602/LCD2004 Demo')
    print_lcd(0, 1, '-222222222BBBBBBBBB-')
    print_lcd(0, 2, '-333333333CCCCCCCCC-')
    print_lcd(0, 3, '-444444444DDDDDDDDD-')