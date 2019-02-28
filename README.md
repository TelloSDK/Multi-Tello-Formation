***Tello Swarm Python Program***

0. This program is only available for the Tello EDU, which is SDK 2.0 and above.

1. First, you need to write the script command set you want to run in the script. 
The file name of the script is suffixed with .txt, which is a normal text document.
The way of the run the python code with '.txt' script is: Open the command line window,and run: python multi_tello_test.py script file name.txt。
'.txt' Scripting examples are as follows：

```
scan 1
battery_check 20
correct_ip
1=0TQDF6GBMB5SMF
*>takeoff
sync 10
1>land

```

The supported script commands are as follows:

- scan [The number of tellos]

  This script command will find the tellos to be connected in the network segment until the corresponding number of tellos are found.
  Attention:This must be the first script command of the script.
  
- battery_check [Minimum power value]

  Check the power of all the tello. If any of the tello's power is less than the provided value, the program will automatically terminate.
  The power value range is 0~100.The recommended setting is 20, which is 'battery_check 20'.
  
- correct_ip

  Bind the SNs of the tello and their assigned ip addresses.By this way you will be able to to be able to specify a specific tello to execute 
  the commands.(You can understand it plainly: This script command is to remember the ip address assigned to each tello under the LAN.)
  Attention:This script command must be placed after 'scan' and 'battery_check', and not be placed after the script command with '>'.
  
- [Tello's id]=[Tello's SN]

  Binding the serial number (SN) of tello with the tello's id (the tello's id is in the script command with '>',and is the number on the left of '>')
  Attention:This script command should be placed after 'correct_ip'.
  The left side of '=' is the id of tello, and the right side is the SN of tello.
  The SN can be read by the script ip.txt.
  E.g. open the command line window and run: 
  
  ```
  python multi_tello_test.py ip.txt
  
  ```
  
  Each time you run the script ip.txt, you can only connect one tello. If the operation is successful, the SN of the tello will be displayed on the command line window. 
  The SN format is like 0TQDF6GBMBTEWV.
  Alternatively, you can also read the SN of tello by its tag in the battery slot.(That is, the tag that records the name of the tello wifi). 
  The first line is the SN of tello.
  
- [Tello's id]>[SDK command]

  Sends an SDK command to the tello with the specified id. Each Tello will execute the next SDK command only after the last SDK command is completed. 
  Therefore, this script command can also be understood as adding the SDK command to be executed by Tello.
  Tello's id range starts from 1. If * is used, it means sending the same SDK command to all Tello.
  The SDK command is command supported by Tello SDK. For example, "takeoff".For more SDK command,please refer to :
  https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf
  
- sync [waiting time]

  Synchronize all SDK commands that have been sent.
  If all the SDK commands before the 'sync' are completed (return the response of 'ok'), continue to execute script commands of the .txt script.
  If the time to wait for the response of the SDK commands exceeds the given [waiting time], it means that the response of the 
  SDK command has not been successfully received, or the previous SDK commands has not been completed.
  In this case, 'sync' will end, and stop waiting.The .txt script will continue to execute downwards.
  
- // 

  Add notes.
  On the same line, the text after '//' will be ignored by the program.
  In-line comment is not supported.
  E.g. Don't program:
  
  ```
  scan 2 // scan 2 drones
  ```
  
  Instead,you should program as follows:
  
  ```
  // scan 2 drones
  scan 2
  ```
  
- delay [delay time(s)]

  The number of seconds set by the delay.
  E.g.If you want 1 and 2 to take off one second apart, you can write:
  
  ```
  1>takeoff
  delay 1
  2>takeoff
  ```
  
  Attention:'delay' cannot be used with '>'.For example,it cannot be written: 1>delay 1
  
2. Environment configuration and installation of related dependencies：

- Use a one-click installation script：

  Enter the install folder, select the corresponding script according to the computer system (windows, linux or macos), 
  and run (Windows:double-click the file, linux or macos:open the command line window and run the file).

- Manual installation：

  Install python2.7 and pip first. Python download on the official website.Pip can be installed using the get-pip.py file 
  (included with the folder). As shown:
  
  ```
  python get-pip.py
  ```
  
  Run command in the command line window:
  Windows：
  
  ```
  python -m pip install netifaces
  python -m pip install netaddr
  ```
 
  Linux&&Macos：
  
  ```
  sudo pip install netifaces
  sudo pip install netaddr
  ```
  
  to install realated dependencies. 

3. Set up Tello to station mode

      1) Turn on Tello
      2) Connected  to Tello's Wi-Fi. (e.g. Tello-AB89C4)
      3) In the formation_setup.py, add the wifi name and wifi password
	  
      ```
      set_ap(ssid, password)
      ``` 
	  
      4) Save the formation_setup.py and run in command line window:
	  
      ```
      python formation_setup.py
      ``` 
	  
      If you see some response text as shown:
	  
      ```
      sending command command
      from ('192.168.10.1', 8889): ok
      sending command ap [your ssid] [your password]
      from ('192.168.10.1', 8889): OK,drone will reboot in 3s
      ``` 
	  
      It means the ap mode setup is successful.

4. Run the python code with .txt script.

  ```
  python multi_tello_test.py filename.txt
  ```
  
  The command line window will print each command and its response. 
  After the execution is finished, a log will be generated in the 'log' folder,named after the ending time.

5. Ways to prevent packet loss.

  If you are worried about the loss of a certain SDK command or tello response during wireless transmission,
  You can add 'Re' to the SDK command in the script command with '>'.After adding this symbol, Python will 
  send special-format command to the tello repeatedly.And Tello will only execute the command once, if tello 
  successfully executes the command,The 'ok' reply in a special format will be repeated sent back by tello.
  E.g.
  
  ```
  1>Re takeoff
  ``` 
  
  Attention:
		1) There must be a space in the 'Re' and SDK command!
		2) 'Re' can only be added before the SDK command, but not before the script command, that is, 
			it can only be used before the SDK command in the script command with '>'!
		3) This way of preventing packet loss is only applicable to tello EDU.
		
6. Executable file version.

  If you are unfamiliar with Python, or if you skip the installation of various Python dependencies directly, 
  you can extract Tello-Swarm.zip. It contains two .exe files, which are
  The main program for tello swarms and the sub program for setting the tello into the station mode.
  Refer to the UserGuide.txt file in the archive for more details.
