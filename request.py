from mcstatus import JavaServer
from mcstatus import dns
from mcstatus import BedrockServer
import re

def detect_ansi(text):
    if "§" in text:
        return True
    else:
        return False

def resolve(ip, port):
    try:
        data = dns.resolve_mc_srv(ip)
        return data[0], str(data[1])
    except:
        return ip, port

def request(ip, type, port):
    if type == "java":
        try:
            player = []
            data = resolve(ip, port)
            server = JavaServer.lookup(data[0] + ":" + str(data[1]))
            status = server.status()
            #print(f"The server has {status.players.online} player(s) online and replied in {status.latency} ms")
            r_replaced = re.sub(r"§.", "", status.description)
            try:
                if len(status.players.sample):
                    for x in status.players.sample:
                        if detect_ansi(x.name) == False:
                            player.append(x.name)
                        else:
                            player.append("Not Avaible")
                            break
                else:
                    player.append("Not Avaible")
            except Exception as e:
                player.append("Not Avaible")
                
            return status.players.online, status.players.max, r_replaced, status.favicon, status.version.name, player
        
        except Exception as e:
            print(f"Request java Except -> {e}")
            return 0, 0, "offline", e

    elif type == "bedrock":
        try:
            player = ['Not Avaible']
            server = BedrockServer.lookup(ip + ":" + port)
            status = server.status()
            r_replaced = re.sub(r"§.", "", status.motd)
            #print(f"The server has {status.players_online} players online and replied in {status.latency} ms")
            return status.players_online, status.players_max, r_replaced, None, status.version.version, player
        except Exception as e:
            print(f"Request bedrock Except -> {e}")
            return 0, 0, "offline", e
        
#print(request("mc.snownetwork.xyz", "java", "25565"))