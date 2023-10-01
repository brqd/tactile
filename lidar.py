from typing import Literal
import asyncio
import struct
import math as m
import numpy as np
import time
import serial_asyncio

import config
import state

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
        self.resolution = 5
        

    def connection_made(self, transport):
        self.transport = transport
        self.state: Literal['IDLE', 'LENGTH', 'DATA'] = 'IDLE'
        self.buffer: bytes = b''
        self.length = 0
        
        print('Lidar port opened', transport)


    def process_data(self, buffer):

        speed, start = struct.unpack('<HH', self.buffer[0:4])
        data = np.zeros((self.length,2))
        for i in range(self.length):
            tmp = struct.unpack('<HB', self.buffer[4+i*3 : 4+i*3+3]) 
            data[i,:] = tmp              
        stop, timestamp = struct.unpack('<HH', self.buffer[4+self.length*3 : 4+self.length*3+4]) # seems this model have no checksum

        for (dist, intensity), angle in zip(data, np.linspace(m.pi*start/18000, m.pi*stop/18000, num=self.length)):

            # filter big distance change - usually caused by lidar glitches
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
                        self.process_data(self.buffer)
                        self.buffer = b''
                        self.state = 'IDLE'
                    else:
                        self.buffer += c.to_bytes(1, 'little')
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




class Lidar():
    _protocol = None
    _transport = None
    _pos_queue = None
    _lidar_pos = (0,0)

    areas_rects = np.empty((0,4))

    def __init__(self, conf: config.Config, state: state.State ):

        self._state = state
        self._lidar = conf.lidar
        self._area = conf.area

    async def run(self):

        loop = asyncio.get_running_loop()
        _transport, _protocol = await serial_asyncio.create_serial_connection(
            loop,
            lambda: LidarProtocol(
                -self._lidar.x,
                -self._lidar.y,
                self._area.w-self._lidar.x,
                self._area.h-self._lidar.x,
                350),
            self._lidar.port,
            baudrate=230400
        )              
        
        try:
            while True:
                current_points = await _protocol.read()
                current_points = [(self._lidar.x + point[0], self._lidar.y + point [1]) for point in current_points]

                for point in current_points:
                    self._state.add_point(point)

        finally:
            _transport.close()
