# coding: utf-8
from applicationinsights import TelemetryClient
import sys,hashlib,os.path,re, uuid
import platform

IKEY = "0823bae8-a3b8-4fd5-80e5-f7272a2377a9"
LANGUAGE = "Python"
DEVICE = "RaspberryPi"
PROMPT_TEXT = "\nMicrosoft would like to collect data about how users use Azure IoT " \
    "samples and some problems they encounter. Microsoft uses this information to improve "\
    "our tooling experience. Participation is voluntary and when you choose to participate " \
    "your device automatically sends information to Microsoft about how you use Azure IoT "\
    "samples. \n\nSelect y to enable data collection (y/n, default is y) "

class Telemetry:

    def __init__(self):
        self.telemetry = TelemetryClient(IKEY)
        if os.path.exists("telemetry.config"):
            config_file = open("telemetry.config", "r")
            if config_file.read() == "1":
                self.enable_telemetry = True
            else:
                self.enable_telemetry = False
        else:
            self.enable_telemetry = self._query_yes_no(PROMPT_TEXT)
            config_file = open("telemetry.config", "w")
            if self.enable_telemetry:
                config_file.write("1")
                self.telemetry.track_event("yes", {"device": DEVICE, "language": LANGUAGE})
            else:
                config_file.write("0")
                self.telemetry.track_event("no", {"device": DEVICE, "language": LANGUAGE})
        self.telemetry.flush()

    def send_telemetry_data(self, iot_hub_name, event, message):
        if self.enable_telemetry:
            hash_mac = self._get_mac_hash()
            hash_iot_hub_name = hashlib.sha256(iot_hub_name.encode("utf-8")).hexdigest()
            self.telemetry.track_event(event, {"iothub": hash_iot_hub_name, "message": message,
                                          "language": LANGUAGE, "device": DEVICE, "mac": hash_mac,
                                          "osType": platform.system(), "osPlatform": platform.dist()[0],
                                          "osRelease": platform.dist()[1]})
            self.telemetry.flush()

    def _get_mac_hash(self):
        mac = ":".join(re.findall("..", "%012x" % uuid.getnode()))
        return hashlib.sha256(mac.encode("utf-8")).hexdigest()

    def _query_yes_no(self, question):
        global input
        default = "y"
        valid = {"y": True, "n": False}
        prompt = " [Y/n] "
        while True:
            sys.stdout.write(question + prompt)
            try:
                input = raw_input
            except NameError:
                pass
            choice = input().lower()
            if default is not None and choice == "":
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'y' or 'n' ")
