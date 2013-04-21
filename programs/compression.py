#!/usr/bin/python

import sys
import struct

def trailing_zeros(num):
  x = num & (~num + 1)
  count = 0
  while x > 1:
    count += 1
    x = x >> 1
  return count

def dgap_encode(arr):
  last_element = 0
  gaps = []
  for num in arr:
    gaps.append(num - last_element)
    #gaps.append(num*100)
    last_element = num
  return gaps

def dgap_decode(arr):
  total = 0
  decoded = []
  for num in arr:
    total += num
    decoded.append(total)
  return decoded

def vb_encode_num(num):
    if num < 0x3F:
      return [chr(0xFF & num)]
    elif num < 0x3FFF:
      byte2 = 0xFF & num
      byte1 = (0x3F00 & num | 0x4000) >> 8
      return [chr(byte1), chr(byte2)]
    elif num < 0x3FFFFF:
      byte3 = 0xFF & num
      byte2 = (0xFF00 & num) >> 8
      byte1 = (0x3F0000 & num | 0x800000) >> 16
      return [chr(byte1), chr(byte2), chr(byte3)]
    else:
      byte4 = 0xFF & num
      byte3 = (0xFF00 & num) >> 8
      byte2 = (0xFF0000 & num) >> 16
      byte1 = (0x3F000000 & num | 0xC0000000) >> 24
      return [chr(byte1), chr(byte2), chr(byte3), chr(byte4)]

def vb_encode(arr):
    bytestream = []
    for n in arr:
      bytes = vb_encode_num(n)
      bytestream.extend(bytes)
    return bytestream

def vb_decode(bytes):
  numbers = []
  i = 0
  while i < len(bytes):
    byte = struct.unpack('B', bytes[i])[0]
    if byte & 0xC0 == 0xC0:
      byte2 = struct.unpack('B', bytes[i+1])[0]
      byte3 = struct.unpack('B', bytes[i+2])[0]
      byte4 = struct.unpack('B', bytes[i+3])[0]
      number = ((0x3F & byte) << 24) + ((0xFF & byte2) << 16) + ((0xFF & byte3) << 8) + (0xFF & byte4)
      i += 3
    elif byte & 0xC0 == 0x80:
      byte2 = struct.unpack('B', bytes[i+1])[0]
      byte3 = struct.unpack('B', bytes[i+2])[0]
      number = ((0x3F & byte) << 16) + ((0xFF & byte2) << 8) + (0xFF & byte3)
      i += 2
    elif byte & 0xC0 == 0x40:
      byte2 = struct.unpack('B', bytes[i+1])[0]
      number = ((0x3F & byte) << 8) + (0xFF & byte2)
      i += 1
    else:
      number = 0xFF & byte
    i += 1
    numbers.append(number)
  return numbers

def gamma_encode(arr):
  bytestream = []
  j = 0
  digits = -1
  numbersLeft = True
  while numbersLeft:
      byte = 0
      for i in range(7,-1,-1):
        if digits < 0:
          if j < len(arr):
            num = arr[j]
            j += 1
            digits = 2 * int(math.floor(math.log(num, 2)))
          else:
            numbersLeft = False
            break
        if (num >> digits) & 0x01 == 0x01:
          byte += 0x01 << i
        digits -= 1
      bytestream.append(chr(byte))
  return bytestream

def gamma_decode(bytes):
  numbers = []
  zeroCount = 0
  isCountingZeros = True
  num = 0
  for b in bytes:
    byte = struct.unpack('B', b)[0]
    i = 7
    while i > -1:
      if isCountingZeros:
        if (byte >> i) & 0x01 == 0x01:
          isCountingZeros = False
        else:
          zeroCount += 1
          i -= 1
      else:
        if (byte >> i) & 0x1 == 0x01:
          num += pow(2,zeroCount)
        zeroCount -= 1
        if zeroCount < 0:
          numbers.append(num)
          zeroCount = 0
          num = 0
          isCountingZeros = True
        i -= 1
  return numbers
