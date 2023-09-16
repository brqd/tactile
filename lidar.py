from typing import Literal
import asyncio
import struct
import math as m
import numpy as np
import time
import serial_asyncio

import config
import display

class LidarProtocol(asyncio.Protocol):
    def __init__(self, x_min, y_min, x_max, y_max, max_intensity):

        super().__init__()
        self.queue = asyncio.Queue(100)
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.max_intensity = max_intensity
        self.min_distance = 400
        self.max_distance = max(
            m.sqrt( (x_min)**2 + (y_min)**2 ),
            m.sqrt( (x_max)**2 + (y_min)**2 ),
            m.sqrt( (x_max)**2 + (y_max)**2 ),
            m.sqrt( (x_min)**2 + (y_max)**2 )
        ) 
        self.last_pos = (0,0)
        self.last_dist = None
        self.limit_dist = 100
        self.resolution = 2
        

    def connection_made(self, transport):
        self.transport = transport
        self.state: Literal['IDLE', 'LENGTH', 'DATA'] = 'IDLE'
        self.buffer: bytes = b''
        self.length = 0
        
        print('Lidar port opened', transport)


    def data_received(self, recv_data: bytes):           
        for c in recv_data:  
            try:         
                if self.state == 'IDLE':
                    if c == 0x54:                    
                        self.state = 'LENGTH'
                elif self.state == 'LENGTH':
                    ver_len = c
                    self.length = ver_len & 0x1F
                    self.buffer = b''
                    self.state = 'DATA'
                elif self.state == 'DATA':
                    if len(self.buffer) == self.length * 3 + 8:
                        speed, start = struct.unpack('<HH', self.buffer[0:4])
                        data = np.zeros((self.length,2))
                        for i in range(self.length):
                            tmp = struct.unpack('<HB', self.buffer[4+i*3 : 4+i*3+3]) 
                            data[i,:] = tmp              
                        # stop, timestamp, sum = struct.unpack('<HHB', self.buffer[4+self.length*3 : 4+self.length*3+5])
                        stop, timestamp = struct.unpack('<HH', self.buffer[4+self.length*3 : 4+self.length*3+4]) # seems this model have no checksum
                        self.buffer = b''
                        self.state = 'IDLE'

                        for (dist, intensity), angle in zip(data, np.linspace(m.pi*start/18000, m.pi*stop/18000, num=self.length)):

                            # filter big distance change - usually caused by lidar glichest
                            if self.last_dist is None or abs(self.last_dist - dist) < self.max_distance:
                                self.last_dist = dist
                            else:
                                self.last_dist = None
                                break
                            
                            # process only points in intensity and distance limit
                            if (
                                0 < intensity < self.max_intensity
                                and self.min_distance < dist < self.max_distance
                            ):
                                y = -dist*m.cos(angle) # marker up
                                x = dist*m.sin(angle)
                                # process only points in given area with given resolution
                                if (
                                    self.x_min < x < self.x_max
                                    and self.y_min < y < self.y_max
                                    and not all(np.isclose((x,y), self.last_pos, atol=self.resolution))
                                ):
                                    self.last_pos = (x,y)
                                    try:
                                        self.queue.put_nowait((x,y))
                                    except asyncio.QueueFull:
                                        ...
                    else:
                        self.buffer += c.to_bytes(1)
            except Exception as e:
                print(e)

    async def read(self):
        points = [await self.queue.get()]
        while True:
            try:
                points += [self.queue.get_nowait()]
            except asyncio.QueueEmpty:
                return points
                    




    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()

    def pause_reading(self):
        self.transport.pause_reading()

    def resume_reading(self):
        self.transport.resume_reading()


_protocol = None
_transport = None
_pos_queue = None
_lidar_pos = (0,0)
_display_points: display.Points = None

async def configure(conf: config.Config, queue: asyncio.Queue, points: display.Points = None ):
    global _transport, _protocol, _pos_queue, _lidar_pos, _display_points

    _display_points = points
    _pos_queue = queue
    _lidar_pos = (conf.lidar.x, conf.lidar.y)

    loop = asyncio.get_running_loop()
    _transport, _protocol = await serial_asyncio.create_serial_connection(
        loop,
        lambda: LidarProtocol(
            -conf.lidar.x,
            -conf.lidar.y,
            conf.area_width-conf.lidar.x,
            conf.area_height-conf.lidar.y,
            350),
        conf.lidar.port,
        baudrate=230400
    )                


_pos = (0,0)
_last_pos = (0,0)
_sensitivity = 10 # mm

_points_size = 50
_points = [(0,0)] * _points_size
_point_index = 0


def add_point(pos):    
    global _points, _point_index
    _points[_point_index] = pos
    _point_index += 1
    if _point_index == _points_size:
        _point_index = 0

def get_points() -> list[tuple[float, float]]:
    return _points

async def run():
    global _pos, _last_pos
    
    try:
        while True:
            current_point = await _protocol.read()
            current_point = [(_lidar_pos[0] + point[0], _lidar_pos[1] + point [1]) for point in current_point]

            for point in current_point:
                add_point(point)
                # drawing
                if _display_points is not None:
                    _display_points.add_point(point, (255,0,0))                 

            points = get_points() # all

            # finding middle of hand
            mean = np.mean(points,0)
            std = np.std(points,0)

            # filter outsiders
            points = filter(lambda p: all(abs(mean-p) <= 3*std), points )
            points = list(points)

            # finding middle of hand again
            mean = np.mean(points,0)
            std = np.std(points,0)

            if _display_points is not None:
                    for point in points:
                        _display_points.add_point(point, (0,255,0))
            
            # finding end of hand            
            A = np.vstack([[p[1] for p in points], np.ones(len(points))]).T
            B = [p[0] for p in points]
            a,b = np.linalg.lstsq(A, B, rcond=None)[0]
            new_y = mean[1]-2*std[1]
            _pos = (a*new_y+b, new_y)

            # detecting change
            if abs(_pos[0]-_last_pos[0]) > _sensitivity or abs(_pos[1]-_last_pos[1]) > _sensitivity:
                try:
                    _pos_queue.put_nowait(_pos)
                    _last_pos = _pos
                except asyncio.QueueFull:
                    ...
    finally:
        _transport.close()

def update(pos: tuple[float,float]):
    ...