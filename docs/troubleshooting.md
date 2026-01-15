# Troubleshooting

Common issues and solutions for the Levolor BLE integration.

## Discovery Issues

### "No Levolor devices found"

**Causes:**
- Remote is not powered on or has dead batteries
- Remote is too far from Home Assistant's Bluetooth adapter
- Another device (phone) is already connected to the remote
- Bluetooth is disabled or not working on the HA host

**Solutions:**
1. Replace batteries in the remote
2. Move the remote closer to your Home Assistant server
3. Disconnect the Levolor app on your phone (turn off Bluetooth or close the app)
4. Check Home Assistant's Bluetooth integration is working:
   - Go to **Settings** → **Devices & Services** → **Bluetooth**
   - Verify the adapter is detected and working

### Remote discovered but setup fails

**Causes:**
- Connection interrupted during setup
- Temporary BLE interference

**Solutions:**
1. Try again - BLE connections can be flaky
2. Move closer to the remote
3. Restart Home Assistant and try again

## Connection Issues

### "Failed to connect to the Levolor remote"

**Causes:**
- Phone app is connected to the remote (only one connection allowed)
- Remote went to sleep
- BLE adapter issues

**Solutions:**
1. **Disconnect phone**: Turn off Bluetooth on your phone or close the Levolor app
2. **Wake the remote**: Press any button on the physical remote to wake it up
3. **Retry**: The integration will retry automatically, but you can trigger a retry by reloading the integration

### Commands succeed but blinds don't move

**Causes:**
- Wrong channel selected
- Remote not paired with the blind
- RF interference

**Solutions:**
1. **Verify channel**: Test with the physical remote to confirm which channel the blind responds to
2. **Re-pair if needed**: Use the physical remote to re-pair the blind to a channel
3. **Check RF path**: Ensure nothing is blocking the RF signal between remote and blinds

### Intermittent connectivity

**Causes:**
- Bluetooth range issues
- Interference from other devices
- Remote entering sleep mode

**Solutions:**
1. Move the remote closer to Home Assistant (or use a Bluetooth proxy)
2. The integration includes retry logic - most intermittent failures recover automatically
3. Consider a USB Bluetooth adapter closer to the remote's location

## Bluetooth Proxy Setup

For remotes that are far from your Home Assistant server, you can use an ESPHome Bluetooth Proxy:

1. Flash an ESP32 with ESPHome Bluetooth Proxy firmware
2. Place the ESP32 near your Levolor remote
3. Connect it to Home Assistant
4. The Levolor remote will be discoverable through the proxy

See the [ESPHome Bluetooth Proxy documentation](https://esphome.io/components/bluetooth_proxy.html) for setup instructions.

## State Accuracy

### Position doesn't match actual blind position

**Cause:** The Levolor protocol doesn't provide position feedback. State is assumed based on commands sent.

**Solutions:**
- This is a limitation of the protocol
- Use Open/Close commands rather than position for reliability
- Actual position may drift if you use the physical remote

### Entity shows unavailable

**Causes:**
- Remote not responding
- Bluetooth adapter issues

**Solutions:**
1. Check remote has batteries
2. Try sending a command - the integration will attempt to reconnect
3. Restart the integration if the issue persists

## Home Assistant Logs

Enable debug logging to troubleshoot issues:

```yaml
logger:
  default: info
  logs:
    custom_components.levolor_ble: debug
```

After adding this to `configuration.yaml`, restart Home Assistant. Logs will show BLE connection details and command execution.

## Getting Help

If you continue to have issues:

1. Check the [GitHub Issues](https://github.com/TheEagleByte/ha-levolor-remote/issues) for known problems
2. Gather debug logs (see above)
3. Open a new issue with:
   - Home Assistant version
   - Debug logs
   - Description of the problem
   - Steps to reproduce

## Related Documentation

- [Protocol Documentation](protocol.md) - Technical BLE protocol details
- [Configuration Guide](configuration.md) - Setup instructions
