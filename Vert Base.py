from z3 import set_option, Bool, Solver, AtLeast, AtMost, Or, Not, sat
# Use this to track solver progress
set_option(verbose=10)

# Set up edge variables
bools = [[Bool('x_%s_%s' % (i,j)) for i in range(99)] for j in range(99)]
x = {i:{j:(bools[j][i] if i>j else (False if i==j else bools[i][j])) for j in range(99)} for i in range(99)}


# Modify xij to simplify problem

# Verts in L and M have degree 14 already, so they don't need more edges
for i in range(0,15):
    for j in range(i+1,99):
        x[i][j] = False
        x[j][i] = False
        
# LMM triangles
for i in range(1,15,2):
    x[0,i] = True
    x[i,0] = True
    x[0,i+1] = True
    x[i+1,0] = True
    x[i,i+1] = True
    x[i+1,i] = True
    
# MR edges
next_vert = 15
for i in range(1,13,2):
    for j in range(i+2,15,2):
        x[i,next_vert]=True
        x[next_vert,i]=True
        x[j,next_vert]=True
        x[next_vert,j]=True
        next_vert += 1
        
        x[i+1,next_vert]=True
        x[next_vert,i+1]=True
        x[j,next_vert]=True
        x[next_vert,j]=True
        next_vert += 1
        
        x[i,next_vert]=True
        x[next_vert,i]=True
        x[j+1,next_vert]=True
        x[next_vert,j+1]=True
        next_vert += 1
        
        x[i+1,next_vert]=True
        x[next_vert,i+1]=True
        x[j+1,next_vert]=True
        x[next_vert,j+1]=True
        next_vert += 1
        
# Set up length-two path variables
bools_2 = [[[Bool('y_%s_%s_%s' % (i,j,k)) for k in range(99)] for j in range(99)] for i in range(99)]
y = {i:{j:{k: (x[i][j] if i==k else (False if (i==j or j==k) else (bools_2[k][j][i] if i>k else bools_2[i][j][k]))) for k in range(99)} for j in range(99)} for i in range(99)}

# Initialize solver
s = Solver()
s.set("sat.cardinality.solver", True)

# Add degree conditions
s.add([AtLeast(*([x[i][j] for j in range(99)]),14) for i in range(15,99)])
s.add([AtMost(*([x[i][j] for j in range(99)]),14) for i in range(15,99)])

# This part takes several minutes to run.
for i in range(1,99):
    # Add common neighbor conditions
    s.add([AtMost(*([y[i][j][k] for j in range(99)]+[x[i][k]]), 2) for k in range(i+1,99)])
    s.add([AtLeast(*([y[i][j][k] for j in range(99)]+[x[i][k]]), 2) for k in range(i+1,99)])
    # Add yijk = (xij and xjk) conditions
    for k in range(i+1,99):
        s.add([Or([j==i, j==k, y[i][j][k], Not(x[i][j]), Not(x[j][k])]) for j in range(99)])
        s.add([Or([j==i, j==k, Not(y[i][j][k]), x[i][j]]) for j in range(99)])
        s.add([Or([j==i, j==k, Not(y[i][j][k]), x[j][k]]) for j in range(99)])

# Check for solution. This part may take a very, very long time to run.
if s.check()==sat:
    print("We found a solution!!! :)")
    # Retrieve and print solution
    m=s.model()
    for i in range(98):
        for j in range(i+1,99):
            if m[x[i][j]] is None:
                continue
            print(i,j,1 if m.evaluate(x[i][j]) else 0)
else:
    print ("Failed to solve :(")