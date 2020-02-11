from Population import Population
import random
from settings import Settings
from graphics import *
class World:

    def __init__(self):
        self.settings = Settings()
        self._width = self.settings.width
        self._height = self.settings.height
        self._obstaclePercent = self.settings.obstaclePercent

        obstacleNum = self._width * self._height * self._obstaclePercent / 100
        self._path = []
        self._badPoints = []
        self._lines = []

        self.population = Population(self)
        self._maxPath = int(.5 * self._width * self._height)

        # Define drawing parameters
        self._drawOffset = 50
        self._cellSize = 40

        # Init graphics
        self._windowWidth = 2 * self._drawOffset + self._width * self._cellSize
        self._windowHeight = 2 * self._drawOffset + self._height * self._cellSize
        self.backgroundColor = self.colorRGB(.1, .5, .752)
        self.win = GraphWin("Genetic Robot Movement",self._windowWidth,self._windowHeight)
        self.win.setBackground(self.backgroundColor)

        # Create world and place obstacles in it
        self._world = [([0 for _ in range(self._height)]) for _ in range(self._width)]
        self.obstacles = set()

        while self.obstacles.__len__() < obstacleNum:
            self.obstacles.add((random.randint(0, self._width - 1), random.randint(0, self._height - 1)))

        for obs in self.obstacles:
            self._world[obs[0]][obs[1]] = 1

        self.obstacles = list(self.obstacles)

        # Generate starting and ending point
        #  Init version 1
        self._startPoint = (0, 0)
        self._endPoint = (self._width - 1, self._height - 1)

        # Init version 2
        # self._startPoint = self.obstacles[0]
        # self._endPoint = self.obstacles[0]
        while self._startPoint in self.obstacles:
            self._startPoint = (random.randint(0, self._width - 1), random.randint(0, self._height - 1))
        while self._endPoint in self.obstacles or self._endPoint == self._startPoint:
            self._endPoint = (random.randint(0, self._width - 1), random.randint(0, self._height - 1))

        self.reset()

    def howManyCells(self):
        return self._width * self._height

    def generatePopulation(self):
        time.sleep(.5)
        self._populationSize = max(150, int(self._width * self._height / 3))

        self.maxPopulationSize = self._populationSize
        text = None
        header = None
        while self.population.size() < self._populationSize:
            if self.population.size() == 0:
                header = Text(Point(self._windowWidth / 2, self._drawOffset / 2), "Generating first path")
                header.setSize(20)
                header.draw(self.win)

            if self.population.size() % int(self.maxPopulationSize/4):
                text = Text(
                    Point(self._windowWidth / 2, self._drawOffset / 2),
                     "Population Size: " + str(self.population.size()) + "/" + str(self.maxPopulationSize)
                     )
                text.setSize(20)
                text.draw(self.win)

            p = self.generatePath()

            if p.__len__() == 0:
                return False

            self.population.append(p)

            if self.population.size() == 1:
                header.undraw()

            if text is not None:
                text.undraw()
            text = None

        return True

    def reset(self):
        if self._lines.__len__() > 0:
            for l in self._lines:
                l.undraw()
        else:
            for x in range(self._width):
                for y in range(self._height):
                    self.drawCell(Point(x, y), self._world[x][y])

            self.drawPoint(Point(self._startPoint[0], self._startPoint[1]), self._world[self._startPoint[0]][self._startPoint[1]])
            self.drawPoint(Point(self._endPoint[0], self._endPoint[1]), self._world[self._endPoint[0]][self._endPoint[1]])

    def terminate(self):
        # self.win.getMouse()
        self.win.close()

    # Normalized colors
    def colorRGB(self, r, g, b):
        return color_rgb(int(255 * r), int(255 * g), int(255 * b))

    def getCellColor(self, type):
        type = type if type < 2 else 0
        return\
            [
                self.colorRGB(0.41, .85, 0.31),     # Land
                self.colorRGB(0.35, 0.15, 0.15),     # Obstacle
            ][type]

    def getPointColor(self, type):
        return\
            [
                self.colorRGB(0, 0, 1),     # Starting Point
                self.colorRGB(1, 0, 1)      # Ending Point
            ][type - 2]

    def drawCell(self, p, type):
        p1 = Point(p.x * self._cellSize + self._drawOffset, p.y * self._cellSize + self._drawOffset)
        p2 = Point(p1.x + self._cellSize, p1.y + self._cellSize)

        r = Rectangle(p1, p2)
        r.setFill(self.getCellColor(type))
        r.draw(self.win)

    def drawPoint(self, p, type):
        p1 = Point(p.x * self._cellSize + self._drawOffset, p.y * self._cellSize + self._drawOffset)
        p2 = Point(p1.x + self._cellSize, p1.y + self._cellSize)

        r = Oval(p1, p2)
        r.setFill(self.getPointColor(type))
        r.draw(self.win)

    def drawLine(self, p1, p2, color=None):
        p_1 = Point(self._drawOffset + p1.x * self._cellSize + .5*self._cellSize, self._drawOffset + p1.y * self._cellSize + .5*self._cellSize)
        p_2 = Point(self._drawOffset + p2.x * self._cellSize + .5*self._cellSize, self._drawOffset + p2.y * self._cellSize + .5*self._cellSize)
        l = Line(p_1, p_2)
        l.setWidth(10)
        if color is None:
            l.setOutline(self.colorRGB(.1, .5026, .14))
        else:
            l.setOutline(color)

        l.draw(self.win)
        return l

    def getNeighbors(self, point):
        res = list()

        _x, _y = int(point.x), int(point.y)

        for x in range(_x - 1, _x + 2):
            if 0 <= x <= self._width:
                for y in range(_y - 1, _y + 2):
                    try:
                        if 0 <= y <= self._height and not (x == point.x and y == point.y) and self._world[x][y] != 1:
                            res.append(Point(x, y))
                    except Exception as e:
                        pass

        return res

    def cheackPath(self, list, point):
        return any((lambda: point.x == p.x and point.y == p.y)() for p in list)

    def generatePath(self):
        point = Point(self._startPoint[0], self._startPoint[1])
        self._path = []
        self._badPoints = []

        try:
            self._recGenPath(point)

            if self.population.size() == 0:
                self.drawPath(self._path)

            return self._path
        except:
            return None

    def drawPath(self, path, joint=-1, final=False):
        p1 = None
        p2 = None
        ls = []

        for i, p in enumerate(path):
            if p1 is None:
                p1 = p
            elif p2 is None:
                p2 = p
                if joint > -1:
                    if final:
                        ls.append(self.drawLine(p1, p2, self.colorRGB(0.3, 0.7, 0.85)))
                    elif joint < i:
                        ls.append(self.drawLine(p1, p2, self.colorRGB(0.3, 0.1, 0.85)))
                    else:
                        ls.append(self.drawLine(p1, p2, self.colorRGB(0.2, 0., 0.5)))
                else:
                    ls.append(self.drawLine(p1, p2, self.colorRGB(0.9, 0.1, 0)))
                p1 = p2
                p2 = None

        self._lines += ls
        return ls

    def removeCandidate(self, candidates, candidate):
        new_c = list()

        for p in candidates:
            if not self.comparePoints(p, candidate):
                new_c.append(p)

        return new_c

    def _recGenPath(self, point):
        if self.population.size() == 0:
            time.sleep(0.02)
        if self._path.__len__() > 1 and self.population.size() == 0:
            self._lines.append(self.drawLine(point, self._path[self._path.__len__() - 1]))

        if point.x == self._endPoint[0] and point.y == self._endPoint[1]:
            self._path.append(point)
            return 1

        candidates = self.getNeighbors(point)

        while candidates.__len__() > 0:
            candidate = candidates[random.randint(0, candidates.__len__() - 1)]
            if self.cheackPath(self._path, candidate) or self.cheackPath(self._badPoints, candidate):
                candidates = self.removeCandidate(candidates, candidate)
                continue

            self._path.append(point)
            stat = self._recGenPath(candidate)
            if stat == 0:
                candidates = self.removeCandidate(candidates, candidate)

            elif stat == 1:
                return 1

        if self._path.__len__() > 0:
            self._badPoints.append(self._path[self._path.__len__() - 1])
        self._path = self._path[:self._path.__len__() - 1]

        return 0

    def comparePoints(self, p1, p2):
        return p1.x == p2.x and p1.y == p2.y

    def evolve(self):
        gen = 1
        while True:
            gen += 1

            text = Text(Point(self._windowWidth / 2, self._drawOffset / 2), "Generation Number: " + str(gen))
            text.setSize(20)
            text.draw(self.win)

            draw = (gen % 1 == 0)
            if self.settings.drawType > 0:
                draw = (gen % self.settings.drawType == 0)

            if self.population.geneticAlgorithm(draw=draw):
                return True

            text.undraw()

    def plot(self):
        plotW = 800
        plotH = 350
        allGens = self.population.allgenerationAvg
        sortedG = sorted(allGens)
        topVal = sortedG[sortedG.__len__() - 1]
        bottomVal = sortedG[0]

        labelColor = color_rgb(234, 44, 44)
        valColor = color_rgb(59, 13, 11)
        backgroundColor = color_rgb(138, 155, 15)
        graphColor = color_rgb(138, 200, 50)
        lineColor = color_rgb(248, 202, 0)

        graph = GraphWin("Summary", plotW + self._drawOffset * 1.5 + 10, plotH + self._drawOffset)
        graph.setBackground(graphColor)

        r = Rectangle(
            Point(self._drawOffset * 1.5, 10),
            Point(self._drawOffset * 1.5 + plotW, 10 + plotH)
        )

        r.setFill(backgroundColor)
        r.draw(graph)

        dx = plotW / allGens.__len__()
        dy = plotH / (topVal - bottomVal)

        topText = Text(
            Point(self._drawOffset * 1.5 / 2, 15),
            str(int(topVal))
        )
        topText.setSize(20)
        topText.setTextColor(valColor)
        topText.draw(graph)

        bottomText = Text(
            Point(self._drawOffset * 1.5 / 2, plotH),
            str(int(bottomVal))
        )
        bottomText.setSize(20)
        bottomText.setTextColor(valColor)
        bottomText.draw(graph)

        gen0 = Text(
            Point(self._drawOffset * 1.5, plotH + 35),
            "0"
        )
        gen0.setTextColor(valColor)
        gen0.setSize(20)
        gen0.draw(graph)

        genLast = Text(
            Point(self._drawOffset + plotW, plotH + 35),
            str(allGens.__len__())
        )
        genLast.setSize(20)
        genLast.setTextColor(valColor)
        genLast.draw(graph)

        generationText = Text(
            Point(self._drawOffset + plotW / 2, plotH + 35),
            "Generation"
        )
        generationText.setTextColor(labelColor)
        generationText.setSize(17)
        generationText.draw(graph)

        PathText = Text(
            Point(self._drawOffset * 1.5 / 2, plotH / 2),
            "Length"
        )
        PathText.setTextColor(labelColor)
        PathText.setSize(17)
        PathText.draw(graph)

        p1 = None
        p2 = None

        for x, y in enumerate(allGens):
            y = topVal - y

            if p1 is None:
                p1 = Point(1.5 + self._drawOffset * 1.5 + x * dx, 10 + y * dy)
            elif p2 is None:
                p2 = Point(1.5 + self._drawOffset * 1.5 + x * dx, 10 + y * dy)
                l = Line(p1, p2)

                l.setWidth(3)
                l.setFill(lineColor)
                l.draw(graph)
                p1 = p2
                p2 = None

        graph.getMouse()
        graph.close()
        self.win.close()
