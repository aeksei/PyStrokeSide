from loggers import logger
from subprocess import Popen, PIPE
from scapy.arch.windows import WinProgPath
from scapy.layers.usb import get_usbpcap_devices, get_usbpcap_interfaces

# r"USBPcapCMD.exe -d \\.\USBPcap1 -o - -A"
LEN_BUF = 1


class USBPcapCMD:
    def __init__(self):
        self.logger = logger('USBPcapCMD')

        self.win = WinProgPath()
        self.usb_interface = self.find_erg()
        self.process = self.capture()

    def find_erg(self):
        for interface in get_usbpcap_interfaces():
            for device in get_usbpcap_devices(interface[0]):
                if device[1][device[1].find(' ') + 1:] == 'USB-устройство ввода':
                    self.logger.debug('Find erg on interface {}'.format(interface[1]))
                    return interface
        self.logger.critical('Not Find erg')
        return None

    def capture(self):
        if self.usb_interface is  None:
            exit()
        else:
            process = Popen([self.win.usbpcapcmd,
                             '-d', self.usb_interface,
                             '-o', '-',
                             '-A'],
                            stdout=PIPE)
            self.logger.info('Start capture traffic')
            return process

    def recv(self, buf=LEN_BUF):
        return self.process.stdout.read(buf)




if __name__ == "__main__":
    usbpcap = USBPcapCMD()

    usbpcap.capture()
