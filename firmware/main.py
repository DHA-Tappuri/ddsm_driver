import machine
import utime
import ujson
import ustruct


# register map
class BNO055_REGISTER:
    MAG_RADIUS_MSB    = 0x6A
    MAG_RADIUS_LSB    = 0x69
    ACC_RADIUS_MSB    = 0x68
    ACC_RADIUS_LSB    = 0x67
    GYRO_OFFSET_Z_MSB = 0x66
    GYRO_OFFSET_Z_LSB = 0x65
    GYRO_OFFSET_Y_MSB = 0x64
    GYRO_OFFSET_Y_LSB = 0x63
    GYRO_OFFSET_X_MSB = 0x62
    GYRO_OFFSET_X_LSB = 0x61
    MAG_OFFSET_Z_MSB  = 0x60
    MAG_OFFSET_Z_LSB  = 0x5F
    MAG_OFFSET_Y_MSB  = 0x5E
    MAG_OFFSET_Y_LSB  = 0x5D
    MAG_OFFSET_X_MSB  = 0x5C
    MAG_OFFSET_X_LSB  = 0x5B
    ACC_OFFSET_Z_MSB  = 0x5A
    ACC_OFFSET_Z_LSB  = 0x59
    ACC_OFFSET_Y_MSB  = 0x58
    ACC_OFFSET_Y_LSB  = 0x57
    ACC_OFFSET_X_MSB  = 0x56
    ACC_OFFSET_X_LSB  = 0x55
    AXIS_MAP_SIGN     = 0x42
    AXIS_MAP_CONFIG   = 0x41
    TEMP_SOURCE       = 0x40
    SYS_TRIGGER       = 0x3F
    PWR_MODE          = 0x3E
    OPR_MODE          = 0x3D
    UNIT_SEL          = 0x3B
    SYS_ERR           = 0x3A
    SYS_STATUS        = 0x39
    SYS_CLK_STATUS    = 0x38
    INT_STA           = 0x37
    ST_RESULT         = 0x36
    CALIB_STAT        = 0x35
    TEMP              = 0x34
    GRV_DATA_Z_MSB    = 0x33
    GRV_DATA_Z_LSB    = 0x32
    GRV_DATA_Y_MSB    = 0x31
    GRV_DATA_Y_LSB    = 0x30
    GRV_DATA_X_MSB    = 0x2F
    GRV_DATA_X_LSB    = 0x2E
    LIA_DATA_Z_MSB    = 0x2D
    LIA_DATA_Z_LSB    = 0x2C
    LIA_DATA_Y_MSB    = 0x2B
    LIA_DATA_Y_LSB    = 0x2A
    LIA_DATA_X_MSB    = 0x29
    LIA_DATA_X_LSB    = 0x28
    QUA_DATA_Z_MSB    = 0x27
    QUA_DATA_Z_LSB    = 0x26
    QUA_DATA_Y_MSB    = 0x25
    QUA_DATA_Y_LSB    = 0x24
    QUA_DATA_X_MSB    = 0x23
    QUA_DATA_X_LSB    = 0x22
    QUA_DATA_W_MSB    = 0x21
    QUA_DATA_W_LSB    = 0x20
    EUL_PITCH_MSB     = 0x1F
    EUL_PITCH_LSB     = 0x1E
    EUL_ROLL_MSB      = 0x1D
    EUL_ROLL_LSB      = 0x1C
    EUL_HEADING_MSB   = 0x1B
    EUL_HEADING_LSB   = 0x1A
    GYR_DATA_Z_MSB    = 0x19
    GYR_DATA_Z_LSB    = 0x18
    GYR_DATA_Y_MSB    = 0x17
    GYR_DATA_Y_LSB    = 0x16
    GYR_DATA_X_MSB    = 0x15
    GYR_DATA_X_LSB    = 0x14
    MAG_DATA_Z_MSB    = 0x13
    MAG_DATA_Z_LSB    = 0x12
    MAG_DATA_Y_MSB    = 0x11
    MAG_DATA_Y_LSB    = 0x10
    MAG_DATA_X_MSB    = 0x0F
    MAG_DATA_X_LSB    = 0x0E
    ACC_DATA_Z_MSB    = 0x0D
    ACC_DATA_Z_LSB    = 0x0C
    ACC_DATA_Y_MSB    = 0x0B
    ACC_DATA_Y_LSB    = 0x0A
    ACC_DATA_X_MSB    = 0x09
    ACC_DATA_X_LSB    = 0x08
    PAGE_ID           = 0x07
    BL_REV_ID         = 0x06
    SW_REV_ID_MSB     = 0x05
    SW_REV_ID_LSB     = 0x04
    GYR_ID            = 0x03
    MAG_ID            = 0x02
    ACC_ID            = 0x01
    CHIP_ID           = 0x00
    UNIQUE_ID         = 0x5F # 0x50-0x5F
    GYR_AM_SET        = 0x1F
    GYR_AM_THRES      = 0x1E
    GYR_DUR_Z         = 0x1D
    GYR_HR_Z_SET      = 0x1C
    GYR_DUR_Y         = 0x1B
    GYR_HR_Y_SET      = 0x1A
    GYR_DUR_X         = 0x19
    GYR_HR_X_SET      = 0x18
    GYR_INT_SETING    = 0x17
    ACC_NM_SET        = 0x16
    ACC_NM_THRE       = 0x15
    ACC_HG_THRES      = 0x14
    ACC_HG_DURATION   = 0x13
    ACC_INT_SETTINGS  = 0x12
    ACC_AM_THRES      = 0x11
    INT_EN            = 0x10
    INT_MSK           = 0x0F
    GYR_SLEEP_CONFIG  = 0x0D
    ACC_SLEEP_CONFIG  = 0x0C
    GYR_CONFIG_1      = 0x0B
    GYR_CONFIG_0      = 0x0A
    MAG_CONFIG        = 0x09
    ACC_CONFIG        = 0x08


# address map
#BNO055_OPR_MODE_ADDR    = 0x3D
#BNO055_POWER_MODE_ADDR  = 0x3E
#BNO055_SYS_TRIGGER_ADDR = 0x3F
#BNO055_UNIT_SEL_ADDR    = 0x3B
#BNO055_QUATERNION_DATA_W_LSB_ADDR = 0x20
# mode
BNO055_CONFIG_MODE = 0x00
BNO055_NDOF_MODE   = 0x0C

def get_i2c_channel(sda_pin, scl_pin):
    # I2C pin map
    i2c_pins = {
        0: {"sda": [0, 4, 8], "scl": [1, 5, 9]},
        1: {"sda": [2, 6, 10], "scl": [3, 7, 11]},
    }

    # check pins
    for channel, pins in i2c_pins.items():
        if sda_pin in pins["sda"] and scl_pin in pins["scl"]:
            return channel

    # invalid pins
    return None


# BNO055 module
class BNO055(object):

    # contructor
    def __init__(self, sda:int=8, scl:int=9, addr:int=0x28):
        utime.sleep(0.5)
        
        # get I2C channel
        i2c_ch = get_i2c_channel( sda_pin=sda, scl_pin=scl )
        # check I2C channel is valid
        if( i2c_ch == None ):
            print( 'invalid pins, exit.' )
            return        
        
        # create I2C
        self._addr = addr
        self._i2c  = machine.I2C( i2c_ch, scl=machine.Pin(scl), sda=machine.Pin(sda), freq=400000 )
        
        # check address
        _addrs=self._i2c.scan()
        
        # search device
        if( len(_addrs) == 0 ):
            print('no I2C device found. exit.')
            return

        # address check
        _pass = False
        for _a in _addrs:
            if( _a == self._addr ):
                print( 'BNO055 device found at address', hex(_a) )
                _pass = True
                break
        if( not _pass ):
            print( 'Invalid device address. found devices :', _addrs, '. exit.' )
            return
        
        # initialize device
        # enter to config mode
        self._i2c.writeto_mem(self._addr, BNO055_REGISTER.OPR_MODE, bytearray([BNO055_CONFIG_MODE]))
        utime.sleep(0.2)
        # set NDOF mode
        self._i2c.writeto_mem(self._addr, BNO055_REGISTER.OPR_MODE, bytearray([BNO055_NDOF_MODE]))
        utime.sleep(0.2)
        
        return


    # read quaternion
    def read_quaternion(self):
        _ret = {}
        try:
            # read register
            _data = bytearray(8)
            self._i2c.readfrom_mem_into(self._addr, BNO055_REGISTER.QUA_DATA_W_LSB, _data)

            # unpack data
            _quat = ustruct.unpack('<hhhh', _data)
            _ret['w'] = _quat[0] / (1<<14)
            _ret['x'] = _quat[1] / (1<<14)
            _ret['y'] = _quat[2] / (1<<14)
            _ret['z'] = _quat[3] / (1<<14)
            
        except:
            _ret['w'] = 1.0
            _ret['x'] = 0.0
            _ret['y'] = 0.0
            _ret['z'] = 0.0

        return _ret


    # destructor
    def __del__(self):
        return


# main function
def main(args=None):
    imu = BNO055()
    
    while(True):
        # get quaternion
        quat  = imu.read_quaternion()
        
        # json dump
        _jstr = ujson.dumps(quat)
        # output json
        print(_jstr)
        
        # for Adafruit 3D model viewer
        #print( 'Quaternion:', quat['w'], ',', quat['x'], ',', quat['y'], ',', quat['z'] )
        # wait
        utime.sleep(0.01)
        
    return


# entry point
if( __name__ == '__main__' ):
    main()