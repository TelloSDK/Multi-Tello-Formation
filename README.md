***Tello命令集测试工具 - 多机编队版本***
1. 将要跑的命令集写在脚本里面，脚本的格式为.txt，即普通的文本文档，运行指令的格式为python multi_tello_test 脚本文件名.txt。
脚本编写示例如下：
```
scan 1
battery_check 20
correct_ip
1=0TQDF6GBMB5SMF
*>takeoff
sync 10
1>land
```
支持的命令：
- scan [要找的tello数量]
    这个指令会在网段中找连接的tello，直到找到对应数量的tello为止
    注意，这必须是脚本的第一个命令。
- battery_check [最低电量值]
    检查所有tello的电量。若有任意一台电量<提供的值，程序自动终止。
    电量值区间为0~100
- [Tello的id]>[发给tello的命令]
  向指定的tello发送命令。每台Tello只有在完成上一个命令后才会执行下一个命令。因此这个命令也可以理解为添加Tello待执行的命令。
  Tello的id范围是由1开始，如果使用*，则代表对全部Tello发送同一指令
  命令为Tello能接受的格式。如"takeoff"
- sync [等待时间]
  对已发送的所有命令进行同步
  如果sync指令之上的所有指令都已经完成（返回ok），则继续往下执行脚本
  如果等待时间超过给定的[等待时间]，且上面的命令仍未全部完成。也会继续向下执行。
- // 
  添加注释
  同一行，在'//'之后的文字将被程序忽略。
  不支持in-line comment。
  E.g. 不要写
  ```
  scan 2 // scan 2 drones
  ```
  而要写
  ```
  // scan 2 drones
  scan 2
  ```
  
- correct_ip
  绑定tello的产品序列号和连上wifi后的ip地址，以便在后续的编队飞行中能够指定特定的飞机执行目标指令
  注意这条指令最好紧接在scan或者battery_check之后，不要放在有'>'的指令之后
  
- [Tello的id]=[Tello的SN]
  绑定tello的产品序列号与飞机id(飞机id即在带有'>'指令中，'>'左边的数字)
  注意这条指令要放在correct_ip之后
  '='左边是飞机的id，右边是飞机的产品序列号
  产品序列号可以通过脚本readip.txt读取，一次连接一架飞机，最后会在终端上显示一个飞机的序列号，格式形如：0TQDF6GBMBTEWV
  
- delay [延时的时间，单位为秒]
  延时设定的秒数，比如延时1秒，则为delay 1
  例如想让1和2相隔一秒起飞，则可编写：
  ```
  1>takeoff
  delay 1
  2>takeoff
  ```
2. 设置Tello到ap模式：
先安装python2.7和pip。python上官网下载，pip可使用get-pip.py文件（文件夹已附带）来安装，如使用python get-pip.py指令。
运行
Windows：
```
python -m pip install netifaces
python -m pip install netaddr
```
Linux&&Macos：
```
sudo pip install netifaces
sudo pip install netaddr
sudo pip install matplotlib
```
以安装依赖。

1) 打开Tello
2) 连上Tello Wi-Fi. (e.g. Tello-AB89C4)
3) 在formation_setup.py里, 加入wifi名字以及wifi密码
```
set_ap(ssid, password)
``` 
4) 保存并且运行
```
python formation_setup.py
``` 
如看到
```
sending command command
from ('192.168.10.1', 8889): ok
sending command ap [your ssid] [your password]
from ('192.168.10.1', 8889): OK,drone will reboot in 3s
``` 
就ok了

3. 跑脚本
```
python multi_tello_test.py 文件名.txt
```
命令行将打出每一个条指令及其回复。执行结束后会把命令都存在log文件夹下，以测试结束时间命名。

4、方便地读取飞机SN
连接飞机的wifi，运行 
```
python multi_tello_test.py ip.txt
``` 
可在命令行窗口打印得到产品序列号
