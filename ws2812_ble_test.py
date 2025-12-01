#!/usr/bin/env python3
"""Simple BLE client to exercise the WS2812 protocol.

Usage examples:

    python ws2812_ble_test.py --name "HOSHI-MATRIX" --event 0x10 --subevent 0x01 --payload 01
    python ws2812_ble_test.py --address AA:BB:CC:DD:EE:FF --event 0x10 --subevent 0x01 --payload 01
    python ws2812_ble_test.py --name "HOSHI-MATRIX" --timesync

The script uses the Bleak library (install via `pip install bleak`).
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import struct
from typing import Optional

from bleak import BleakClient, BleakScanner

FRAME_HEADER = 0xAA55
PROTOCOL_VERSION = 0x01
MAX_PAYLOAD = 32

UUID_SERVICE = "0000ff00-0000-1000-8000-00805f9b34fb"
UUID_CHAR_COMMAND = "0000ff01-0000-1000-8000-00805f9b34fb"

logger = logging.getLogger("ws2812_ble_test")


async def discover_device_by_name(device_name: str, timeout: float = 10.0) -> Optional[str]:
    """Discover BLE device by advertised name and return its address."""
    logger.info(f"Scanning for device with name: {device_name}")
    
    devices = await BleakScanner.discover(timeout=timeout)
    
    for device in devices:
        if device.name and device.name == device_name:
            logger.info(f"Found device: {device.name} at {device.address}")
            return device.address
    
    logger.warning(f"Device with name '{device_name}' not found")
    return None


def crc_xor(data: bytes) -> int:
    checksum = 0
    for b in data:
        checksum ^= b
    return checksum


def build_frame(event: int, sub_event: int, sequence: int, payload: bytes) -> bytes:
    if len(payload) > MAX_PAYLOAD:
        raise ValueError("payload too long")

    frame = bytearray()
    frame += bytes([(FRAME_HEADER >> 8) & 0xFF, FRAME_HEADER & 0xFF])
    frame.append(PROTOCOL_VERSION)
    frame.append(event & 0xFF)
    frame.append(sub_event & 0xFF)
    frame.append(sequence & 0xFF)
    frame.append(len(payload))
    frame += payload
    checksum = crc_xor(frame)
    frame.append(checksum)
    return bytes(frame)


def parse_ack(data: bytes) -> dict:
    if len(data) < 9:
        raise ValueError("ACK frame too short")
    header = (data[0] << 8) | data[1]
    if header != FRAME_HEADER:
        raise ValueError("Invalid header")
    version = data[2]
    if version != PROTOCOL_VERSION:
        raise ValueError("Protocol version mismatch")
    event = data[3]
    sub_event = data[4]
    seq = data[5]
    data_len = data[6]
    payload = data[7:7 + data_len]
    checksum_index = 7 + data_len
    if checksum_index >= len(data):
        raise ValueError("ACK data length mismatch")
    checksum = data[checksum_index]
    if checksum != crc_xor(data[:-1]):
        raise ValueError("Checksum mismatch")
    return {
        "event": event,
        "sub_event": sub_event,
        "sequence": seq,
        "status": payload[0] if payload else None,
        "ref_event": payload[1] if len(payload) > 1 else None,
        "ref_sub": payload[2] if len(payload) > 2 else None,
    }


async def run(args: argparse.Namespace) -> None:
    logging.basicConfig(level=logging.INFO)
    sequence = args.sequence & 0xFF

    payload = bytes.fromhex(args.payload) if args.payload else b""

    if args.timesync:
        import time
        ts = int(time.time())
        payload = struct.pack("<I", ts)
        args.event = 0x11
        args.subevent = 0x00

    frame = build_frame(args.event, args.subevent, sequence, payload)
    logger.info("Frame bytes: %s", frame.hex())

    # Determine device address
    device_address = args.address
    if args.name:
        device_address = await discover_device_by_name(args.name, args.scan_timeout)
        if not device_address:
            raise RuntimeError(f"Could not find device with name: {args.name}")

    logger.info(f"Connecting to device: {device_address}")

    async with BleakClient(device_address) as client:
        if not client.is_connected:
            raise RuntimeError("Failed to connect")

        await client.start_notify(UUID_CHAR_COMMAND, lambda _, data: logger.info("ACK: %s", parse_ack(data)))
        await client.write_gatt_char(UUID_CHAR_COMMAND, frame)
        await asyncio.sleep(args.wait)
        await client.stop_notify(UUID_CHAR_COMMAND)


def main() -> None:
    parser = argparse.ArgumentParser(description="WS2812 BLE Protocol Tester")
    
    # Device selection (mutually exclusive)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--address", help="BLE MAC address of the ESP32C3")
    group.add_argument("--name", help="BLE advertised name of the device (e.g., 'HOSHI-MATRIX')")
    
    parser.add_argument("--event", type=lambda x: int(x, 0), default=0x10)
    parser.add_argument("--subevent", type=lambda x: int(x, 0), default=0x01)
    parser.add_argument("--payload", default="01", help="Payload bytes in hex, e.g. 01 or 010203")
    parser.add_argument("--sequence", type=lambda x: int(x, 0), default=1, help="Sequence number (0-255)")
    parser.add_argument("--wait", type=float, default=2.0, help="Seconds to wait for ACK notifications")
    parser.add_argument("--scan-timeout", type=float, default=10.0, help="Seconds to scan for device by name")
    parser.add_argument("--timesync", action="store_true", help="Send a timestamp sync frame")

    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
