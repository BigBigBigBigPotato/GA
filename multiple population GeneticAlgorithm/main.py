import random
import math
import turtle
import numpy as np
import copy

# pop_size表示种群数量,DNA_size表示拣选数量,K_Bound表示区域范围，X_Bound表示行数范围,Y_Bound表示列数范围,Pc为交叉率，Pm为变异率

POP_size = 200
DNA_size = 5
K_Bound = [1, 4]
X_Bound = [1, 10]
Y_Bound = [1, 10]
Pc = 0.8
Pm = 0.02
Generation = 1000  # 迭代次数


# 定义画一个运输单位的函数
def drawrectangle(x, y):
    turtle.up()
    turtle.setpos(x, y)
    turtle.down()
    i = 0
    while i < 4:
        turtle.forward(20)
        turtle.right(90)
        i += 1


# 画仓库的函数
def DrawWarehouse():
    # 货仓长48个单位长度，宽24个单位长度，每个拣选单位长宽20像素
    turtle.setup(960, 480)
    # 画出仓库模型
    turtle.tracer(False)
    drawrectangle(-460, 180)
    drawrectangle(460 - 20, 180)
    drawrectangle(-420, 220)
    drawrectangle(420 - 20, 220)
    # x为横坐标，y为纵坐标
    x = -460
    y = 140
    # i，j分别为控制仓库横纵布局的临时变量
    i = 3
    j = 0
    while y > -240:
        while x < -460 + i * 20:
            drawrectangle(x, y)
            drawrectangle(-x - 20, y)
            drawrectangle(-y - 240, -x - 240)
            drawrectangle(y + 240 - 20, -x - 240)
            print(-y - 240, -x - 240)
            print(y + 240 - 20, -x - 240)
            x += 20
        x = -460
        y -= 20
        i += 1
        j += 1
        if j == 2:
            i += 1
            j = 0
            y -= 20

    turtle.done()


# 初始种群
def init_pop(POP_size, DNA_size, K_Bound, X_Bound, Y_Bound):
    pop = []
    for i in range(POP_size):
        pop.append(random.sample(range(1, DNA_size + 1), DNA_size))

    individual = {}
    for i in range(1, DNA_size + 1):
        x_random = random.randint(X_Bound[0], X_Bound[1])
        individual[i] = [random.randint(K_Bound[0], K_Bound[1]),
                         x_random,
                         random.randint(Y_Bound[0], x_random + ((x_random - 1) // 2))]

    return pop, individual


# 自然选择，优胜劣汰
# def SelectBest(individual):


# 距离函数，给定个体DNA序列，即拣选点的次序，返回距离
def Distance(coordinate1, coordinate2):
    # coordinate1、coordinate2分别表示两个拣货单位的坐标
    k1 = coordinate1[0]
    x1 = coordinate1[1]
    y1 = coordinate1[2]
    k2 = coordinate2[0]
    x2 = coordinate2[1]
    y2 = coordinate2[2]
    a = 60  # a表示相邻拣货通道的距离
    w = 40  # w表示拣货通道转至斜主通道的距离
    # (Xi // 2)表示通道号,(Xi // 2)*3*20 表示Li，即通道长度
    # Yi * 20 表示Si
    # b 为 math.sqrt(2) * a
    if k1 == 0 and x1 == 0 and y1 == 0:  # P&D点到货位的距离
        return (x1 // 2) * 3 * 20 - y1 * 20 + w + math.sqrt(2) * a * (5 - x1 // 2)
    elif k2 == 0 and x2 == 0 and y2 == 0:  # 货位到P&D点的距离
        return (x2 // 2) * 3 * 20 - y2 * 20 + w + math.sqrt(2) * a * (5 - x2 // 2)
    elif k1 == k2 and x1 // 2 == x2 // 2:  # 两货位位于同区同一通道时
        return abs(y2 - y1) * 20
    elif k1 == k2 and x1 // 2 != x2 // 2:  # 两货位位于同区不同通道时
        d1 = (y1 + y2) * 20 + a * abs(x1 // 2 - x2 // 2)
        d2 = (x1 // 2 + x2 // 2) * 3 * 20 - (y1 + y2) * 20 + math.sqrt(2) * a * abs(x1 // 2 - x2 // 2) + 2 * w
        return min(d1, d2)
    elif (k1 == 1 and k2 == 2) or (k1 == 2 and k2 == 1) or (k1 == 3 and k2 == 4) or (k1 == 4 and k2 == 3):
        # 两货位位于1、2区时，3、4是对称的，故计算方法一致
        if x1 == x2:  # 同一通道
            return (x1 // 2 + x2 // 2) * 3 * 20 - (y1 + y2) * 20 + 2 * w
        else:  # 不同通道
            d1 = (x1 // 2 + x2 // 2) * 3 * 20 - (y1 + y2) * 20 + math.sqrt(2) * a * abs(x1 // 2 - x2 // 2) + 2 * w
            d2 = 2 * (x1 // 2) * 3 * 20 - y1 * 20 + y2 * 20 + 2 * w + a * abs(x1 // 2 - x2 // 2)
            return min(d1, d2)
    elif (k1 == 1 and k2 == 3) or (k1 == 3 and k2 == 1) or (k1 == 2 and k2 == 4) or (k1 == 4 and k2 == 2):
        # 两货位位于1、3或2、4区时
        d1 = (x1 // 2 + x2 // 2) * 3 * 20 - (y1 + y2) * 20 + math.sqrt(2) * a * (10 - x1 // 2 - x2 // 2) + 2 * w
        d2 = 2 * (x1 // 2) * 3 * 20 - y1 * 20 + y2 * 20 + 2 * w + a * (10 - x1 // 2 - x2 // 2)
        return min(d1, d2)
    elif (k1 == 1 and k2 == 4) or (k1 == 4 and k2 == 1):  # 两货位位于1、4区时
        d1 = (x1 // 2 + x2 // 2) * 3 * 20 - (y1 + y2) * 20 + math.sqrt(2) * a * (10 - x1 // 2 - x2 // 2) + 2 * w
        d2 = 2 * (x1 // 2 + x2 // 2) * 3 * 20 - (y1 + y2) * 20 + 4 * w + a * (10 - x1 // 2 - x2 // 2)
        return min(d1, d2)
    elif (k1 == 2 and k2 == 3) or (k1 == 3 and k2 == 2):  # 两货位位于2、3区时
        if x1 // 2 == x2 // 2 == 5:  # 都位于5号通道时
            return abs(y2 - y1) * 20
        else:  # 没有都位于5号通道时
            d1 = (y1 + y2) * 20 + a * (10 - x1 // 2 - x2 // 2)
            d2 = (x1 // 2 + x2 // 2) * 3 * 20 - (y1 + y2) * 20 + math.sqrt(2) * a * (10 - x1 // 2 - x2 // 2) + 2 * w
            return min(d1, d2)


# 计算每一个个体被选中的概率，得到适应度列表
def get_fitness(pop, individual):
    fitness = []
    # 计算每一个个体的的适应度，即 1 / 距离distance
    for i in range(len(pop)):
        distance = 0
        for j in range(len(pop[i])):
            if j == 0:
                distance = distance + Distance([0, 0, 0], individual[pop[i][j]])
            elif 0 < j < 4:
                distance = distance + Distance(individual[pop[i][j]], individual[pop[i][j + 1]])
            else:
                distance = distance + Distance(individual[pop[i][j]], [0, 0, 0])
        fitness.append(20 / distance)
    return fitness


# 物竞天择，适者生存。选择函数选出存活的个体
def select(pop, fitness):
    pop = np.asarray(pop)
    fitness = np.asarray(fitness)
    index = np.random.choice(np.arange(0, len(pop)), size=POP_size, replace=True, p=fitness / (fitness.sum()))
    return pop[index]


# 染色体交叉
def chromosome_crossover(a, b, father, mother):
    # 找出两个染色体交叉部分的独特基因
    father_unique = []
    mother_unique = []
    for i in father[a: b]:
        if i not in mother[a:b]:
            father_unique.append(i)
    for i in mother[a: b]:
        if i not in father[a:b]:
            mother_unique.append(i)
    father_unique_copy = father_unique.copy()
    # 父亲与母亲的染色体交叉
    father[a:b], mother[a:b] = mother[a:b], father[a:b]
    # 确保交叉后每一个染色体上的基因都不重复
    for i in range(len(father)):
        if (i < a or i >= b) and (father[i] in mother_unique):
            temp = random.choice(father_unique)
            father[i] = temp
            father_unique.remove(father[i])
        if len(father_unique) == 0:
            break
    father_unique = father_unique_copy.copy()
    for i in range(len(mother)):
        if (i < a or i >= b) and (mother[i] in father_unique):
            temp = random.choice(mother_unique)
            mother[i] = temp
            mother_unique.remove(mother[i])
        if len(mother_unique) == 0:
            break
    return father, mother


# 交叉函数
def crossover(pop, cross_rate):
    # pop = pop.tolist()
    new_pop = copy.deepcopy(pop)
    for i in range(len(pop) // 2):
        # 如果种群只剩一个个体，则不进行繁殖，直接跳出循环
        if len(pop) == 1:
            break
        father = pop[0]
        mom = pop[random.randint(1, len(pop) - 1)]
        pop.remove(father)
        pop.remove(mom)
        if np.random.rand() < cross_rate:
            a, b = np.random.choice(np.arange(0, DNA_size), size=2, replace=False)
            child1, child2 = chromosome_crossover(min(a, b), max(a, b), father, mom)
            child1 = mutation(child1, Pm)
            child2 = mutation(child1, Pm)
            new_pop.append(child1)
            new_pop.append(child2)
    return new_pop


# 变异函数，变异策略采取随机选取两个点，将其对换位置
def mutation(child, mutation_rate):
    if np.random.rand() < mutation_rate:
        a, b = np.random.choice(np.arange(0, DNA_size), size=2, replace=False)
        child[a], child[b] = child[b], child[a]
        # child[min(a, b): max(a, b)] = child[max(a, b)-1:min(a, b)-1:-1]
    return child


def print_info(pop, individual):
    fitness = get_fitness(pop, individual)
    max_fitness_index = fitness.index(max(fitness))
    print("最近距离路线:", pop[max_fitness_index])
    print("距离为:", 1 / max(fitness))
    print("----------------------------------------------------------------------------------------------------")


pop, individual = init_pop(POP_size, DNA_size, K_Bound, X_Bound, Y_Bound)
'''
print(pop)
print(individual)
fitness = get_fitness(pop, individual)
print(fitness)
# fitness = np.asarray(fitness)
# print(fitness/fitness.sum())
'''
for i in range(Generation):
    pop = crossover(pop, Pc)
    fitness = get_fitness(pop, individual)
    pop = select(pop, fitness)
    pop = pop.tolist()
    print_info(pop, individual)

