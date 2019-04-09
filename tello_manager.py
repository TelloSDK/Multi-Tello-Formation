import threading
from threading import Thread
import socket
import time
import netifaces
import netaddr
from netaddr import IPNetwork
from collections import defaultdict
from stats import Stats
import binascii
class Tello:
    """
    A wrapper class to interact with Tello
    Communication with Tello is handled by Tello_Manager
    """
    def __init__(self, tello_ip, Tello_Manager):
        self.tello_ip = tello_ip
        self.Tello_Manager = Tello_Manager
    def send_command(self, command):
        return self.Tello_Manager.send_command(command, self.tello_ip)

class Tello_Manager:
    def __init__(self):
        self.local_ip = ''
        self.local_port = 8889
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket.bind((self.local_ip, self.local_port))

        # thread for receiving cmd ack
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.tello_ip_list = []
        self.tello_list = []
        self.log = defaultdict(list)

        self.COMMAND_TIME_OUT = 9.0

        self.last_response_index = {}
        self.str_cmd_index = {}

    def find_avaliable_tello(self, num):
        """
        Find avaliable tello in server's subnets
        :param num: Number of Tello this method is expected to find
        :return: None
        """
        print '[Start_Searching]Searching for %s available Tello...\n' % num

        subnets, address = self.get_subnets()
        possible_addr = []

        for subnet, netmask in subnets:
            for ip in IPNetwork('%s/%s' % (subnet, netmask)):
                # skip local and broadcast
                if str(ip).split('.')[3] == '0' or str(ip).split('.')[3] == '255':
                    continue
                possible_addr.append(str(ip))

        while len(self.tello_ip_list) < num:
            print '[Still_Searching]Trying to find Tello in subnets...\n'

            # delete already fond Tello
            for tello_ip in self.tello_ip_list:
                if tello_ip in possible_addr:
                    possible_addr.remove(tello_ip)
            # skip server itself
            for ip in possible_addr:
                if ip in address:
                    continue

                # record this command
                self.log[ip].append(Stats('command', len(self.log[ip])))
                self.socket.sendto(b'command', (ip, 8889))
            time.sleep(5)

        # filter out non-tello addresses in log
        temp = defaultdict(list)
        for ip in self.tello_ip_list:
            temp[ip] = self.log[ip]
        self.log = temp



    def get_subnets(self):
        """
        Look through the server's internet connection and
        returns subnet addresses and server ip
        :return: list[str]: subnets
                 list[str]: addr_list
        """
        subnets = []
        ifaces = netifaces.interfaces()
        addr_list = []
        for myiface in ifaces:
            addrs = netifaces.ifaddresses(myiface)

            if socket.AF_INET not in addrs:
                continue
            # Get ipv4 stuff
            ipinfo = addrs[socket.AF_INET][0]
            address = ipinfo['addr']
            netmask = ipinfo['netmask']

            # limit range of search. This will work for router subnets
            if netmask != '255.255.255.0':
                continue

            # Create ip object and get
            cidr = netaddr.IPNetwork('%s/%s' % (address, netmask))
            network = cidr.network
            subnets.append((network, netmask))
            addr_list.append(address)
        return subnets, addr_list

    def get_tello_list(self):
        return self.tello_list

    def send_command(self, command, ip):
        """
        Send a command to the ip address. Will be blocked until
        the last command receives an 'OK'.
        If the command fails (either b/c time out or error),
        will try to resend the command
        :param command: (str) the command to send
        :param ip: (str) the ip of Tello
        :return: The latest command response
        """
        #global cmd
        command_sof_1 = ord(command[0])
        command_sof_2 = ord(command[1])
        if command_sof_1 == 0x52 and command_sof_2 == 0x65:
            multi_cmd_send_flag = True
        else :
            multi_cmd_send_flag = False

        if multi_cmd_send_flag == True:      
            self.str_cmd_index[ip] = self.str_cmd_index[ip] + 1
            for num in range(1,5):                
                str_cmd_index_h = self.str_cmd_index[ip]/128 + 1
                str_cmd_index_l = self.str_cmd_index[ip]%128
                if str_cmd_index_l == 0:
                    str_cmd_index_l = str_cmd_index_l + 2
                cmd_sof =[0x52,0x65,str_cmd_index_h,str_cmd_index_l,0x01,num + 1,0x20]
                cmd_sof_str = str(bytearray(cmd_sof))
                cmd = cmd_sof_str + command[3:]
                self.socket.sendto(cmd.encode('utf-8'), (ip, 8889))

            print '[Multi_Command]----Multi_Send----IP:%s----Command:   %s\n' % (ip, command[3:])           
            real_command = command[3:]
        else:
            self.socket.sendto(command.encode('utf-8'), (ip, 8889))
            print '[Single_Command]----Single_Send----IP:%s----Command:   %s\n' % (ip, command)
            real_command = command
        
        self.log[ip].append(Stats(real_command, len(self.log[ip])))
        start = time.time()
        while not self.log[ip][-1].got_response():
            now = time.time()
            diff = now - start
            if diff > self.COMMAND_TIME_OUT:
                print '[Not_Get_Response]Max timeout exceeded...command: %s \n' % real_command
                return    

    def _receive_thread(self):
        """Listen to responses from the Tello.

        Runs as a thread, sets self.response to whatever the Tello last returned.

        """
        while True:
            try:
                self.response, ip = self.socket.recvfrom(1024)
                ip = ''.join(str(ip[0]))
                if self.response.upper() == 'OK' and ip not in self.tello_ip_list:
                    print '[Found_Tello]Found Tello.The Tello ip is:%s\n' % ip
                    self.tello_ip_list.append(ip)
                    self.last_response_index[ip] = 100
                    self.tello_list.append(Tello(ip, self))
                    self.str_cmd_index[ip] = 1
                response_sof_part1 = ord(self.response[0])               
                response_sof_part2 = ord(self.response[1])
                if response_sof_part1 == 0x52 and response_sof_part2 == 0x65:
                    response_index = ord(self.response[3])
                    
                    if response_index != self.last_response_index[ip]:
                        #print '--------------------------response_index:%x %x'%(response_index,self.last_response_index)
                        print'[Multi_Response] ----Multi_Receive----IP:%s----Response:   %s ----\n' % (ip, self.response[7:])
                        self.log[ip][-1].add_response(self.response[7:],ip)
                    self.last_response_index[ip] = response_index
                else:
                    print'[Single_Response]----Single_Receive----IP:%s----Response:   %s ----\n' % (ip, self.response)
                    self.log[ip][-1].add_response(self.response,ip)
                #print'[Response_WithIP]----Receive----IP:%s----Response:%s----\n' % (ip, self.response)
                         
            except socket.error, exc:
                print "[Exception_Error]Caught exception socket.error : %s\n" % exc

    def get_log(self):
        return self.log


