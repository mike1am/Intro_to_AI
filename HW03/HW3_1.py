import random
import csv
import copy
import matplotlib.pyplot as plt


BAGS = [10.0, 6.5, 3.2] # максимальные веса рюкзаков и сумок
GEN_SIZE = 80 # размер популяции
SEL_FACTOR = 0.6 # сколько остаётся из старой популяции
MUTATE_FACTOR = 0.2 # вероятность мутации
EVOLUTIONS = 100 # число поколений


def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class Indiv(list):
    CHROMO_DESC = [ # описание элементов хромосомы
        {'tp': int}
    ]

    size = 0
    mutateFactor = 0
    
    def __init__(self, *args) -> None:
        super().__init__(*args)
        if args: # актуально при копировании
            return

        while self.culling():
            self[:] = [
                [el['tp'](random.random() * el.setdefault('lim', 1)) for el in self.CHROMO_DESC]
                for _ in range(self.size)
            ]

    def fitness(self):
        return 0
    
    def culling(self):
        """
        Проверка ограничений. 
        Возвращает True, если проверка не пройдена
        """
        return False
    
    def mutate(self):
        for el in self:
            if random.random() < self.mutateFactor:
                inc = random.choice([-1, 1])
                for i in range(len(self.CHROMO_DESC)):
                    el[i] += inc
                    if el[i] < 0:
                        el[i] = self.CHROMO_DESC[i]['lim'] - 1
                    if el[i] >= self.CHROMO_DESC[i]['lim']:
                        el[i] = 0

    @classmethod
    def generate(cls, parent1, parent2):
        delim = random.randint(1, cls.size - 1)
        newIndiv = parent1.clone()
        newIndiv[delim:] = parent2.clone()[delim:]

        return newIndiv
    
    def clone(self):
        return copy.deepcopy(self)


class Generation(list):
    def __init__(self, size, indivType, selFactor) -> None:
        super().__init__()
        self.size = size
        self.indivType = indivType
        self.selFactor = selFactor

        self.extend([indivType() for _ in range(size)])

    def selection(self):
        self.sort(key=self.indivType.fitness)
        champFit = self[-1].fitness()
        meanFit = sum(map(self.indivType.fitness, self)) / self.size
        
        newLen = int(len(self) * self.selFactor)
        self[:] = self[(len(self) - newLen):]
        
        for _ in range(self.size - newLen):
            while True:
                p1_ind = random.randint(0, newLen - 1)
                p2_ind = p1_ind
                while p2_ind == p1_ind and newLen > 2:
                    p2_ind = random.randint(0, newLen - 1)

                newIndiv = self.indivType.generate(self[p1_ind], self[p2_ind])
                newIndiv.mutate()
                if not newIndiv.culling():
                    break
            # сторго говоря, код нужен, но для скорости можно сократить:
            # newFit = newIndiv.fitness()
            # if newFit > champFit:
            #     champFit = newFit
            self.append(newIndiv)

        return champFit, meanFit


def loadCSV(fileName):
    with open(fileName, encoding="utf-8") as inFile:
        csvReader = csv.DictReader(inFile, delimiter=";")
        return [{
            k.strip(" \ufeff"): (
                int(v)
                if str.isnumeric (v)
                    else float(v)
                    if isFloat(v) else v
            )
            for k, v in itemDict.items()
        } for itemDict in csvReader]


class ThingsLayout(Indiv):
    thingList = []
    bagMaxWeights = []

    CHROMO_DESC = [ # описание элементов хромосомы
        {'tp': int, 'lim': len(BAGS) + 1}
    ]

    # Проверка ограничений по весу
    def culling(self):
        if not self:
            return True # если хромосома пустая, то отбраковка

        weightSums = {}
        for thingNum, chromoEl in enumerate(self):
            if chromoEl[0]:
                bagNum = chromoEl[0] - 1 # поскольку 0 - отсутствие вещи в сумке
                weightSums[bagNum] = weightSums.setdefault(bagNum, 0) + self.thingList[thingNum]['weight']
                if weightSums[bagNum] > self.bagMaxWeights[bagNum]:
                    return True
        return False

    def fitness(self):
        res = 0
        for thingNum, chromoEl in enumerate(self):
            if chromoEl[0]: # если не 0, т.е. вещь взята
                res += self.thingList[thingNum]['value']
        return res


ThingsLayout.thingList = loadCSV(".\\HW3\\items.csv")
ThingsLayout.bagMaxWeights = BAGS
ThingsLayout.size = len(ThingsLayout.thingList)
ThingsLayout.mutateFactor = MUTATE_FACTOR

generation = Generation(GEN_SIZE, ThingsLayout, SEL_FACTOR)

metrics = []
for _ in range(EVOLUTIONS):
    metrics.append(generation.selection())

generation.sort(key=ThingsLayout.fitness)
for bagNum in range(1, len(BAGS) + 1):
    print(f"\nСумка {bagNum}:")
    n = 0
    for i, thing in enumerate(ThingsLayout.thingList):
        if generation[-1][i][0] == bagNum:
            n += 1
            print(f"{n :>3}. {thing['name'] :<25}{thing['weight'] :>6.1f}")

maxValues, meanValues = zip(*metrics)
plt.plot(maxValues, color="red", label="Макс. приспособленность")
plt.plot(meanValues, color="green", label="Средняя приспособленность")
plt.xlabel("Поколение")
plt.ylabel("Приспособленность")
plt.title("Зависимость макс. и средней приспособленности от поколения")
plt.legend()
plt.savefig(".\\HW3\\metrics_fig.png")
