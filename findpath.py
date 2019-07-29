from graph_tool.all import *
from pylab import *
import pickle
import sys

def intersect(a, b):
    return set(a).intersection(b)

def getAdrsForTxId(txId):
    adrList = []
    for key in txIds:
        if txId in txIds[key]:
           if key not in adrList:
                adrList.append(key)
    return adrList

def edgeExists(a, b):
    if a in edges:
       if b in edges[a]:
           return True
    elif b in edges:
       if a in edges[b]:
           return True
    return False


clusterAddresses = pickle.load(open("clusterAddresses.txt", "rb"))
txIds = pickle.load(open("txIds.txt", "rb"))
startAdr = sys.argv[1]
endAdr = sys.argv[2]

g = Graph(directed = False)
vertexLabels = g.new_vertex_property("string")
vertexLabelsLong = g.new_vertex_property("string")
edgeLabels = g.new_edge_property("string")
edgeLabelsLong = g.new_edge_property("string")

with open("cluster.csv", "w") as file:
    for adr in clusterAddresses:
        file.write(adr + "\n")

with open("cluster-txIds.csv", "w") as file:
    for adr in txIds:
        file.write(adr + ";" + ";".join(txIds[adr]) + "\n")

vertexes = {}
edges = {}
rootNode = None
endNode = None
for adr in clusterAddresses:
    v = g.add_vertex()
    if adr == startAdr or adr == endAdr:
    	  vertexLabels[v] = adr
    else:
        vertexLabels[v] = adr[:8]
    vertexLabelsLong[v] = adr
    vertexes[adr] = v
    if adr == startAdr:
        rootNode = v
    if adr == endAdr:
        endNode = v

for adr in clusterAddresses:
    for txId in txIds[adr]:
        for adrTarget in getAdrsForTxId(txId):
            if adr != adrTarget:
                if not edgeExists(adr, adrTarget):
                    e = g.add_edge(vertexes[adr], vertexes[adrTarget])
                    if adr not in edges:
                       edges[adr] = {}
                    if adrTarget not in edges:
                       edges[adrTarget] = {}
                    edges[adr][adrTarget] = 1
                    edges[adrTarget][adr] = 1
                    edgeLabels[e] = txId[:10]
                    edgeLabelsLong[e] = txId

if rootNode == None:
    print("rootNode is None")
    quit()

vertexList, edgeList = graph_tool.topology.shortest_path(g, rootNode, endNode)
print("Vertexes:")
for vertex in vertexList:
    print(str(vertex) + ": " + vertexLabelsLong[vertex])

print("\nEdges:")
for edge in edgeList:
    print(str(edge) + ": " + edgeLabelsLong[edge])


gRender = Graph(directed = False)
vertexLabelsRender = gRender.new_vertex_property("string")
vertexLabelsLongRender = gRender.new_vertex_property("string")
edgeLabelsRender = gRender.new_edge_property("string")
edgeLabelsLongRender = gRender.new_edge_property("string")
vertexesRender = {}

for edge in edgeList:
    for address in getAdrsForTxId(edgeLabelsLong[edge]):
        newVertex = gRender.add_vertex()
        vertexLabelsRender[newVertex] = address[:8]
        vertexLabelsLongRender[newVertex] = address
        vertexesRender[address] = newVertex
    for address1 in getAdrsForTxId(edgeLabelsLong[edge]):
        for address2 in getAdrsForTxId(edgeLabelsLong[edge]):
            if address1 != address2:
                newEdge = gRender.add_edge(vertexesRender[address1], vertexesRender[address2])
                edgeLabelsRender[newEdge] = edgeLabels[edge]
                edgeLabelsLongRender[newEdge] = edgeLabelsLong[edge]

for edge in edgeList:
    newEdge = gRender.add_edge(vertexesRender[vertexLabelsLong[edge.source()]], vertexesRender[vertexLabelsLong[edge.target()]])

pos = sfdp_layout(gRender, K = 650)
graph_draw(gRender, pos, output_size=(3000, 3000), vertex_color=[1,1,1,0],
           vertex_size=12, edge_pen_width=1.2,
           vcmap=matplotlib.cm.gist_heat_r, output="cluster.png",
           vertex_text = vertexLabelsRender, edge_text = edgeLabelsRender)
