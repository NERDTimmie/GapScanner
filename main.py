from digi import ble
import xbee
import time
import machine
import uos

LOCATION_SCAN_REQUEST = "SCAN_REQUEST"
ADVERTISMENT_PREFIX = "AAA_"


def form_mac_address(addr: bytes) -> str:
    return ":".join('{:02x}'.format(b) for b in addr)


def form_adv_name(name):
    payload = bytearray()
    payload.append(len(name) + 1)
    payload.append(0x08)
    payload.extend(name.encode())
    return payload


def turn_on_ble():
    ble.active(True)
    print("Started Bluetooth with address of: {}".format(form_mac_address(ble.config("mac"))))


def turn_off_ble():
    ble.active(False)
    print("Stopped Bluetooth")


def start_advertising():
    payload = form_adv_name(ADVERTISMENT_PREFIX + form_mac_address(ble.config("mac")))
    print("Advertising payload: {}".format(payload))
    ble.gap_advertise(100000, payload)


def send_scan_request():
    try:
        xbee.transmit(xbee.ADDR_BROADCAST, LOCATION_SCAN_REQUEST)
        print("Data sent successfully")
    except Exception as e:
        print("Transmit failure: %s" % str(e))


def start_scan():
    scanner = None
    mac_address_rssi_values = {}
    mac_address_rssi_values_avg = {}
    try:
        # Start a scan to run for 30 seconds
        scanner = ble.gap_scan(30000, interval_us=50000, window_us=50000)
        # Loop through all advertisements until the scan has stopped.
        for adv in scanner:
            if ADVERTISMENT_PREFIX in adv["payload"]:
                mac_address = adv["payload"].split(b'_')[1].decode()
                print(mac_address)
                print(adv["rssi"])
                if mac_address not in mac_address_rssi_values:
                    mac_address_rssi_values[mac_address] = [adv["rssi"]]
                else:
                    mac_address_rssi_values[mac_address].append(adv["rssi"])
    finally:
        print("Scan done, Results:")
        if scanner is not None:
            scanner.stop()
        for mac_address, rssi_values in mac_address_rssi_values.items():
            avg_rssi = sum(rssi_values) // len(rssi_values)
            print(mac_address)
            print(avg_rssi)
            mac_address_rssi_values_avg[mac_address] = avg_rssi
    return mac_address_rssi_values_avg


def localiation_cycle():
    turn_on_ble()
    start_advertising()
    scan_result = start_scan()
    turn_off_ble()
    return scan_result


#while True:
#    received_msg = xbee.receive()
#    if received_msg:
#        sender = received_msg['sender_eui64']
#        payload = received_msg['payload']
#        message = (''.join('{:02x}'.format(x).upper() for x in sender), payload.decode())
#        print(received_msg)
#        if message == LOCATION_SCAN_REQUEST:
#            scan_result = localiation_cycle()
#            xbee.transmit(sender, scan_result)
#            print("completed scan")

print(localiation_cycle())