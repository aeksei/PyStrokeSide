import os
from loggers import logger
from subprocess import Popen, PIPE

# r"USBPcapCMD.exe -d \\.\USBPcap1 -o - -A"
_PATH_USBPCAP = 'C:\\Program Files\\USBPcap\\USBPcapCMD.exe'
LEN_BUF = 1
C2_VENDOR_ID = 0x17a4


class USBPcapCMD:
    def __init__(self):
        self.logger = logger('USBPcapCMD')

        if not os.path.isfile(_PATH_USBPCAP):
            self.logger.critical('Not found "USBPcapCMD.exe" in path C:\\Program Files\\USBPcap')
            exit()

        self.usb_interface = None
        self.capture_process = None

        self.find_erg()

    def find_erg(self):
        process = Popen('listdevs.exe', stdout=PIPE, shell=True)
        for dev in process.stdout.readlines():
            if int(dev[:4], 16) == C2_VENDOR_ID:
                dev_interface = dev[dev.find(b'(')+1:dev.find(b')')]
                dev_interface = dev_interface.decode().replace(',', '').split(' ')
                self.usb_interface = '\\\\.\\USBPcap' + dev_interface[1], str(int(dev_interface[3]) - 1)

        if self.usb_interface is None:
            self.logger.critical('Not found ergs')
            exit()

    def capture(self):
        command = ' '.join([_PATH_USBPCAP.replace(':\\', ':\\"')+'"',
                            '-d', self.usb_interface[0],
                            '-o', '-',
                            '--devices', self.usb_interface[1]])
        self.logger.debug(command)
        self.capture_process = Popen(command, stdout=PIPE, shell=True)
        self.logger.info('Start capture traffic')

    def recv(self, buf=LEN_BUF):
        return self.capture_process.stdout.read(buf)


if __name__ == "__main__":
    usbpcap = USBPcapCMD()
    usbpcap.capture()
