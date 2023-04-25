from mcstatus import JavaServer, dns

def resolve(ip, port):
    try:
        data = dns.resolve_mc_srv(ip)
        return data[0], str(data[1])
    except:
        return ip, port

datas = resolve("doskapmc.net", "25565")
server = JavaServer.lookup(datas[0] + ":" + datas[1])
status = server.status()
print("Total online: " + str(status.players.online))