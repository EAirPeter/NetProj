ss = '''[overall-config]
# the difficulty should be a float in range (0.000, 1.000)
difficulty = 0.003 
# the contentFilePath points to the file (text-file recommended) that will be used as the content of blocks
# make sure all the clients contentFile share the same content, so that you can see it in the chain as a whole
contentFilePath = ./article.txt

# appoint the ipAddr and port of this client
[local-config]
ipAddr = %s
port = %s
# note that id should be less than 4 characters
id = %s
# RTO's unit is second
RTO = 0.1

# give all the peers ip address and port
# including this client is permitted
[peer-config]
'''

peer_list = ""
for machine in range(0, 4):
    for process in range(0, 16):
        peer_list += "node" + str(machine* 16 + process) + " = 11.11.3." + \
            str(19 + machine) + ":" + str(20000 + process) + "\n"
ss += peer_list
for machine in range(0, 4):
    for process in range(0, 16):
        f = open("config/" + str(machine) +"-"+ str(process) + ".cfg", "w")
        print(ss % ("11.11.3." + str(19 + machine), str(20000 + process),
                    (process + 100 * machine)), file=f)
        f.close()
