import ev3dev.ev3 as ev3
import time


def closest_color(r, g, b, **kwargs):

    min_distance_sq = 0
    min_color = None

    for color in kwargs:

        r2, g2, b2 = kwargs[color]

        distance_sq = (r - r2)**2 + (g - g2)**2 + (b - b2)**2

        if min_color is None:  # first color
            min_color = color
            min_distance_sq = distance_sq
        elif distance_sq < min_distance_sq:
            min_color = color
            min_distance_sq = distance_sq
        else:
            pass

    return min_color


class Timer(object):
    def __init__(self):
        self._reset()

    def _reset(self):
        self.t0 = time.time()

    def time(self):
        return time.time() - self.t0

    def seconds(self):
        return time.time() - self.t0


def Beep():
    ev3.Sound.beep()


def Sensors(one=None, two=None, three=None, four=None):

    sensors = []
    for i, v in enumerate([one, two, three, four]):
        if not v:
            sensors.append(None)
            continue

        sensor_port_name = 'in%d' % (i + 1)
        v = v.lower()

        if v == 'ir' or v.startswith('infra'):
            sensors.append(ev3.InfraredSensor(sensor_port_name))
        elif v == 'touch':
            sensors.append(ev3.TouchSensor(sensor_port_name))
        elif v == 'us' or v.startswith('ultra'):
            sensors.append(ev3.UltrasonicSensor(sensor_port_name))
            sensors[-1].mode = sensors[-1].MODE_US_DIST_CM
        elif v == 'color':
            sensors.append(ev3.ColorSensor(sensor_port_name))
            sensors[-1].mode = sensors[-1].MODE_RGB_RAW
        elif 'gyro' in v:
            sensors.append(ev3.GyroSensor(sensor_port_name))
            sensors[-1].mode = 'GYRO-ANG'
        else:
            raise ValueError('Not implemented:' % v)

    return sensors


def Motors(port_letters, size=None):
    m = []
    unused = ''
    for letter in port_letters:
        letter_up = letter.upper()
        if size is None:
            m.append(ev3.LargeMotor('out%s' % letter_up))
        elif 'large' in size.lower():
            m.append(ev3.LargeMotor('out%s' % letter_up))
        elif 'med' in size.lower():
            m.append(ev3.MediumMotor('out%s' % letter_up))

    assert all([motor.connected for motor in m]), \
            "Motors need to be attached to %s" % port_letters

    # `run-direct` command will allow to vary motor
    # performance on the fly by adjusting `duty_cycle_sp` attribute.
    for motor in m:
        motor.run_direct()
        motor.duty_cycle_sp = 0

    return m


def Rotate(*args, **kwargs):
    if isinstance(args[0], list):
        motors = args[0]
    else:
        motors = args

    angle = kwargs['angle']
    if angle < 0:
        Fw = Backward  # gotta love this
        angle = -angle
    else:
        Fw = Forward

    for m in motors:
        m.position = 0
        m.stop_action = 'brake'

    while True:
        count = 0
        for m in motors:
            pos = m.position
            if pos < 0:
                pos = -pos

            if 0 < pos < (angle / 2):
                Fw(m, speed=100)
            elif pos < (3 * angle / 4):
                Fw(m, speed=50)
            elif pos < (angle):
                Fw(m, speed=20)
            else:
                Off(m)
                count += 1

        if count == len(motors):
            break

        Wait(0.1)


def Forward(*args, **kwargs):
    if isinstance(args[0], list):
        motors = args[0]
    else:
        motors = args

    for m in motors:
        if 'speed' in kwargs:
            m.duty_cycle_sp = kwargs['speed']
        else:
            m.duty_cycle_sp = 100


def Backward(*args, **kwargs):
    if isinstance(args[0], list):
        motors = args[0]
    else:
        motors = args

    for m in motors:
        if 'speed' in kwargs:
            m.duty_cycle_sp = -kwargs['speed']
        else:
            m.duty_cycle_sp = -100


def Off(*args):
    if isinstance(args[0], list):
        motors = args[0]
    else:
        motors = args
    for m in motors:
        m.duty_cycle_sp = 0


def Wait(seconds):
    time.sleep(seconds)


buttons = ev3.Button()


def Shutdown(*args):
    if isinstance(args[0], list):
        motors = args[0]
    else:
        motors = args
    for m in motors:
        m.stop()
