import os,pydot,sys,trace,socket,query,shelve

#our default set of options
ShowOurNode=True
MakeASNLookup=False
MakeCountryLookup=False
WaitTime=None
MaxTTL=None
DBName=None
GraphDpi=100
OutName="out.jpg"
OurNode="Grapher"
Verbose=False

_NotImplemented="Not implemented!"
_InvalidArgs="Invalid (or not enough) arguments!"

class NetworkGraph:
    """The main NetworkGraph object
    It has methods for adding new traces in the graph, as well as a method for
    "adding" two NetworkGraph objects. Note that we cannot delete a specific
    trace from the graph!"""
    def __init__(self):
        self.graph={}
    def __add__(self,othergraph):
        """Adding two graphs."""
        retgraph=NetworkGraph()
        retgraph.graph=othergraph.graph
        for v in self.graph.keys():
            if v in retgraph.graph.keys():
                #we already have this node
                for q in self.graph[v]:
                    if not q in retgraph.graph[v]:
                        retgraph.graph[v].append(q)
            else:
                #we don't have it
                retgraph.graph[v]=self.graph[v]
        return retgraph
    def addRoute(self,route):
        """Adds a route to the specified destination to the graph.
        Not intended for direct callingm use addTrace instead!."""
        for t in range(len(route)):
            if route[t] in self.graph.keys():
                if not route[t-1] in self.graph[route[t]] and t>0:
                    self.graph[route[t]].append(route[t-1])
                try:
                    if not route[t+1] in self.graph[route[t]]:
                        self.graph[route[t]].append(route[t+1])
                except(IndexError):pass
            else:
                self.graph[route[t]]=[]
                if t>0: self.graph[route[t]].append(route[t-1])
                try: self.graph[route[t]].append(route[t+1])
                except(IndexError):pass
    def addTrace(self,dest):
        """Adds the trace to every destination to the graph"""
        for v in dest:
            if Verbose:
                print'Tracing '+str(v)+'...'
            try:
                if ShowOurNode: self.addRoute([OurNode]+trace.traceRoute(v,MaxTTL,WaitTime))
                else: self.addRoute(trace.traceRoute(v,MaxTTL,WaitTime))
            except(trace.TraceError):
                print 'Error tracing '+str(v)+'. Skipping target.'

def printGraph(ingraph,outputname='out.jpg'):
    """Gets an NetworkGraph object and 'prints' it in jpg file."""
    print 'Building DNS cache...'
    dnscache={}
    for t in ingraph.graph.keys():
        if not t in dnscache.keys() and not t==OurNode:
            try: dnscache[t]=socket.gethostbyaddr(t)[0]
            #added gaierror to avoid exceptions on grapher nodes:
            except(socket.herror,socket.gaierror): pass
    if MakeASNLookup:
        print 'Building ASN cache...'
        ascache={}
        for t in ingraph.graph.keys():
            if not t in ascache.keys() and not t==OurNode:
                try: ascache[t]=query.getASN(t)
                except:pass
    if MakeCountryLookup:
        print 'Building country code cache...'
        ccache={}
        for t in ingraph.graph.keys():
            if not t in ccache.keys() and not t==OurNode:
                try: ccache[t]=query.getCountry(t)
                except:pass
    edges=[]
    print 'Creating the output image...'
    for k in ingraph.graph.keys():
        for t in ingraph.graph[k]:
            if not (k,t) in edges:
                edge1=t
                edge2=k
                if t in dnscache.keys():
                    edge1=dnscache[t]
                if k in dnscache.keys():
                    edge2=dnscache[k]
                if MakeASNLookup:
                    if t in ascache.keys():
                        edge1+=" ["+str(ascache[t])+"]"
                    if k in ascache.keys():
                        edge2+=" ["+str(ascache[k])+"]"
                if MakeCountryLookup:
                    if t in ccache.keys():
                        edge1+=" ["+str(ccache[t])+"]"
                    if k in ascache.keys():
                        edge2+=" ["+str(ccache[k])+"]"
                if not (edge2,edge1) in edges:edges.append((edge1,edge2))
    g=pydot.graph_from_edges(edges)
    g.dpi=GraphDpi
    g.write_jpeg(outputname, prog='dot') 

def showUsage():
    """Basic usage help"""
    print 'Usage: yogi.py [-a] [-bDBNAME] [-c] [-dRES] [-hHOPS] [-nGRAPHER] [-oOUT] [-tTIME] [-v] TARGET_1 ... TARGET_N'
    print 'Options:'
    print '     -a      Show AS the numbers in the graph'
    print '     -b      Sets the name of the DB file'
    print '     -c      Show the country codes in the graph'
    print '     -d      Sets the resolution (in dpi, default is 100)'
    print '     -o      Sets the name of the output image (default is \'out.jpg\')'
    print '     -h      Sets the maximum hop count (TTL) (default is system default)'
    print '     -n      Sets the name of the Grapher host (default is \'Grapher\')'
    print '     -t      Sets the maximum wait time for the trace (in seconds, default is system default)'
    print '     -v      Verbose mode'
    
if __name__=="__main__": #we are not imported
    dest=[]
    if len(sys.argv)<2:
        print 'Not enough arguments'
        showUsage()
        sys.exit(-1)
    for k in range(1,len(sys.argv)):
        if sys.argv[k][0]=="-": #an option
            if len(sys.argv[k])==1: #only a dash
                print 'Invalid option:',sys.argv[k]
                showUsage()
                sys.exit(-1)
            if sys.argv[k].startswith('-b'):
                DBName=sys.argv[k][2:]
                for chk in DBName:
                    if not chk.isalnum() and not chk=='.':
                        print 'Invalid database file name!'
                        showUsage()
                        sys.exit(-1)
                continue
            if sys.argv[k].startswith('-d'):
                GraphDpi=int(sys.argv[k][2:])
                if GraphDpi<10 or GraphDpi>10000:
                    print 'Invalid DPI value!'
                    showUsage()
                    sys.exit(-1)
                continue
            if sys.argv[k].startswith('-h'):
                MaxTTL=int(sys.argv[k][2:])
                if MaxTTL<=1 or MaxTTL>100:
                    print 'Invalid maximum TTL value!'
                    showUsage()
                    sys.exit(-1)
                continue
            if sys.argv[k].startswith('-n'):
                OurNode=sys.argv[k][2:]
                for chk in OurNode:
                    if not chk.isalnum():
                        print 'Invalid grapher node name!'
                        showUsage()
                        sys.exit(-1)
                continue
            if sys.argv[k].startswith('-o'):
                OutName=sys.argv[k][2:]
                for chk in OutName:
                    if not chk.isalnum() and not chk=='.':
                        print 'Invalid output file name!'
                        showUsage()
                        sys.exit(-1)
                continue
            if sys.argv[k].startswith('-t'):
                WaitTime=int(sys.argv[k][2:])
                if WaitTime<1 or WaitTime>120:
                    print 'Invalid wait time value!'
                    showUsage()
                    sys.exit(-1)
                continue
            for v in sys.argv[k][1:]:
                if v.lower()=="a":
                    MakeASNLookup=True
                    continue
                if v.lower()=="c":
                    MakeCountryLookup=True
                    continue
                if v.lower()=="v":
                    Verbose=True
                    continue
                #it's an unknown character...
                print 'Invalid option:',sys.argv[k],'(near "'+str(v)+'")'
                showUsage()
                sys.exit(-1)
        else: dest.append(sys.argv[k]) #not an option, it's a host
    if not len(dest):
        if not DBName:
            print 'No targets defined.'
            showUsage()
            sys.exit(-1)
        else:
            print 'No targets defined, but found DB file name.'
            try:
                fp=shelve.open(DBName)
            except:
                print "Error opening the DB file!"
                sys.exit(-1)
                
            if fp.has_key('data'):
                printGraph(fp['data'])
                fp.close()
                sys.exit(0)
            else:
                print "No data found in the DB file."
                fp.close()
                sys.exit(-1)

    if Verbose:
        print 'ASN lookup:',MakeASNLookup
        print 'Country lookup:',MakeCountryLookup
        print 'Resolution:',GraphDpi
        print 'Output name:',OutName
        if DBName: print 'DB name:',DBName
        if MaxTTL: print 'MaxTTL',MaxTTL
        if WaitTime: print 'WaitTime',WaitTime
        print 'Destinations:',dest
        
    if sys.platform=="linux2":
        sys.stderr.close() #closing the stderr. should be in trace.py!
        os.close(2) #the same, on C level
        
    c=NetworkGraph()
    c.addTrace(dest)
    if DBName:
        #we're using a db
        #certainly not the smartest way
        try:
            fp=shelve.open(DBName)
        except:
            print "Error opening the DB file!"
            sys.exit(-1)
        if fp.has_key('data'):
            #we already have some data
            if(Verbose):
                print 'We already have data in '+DBName+'.'
            outgraph=c+fp['data']
            fp['data']=outgraph
        else:
            if(Verbose):
                print 'Data file '+DBName+' is empty.'
            fp['data']=c
            outgraph=c
        fp.close()
        printGraph(outgraph,OutName)
    else:
        printGraph(c,OutName)