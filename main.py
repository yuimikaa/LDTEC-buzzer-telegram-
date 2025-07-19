import network
import urequests
import time
from machine import Pin, time_pulse_us

# === WiFi Credentials ===
ssid = 'WFI_NAME'
password = 'WIFI_PASSWORD'

# === Telegram Bot Info ===
bot_token = 'BOT_TOKEN'
chat_id = 'CHAT_ID'

# === Pin Setup ===
trig = Pin(5, Pin.OUT)
echo = Pin(18, Pin.IN)
buzzer = Pin(21, Pin.OUT)

# === Measure Distance ===
def get_distance():
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()
    
    # Take multiple readings for averaging
    readings = []
    for _ in range(5):  # Take 5 measurements to average
        try:
            duration = time_pulse_us(echo, 1, 30000)
            distance_cm = (duration / 2) / 29.1
            # Only add valid readings (below 400 cm or so)
            if distance_cm < 400:
                readings.append(distance_cm)
            time.sleep(0.05)  # Short delay between readings
        except OSError as e:
            print("Error measuring distance:", e)
            return -1  # Error or timeout
    
    # If we have valid readings, calculate average
    if readings:
        average_distance = sum(readings) / len(readings)
        return average_distance
    return -1  # In case all readings failed

# === Connect to WiFi ===
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Connecting to WiFi...", end='')

    timeout = 30  # Set a timeout for WiFi connection (in seconds)
    start_time = time.time()
    
    while not wlan.isconnected():
        if time.time() - start_time > timeout:
            print("\nWiFi connection timed out!")
            return False
        print(".", end='')
        time.sleep(0.5)
        
    print("\nConnected to WiFi:", wlan.ifconfig())
    return True

# === Send Message to Telegram ===
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        print("Sending to Telegram:", message)
        response = urequests.post(url, json=payload)
        
        # Check the response status code for successful delivery
        if response.status_code == 200:
            print("Telegram response:", response.text)
        else:
            print("Error: Failed to send Telegram message. Status code:", response.status_code)
        
        response.close()
    except Exception as e:
        print("Telegram Error:", e)

# === Main Program ===
if connect_wifi():
    last_sent_time = time.ticks_ms()

    while True:
        distance = get_distance()
        print("Distance:", distance, "cm")

        if distance > 0:
            # Send distance to Telegram every 5 seconds
            if time.ticks_diff(time.ticks_ms(), last_sent_time) > 5000:
                send_telegram_message(f"Jarak semasa: {distance:.2f} cm")
                last_sent_time = time.ticks_ms()

            # Trigger buzzer if distance is under 10 cm
            if distance < 10:
                buzzer.on()
                print("Buzzer ON - Distance:", distance, "cm")  # Debugging
            else:
                buzzer.off()
                print("Buzzer OFF - Distance:", distance, "cm")  # Debugging

        time.sleep(0.5)
else:
    print("Failed to connect to WiFi.")
