from flask import Flask, render_template, jsonify, request
import RPi.GPIO as GPIO
import time
import threading

app = Flask(__name__)

# GPIO 핀 번호 설정
TRIG = 23
ECHO = 24
LED_PIN = 17

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

# 전역 변수
current_distance = 0
led_status = False

# 거리 측정 함수
def measure_distance():
    GPIO.output(TRIG, True) # 1로 올림
    time.sleep(0.00001) 
    GPIO.output(TRIG, False) # 0으로 내림
    
    start_time = time.time() # 시간을 기록
    timeout = time.time() + 0.1  # 100ms 타임아웃
    
    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        start_time = time.time()
    
    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        end_time = time.time()
    
    try:
        elapsed_time = end_time - start_time # 왔다갔다 작동한 시간 측정
        distance = (elapsed_time * 34300) / 2
        return round(distance, 2)
    except:
        return -1  # 에러 시


def update_sensor_data():
    global current_distance # 전역 변수
    while True:
        current_distance = measure_distance()
        time.sleep(0.5) # 0.5초 딜레이

# 백그라운드에서 센서 데이터 업데이트
sensor_thread = threading.Thread(target=update_sensor_data) # 스레딩 모듈의 스레딩 모듈 생성 / 함수 바인딩
sensor_thread.daemon = True # 백그라운드 스레드
sensor_thread.start() 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_distance')
def get_distance():
    return jsonify({'distance': current_distance})

@app.route('/led/<action>')
def control_led(action):
    global led_status
    if action == 'on':
        GPIO.output(LED_PIN, GPIO.HIGH)
        led_status = True
        return jsonify({'status': 'LED ON'})
    elif action == 'off':
        GPIO.output(LED_PIN, GPIO.LOW)
        led_status = False
        return jsonify({'status': 'LED OFF'})
    return jsonify({'status': 'Invalid action'})

@app.route('/get_led_status')
def get_led_status():
    return jsonify({'led_on': led_status})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        GPIO.cleanup()
