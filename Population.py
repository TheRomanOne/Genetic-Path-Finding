import random
from graphics import *

class Chromeosome:
    def __init__(self, path, eval):
        self.path = path
        self.fitness = path.__len__()
        self.evalutation = self.fitness / eval


class Population:

    def __init__(self, world):
        self.text = None
        self.shortestPath = [x for x in range(world.howManyCells() + 1)]    # Initial list of length width x height
        self.population = list()
        self.allgenerationAvg = list()
        self.totalLengts = 0
        self.world = world

        self._evolutionList = dict()

        self.mutation = self.world.settings.mutation
        self.elitism = self.world.settings.elitism
        self.mutationProp = self.world.settings.mutationProp

    def size(self):
        return self.population.__len__()

    def append(self, p):
        self.population.append(p)
        self.totalLengts += p.__len__()

    def crossover(self, chrom1, chrom2, newGen, draw):
        dist = random.randint(0, int(chrom1.__len__() / 2)) * (1 if random.randint(0, 1) == 1 else -1)
        cut = 1 + int(chrom1.__len__() / 2 + dist)

        reversed2 = chrom2.copy()
        reversed2.reverse()

        child = chrom1[:cut]

        edge = child[child.__len__() - 1]
        for i, x in enumerate(reversed2):
            if self.world.comparePoints(edge, x):
                child += chrom2[chrom2.__len__() - i:]

                if newGen == int(self.world.maxPopulationSize / 2) and draw:
                    self.drawTexts(child)
                    self.world.drawPath(child, cut)

                return child

        return None

    def drawTexts(self, child):
        self.world.reset()

        if self.text is not None:
            self.text.undraw()

        cLen = child.__len__()
        if cLen < self.shortestPath.__len__():
            self.shortestPath = child

        self.text = Text(
            Point(self.world._windowWidth / 2, self.world._windowHeight - self.world._drawOffset / 2),
            "Current path length: " + str(cLen) + "  Shortest path detected: " + str(self.shortestPath.__len__())
        )
        self.text.setSize(20)
        self.text.draw(self.world.win)

    def mutateIndices(self, indices):

        for i in indices:
            for c in range(1, self.population[i].__len__() - 1):

                r = random.randint(0, 10) / 10
                m = self.mutationProp
                if r <= m:
                    preNs = self.world.getNeighbors(self.population[i][c - 1])
                    ns = self.population[i][c]
                    postNs = self.world.getNeighbors(self.population[i][c + 1])

                    # Intersection
                    inters = [p for p in preNs if self.world.cheackPath(postNs, p) and not (p.x == ns.x and p.y == ns.y)]
                    if inters.__len__() > 0:
                        self.population[i][c] = inters[random.randint(0, inters.__len__() - 1)]

    def parentByTournoment(self):
        currentSize = self.population.__len__()
        chrom1 = self.population[random.randint(0, currentSize - 1)]
        chrom2 = self.population[random.randint(0, currentSize - 1)]
        l1 = chrom1.__len__()
        l2 = chrom2.__len__()

        return chrom1 if l1 < l2 else chrom2


    def geneticAlgorithm(self, draw):

        evaluation = self.totalLengts / self.population.__len__()

        if evaluation == self.shortestPath.__len__():
            self.drawTexts(self.shortestPath)
            self.world.drawPath(self.shortestPath)
            return True

        child = None
        evaluatedPopulation = []

        self.allgenerationAvg.append(evaluation)
        self.totalLengts = 0

        for path in self.population:
            evaluatedPopulation.append(Chromeosome(path, evaluation))

        sortedChroms = sorted(evaluatedPopulation, key=lambda x: x.evalutation)
        sortedPopulation = [x.path for x in sortedChroms]
        currentSize = self.population.__len__()

        # ELITISM
        s = int(currentSize * self.elitism / 100)
        newGeneration = sortedPopulation[:s]
        # newGeneration = sorted(self.population, key=lambda x: x.__len__())[:s]


        while newGeneration.__len__() < currentSize:

            # chrom1 = self.population[random.randint(0, currentSize - 1)]
            chrom2 = self.population[random.randint(0, currentSize - 1)]
            # chrom2 = self.parentByTournoment()
            chrom1 = self.parentByTournoment()

            while child is None:
                child = self.crossover(chrom1, chrom2, newGeneration.__len__(), draw=draw)
                if child is not None:
                    try:
                        self._evolutionList[child.__len__()] += 1
                    except:
                        self._evolutionList[child.__len__()] = 1

                    newGeneration.append(child)

            child = None

        # Mutation
        toMutate = set()
        mut = self.population.__len__() * self.mutation / 100
        while toMutate.__len__() < mut:
            i = random.randint(1, newGeneration.__len__() - 2)
            if i in toMutate:
                continue
            toMutate.add(i)
            mut -= 1

        self.population = newGeneration
        self.mutateIndices(toMutate)

        for x in self.population:
            self.totalLengts += x.__len__()
