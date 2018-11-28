# -*- coding: utf-8 -*-
import sys
import time
from tello_manager import *
import Queue
import time
import os
import binascii
reload(sys)
sys.setdefaultencoding('utf-8')

def create_execution_pools(num):
    pools = []
    for x in range(num):
        execution_pool = Queue.Queue()
        pools.append(execution_pool)
    return pools


def drone_handler(tello, queue):
    while True:
        while queue.empty():
            pass
        command = queue.get()
        tello.send_command(command)


def all_queue_empty(execution_pools):
    for queue in execution_pools:
        if not queue.empty():
            return False
    return True

def all_got_response(manager):
    for tello_log in manager.get_log().values():
        if not tello_log[-1].got_response():
            return False
    return True

def save_log(manager):
    log = manager.get_log()

    if not os.path.exists('log'):
        try:
            os.makedirs('log')
        except Exception, e:
            pass

    out = open('log/' + start_time + '.txt', 'w')
    cnt = 1
    for stat_list in log.values():
        out.write('------\nDrone: %s\n' % cnt)
        cnt += 1
        for stat in stat_list:
            #stat.print_stats()
            str = stat.return_stats()
            out.write(str)
        out.write('\n')

def check_timeout(start_time, end_time, timeout):
    diff = end_time - start_time
    time.sleep(0.1)
    return diff > timeout


manager = Tello_Manager()
start_time = str(time.strftime("%a-%d-%b-%Y_%H-%M-%S-%Z", time.localtime(time.time())))

try:
    file_name = sys.argv[1]
    f = open(file_name, "r")
    commands = f.readlines()

    tello_list = []
    execution_pools = []
    sn_ip_dict = {}
    id_sn_dict = {}
    ip_fid_dict = {}

    for command in commands:
        if command != '' and command != '\n':
            command = command.rstrip()

            if '//' in command:
                # ignore comments
                continue
            elif 'scan' in command:
                num_of_tello = int(command.partition('scan')[2])

                manager.find_avaliable_tello(num_of_tello)
                tello_list = manager.get_tello_list()
                execution_pools = create_execution_pools(num_of_tello)

                for x in range(len(tello_list)):
                    t1 = Thread(target=drone_handler, args=(tello_list[x], execution_pools[x]))
                    ip_fid_dict[tello_list[x].tello_ip] = x
                    #str_cmd_index_dict_init_flag [x] = None
                    t1.daemon = True
                    t1.start()


            elif '>' in command:
                id_list = []
                id = command.partition('>')[0]
                if id == '*':
                    for x in range(len(tello_list)):
                        id_list.append(x)
                else:
                    # index starbattery_checkt from 1
                    id_list.append(int(id)-1) 
                action = str(command.partition('>')[2])

                # push command to pools               
                for tello_id in id_list:
                    tmp_sn = id_sn_dict[tello_id]
                    reflec_ip = sn_ip_dict[tmp_sn]
                    fid = ip_fid_dict[reflec_ip]
                    execution_pools[fid].put(action)

            elif 'battery_check' in command:
                
                threshold = int(command.partition('battery_check')[2])
                for queue in execution_pools:
                    queue.put('battery?')

                # wait till all commands are executed
                while not all_queue_empty(execution_pools):
                    time.sleep(0.5)

                # wait for new log object append
                time.sleep(1)

                # wait till all responses are received
                while not all_got_response(manager):
                    time.sleep(0.5)

                for tello_log in manager.get_log().values():
                    battery = int(tello_log[-1].response)
                    print ('[Battery_Show]show drone battery: %d  ip:%s\n' % (battery,tello_log[-1].drone_ip))
                    if battery < threshold:
                        print('[Battery_Low]IP:%s  Battery < Threshold. Exiting...\n'%tello_log[-1].drone_ip)
                        save_log(manager)
                        exit(0)
                print ('[Battery_Enough]Pass battery check\n')
            elif 'delay' in command:
                delay_time = float(command.partition('delay')[2])
                print ('[Delay_Seconds]Start Delay for %f second\n' %delay_time)
                time.sleep(delay_time)  
            elif 'correct_ip' in command:
                for queue in execution_pools:
                    queue.put('sn?') 
                while not all_queue_empty(execution_pools):
                    time.sleep(0.5)
                
                time.sleep(1)

                while not all_got_response(manager):
                    time.sleep(0.5) 
                for tello_log in manager.get_log().values():
                    sn = str(tello_log[-1].response)
                    tello_ip = str(tello_log[-1].drone_ip)
                    sn_ip_dict[sn] = tello_ip  
                    
            elif '=' in command:
                drone_id = int(command.partition('=')[0])
                drone_sn = command.partition('=')[2]
                id_sn_dict[drone_id-1] = drone_sn
                print ('[IP_SN_FID]:Tello_IP:%s------Tello_SN:%s------Tello_fid:%d\n'%(sn_ip_dict[drone_sn],drone_sn,drone_id))
                #print id_sn_dict[drone_id]
            elif 'sync' in command:
                timeout = float(command.partition('sync')[2])
                print '[Sync_And_Waiting]Sync for %s seconds \n' % timeout
                time.sleep(1)
                try:
                    start = time.time()
                    # wait till all commands are executed
                    while not all_queue_empty(execution_pools):
                        now = time.time()
                        if check_timeout(start, now, timeout):
                            raise RuntimeError

                    print '[All_Commands_Send]All queue empty and all command send,continue\n'
                    # wait till all responses are received
                    while not all_got_response(manager):
                        now = time.time()
                        if check_timeout(start, now, timeout):
                            raise RuntimeError
                    print '[All_Responses_Get]All response got, continue\n'
                except RuntimeError:
                    print '[Quit_Sync]Fail Sync:Timeout exceeded, continue...\n'


    # wait till all commands are executed
    while not all_queue_empty(execution_pools):
        time.sleep(0.5)

    time.sleep(1)

    # wait till all responses are received
    while not all_got_response(manager):
        time.sleep(0.5)

    save_log(manager)

except KeyboardInterrupt:
    print '[Quit_ALL]Multi_Tello_Task got exception. Sending land to all drones...\n'
    for ip in manager.tello_ip_list:
        manager.socket.sendto('land'.encode('utf-8'), (ip, 8889))

    save_log(manager)

