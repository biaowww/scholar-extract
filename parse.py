node = open("node.txt","w")
edges = open("edges.txt","w")

nodes = {}
with open("all.csv") as inf:
    aaa = inf.readline()
    n =
    for zz in inf:
        n += 1
        if n > 1000 :
            break
        z = zz.rstrip().split(",")
        if len(z) != 8 : continue
        name = z[2]

       # print name,z[5]
        nodes[z[5]] = z[2]
        conames = z[6].split("#")
        for coname in conames:
            name2 = coname.split("|")
            #print z[5], name2
            if len(name2[0]) == 0:
                continue
            nodes[name2[2]] = name2[0]
            edges.write("\t".join([z[5],name2[2]])+"\n")


for key in nodes:
    node.write(key+'\t'+nodes[key]+'\n')

node.close()
edges.close()