#!/usr/bin/env python3
"""
WS2812 Matrix Configuration Interface
A Streamlit-based GUI for configuring WS2812 LED matrix effects
"""

import streamlit as st
import asyncio
import json
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# BLE related imports are intentionally performed lazily inside methods so
# the script can be executed (for help / info) on machines without BLE
# dependencies or without Streamlit available.

# Constants
DEVICE_NAME = "HOSHI-MATRIX"
FRAME_HEADER = 0xAA55
PROTOCOL_VERSION = 0x01

# Effect definitions
EFFECTS = {
    "Water Effect": 0x00,
    "Turn Left V1": 0x01,
    "Turn Left V2": 0x02,
    "Turn Left V3": 0x03,
    "Turn Right V1": 0x04,
    "Turn Right V2": 0x05,
    "Turn Right V3": 0x06,
    "Go Forward V1": 0x07,
    "Go Forward V2": 0x08,
    "Go Forward V3": 0x09,
    "Aurora Wave": 0x0A,
    "Rainbow Cycle": 0x10,
    "Plasma": 0x11,
    "Ripple": 0x12,
    "Cloud": 0x13,
    "Cylon": 0x14,
}

class WS2812Controller:
    def __init__(self):
        # Device state
        self.device_address = None
        self.client = None

        # Start a background event loop thread so BleakClient and scanner
        # always run on the same asyncio event loop.
        import threading

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _run_coro(self, coro):
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut.result()

    def connect(self, device_name: str) -> bool:
        return self._run_coro(self.connect_device(device_name))

    def send_command_sync(self, event: int, subevent: int, payload: bytes = b"") -> Dict[str, Any]:
        return self._run_coro(self.send_command(event, subevent, payload))

    def disconnect_sync(self) -> None:
        return self._run_coro(self.disconnect())

    async def connect_device(self, device_name: str) -> bool:
        """Connect to WS2812 device by name"""
        try:
            # Import BLE helpers lazily so script can be run on systems
            # without bleak installed (e.g., just to show the Streamlit hint)
            from ws2812_ble_test import discover_device_by_name
            from bleak import BleakClient

            self.device_address = await discover_device_by_name(device_name)
            if self.device_address:
                self.client = BleakClient(self.device_address)
                await self.client.connect()
                return True
            return False
        except Exception:
            # Re-raise so callers (UI) can present the error message in the
            # Streamlit context rather than trying to call Streamlit inside the
            # background coroutine thread.
            raise

    async def send_command(self, event: int, subevent: int, payload: bytes = b"") -> Dict[str, Any]:
        """Send command to device and wait for ACK"""
        if not self.client or not self.client.is_connected:
            raise Exception("Device not connected")

        # Import helpers lazily
        try:
            from ws2812_ble_test import build_frame, parse_ack
        except Exception as e:
            # If helper functions are not available, bubble up a clear error
            raise RuntimeError(
                "BLE helper functions not available (is ws2812_ble_test.py present?)"
            ) from e

        frame = build_frame(event, subevent, 1, payload)
        UUID_CHAR_COMMAND = "0000ff01-0000-1000-8000-00805f9b34fb"

        # Set up ACK handler
        ack_received = None

        def ack_handler(sender, data):
            nonlocal ack_received
            try:
                ack_received = parse_ack(data)
            except Exception as e:
                st.warning(f"Failed to parse ACK: {e}")

        # Start notification with error handling
        notify_started = False
        try:
            await self.client.start_notify(UUID_CHAR_COMMAND, ack_handler)
            notify_started = True

            # Send command
            await self.client.write_gatt_char(UUID_CHAR_COMMAND, frame)

            # Wait for ACK
            await asyncio.sleep(2.0)

        except Exception as e:
            raise Exception(f"Command send error: {e}") from e
        finally:
            # Always stop notification if it was started
            if notify_started:
                try:
                    await self.client.stop_notify(UUID_CHAR_COMMAND)
                except Exception as e:
                    st.warning(f"Error stopping notification: {e}")

        return ack_received

    async def disconnect(self):
        """Disconnect from device"""
        if self.client:
            await self.client.disconnect()

def main():
    st.set_page_config(
        page_title="WS2812 Matrix Config",
        page_icon="🎨",
        layout="wide"
    )

    st.title("🎨 WS2812 LED Matrix Configuration")
    st.markdown("Control your ESP32 WS2812 LED matrix via Bluetooth")

    # Initialize controller in session state
    if 'controller' not in st.session_state:
        st.session_state.controller = WS2812Controller()

    if 'connected' not in st.session_state:
        st.session_state.connected = False

    # Connection section
    st.header("🔗 Device Connection")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        device_name = st.text_input("Device Name", value=DEVICE_NAME, key="device_name")

    with col2:
        if st.button("🔍 Scan & Connect", type="primary"):
            with st.spinner("Scanning for device..."):
                try:
                    success = st.session_state.controller.connect(device_name)
                except Exception as e:
                    st.session_state.connected = False
                    st.error(f"Connection failed: {e}")
                else:
                    st.session_state.connected = bool(success)
                    if success:
                        st.success(f"✅ Connected to {device_name}")
                    else:
                        st.error(f"❌ Could not find device '{device_name}'")

    with col3:
        if st.button("🔌 Disconnect", disabled=not st.session_state.connected):
            try:
                st.session_state.controller.disconnect_sync()
            except Exception as e:
                st.warning(f"Disconnect error: {e}")
            st.session_state.connected = False
            st.info("📴 Disconnected")

    # Connection status
    if st.session_state.connected:
        st.success("🟢 Connected")
    else:
        st.warning("🟡 Not Connected")

    # Configuration section
    if st.session_state.connected:
        st.header("⚙️ Effect Configuration")

        # Effect selection
        effect_name = st.selectbox(
            "Select Effect",
            options=list(EFFECTS.keys()),
            key="effect_select"
        )

        effect_code = EFFECTS[effect_name]

        # Effect parameters based on selection
        st.subheader(f"📋 {effect_name} Parameters")

        if "Turn" in effect_name or "Forward" in effect_name:
            # Direction effects - might have speed or intensity
            intensity = st.slider("Intensity", 1, 255, 128, key="intensity")
            speed = st.slider("Speed", 1, 10, 5, key="speed")

            payload = bytes([intensity, speed])

        elif effect_name == "Aurora Wave":
            # Aurora specific parameters
            wave_speed = st.slider("Wave Speed", 1, 20, 10, key="wave_speed")
            brightness = st.slider("Brightness", 1, 255, 180, key="brightness")

            payload = bytes([wave_speed, brightness])

        elif effect_name in ["Rainbow Cycle", "Plasma", "Ripple", "Cloud"]:
            # Animation effects
            speed = st.slider("Animation Speed", 1, 20, 8, key="anim_speed")
            brightness = st.slider("Brightness", 1, 255, 200, key="anim_brightness")

            payload = bytes([speed, brightness])

        else:
            # Default payload
            payload = b"\x01"

        # Send command button
        if st.button("🚀 Apply Effect", type="primary"):
            with st.spinner("Sending command..."):
                try:
                    ack = st.session_state.controller.send_command_sync(
                        0x10,  # Event: Set Effect
                        effect_code,  # Sub-event: Effect code
                        payload
                    )

                    if ack:
                        if ack.get('status') == 0:  # Success
                            st.success(f"✅ Effect '{effect_name}' applied successfully!")
                        else:
                            st.error(f"❌ Command failed with status: {ack.get('status')}")
                    else:
                        st.warning("⚠️ No ACK received")

                except Exception as e:
                    st.error(f"❌ Failed to send command: {e}")

        # Advanced commands
        st.header("🔧 Advanced Commands")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⏰ Sync Time"):
                with st.spinner("Syncing time..."):
                    import time
                    ts = int(time.time())
                    payload = ts.to_bytes(4, byteorder='little')

                    try:
                        ack = st.session_state.controller.send_command_sync(
                            0x11,  # Event: Time Sync
                            0x00,  # Sub-event
                            payload
                        )

                        if ack and ack.get('status') == 0:
                            st.success("✅ Time synchronized!")
                        else:
                            st.error("❌ Time sync failed")

                    except Exception as e:
                        st.error(f"❌ Time sync error: {e}")

        with col2:
            if st.button("🔄 Clear Matrix"):
                with st.spinner("Clearing matrix..."):
                    try:
                        ack = st.session_state.controller.send_command_sync(
                            0x10,  # Event: Set Effect
                            0xFF,  # Sub-event: Clear
                            b""
                        )

                        if ack and ack.get('status') == 0:
                            st.success("✅ Matrix cleared!")
                        else:
                            st.error("❌ Clear failed")

                    except Exception as e:
                        st.error(f"❌ Clear error: {e}")

    # Footer
    st.markdown("---")
    st.markdown("*WS2812 Matrix Configuration Interface v1.0*")

if __name__ == "__main__":
    main()