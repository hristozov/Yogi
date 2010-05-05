import sys,os

InvalidArgument="Invalid argument passed to module trace"
_NotSupportedPlatform="This platform is not supported!"
class TraceError:pass

def traceRoute(host,MaxTTL=None,WaitTime=None):
    """Returns the route to the specified host.
       I prefer to use the built-in traceroute tools - it's far less coding and we don't need setuid"""
    if sys.platform=="win32":
        commandline="tracert "
        if MaxTTL: commandline+="-h "+str(MaxTTL)+" "
        if WaitTime: commandline+="-w "+str(1000*int(WaitTime))+" "
        commandline+=host
        route=[q.split()[-1] for q in os.popen(commandline).readlines()[4:-2]]
        for t in range(len(route)):
            route[t]=route[t].replace('[','')
            route[t]=route[t].replace(']','')
        if filter((lambda t: not t=="." and not t.isdigit()),[x for v in route for x in v]):raise TraceError
        if not len(route): raise TraceError
        return route
    elif sys.platform=="linux2":
        #to be fixed:
        #sys.stderr.close()
        #os.close(2)
        commandline="traceroute "
        if MaxTTL: commandline+="-m "+str(MaxTTL)+" "
        if WaitTime: commandline+="-w "+str(WaitTime)+" "
        commandline+=host
        route=[]
        #route=[q.split()[2] for q in os.popen(commandline).readlines()[1:]]
        #for t in range(len(route)):
        #    route[t]=route[t].replace('(','')
        #    route[t]=route[t].replace(')','')
        for line_output in os.popen(commandline).readlines()[0:]:
            startindex=-1
            endindex=-1
            for v in range(len(line_output)):
                if line_output[v]=="(":
                    startindex=v
                if line_output[v]==")":
                    endindex=v
                    if startindex>=endindex or startindex<=0:
                        raise TraceError
                    else:
                        route.append(line_output[startindex+1:endindex])
                    break
        if filter((lambda t: not t=="." and not t.isdigit()),[x for v in route for x in v]):raise TraceError
        if not len(route): raise TraceError
        return route
    else:raise(_NotSupportedPlatform) #none of the if-s
    
if __name__=="__main__":
    pass #testing
