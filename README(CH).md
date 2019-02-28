***Tello多机编队程序(Python)***

0.该程序仅适用于tello EDU,即SDK2.0及以上版本。

1. 首先，你需要将你要跑的脚本指令写在脚本里面，脚本的格式为.txt，即普通的文本文档。
运行这套代码的方式为:打开命令行窗口,运行: python multi_tello_test.py 脚本文件名.txt。
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
支持的脚本指令：
- scan [要找的tello数量]
  这个脚本指令会在网段中找连接的tello，直到找到对应数量的tello为止
  注意:这必须是脚本的第一个脚本指令。
  
- battery_check [最低电量值]
  检查所有tello的电量。若有任意一台电量<提供的值，程序自动终止。
  电量值区间为0~100，建议设置为20，即battery_check 20。
  
- correct_ip
  绑定tello的产品序列号和连上wifi后的ip地址，以便在后续的编队飞行中能够指定特定的飞机执行特定的脚本指令
  (你可以理解为:这条指令是为了记录所有已连接的tello在局域网中被分配的ip地址)
  注意:这条脚本指令最好紧接在'scan'和'battery_check'之后，不要放在有'>'的脚本指令之后 
  
- [Tello的id]=[Tello的SN]
  绑定tello的产品序列号(SN)与飞机id(飞机id即在带有'>'的脚本指令中，'>'左边的数字)
  注意这条脚本指令要放在correct_ip之后
  '='左边是飞机的id，右边是飞机的产品序列号
  产品序列号可以通过脚本ip.txt读取，即打开命令行窗口并运行:python multi_tello_test.py ip.txt
  每次运行脚本ip.txt时，只能连接一架飞机，若运行成功，则会在命令行窗口上显示这架tello的SN，格式形如：0TQDF6GBMBTEWV
  或者，也可以在tello的电池槽中的标签(即记录着tello wifi名称的标签)中读取tello的SN，第一行即为tello的SN。
  
- [Tello的id]>[发给tello的SDK命令]
  向指定id的tello发送SDK指令。每台Tello只有在完成上一个SDK指令后才会执行下一个SDK指令。因此这个脚本指令也可以理解为添加Tello待执行的SDK指令。
  Tello的id范围是由1开始，如果使用*，则代表对全部Tello发送同一个SDK指令
  SDK指令为Tello SDK 支持的指令。如"takeoff"，更多的SDK指令请参照：
  https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello_SDK_2.0_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E.pdf
  
- sync [等待时间]
  对已发送的所有SDK指令进行同步
  如果在sync这一脚本指令之前的所有SDK指令都已经完成（返回ok），则继续往下执行txt脚本
  如果等待SDK指令的回复的时间超过给定的[等待时间]，则意为着没有成功收到SDK指令的回复，或者之前的SDK指令仍未全部完成。
  在这种情况下，sync会结束，即停止等待，脚本会继续向下执行。
  
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
  
- delay [延时的时间，单位为秒]
  延时设定的秒数，比如延时1秒，则为delay 1
  例如:想让1和2相隔一秒起飞，则可编写：
  ```
  1>takeoff
  delay 1
  2>takeoff
  ```
  注意:'delay'不能与'>'配合使用，即不能书写：1>delay 1
2. 环境配置及安装依赖项：

- 使用一键安装脚本：
  进入install文件夹，根据电脑的系统（windows,linux或macos）选择对应的脚本并运行（windows系统双击文件，linux或macos则打开命令行窗口并运行文件）

- 手动安装：
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

3. 设置Tello到station模式
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

4. 跑脚本
  ```
  python multi_tello_test.py 文件名.txt
  ```
  命令行将打出每一个条指令及其回复。执行结束后会把命令都存在log文件夹下，以测试结束时间命名。
  在example_script文件夹中，提供了若干个示例脚本，仅供参考。
	
5. 方便地读取飞机SN
  连接飞机的wifi，运行 
  ```
  python multi_tello_test.py ip.txt
  ``` 
  可在命令行窗口打印得到产品序列号

6. 防止丢包的方式
  如果担心某一条SDK指令或者tello的应答，在无线传输过程中发生丢包，可以使用在含有'>'的脚本指令中，
  在SDK指令前加入'Re'，加入该符号后，python对tello将对tello重复发送多条特殊格式的指令，tello将
  只执行一次该指令，如果tello成功执行指令，将会重复返回多条特殊格式的'ok'回复。
  示例:
  ```
  1>Re takeoff
  ``` 
  注意：1、'Re'和SDK指令中必须有一个空格!
		2、'Re'只能加在SDK指令之前，而不能加在脚本指令之前,即只能用于含'>'的脚本指令中的SDK指令之前!
		3、该防止丢包的方式只适用于tello EDU。
		
7. 可直接执行的多机编队程序(.exe)
  如果你对python不熟悉，或者你直接跳过各种Python依赖项的安装，你可以解压Tello-Swarm.zip。里面包含两个.exe文件，分别是
  用于编队飞行的主程序和用于设置tello进入station模式的副程序。具体使用细节参照压缩包中的UserGuide.txt文件。
