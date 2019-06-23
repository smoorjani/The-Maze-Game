def make_maze(w = 16, h = 8):
    from random import shuffle, randrange
    import numpy as np

    vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
    

    ver = [["#  "] * w + ['#'] for _ in range(h)] + [[]]
    hor = [["###"] * w + ['#'] for _ in range(h + 1)]


    def walk(x, y):
        vis[y][x] = 1
 
        d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        shuffle(d)
        for (xx, yy) in d:
            if vis[yy][xx]: continue
            if xx == x:
                hor[max(y, yy)][x] = "#  "
            if yy == y:
                #ver[y][max(x, xx)] = "   "
                if randrange(1,10) == 1:
                    ver[y][max(x, xx)] = " S "
                else:
                    ver[y][max(x, xx)] = "   "
            walk(xx, yy)
 
    def teleport():
        for x in range(len(hor)):
            r = randrange(0,w-1)
            if randrange(1,5) == 1 and hor[x][r] == "###":
                hor[x][r] = "#TT"
        return hor

    walk(randrange(w), randrange(h))
    r_ver = ver[:]

    ver[1][0] = '#P '
    ver[h-1][w] = 'D'

    hor = teleport()
    #print(hor)

    f = open("level/maze_lvl","w+")
    s = ""
    for (a, b, c) in zip(hor, ver, r_ver):
        b = list(map(lambda x: x.replace('S',' ').replace('P',' ').replace('D','#'),c))
        f.write(''.join(a + ['\n'] + b + ['\n'] + c + ['\n']))
        #s += ''.join(a + ['\n'] + b + ['\n'])
    f.close()
    return s
 
if __name__ == '__main__':
    print(make_maze())
